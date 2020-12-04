from fastapi import APIRouter

router = APIRouter()

@router.get("/jobs")
async def get_jobs():
    return {}


@router.get("/jobs/{jobid}")
async def get_job(jobid: int):
    return {}

