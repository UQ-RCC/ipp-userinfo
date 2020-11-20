from fastapi import APIRouter

router = APIRouter()

@router.get("/job")
async def get_jobs():
    return {}

