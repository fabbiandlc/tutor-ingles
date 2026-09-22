from fastapi import APIRouter
from app.database.db_profile import get_profile, get_stats
from app.database.db_errors import get_top_errors, get_errors_summary

router = APIRouter()


@router.get("/profile")
async def profile():
    data = await get_profile()
    stats = await get_stats()
    return {**data, **stats}


@router.get("/errors")
async def errors():
    top = await get_top_errors()
    summary = await get_errors_summary()
    return {"top_errors": top, "summary": summary}