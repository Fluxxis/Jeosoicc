#!/usr/bin/env python3
import asyncio
import json
import os
import subprocess
import logging
from aiogram import Bot, Dispatcher, Router, F, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardButton, FSInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder

# Настройки
MANAGER_BOT_TOKEN = "8577416105:AAGTmKHhz8cN2u5lUcRSczUU_kxM5FXjdZ0"  # Замените на токен бота-менеджера
MAIN_BOT_SETTINGS_FILE = "settings.json"
MAIN_BOT_SCRIPT = "main.py"
ADMIN_IDS = [7225974704,7292589574]  # ID администраторов менеджера

# Логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Состояния
class ChangeTokenState(StatesGroup):
    waiting_for_token = State()

class ChangeTagState(StatesGroup):
    waiting_for_tag = State()

def load_main_settings():
    if not os.path.exists(MAIN_BOT_SETTINGS_FILE):
        return {}
    with open(MAIN_BOT_SETTINGS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_main_settings(data):
    with open(MAIN_BOT_SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

def is_admin(user_id):
    return user_id in ADMIN_IDS

async def send_admin_menu(message: types.Message):
    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text="🔑 Изменить токен бота", callback_data="change_token"))
    kb.row(InlineKeyboardButton(text="🏷 Изменить тег бота", callback_data="change_tag"))
    kb.row(InlineKeyboardButton(text="📊 Просмотр настроек", callback_data="view_settings"))
    kb.row(InlineKeyboardButton(text="📋 Просмотр логов", callback_data="view_logs"))
    kb.row(InlineKeyboardButton(text="🔄 Перезапуск бота", callback_data="restart_bot"))
    kb.row(InlineKeyboardButton(text="📈 Статистика", callback_data="view_stats"))
    kb.row(InlineKeyboardButton(text="🗂 Управление сессиями", callback_data="manage_sessions"))

    text = (
        "🤖 <b>МЕНЕДЖЕР ОСНОВНОГО БОТА</b>\n\n"
        "Выберите действие для управления основным ботом:"
    )

    await message.answer(text, reply_markup=kb.as_markup(), parse_mode=ParseMode.HTML)

def get_main_router():
    router = Router()

    @router.message(CommandStart())
    async def start(message: types.Message):
        if not is_admin(message.from_user.id):
            return await message.answer("❌ Доступ запрещен")

        await send_admin_menu(message)

    @router.callback_query(F.data == "change_token")
    async def change_token_start(call: types.CallbackQuery, state: FSMContext):
        if not is_admin(call.from_user.id):
            return await call.answer("❌ Доступ запрещен")

        kb = InlineKeyboardBuilder()
        kb.row(InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_menu"))

        text = (
            "🔑 <b>Изменение токена бота</b>\n\n"
            "Отправьте новый токен бота от @BotFather\n\n"
            "⚠️ <b>Внимание:</b> После изменения токена бот будет недоступен по старому токену!"
        )

        await call.message.edit_text(text, reply_markup=kb.as_markup(), parse_mode=ParseMode.HTML)
        await state.set_state(ChangeTokenState.waiting_for_token)

    @router.message(ChangeTokenState.waiting_for_token)
    async def change_token_finish(message: types.Message, state: FSMContext):
        if not is_admin(message.from_user.id):
            return

        new_token = message.text.strip()
        if not new_token or len(new_token) < 45:
            return await message.answer("❌ Неверный формат токена")

        settings = load_main_settings()
        old_token = settings.get('bot_token', 'не установлен')

        settings['bot_token'] = new_token
        save_main_settings(settings)

        text = (
            "✅ <b>Токен успешно изменен!</b>\n\n"
            f"Старый токен: <code>{old_token[:20]}...</code>\n"
            f"Новый токен: <code>{new_token[:20]}...</code>\n\n"
            "🔄 <b>Рекомендуется перезапустить бота</b>"
        )

        kb = InlineKeyboardBuilder()
        kb.row(InlineKeyboardButton(text="🔄 Перезапустить", callback_data="restart_bot"))
        kb.row(InlineKeyboardButton(text="🏠 В меню", callback_data="back_to_menu"))

        await message.answer(text, reply_markup=kb.as_markup(), parse_mode=ParseMode.HTML)
        await state.clear()

    @router.callback_query(F.data == "change_tag")
    async def change_tag_info(call: types.CallbackQuery):
        if not is_admin(call.from_user.id):
            return await call.answer("❌ Доступ запрещен")

        kb = InlineKeyboardBuilder()
        kb.row(InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_menu"))

        text = (
            "🏷 <b>Изменение тега бота</b>\n\n"
            "⚠️ <b>Важно:</b> Username бота нельзя изменить программно!\n\n"
            "Для изменения username:\n"
            "1. Перейдите к @BotFather\n"
            "2. Выберите бота\n"
            "3. Нажмите 'Bot Settings'\n"
            "4. Выберите 'Username'\n\n"
            "После изменения username обновите токен бота в настройках."
        )

        await call.message.edit_text(text, reply_markup=kb.as_markup(), parse_mode=ParseMode.HTML)

    @router.callback_query(F.data == "view_settings")
    async def view_settings(call: types.CallbackQuery):
        if not is_admin(call.from_user.id):
            return await call.answer("❌ Доступ запрещен")

        settings = load_main_settings()

        text = "⚙️ <b>НАСТРОЙКИ ОСНОВНОГО БОТА</b>\n\n"
        for key, value in settings.items():
            if 'token' in key.lower():
                value = f"{str(value)[:20]}..." if value else "не установлен"
            elif 'hash' in key.lower():
                value = f"{str(value)[:10]}..." if value else "не установлен"
            text += f"<b>{key}:</b> <code>{value}</code>\n"

        kb = InlineKeyboardBuilder()
        kb.row(InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_menu"))

        await call.message.edit_text(text, reply_markup=kb.as_markup(), parse_mode=ParseMode.HTML)

    @router.callback_query(F.data == "view_logs")
    async def view_logs(call: types.CallbackQuery):
        if not is_admin(call.from_user.id):
            return await call.answer("❌ Доступ запрещен")

        try:
            with open('bot.log', 'r', encoding='utf-8') as f:
                lines = f.readlines()[-20:]  # Последние 20 строк

            log_text = ''.join(lines)

            # Отправляем как файл, если слишком длинное
            if len(log_text) > 4000:
                with open('temp_logs.txt', 'w', encoding='utf-8') as f:
                    f.write(log_text)
                await call.message.answer_document(
                    FSInputFile('temp_logs.txt'),
                    caption="📋 Последние логи бота"
                )
                os.remove('temp_logs.txt')
            else:
                kb = InlineKeyboardBuilder()
                kb.row(InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_menu"))
                await call.message.edit_text(
                    f"📋 <b>ПОСЛЕДНИЕ ЛОГИ</b>\n\n<code>{log_text}</code>",
                    reply_markup=kb.as_markup(),
                    parse_mode=ParseMode.HTML
                )

        except Exception as e:
            await call.message.edit_text(
                f"❌ Ошибка чтения логов: {e}",
                reply_markup=InlineKeyboardBuilder().row(
                    InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_menu")
                ).as_markup(),
                parse_mode=ParseMode.HTML
            )

    @router.callback_query(F.data == "restart_bot")
    async def restart_bot(call: types.CallbackQuery):
        if not is_admin(call.from_user.id):
            return await call.answer("❌ Доступ запрещен")

        kb = InlineKeyboardBuilder()
        kb.row(InlineKeyboardButton(text="✅ Подтвердить", callback_data="confirm_restart"))
        kb.row(InlineKeyboardButton(text="❌ Отмена", callback_data="back_to_menu"))

        text = (
            "🔄 <b>ПЕРЕЗАПУСК ОСНОВНОГО БОТА</b>\n\n"
            "⚠️ <b>Внимание:</b> Бот будет остановлен и запущен заново!\n\n"
            "Все активные процессы будут прерваны.\n\n"
            "Подтвердить перезапуск?"
        )

        await call.message.edit_text(text, reply_markup=kb.as_markup(), parse_mode=ParseMode.HTML)

    @router.callback_query(F.data == "confirm_restart")
    async def confirm_restart(call: types.CallbackQuery):
        if not is_admin(call.from_user.id):
            return await call.answer("❌ Доступ запрещен")

        try:
            # Используем start_all.sh для полного перезапуска всех сервисов
            script_path = "start_all.sh"
            if os.path.exists(script_path):
                result = subprocess.run(["bash", script_path], capture_output=True, text=True, timeout=30)

                if result.returncode == 0:
                    text = "✅ <b>Все сервисы успешно перезапущены!</b>\n\nВключая бота, ngrok и другие компоненты."
                else:
                    text = f"⚠️ <b>Перезапуск с ошибками:</b>\n<code>{result.stderr[:500]}</code>"
            else:
                # Fallback: пытаемся перезапустить только бота
                result = subprocess.run(["python", MAIN_BOT_SCRIPT], capture_output=True, text=True, timeout=15)

                if result.returncode == 0:
                    text = "✅ <b>Бот успешно запущен!</b>\n\n<i>Примечание: старый процесс может еще работать</i>"
                else:
                    text = f"⚠️ <b>Запуск с ошибками:</b>\n<code>{result.stderr[:500]}</code>"

        except subprocess.TimeoutExpired:
            text = "✅ <b>Команда перезапуска отправлена</b>\n\nСервисы запускаются в фоне."
        except Exception as e:
            text = f"❌ <b>Ошибка перезапуска:</b> {e}"

        kb = InlineKeyboardBuilder()
        kb.row(InlineKeyboardButton(text="🏠 В меню", callback_data="back_to_menu"))

        await call.message.edit_text(text, reply_markup=kb.as_markup(), parse_mode=ParseMode.HTML)

    @router.callback_query(F.data == "view_stats")
    async def view_stats(call: types.CallbackQuery):
        if not is_admin(call.from_user.id):
            return await call.answer("❌ Доступ запрещен")

        try:
            # Импортируем базу данных основного бота
            import sqlite3
            conn = sqlite3.connect("bot_database.db")
            cursor = conn.cursor()

            # Получаем статистику
            cursor.execute("SELECT COUNT(*) FROM users")
            users_count = cursor.fetchone()[0]

            cursor.execute("SELECT SUM(amount) FROM checks")
            checks_total = cursor.fetchone()[0] or 0

            cursor.execute("SELECT COUNT(*) FROM activity_logs WHERE timestamp > datetime('now', '-1 day')")
            logs_today = cursor.fetchone()[0]

            conn.close()

            text = (
                "📈 <b>СТАТИСТИКА ОСНОВНОГО БОТА</b>\n\n"
                f"👥 <b>Всего пользователей:</b> {users_count}\n"
                f"💰 <b>Выдано чеков на сумму:</b> {checks_total} ⭐️\n"
                f"📝 <b>Активность за сегодня:</b> {logs_today} действий\n\n"
                f"🗂️ <b>База данных:</b> bot_database.db\n"
                f"📁 <b>Сессии:</b> {len([f for f in os.listdir('sessions') if f.endswith('.session')]) if os.path.exists('sessions') else 0} файлов"
            )

        except Exception as e:
            text = f"❌ Ошибка получения статистики: {e}"

        kb = InlineKeyboardBuilder()
        kb.row(InlineKeyboardButton(text="🔄 Обновить", callback_data="view_stats"))
        kb.row(InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_menu"))

        await call.message.edit_text(text, reply_markup=kb.as_markup(), parse_mode=ParseMode.HTML)

    @router.callback_query(F.data == "manage_sessions")
    async def manage_sessions(call: types.CallbackQuery):
        if not is_admin(call.from_user.id):
            return await call.answer("❌ Доступ запрещен")

        try:
            sessions_dir = "sessions"
            if not os.path.exists(sessions_dir):
                text = "📁 <b>Папка sessions не найдена</b>"
            else:
                sessions = [f for f in os.listdir(sessions_dir) if f.endswith('.session')]
                text = f"📁 <b>СЕССИИ ({len(sessions)})</b>\n\n"

                for i, session in enumerate(sessions[:10]):  # Показываем первые 10
                    size = os.path.getsize(os.path.join(sessions_dir, session)) / 1024
                    text += f"{i+1}. <code>{session}</code> ({size:.1f} KB)\n"

                if len(sessions) > 10:
                    text += f"\n<i>...и еще {len(sessions) - 10} сессий</i>"

        except Exception as e:
            text = f"❌ Ошибка: {e}"

        kb = InlineKeyboardBuilder()
        kb.row(InlineKeyboardButton(text="🧹 Очистить старые", callback_data="clean_old_sessions"))
        kb.row(InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_menu"))

        await call.message.edit_text(text, reply_markup=kb.as_markup(), parse_mode=ParseMode.HTML)

    @router.callback_query(F.data == "clean_old_sessions")
    async def clean_old_sessions(call: types.CallbackQuery):
        if not is_admin(call.from_user.id):
            return await call.answer("❌ Доступ запрещен")

        try:
            sessions_dir = "sessions"
            if not os.path.exists(sessions_dir):
                return await call.answer("Папка sessions не найдена")

            import time
            current_time = time.time()
            deleted = 0

            for session_file in os.listdir(sessions_dir):
                if session_file.endswith('.session'):
                    file_path = os.path.join(sessions_dir, session_file)
                    file_age = current_time - os.path.getmtime(file_path)

                    # Удаляем сессии старше 30 дней
                    if file_age > 30 * 24 * 3600:
                        os.remove(file_path)
                        deleted += 1

            text = f"🧹 <b>Очистка завершена</b>\n\nУдалено старых сессий: {deleted}"

        except Exception as e:
            text = f"❌ Ошибка очистки: {e}"

        kb = InlineKeyboardBuilder()
        kb.row(InlineKeyboardButton(text="🔙 Назад", callback_data="manage_sessions"))

        await call.message.edit_text(text, reply_markup=kb.as_markup(), parse_mode=ParseMode.HTML)

    @router.callback_query(F.data == "back_to_menu")
    async def back_to_menu(call: types.CallbackQuery):
        if not is_admin(call.from_user.id):
            return await call.answer("❌ Доступ запрещен")

        await send_admin_menu(call.message)

    return router

async def main():
    if not MANAGER_BOT_TOKEN or MANAGER_BOT_TOKEN == "YOUR_MANAGER_BOT_TOKEN_HERE":
        print("❌ Установите MANAGER_BOT_TOKEN в файле manager_bot.py")
        return

    bot = Bot(token=MANAGER_BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    dp.include_router(get_main_router())

    print("🤖 Менеджер-бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
