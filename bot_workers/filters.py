import os

from aiogram.enums import ChatMemberStatus, ChatType
from aiogram.types import Message
from loguru import logger

TELEGRAM_GROUP = os.getenv("WORKERS_GROUP")


async def is_in_group(message: Message) -> bool:
    """
    Проверяет, состоит ли пользователь в  Telegram-группе сотрудников.
    """
    try:
        member = await message.bot.get_chat_member(chat_id=TELEGRAM_GROUP, user_id=message.from_user.id)
        return member.status in {
            ChatMemberStatus.MEMBER,
            ChatMemberStatus.ADMINISTRATOR,
            ChatMemberStatus.CREATOR,
        }
    except Exception as e:
        logger.exception(e)
        return False


async def is_in_private_chat(message: Message) -> bool:
    """
    Проверяет, отправлено ли сообщение в личном чате с ботом.
    """
    return message.chat.type == ChatType.PRIVATE
