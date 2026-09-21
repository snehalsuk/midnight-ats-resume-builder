from app.ats.jd_sanitizer import sanitize_atomic_terms


def test_drops_full_sentences():
    terms = [
        "TypeScript",
        "Strong hands-on experience with TypeScript and JavaScript",
        "React.js",
        "Experience implementing JWT-based authentication and authorization",
        "Node.js",
        "3-6 years of professional software development experience",
    ]
    result = sanitize_atomic_terms(terms)
    assert result == ["TypeScript", "React.js", "Node.js"]


def test_keeps_multi_word_atomic_terms():
    terms = ["React.js", "Spring Boot", "Role-Based Access Control (RBAC)", "CI/CD"]
    result = sanitize_atomic_terms(terms)
    assert set(result) == set(terms)


def test_drops_empty_and_trailing_period_entries():
    terms = ["Docker", "", "Kubernetes."]
    assert sanitize_atomic_terms(terms) == ["Docker"]
