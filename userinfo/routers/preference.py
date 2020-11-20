from fastapi import APIRouter

router = APIRouter()

@router.get("/preference")
async def get_prefs():
    return {}

