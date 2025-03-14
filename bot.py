import time
import requests
import random

# 🔹 Данные API
BASE_URL = "https://tvoyhod.online"
LOGIN_URL = f"{BASE_URL}/api/auth/login"
SURVEY_LIST_URL = f"{BASE_URL}/api/survey/list"
SURVEY_DETAIL_URL = f"{BASE_URL}/api/survey/detail"
SURVEY_ANSWER_URL = f"{BASE_URL}/api/survey/answer"
TELEGRAM_BOT_TOKEN = "8066056191:AAED0C-0KtQBRKTsItV60-lAPe-md0eUblw"
TELEGRAM_CHAT_ID = "408805483"

HEADERS = {
    "User-Agent":
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Referer": "https://tvoyhod.online/auth/signin"
}

# 🔹 Данные для входа
data = {"email": "anenko-a@mail.ru", "password": "346123Cfif"}

# 🔹 Авторизация и получение токена
session = requests.Session()
print("🔄 Отправляю данные для входа...")
response = session.post(LOGIN_URL, json=data, headers=HEADERS)

if response.status_code == 200:
    response_data = response.json()
    token = response_data.get("token")
    if not token:
        print("❌ Ошибка: токен не найден в ответе сервера!")
        exit()
    print("✅ Успешная авторизация! Токен сохранен.")
    HEADERS["Authorization"] = f"Bearer {token}"
else:
    print(f"❌ Ошибка авторизации: {response.status_code}")
    print("Ответ сервера:", response.text)
    exit()


# 🔹 Отправка уведомлений в Telegram
def send_telegram_message(text):
    """Отправляет уведомление в Telegram"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": text}
    requests.post(url, json=payload)


# 🔹 Получение деталей опроса
def get_survey_details(survey_id):
    """Получает детали опроса"""
    response = session.get(f"{SURVEY_DETAIL_URL}/{survey_id}", headers=HEADERS)
    if response.status_code == 200:
        return response.json()
    else:
        print(
            f"⚠️ Ошибка при получении деталей опроса {survey_id}: {response.status_code}"
        )
        return None


# 🔹 Генерация ответов
def generate_answers(questions):
    """Генерирует автоматические ответы на вопросы"""
    answers = {}
    for question in questions:
        q_id = question["id"]
        q_options = question.get("options", [])

        if q_options:
            answer = random.choice(q_options)  # Выбираем случайный вариант
        else:
            answer = "Не знаю"  # Ответ по умолчанию

        answers[q_id] = answer

    return answers


# 🔹 Прохождение опроса
def complete_survey(survey_id):
    """Функция автоматического прохождения опроса"""
    details = get_survey_details(survey_id)
    if not details:
        return

    questions = details.get("questions", [])
    if not questions:
        print(f"⚠️ Опрос {survey_id} не содержит вопросов.")
        return

    answers = generate_answers(questions)

    payload = {"survey_id": survey_id, "answers": answers}

    response = session.post(SURVEY_ANSWER_URL, json=payload, headers=HEADERS)
    if response.status_code == 200:
        print(f"✅ Опрос {survey_id} успешно пройден!")
        send_telegram_message(f"✅ Опрос {survey_id} пройден автоматически!")
    else:
        print(
            f"⚠️ Ошибка при прохождении опроса {survey_id}: {response.status_code}"
        )
        send_telegram_message(f"⚠️ Ошибка при прохождении опроса {survey_id}")


# 🔹 Проверка новых опросов
def check_new_surveys():
    """Функция для проверки новых опросов."""
    response = session.get(SURVEY_LIST_URL, headers=HEADERS)

    if response.status_code == 200:
        try:
            surveys = response.json()
            new_surveys = [s for s in surveys if "id" in s]

            if new_surveys:
                print("🆕 Найдены новые опросы:")
                for survey in new_surveys:
                    print(f"- {survey['title']}")
                    send_telegram_message(
                        f"🆕 Найден новый опрос: {survey['title']}")
                    complete_survey(survey["id"])
            else:
                print("✅ Новых опросов нет.")
        except requests.exceptions.JSONDecodeError:
            print(
                "⚠️ Ошибка обработки JSON: сервер вернул некорректный ответ.")
    else:
        print(
            f"⚠️ Ошибка при получении списка опросов: {response.status_code}")


# 🔹 Запуск мониторинга
print("🚀 Начинаем мониторинг опросов...")
while True:
    check_new_surveys()
    time.sleep(600)  # Проверяем раз в минуту
