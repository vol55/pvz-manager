import os
from datetime import datetime, timezone

from aiogram.enums import ChatMemberStatus
from aiogram.utils.web_app import safe_parse_webapp_init_data
from fastapi import HTTPException, Header
from fastapi import Request

from config.reference import POSITIONS, PVZ_LIST

BOT_TOKEN = os.getenv("BOT_WORKERS_TOKEN", "")
TELEGRAM_GROUP = os.getenv("WORKERS_GROUP", -1)
MAX_AGE_SECONDS = 60 * 60


async def validate_user(
        request: Request,
        x_telegram_init_data: str = Header(..., alias="X-Telegram-Init-Data"),
):
    """
    Проверяет авторизацию пользователя по состоянию в группе Telegram
    """
    bot = request.app.state.bot

    try:
        data = safe_parse_webapp_init_data(
            token=BOT_TOKEN,
            init_data=x_telegram_init_data,
        )
    except ValueError:
        raise HTTPException(status_code=401, detail="Ошибка аутентификации")

    if not data.user:
        raise HTTPException(status_code=401, detail="Ошибка аутентификации")

    age = (datetime.now(timezone.utc) - data.auth_date).total_seconds()
    if age > MAX_AGE_SECONDS:
        raise HTTPException(status_code=401, detail="Сессия истекла")

    member = await bot.get_chat_member(
        chat_id=TELEGRAM_GROUP,
        user_id=data.user.id,
    )

    if member.status not in {
        ChatMemberStatus.MEMBER,
        ChatMemberStatus.ADMINISTRATOR,
        ChatMemberStatus.CREATOR,
    }:
        raise HTTPException(status_code=403, detail="Необходимо состоять в группе")

    return data


def validate_profile_form(form):
    """
    Проверяет и очищает данные формы профиля перед сохранением
    """

    data = {
        "last_name": strip_or_none("last_name"),
        "first_name": strip_or_none("first_name"),
        "position": strip_or_none("position"),
        "phone": strip_or_none("phone"),
        "salary_pickup_point": strip_or_none("salary_pickup_point"),
        "salary_payment_method": strip_or_none("salary_payment_method"),
        "salary_card_number": strip_or_none("salary_card_number"),
        "salary_phone_number": strip_or_none("salary_phone_number"),
        "salary_recipient": strip_or_none("salary_recipient"),
        "bank_name": strip_or_none("bank_name"),
    }

    # Required
    if not data["last_name"]:
        raise ValueError("Фамилия обязательна")
    if not data["first_name"]:
        raise ValueError("Имя обязательно")
    if not data["position"]:
        raise ValueError("Должность обязательна")
    if not data["phone"]:
        raise ValueError("Телефон обязателен")
    if not data["salary_pickup_point"]:
        raise ValueError("ПВЗ обязателен")

    # Max lengths (ПВЗ: ВАЖНО согласовать с DB!)
    if len(data["last_name"]) > 100:
        raise ValueError("Слишком длинная фамилия")
    if len(data["first_name"]) > 100:
        raise ValueError("Слишком длинное имя")
    if len(data["position"]) > 100:
        raise ValueError("Слишком длинная должность")
    if len(data["phone"]) > 18:
        raise ValueError("Слишком длинный телефон")

    if len(data["salary_pickup_point"]) > 100:
        raise ValueError("Слишком длинный ПВЗ")

    if len(data["salary_payment_method"]) > 50:
        raise ValueError("Слишком длинный способ выплаты")
    if len(data["salary_card_number"]) > 50:
        raise ValueError("Слишком длинный номер карты")
    if len(data["salary_phone_number"]) > 18:
        raise ValueError("Слишком длинный номер телефона")
    if len(data["salary_recipient"]) > 255:
        raise ValueError("Слишком длинный получатель")
    if len(data["bank_name"]) > 100:
        raise ValueError("Слишком длинное название банка")

    if data["position"] not in POSITIONS:
        raise ValueError("Некорректная должность")
    if data["salary_pickup_point"] not in PVZ_LIST:
        raise ValueError("Выберите ПВЗ из списка")

    allowed_methods = {"", "На карту", "По номеру телефона"}
    if data["salary_payment_method"] not in allowed_methods:
        raise ValueError("Некорректный способ выплаты")

    phone_digits = digits(data["phone"])
    if len(phone_digits) != 11 or phone_digits[0] not in "8":
        raise ValueError("Введите корректный телефон: 8 (123) 456-78-90")
    data["phone"] = phone_digits

    method = data["salary_payment_method"]

    if method == "На карту":
        card_digits = digits(data["salary_card_number"])
        if len(card_digits) > 35:
            raise ValueError("Укажите корректный номер карты")
        data["salary_card_number"] = card_digits
        if not data["salary_recipient"]:
            raise ValueError("Укажите получателя")
        if not data["bank_name"]:
            raise ValueError("Укажите банк")
        data["salary_phone_number"] = ""

    elif method == "По номеру телефона":
        sp = digits(data["salary_phone_number"])
        if len(sp) != 11 or sp[0] not in ("7", "8"):
            raise ValueError("Укажите корректный номер телефона для ЗП")
        data["salary_phone_number"] = sp
        data["salary_card_number"] = ""
        if not data["salary_recipient"]:
            raise ValueError("Укажите получателя")
        if not data["bank_name"]:
            raise ValueError("Укажите банк")

    else:
        data["salary_card_number"] = ""
        data["salary_phone_number"] = ""
        data["salary_recipient"] = ""
        data["bank_name"] = ""

    return data

def strip_or_none(key: str) -> str:
    value = form.get(key)
    if value is None:
        return ""
    return str(value).strip()

def digits(v: str) -> str:
    return "".join(ch for ch in (v or "") if ch.isdigit())
