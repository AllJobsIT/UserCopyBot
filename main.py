import asyncio
import json
import logging
import os
import re

from aiohttp import ClientSession
from dotenv import load_dotenv
from openai import Client as AIClient
from pyrogram import Client, filters, idle

from api.post_vacancy import send_vacancy

load_dotenv()

logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)
logging.getLogger('pika').setLevel(logging.WARNING)
log = logging.getLogger()

all_chats = []

phone = os.getenv("PHONE")
password = os.getenv("PASS")

app = Client(name=os.getenv("SESSION_NAME"), api_id=int(os.getenv('API_ID')),
             api_hash=os.getenv('API_HASH'), phone_number=phone, password=password)
session = ClientSession()


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


@app.on_message(filters.text)
async def my_event_handler(_, message):
    msg = message.text
    ai_client = AIClient()
    log.info(f"Получено сообщение с канала {message.chat.id}. Начинаю обработку!")
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
        log.info(f"Сообщение с канала {message.chat.id} отправляю в CMS!")
        response = await send_vacancy(msg, str(message.chat.id))
        if response:
            pass


@app.on_message(filters.command("ping") & filters.chat("me"))
async def test(_, message):
    await message.reply("PONG")


async def start():
    await app.start()
    print("Bot started!")
    await idle()
    await session.close()


loop = asyncio.get_event_loop()
loop.run_until_complete(start())
