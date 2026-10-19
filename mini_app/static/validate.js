// Отправляет запрос на сервер для авторизации пользователя
async function validate() {
  const initData = tg?.initData || "";

  const r = await fetch(`${prefix}/api/auth`, {
    method: "POST",
    headers: {
      "X-Telegram-Init-Data": initData,
    },
  });

  let payload = {};
  try {
    payload = await r.json();
  } catch (_) {
    payload = {};
  }

  if (!r.ok) {
    throw new Error(payload.detail || "Ошибка авторизации");
  }

  return payload;
}
