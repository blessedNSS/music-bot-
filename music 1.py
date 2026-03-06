import os
import asyncio
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile
from aiogram.filters import CommandStart, Command
import yt_dlp

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher()

def search_and_download(query: str):
    ydl_opts = {'ffmpeg_location': '/opt/homebrew/bin', 'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': '%(id)s.%(ext)s',
        'quiet': True,
        'noplaylist': True
    }
    if not query.startswith('http'):
        query = f"ytsearch1:{query}"
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(query, download=True)

    if 'entries' in info:
        if not info['entries']:
            raise Exception("Ничего не найдено")
        info = info['entries'][0]

    filename = f"{info['id']}.mp3"
    title = info.get('title', 'Unknown Title')
    performer = info.get('uploader', 'Unknown Artist')
    return filename, title, performer


@dp.message(CommandStart())
async def cmd_start(message: types.Message):

    main_kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🔍 Найти песню")],  # Первый ряд
            [KeyboardButton(text="❓ Помощь")]  # Второй ряд
        ],
        resize_keyboard=True,
        input_field_placeholder="Выбери действие..."
    )

    insta_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📸 Мой Instagram", url="https://www.instagram.com/3888nss")]
    ])


    await message.answer(
        "Привет! Я готов к работе. Используй кнопку внизу для поиска треков. 🎵",
        reply_markup=main_kb
    )


    await message.answer(
        "А здесь ты можешь найти мой Instagram:",
        reply_markup=insta_kb
    )

@dp.message(Command('site'))
async def site_command(message: types.Message):
    await message.answer("Вот ссылка на сайт: https://music.youtube.com/")


@dp.message(F.text == "🔍 Найти песню")
async def start_search_btn(message: types.Message):
    await message.answer("Отлично! Просто введи название песни или исполнителя, и я начну поиск. 👇")


@dp.message(F.text == "❓ Помощь")
async def help_btn(message: types.Message):
    # Здесь ты можешь написать абсолютно любой свой текст.
    # \n означает перенос на новую строку.
    my_help_text = (
        "🤖 **Справка по боту:**\n\n"
        "1. Просто отправь мне название песни или имя артиста. ✍️\n"
        "2. поддержать создателя - 4441 1111 3567 9144 💳\n"
        "3. Если возникнут вопросы, пиши мне в инст! 🧑🏻‍💻\n"
        "4. /site- для перехода на ютуб мюзик. 🎶\n\n"
        "Приятного прослушивания! 🎧"
    )

    await message.answer(text=my_help_text, parse_mode="Markdown")


@dp.message(F.text)
async def handle_music_request(message: types.Message):
    query = message.text
    status_msg = await message.reply("поиск...")

    try:
        filename, title, performer = await asyncio.to_thread(search_and_download, query)
        await status_msg.edit_text("✅ Трек найден! Отправляю...")

        audio = FSInputFile(filename)

        await message.reply_audio(
            audio=audio,
            title=title,
            performer=performer
        )
        os.remove(filename)
        await status_msg.delete()
    except Exception as e:
        await status_msg.edit_text("😔 Не удалось найти или скачать этот трек. Попробуй уточнить запрос.")
        print(f"Ошибка: {e}")


async def main():
    print("Бот запущен и готов искать музыку!")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
