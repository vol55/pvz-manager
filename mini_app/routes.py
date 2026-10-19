import os
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from config.config import settings
from config.reference import BANKS, PVZ_LIST, POSITIONS
from dao.profiles import ProfilesDAO
from mini_app.validators import validate_user, validate_profile_form
from redis_dao.manager import redis_manager

BASE_DIR = Path(__file__).resolve().parent

router = APIRouter(prefix=f'/{os.getenv("MINI_APP_PREFIX")}')
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


@router.post("/api/load-profile")
async def load_profile(data=Depends(validate_user)):
    profile = await ProfilesDAO.get(data.user.id)
    if not profile:
        return {"profile": None}

    return {
        "profile": {
            "last_name": profile.last_name,
            "first_name": profile.first_name,
            "position": profile.position,
            "phone": profile.phone,
            "pvz": profile.pvz,
            "payment_method": profile.payment_method,
            "salary_card": profile.salary_card,
            "salary_phone": profile.salary_phone,
            "recipient": profile.recipient,
            "bank": profile.bank,
        }
    }


@router.get("/edit-profile", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse(
        "edit_profile.html",
        {
            "request": request,
            "banks": BANKS,
            "pvz_list": PVZ_LIST,
            "positions": POSITIONS,
        },
    )


@router.post("/edit-profile")
async def post_profile(
        request: Request,
        data=Depends(validate_user),
):
    form = await request.form()

    try:
        cleaned = validate_profile_form(form)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Не удалось сохранить данные. Проверьте поля и попробуйте ещё раз",
        )

    profile = await ProfilesDAO.get(data.user.id)

    payload = {
        "position": cleaned["position"],
        "phone": cleaned["phone"],
        "pvz": cleaned["salary_pickup_point"],
        "payment_method": cleaned["salary_payment_method"],
        "salary_card": cleaned["salary_card_number"],
        "salary_phone": cleaned["salary_phone_number"],
        "recipient": cleaned["salary_recipient"],
        "bank": cleaned["bank_name"],
        "uploaded": False,
    }

    if profile:
        await ProfilesDAO.update(
            data.user.id,
            **payload,
        )
        return {
            "ok": True,
            "message": "Данные сохранены",
            "toast": "snack",
            "duration_ms": 4000,
        }

    await ProfilesDAO.save(
        telegram_id=data.user.id,
        last_name=cleaned["last_name"].title(),
        first_name=cleaned["first_name"].title(),
        **payload,
    )
    return {
        "ok": True,
        "message": "Данные сохранены",
        "toast": "alert",
        "close_on_ok": True,
    }


@router.post("/api/rating")
async def get_rating(data=Depends(validate_user)):
    redis = redis_manager.get_client()
    return {
        "id": data.user.id,
        "employees": await redis.get_json(settings.REDIS_KEY_EMPLOYEE_STATISTICS)
    }


@router.get("/rating", response_class=HTMLResponse)
async def rating_page(request: Request):
    return templates.TemplateResponse(
        "rating.html",
        {
            "request": request,
        },
    )
