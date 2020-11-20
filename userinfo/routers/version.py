from fastapi import APIRouter

router = APIRouter()

@router.get("/version")
async def get_version():
    return {"version": "0.0.1"}

