import json
import logging
import os
import re

from dotenv import load_dotenv
from g4f.client import Client
from telethon import TelegramClient, events

from api.post_vacancy import send_vacancy

load_dotenv()

logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)
logging.getLogger('pika').setLevel(logging.WARNING)
log = logging.getLogger()

client = TelegramClient(session=os.getenv("SESSION_NAME"), api_id=int(os.getenv('API_ID')),
                        api_hash=os.getenv('API_HASH'))
all_chats = []

phone = os.getenv("PHONE")
password = os.getenv("PASS")


async def is_valid_json(text):
    try:
        json.loads(text)
        return True
    except json.JSONDecodeError:
        return False


async def json_to_dict(json_message):
    if "```json" in json_message:
        pattern = re.compile(r'```json(.*?)```', re.DOTALL)
        matches = pattern.findall(json_message)
        json_objects = [
            json.loads(match.strip())
            for match in matches
            if await is_valid_json(match.strip())
        ]

        return json_objects[0]
    else:
        return json.loads(json_message.replace("\n", ""))


def get_prompt(text):
    prompt = (
        "Проанализируй текст и скажи, является ли это вакансией/проектом с поиском разработчиков. Ответ дай в "
        'формате JSON СТРОГО по шаблону:{"vacancy": true/false} и никаких лишних символов.'
        f"Текст: {text}"
    )
    return prompt


@client.on(events.NewMessage(chats=all_chats))
async def my_event_handler(event):
    msg = event.text
    ai_client = Client()
    log.info(f"Получено сообщение с канала {event.chat_id}. Начинаю обработку!")
    response = ai_client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system",
             "content": "Ты продвинутый анализатор текста"
             },
            {"role": "user",
             "content": get_prompt(msg)}
        ]
    )
    result = response.choices[0].message.content
    result_dict = await json_to_dict(json_message=result)
    if result_dict['vacancy']:
        log.info(f"Сообщение с канала {event.chat_id} отправляю в CMS!")
        response = await send_vacancy(msg, str(event.chat_id))
        if response:
            pass


async def main():
    log.info("Получаю список каналов.")
    async for dialog in client.iter_dialogs():
        if dialog.is_channel:
            all_chats.append(dialog.id)


if __name__ == "__main__":
    log.info("Запуск...")
    with client.start(phone=lambda: phone, password=lambda: password):
        client.session.save()
        client.loop.run_until_complete(main())
        log.info("Получен список каналов. Начинаю слушать")
        client.run_until_disconnected()
