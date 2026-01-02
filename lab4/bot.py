"""
Telegram-бот "GameInfo Bot" для получения информации о компьютерных играх.
Использует RAWG API (https://rawg.io/apidocs)

Функционал:
1. Поиск игры по названию
2. Топ игр по выбранному жанру
3. Случайная игра (рекомендация)
4. Сохранение пользовательских настроек (любимый жанр)

Автор: [Ваше имя]
Дата: 2025
"""

import asyncio
import logging
import random
from typing import Optional
import aiohttp
from aiogram import Bot, Dispatcher, Router, F
from aiogram.filters import Command, CommandStart
from aiogram.types import (
    Message, 
    CallbackQuery,
    InlineKeyboardMarkup, 
    InlineKeyboardButton
)
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

# ===================== КОНФИГУРАЦИЯ =====================

# Токен Telegram-бота 
TELEGRAM_TOKEN = "8010730641:AAGGADZCdhDPhZSDrrBZhPoknUDScA4bNPY"

# API ключ RAWG 
RAWG_API_KEY = "b39195717641407d83117fec2a4a30f5"

# Базовый URL для RAWG API
RAWG_BASE_URL = "https://api.rawg.io/api"

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# ===================== ХРАНИЛИЩЕ ДАННЫХ =====================

# Словарь для хранения пользовательских настроек (в реальном проекте лучше использовать БД)
user_settings: dict[int, dict] = {}

# Доступные жанры игр (id и название из RAWG API)
GENRES = {
    4: "Action",
    51: "Indie", 
    3: "Adventure",
    5: "RPG",
    10: "Strategy",
    2: "Shooter",
    40: "Casual",
    14: "Simulation",
    7: "Puzzle",
    11: "Arcade",
    83: "Platformer",
    1: "Racing",
    15: "Sports",
    6: "Fighting",
    59: "Massively Multiplayer"
}

# ===================== СОСТОЯНИЯ FSM =====================

class SearchStates(StatesGroup):
    """Состояния для поиска игры"""
    waiting_for_game_name = State()

class SettingsStates(StatesGroup):
    """Состояния для настроек"""
    waiting_for_genre = State()

# ===================== ИНИЦИАЛИЗАЦИЯ =====================

router = Router()

# ===================== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ =====================

async def fetch_api(session: aiohttp.ClientSession, endpoint: str, params: dict = None) -> Optional[dict]:
    """
    Выполняет GET-запрос к RAWG API.
    
    Args:
        session: Сессия aiohttp
        endpoint: Конечная точка API (например, "/games")
        params: Параметры запроса
    
    Returns:
        Словарь с данными или None при ошибке
    
    Raises:
        aiohttp.ClientError: При ошибке сети
    """
    if params is None:
        params = {}
    params["key"] = RAWG_API_KEY
    
    url = f"{RAWG_BASE_URL}{endpoint}"
    
    try:
        async with session.get(url, params=params, timeout=10) as response:
            if response.status == 200:
                return await response.json()
            elif response.status == 401:
                logger.error("Ошибка авторизации API. Проверьте API ключ.")
                return None
            elif response.status == 404:
                logger.warning(f"Ресурс не найден: {endpoint}")
                return None
            else:
                logger.error(f"Ошибка API: статус {response.status}")
                return None
    except asyncio.TimeoutError:
        logger.error("Превышено время ожидания запроса к API")
        return None
    except aiohttp.ClientError as e:
        logger.error(f"Ошибка сети: {e}")
        return None


def format_game_info(game: dict) -> str:
    """
    Форматирует информацию об игре для отправки пользователю.
    
    Args:
        game: Словарь с данными игры из API
    
    Returns:
        Отформатированная строка с информацией
    """
    name = game.get("name", "Неизвестно")
    released = game.get("released", "Неизвестно")
    rating = game.get("rating", 0)
    metacritic = game.get("metacritic", "N/A")
    
    # Получаем жанры
    genres = game.get("genres", [])
    genres_str = ", ".join([g["name"] for g in genres]) if genres else "Не указаны"
    
    # Получаем платформы
    platforms = game.get("platforms", [])
    platforms_str = ", ".join([p["platform"]["name"] for p in platforms[:5]]) if platforms else "Не указаны"
    if len(platforms) > 5:
        platforms_str += f" и ещё {len(platforms) - 5}"
    
    # Формируем сообщение
    message = (
        f"🎮 <b>{name}</b>\n\n"
        f"📅 Дата выхода: {released}\n"
        f"⭐ Рейтинг: {rating}/5\n"
        f"📊 Metacritic: {metacritic}\n"
        f"🏷 Жанры: {genres_str}\n"
        f"🖥 Платформы: {platforms_str}"
    )
    
    return message


def get_genre_keyboard() -> InlineKeyboardMarkup:
    """
    Создаёт клавиатуру с выбором жанров.
    
    Returns:
        InlineKeyboardMarkup с кнопками жанров
    """
    buttons = []
    row = []
    
    for genre_id, genre_name in GENRES.items():
        row.append(InlineKeyboardButton(
            text=genre_name,
            callback_data=f"genre_{genre_id}"
        ))
        if len(row) == 3:
            buttons.append(row)
            row = []
    
    if row:
        buttons.append(row)
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_settings_genre_keyboard() -> InlineKeyboardMarkup:
    """
    Создаёт клавиатуру с выбором жанров для настроек.
    
    Returns:
        InlineKeyboardMarkup с кнопками жанров
    """
    buttons = []
    row = []
    
    for genre_id, genre_name in GENRES.items():
        row.append(InlineKeyboardButton(
            text=genre_name,
            callback_data=f"setgenre_{genre_id}"
        ))
        if len(row) == 3:
            buttons.append(row)
            row = []
    
    if row:
        buttons.append(row)
    
    # Добавляем кнопку сброса
    buttons.append([InlineKeyboardButton(
        text="❌ Сбросить настройки",
        callback_data="setgenre_reset"
    )])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_main_keyboard() -> InlineKeyboardMarkup:
    """
    Создаёт главную клавиатуру бота.
    
    Returns:
        InlineKeyboardMarkup с основными командами
    """
    buttons = [
        [InlineKeyboardButton(text="🔍 Поиск игры", callback_data="main_search")],
        [InlineKeyboardButton(text="🏆 Топ по жанру", callback_data="main_top")],
        [InlineKeyboardButton(text="🎲 Случайная игра", callback_data="main_random")],
        [InlineKeyboardButton(text="⚙️ Настройки", callback_data="main_settings")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# ===================== ОБРАБОТЧИКИ КОМАНД =====================

@router.message(CommandStart())
async def cmd_start(message: Message):
    """
    Обработчик команды /start.
    Отправляет приветственное сообщение с описанием функционала.
    """
    user_name = message.from_user.first_name
    
    welcome_text = (
        f"👋 Привет, <b>{user_name}</b>!\n\n"
        "Я бот для поиска информации о компьютерных играх. 🎮\n\n"
        "<b>Мои возможности:</b>\n"
        "🔍 /search — Поиск игры по названию\n"
        "🏆 /top — Топ игр по жанру\n"
        "🎲 /random — Случайная игра\n"
        "⚙️ /settings — Настройки (любимый жанр)\n"
        "❓ /help — Помощь\n\n"
        "Выберите действие:"
    )
    
    await message.answer(
        welcome_text,
        parse_mode="HTML",
        reply_markup=get_main_keyboard()
    )


@router.message(Command("help"))
async def cmd_help(message: Message):
    """
    Обработчик команды /help.
    Отправляет справочную информацию.
    """
    help_text = (
        "📚 <b>Справка по командам:</b>\n\n"
        "🔍 <b>/search</b> — Поиск игры по названию.\n"
        "Введите название игры, и я найду информацию о ней.\n\n"
        "🏆 <b>/top</b> — Топ игр по жанру.\n"
        "Выберите жанр и получите список лучших игр.\n\n"
        "🎲 <b>/random</b> — Случайная игра.\n"
        "Получите рекомендацию случайной игры "
        "(учитывает ваш любимый жанр, если он установлен).\n\n"
        "⚙️ <b>/settings</b> — Настройки.\n"
        "Установите любимый жанр для персонализированных рекомендаций.\n\n"
        "💡 <i>Данные предоставлены RAWG API</i>"
    )
    
    await message.answer(help_text, parse_mode="HTML")


# ===================== ПОИСК ИГРЫ =====================

@router.message(Command("search"))
async def cmd_search(message: Message, state: FSMContext):
    """
    Обработчик команды /search.
    Запрашивает название игры для поиска.
    """
    await state.set_state(SearchStates.waiting_for_game_name)
    await message.answer(
        "🔍 Введите название игры для поиска:",
        parse_mode="HTML"
    )


@router.callback_query(F.data == "main_search")
async def callback_search(callback: CallbackQuery, state: FSMContext):
    """Обработчик нажатия кнопки поиска"""
    await state.set_state(SearchStates.waiting_for_game_name)
    await callback.message.answer(
        "🔍 Введите название игры для поиска:",
        parse_mode="HTML"
    )
    await callback.answer()


@router.message(SearchStates.waiting_for_game_name)
async def process_game_search(message: Message, state: FSMContext):
    """
    Обрабатывает введённое название игры и выполняет поиск.
    """
    game_name = message.text.strip()
    
    if len(game_name) < 2:
        await message.answer("❌ Название слишком короткое. Введите минимум 2 символа.")
        return
    
    await state.clear()
    
    # Отправляем сообщение о поиске
    search_msg = await message.answer("🔄 Ищу игру...")
    
    try:
        async with aiohttp.ClientSession() as session:
            # Выполняем поиск
            data = await fetch_api(session, "/games", {
                "search": game_name,
                "page_size": 5
            })
            
            if data is None:
                await search_msg.edit_text(
                    "❌ Произошла ошибка при обращении к API. Попробуйте позже."
                )
                return
            
            results = data.get("results", [])
            
            if not results:
                await search_msg.edit_text(
                    f"😔 По запросу «{game_name}» ничего не найдено.\n"
                    "Попробуйте другое название."
                )
                return
            
            # Если найдена одна игра или несколько, показываем первую
            game = results[0]
            
            # Получаем детальную информацию об игре
            game_details = await fetch_api(session, f"/games/{game['id']}")
            
            if game_details:
                game_info = format_game_info(game_details)
            else:
                game_info = format_game_info(game)
            
            # Если найдено несколько результатов, добавляем информацию
            if len(results) > 1:
                other_results = "\n\n📋 <b>Другие результаты:</b>\n"
                for i, g in enumerate(results[1:5], 2):
                    other_results += f"{i}. {g['name']}\n"
                game_info += other_results
            
            await search_msg.edit_text(game_info, parse_mode="HTML")
            
    except Exception as e:
        logger.error(f"Ошибка при поиске игры: {e}")
        await search_msg.edit_text(
            "❌ Произошла непредвиденная ошибка. Попробуйте позже."
        )


# ===================== ТОП ИГР ПО ЖАНРУ =====================

@router.message(Command("top"))
async def cmd_top(message: Message):
    """
    Обработчик команды /top.
    Показывает выбор жанров.
    """
    await message.answer(
        "🏆 Выберите жанр для просмотра топа игр:",
        reply_markup=get_genre_keyboard()
    )


@router.callback_query(F.data == "main_top")
async def callback_top(callback: CallbackQuery):
    """Обработчик нажатия кнопки топа"""
    await callback.message.answer(
        "🏆 Выберите жанр для просмотра топа игр:",
        reply_markup=get_genre_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data.startswith("genre_"))
async def process_genre_selection(callback: CallbackQuery):
    """
    Обрабатывает выбор жанра и показывает топ игр.
    """
    genre_id = int(callback.data.split("_")[1])
    genre_name = GENRES.get(genre_id, "Неизвестный жанр")
    
    await callback.answer(f"Загружаю топ {genre_name}...")
    
    # Отправляем сообщение о загрузке
    loading_msg = await callback.message.answer("🔄 Загружаю топ игр...")
    
    try:
        async with aiohttp.ClientSession() as session:
            data = await fetch_api(session, "/games", {
                "genres": genre_id,
                "ordering": "-rating",
                "page_size": 10
            })
            
            if data is None:
                await loading_msg.edit_text(
                    "❌ Произошла ошибка при обращении к API. Попробуйте позже."
                )
                return
            
            results = data.get("results", [])
            
            if not results:
                await loading_msg.edit_text(
                    f"😔 Не удалось найти игры в жанре {genre_name}."
                )
                return
            
            # Формируем список топа
            top_text = f"🏆 <b>Топ-10 игр в жанре {genre_name}:</b>\n\n"
            
            for i, game in enumerate(results, 1):
                name = game.get("name", "Неизвестно")
                rating = game.get("rating", 0)
                released = game.get("released", "N/A")
                
                # Эмодзи для топ-3
                if i == 1:
                    medal = "🥇"
                elif i == 2:
                    medal = "🥈"
                elif i == 3:
                    medal = "🥉"
                else:
                    medal = f"{i}."
                
                top_text += f"{medal} <b>{name}</b>\n"
                top_text += f"    ⭐ {rating}/5 | 📅 {released}\n\n"
            
            await loading_msg.edit_text(top_text, parse_mode="HTML")
            
    except Exception as e:
        logger.error(f"Ошибка при получении топа: {e}")
        await loading_msg.edit_text(
            "❌ Произошла непредвиденная ошибка. Попробуйте позже."
        )


# ===================== СЛУЧАЙНАЯ ИГРА =====================

@router.message(Command("random"))
async def cmd_random(message: Message):
    """
    Обработчик команды /random.
    Показывает случайную игру (с учётом любимого жанра пользователя).
    """
    await get_random_game(message)


@router.callback_query(F.data == "main_random")
async def callback_random(callback: CallbackQuery):
    """Обработчик нажатия кнопки случайной игры"""
    await callback.answer("Ищу случайную игру...")
    await get_random_game(callback.message, callback.from_user.id)


async def get_random_game(message: Message, user_id: int = None):
    """
    Получает и отправляет информацию о случайной игре.
    
    Args:
        message: Объект сообщения
        user_id: ID пользователя (для получения настроек)
    """
    if user_id is None:
        user_id = message.from_user.id
    
    # Проверяем, есть ли у пользователя любимый жанр
    favorite_genre = user_settings.get(user_id, {}).get("favorite_genre")
    
    loading_msg = await message.answer("🔄 Ищу случайную игру...")
    
    try:
        async with aiohttp.ClientSession() as session:
            # Параметры запроса
            params = {
                "page_size": 40,
                "ordering": "-rating",
                "metacritic": "70,100"  # Только игры с хорошим рейтингом
            }
            
            # Если есть любимый жанр, добавляем его
            if favorite_genre:
                params["genres"] = favorite_genre
                genre_name = GENRES.get(favorite_genre, "")
                genre_info = f"\n\n💡 <i>Рекомендация основана на вашем любимом жанре: {genre_name}</i>"
            else:
                genre_info = "\n\n💡 <i>Установите любимый жанр в /settings для персонализированных рекомендаций</i>"
            
            # Случайная страница для разнообразия
            params["page"] = random.randint(1, 5)
            
            data = await fetch_api(session, "/games", params)
            
            if data is None:
                await loading_msg.edit_text(
                    "❌ Произошла ошибка при обращении к API. Попробуйте позже."
                )
                return
            
            results = data.get("results", [])
            
            if not results:
                await loading_msg.edit_text(
                    "😔 Не удалось найти игру. Попробуйте ещё раз."
                )
                return
            
            # Выбираем случайную игру
            game = random.choice(results)
            
            # Получаем детальную информацию
            game_details = await fetch_api(session, f"/games/{game['id']}")
            
            if game_details:
                game_info = format_game_info(game_details)
            else:
                game_info = format_game_info(game)
            
            game_info = "🎲 <b>Случайная рекомендация:</b>\n\n" + game_info + genre_info
            
            # Кнопка для получения новой рекомендации
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(
                    text="🎲 Ещё одна игра",
                    callback_data="main_random"
                )]
            ])
            
            await loading_msg.edit_text(
                game_info, 
                parse_mode="HTML",
                reply_markup=keyboard
            )
            
    except Exception as e:
        logger.error(f"Ошибка при получении случайной игры: {e}")
        await loading_msg.edit_text(
            "❌ Произошла непредвиденная ошибка. Попробуйте позже."
        )


# ===================== НАСТРОЙКИ =====================

@router.message(Command("settings"))
async def cmd_settings(message: Message):
    """
    Обработчик команды /settings.
    Показывает текущие настройки и позволяет их изменить.
    """
    await show_settings(message, message.from_user.id)


@router.callback_query(F.data == "main_settings")
async def callback_settings(callback: CallbackQuery):
    """Обработчик нажатия кнопки настроек"""
    await callback.answer()
    await show_settings(callback.message, callback.from_user.id)


async def show_settings(message: Message, user_id: int):
    """
    Показывает текущие настройки пользователя.
    
    Args:
        message: Объект сообщения
        user_id: ID пользователя
    """
    current_settings = user_settings.get(user_id, {})
    favorite_genre_id = current_settings.get("favorite_genre")
    
    if favorite_genre_id:
        genre_name = GENRES.get(favorite_genre_id, "Неизвестный")
        settings_text = (
            f"⚙️ <b>Ваши настройки:</b>\n\n"
            f"❤️ Любимый жанр: <b>{genre_name}</b>\n\n"
            "Выберите новый жанр или сбросьте настройки:"
        )
    else:
        settings_text = (
            "⚙️ <b>Ваши настройки:</b>\n\n"
            "❤️ Любимый жанр: <i>не установлен</i>\n\n"
            "Выберите любимый жанр для персонализированных рекомендаций:"
        )
    
    await message.answer(
        settings_text,
        parse_mode="HTML",
        reply_markup=get_settings_genre_keyboard()
    )


@router.callback_query(F.data.startswith("setgenre_"))
async def process_settings_genre(callback: CallbackQuery):
    """
    Обрабатывает выбор любимого жанра в настройках.
    """
    action = callback.data.split("_")[1]
    user_id = callback.from_user.id
    
    if action == "reset":
        # Сброс настроек
        if user_id in user_settings:
            del user_settings[user_id]
        await callback.answer("Настройки сброшены!")
        await callback.message.edit_text(
            "✅ Настройки успешно сброшены!",
            parse_mode="HTML"
        )
    else:
        # Установка жанра
        genre_id = int(action)
        genre_name = GENRES.get(genre_id, "Неизвестный")
        
        user_settings[user_id] = {"favorite_genre": genre_id}
        
        await callback.answer(f"Жанр {genre_name} сохранён!")
        await callback.message.edit_text(
            f"✅ Любимый жанр установлен: <b>{genre_name}</b>\n\n"
            "Теперь команда /random будет учитывать ваши предпочтения!",
            parse_mode="HTML"
        )


# ===================== ОБРАБОТКА НЕИЗВЕСТНЫХ СООБЩЕНИЙ =====================

@router.message()
async def unknown_message(message: Message):
    """
    Обработчик неизвестных сообщений.
    """
    await message.answer(
        "🤔 Не понимаю эту команду.\n"
        "Используйте /help для просмотра доступных команд.",
        reply_markup=get_main_keyboard()
    )


# ===================== ЗАПУСК БОТА =====================

async def main():
    """
    Главная функция запуска бота.
    """
    # Проверка токенов
    if TELEGRAM_TOKEN == "YOUR_TELEGRAM_BOT_TOKEN":
        logger.error("Установите TELEGRAM_TOKEN!")
        return
    
    if RAWG_API_KEY == "YOUR_RAWG_API_KEY":
        logger.error("Установите RAWG_API_KEY!")
        return
    
    # Создаём бота и диспетчер
    bot = Bot(token=TELEGRAM_TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    
    # Регистрируем роутер
    dp.include_router(router)
    
    # Запускаем бота
    logger.info("Бот запущен!")
    
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
