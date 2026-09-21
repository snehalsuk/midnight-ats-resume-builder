from fastapi import APIRouter

from app.api.v1 import ai_tailoring, ats, auth, export, job_descriptions, resumes

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(resumes.router)
api_router.include_router(job_descriptions.router)
api_router.include_router(ats.router)
api_router.include_router(export.router)
api_router.include_router(ai_tailoring.router)
