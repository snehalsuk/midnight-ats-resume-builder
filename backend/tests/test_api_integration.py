"""End-to-end API integration test for the core upload -> edit -> analyze ->
export flow (spec §42)."""

from app.core.db import SessionLocal
from app.repositories.job_description_repo import JobDescriptionRepository
from app.schemas.job_description import ParsedJobDescription


def test_ats_analyze_respects_job_description_id(client, auth_headers, sample_resume_pdf_bytes):
    """Regression test: AtsAnalyzeRequest must accept camelCase
    `jobDescriptionId` like every other request body in this API — a prior
    bug had it snake_case-only, so the field was silently dropped and the
    score always came back as if no JD had been selected."""
    r = client.post(
        "/api/v1/resumes/upload",
        headers=auth_headers,
        files={"file": ("sample_resume.pdf", sample_resume_pdf_bytes, "application/pdf")},
    )
    resume_id = r.json()["id"]
    owner_id = r.json()["id"] and client.get("/api/v1/auth/me", headers=auth_headers).json()["id"]

    db = SessionLocal()
    try:
        jd = JobDescriptionRepository(db).create(
            owner_id=owner_id,
            company="Acme",
            raw_text="Need a Java Spring Boot React.js developer.",
            parsed=ParsedJobDescription(job_title="Java Developer", required_skills=["Java", "Spring Boot", "React.js"]),
        )
        jd_id = jd.id
    finally:
        db.close()

    r = client.post(f"/api/v1/resumes/{resume_id}/ats/analyze", headers=auth_headers, json={"jobDescriptionId": jd_id})
    assert r.status_code == 200
    body = r.json()
    assert body["keywordMatchPct"] > 0
    assert "Java" in body["matchedKeywords"]


def test_full_resume_lifecycle(client, auth_headers, sample_resume_pdf_bytes):
    # upload
    r = client.post(
        "/api/v1/resumes/upload",
        headers=auth_headers,
        files={"file": ("sample_resume.pdf", sample_resume_pdf_bytes, "application/pdf")},
    )
    assert r.status_code == 201, r.text
    resume = r.json()
    resume_id = resume["id"]
    assert resume["personalInfo"]["name"] == "SNEHAL SUKHADEVE"
    assert resume["kind"] == "MASTER"

    # fetch
    r = client.get(f"/api/v1/resumes/{resume_id}", headers=auth_headers)
    assert r.status_code == 200

    # edit summary text
    data = r.json()
    for s in data["sections"]:
        if s["type"] == "summary":
            s["content"]["text"] = "Updated summary text for testing."
    r = client.put(f"/api/v1/resumes/{resume_id}", headers=auth_headers, json={"sections": data["sections"]})
    assert r.status_code == 200
    assert any(s["content"]["text"] == "Updated summary text for testing." for s in r.json()["sections"] if s["type"] == "summary")

    # ATS analyze without JD
    r = client.post(f"/api/v1/resumes/{resume_id}/ats/analyze", headers=auth_headers, json={})
    assert r.status_code == 200
    assert r.json()["parsingAccuracyPct"] == 100.0

    # quality gate
    r = client.post(f"/api/v1/resumes/{resume_id}/validate", headers=auth_headers)
    assert r.status_code == 200
    assert r.json()["passed"] is True

    # export pdf
    r = client.post(f"/api/v1/resumes/{resume_id}/export/pdf", headers=auth_headers)
    assert r.status_code == 200
    assert r.json()["pageCount"] == 1
    assert r.json()["filename"].endswith(".pdf")

    # export docx
    r = client.post(f"/api/v1/resumes/{resume_id}/export/docx", headers=auth_headers)
    assert r.status_code == 200
    assert r.json()["filename"].endswith(".docx")

    # versions list (should be empty — no tailored version created yet)
    r = client.get(f"/api/v1/resumes/{resume_id}/versions", headers=auth_headers)
    assert r.status_code == 200
    assert r.json() == []

    # duplicate
    r = client.post(f"/api/v1/resumes/{resume_id}/duplicate", headers=auth_headers)
    assert r.status_code == 201
    assert r.json()["id"] != resume_id


def test_resume_diff_detects_modified_section(client, auth_headers, sample_resume_pdf_bytes):
    r = client.post(
        "/api/v1/resumes/upload",
        headers=auth_headers,
        files={"file": ("sample_resume.pdf", sample_resume_pdf_bytes, "application/pdf")},
    )
    master_id = r.json()["id"]

    r = client.post(f"/api/v1/resumes/{master_id}/duplicate", headers=auth_headers)
    version = r.json()
    for s in version["sections"]:
        if s["type"] == "summary":
            s["content"]["text"] = "A completely different tailored summary."
    client.put(f"/api/v1/resumes/{version['id']}", headers=auth_headers, json={"sections": version["sections"]})

    r = client.get(f"/api/v1/resumes/{master_id}/diff", headers=auth_headers, params={"compare_to_id": version["id"]})
    assert r.status_code == 200
    body = r.json()
    assert any(m["section"] == "PROFESSIONAL SUMMARY" for m in body["modified"])
    assert "TECHNICAL SKILLS" in body["unchanged"]


def test_preview_returns_authoritative_page_count(client, auth_headers, sample_resume_pdf_bytes):
    """Regression: the preview endpoint must return a real WeasyPrint-
    derived page count (matching what Export will actually produce), not
    just HTML — the on-screen HTML's height in a browser is not a
    reliable proxy for real PDF pagination (different font metrics, and
    @page margins aren't honored by browsers at all)."""
    r = client.post(
        "/api/v1/resumes/upload",
        headers=auth_headers,
        files={"file": ("sample_resume.pdf", sample_resume_pdf_bytes, "application/pdf")},
    )
    resume = r.json()

    r = client.post(
        f"/api/v1/resumes/{resume['id']}/preview",
        headers=auth_headers,
        json={"personalInfo": resume["personalInfo"], "sections": resume["sections"]},
    )
    assert r.status_code == 200
    body = r.json()
    assert "html" in body and len(body["html"]) > 0
    assert isinstance(body["pageCount"], int) and body["pageCount"] >= 1


def test_upload_rejects_unsupported_file_type(client, auth_headers):
    r = client.post(
        "/api/v1/resumes/upload",
        headers=auth_headers,
        files={"file": ("malware.exe", b"MZ\x90\x00fake exe content", "application/octet-stream")},
    )
    assert r.status_code == 415
    body = r.json()
    assert body["success"] is False
    assert body["errorCode"] == "UNSUPPORTED_FILE_TYPE"


def test_unauthenticated_request_is_rejected(client):
    r = client.get("/api/v1/resumes")
    assert r.status_code == 401
    assert r.json()["success"] is False


def test_register_and_login_flow(client):
    r = client.post(
        "/api/v1/auth/register",
        json={"email": "flow@example.com", "password": "supersecret1", "firstName": "Flow", "lastName": "Test"},
    )
    assert r.status_code == 201
    assert r.json()["firstName"] == "Flow"

    r = client.post("/api/v1/auth/login", json={"email": "flow@example.com", "password": "supersecret1"})
    assert r.status_code == 200
    assert "accessToken" in r.json()

    r = client.post("/api/v1/auth/login", json={"email": "flow@example.com", "password": "wrongpassword"})
    assert r.status_code == 401
