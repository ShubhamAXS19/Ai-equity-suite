from fastapi import APIRouter
from app.config import COMPANIES

router = APIRouter(prefix="/api", tags=["companies"])


@router.get("/companies")
def list_companies():
    return {"companies": COMPANIES}
