#!/usr/bin/env python3
"""
Скрипт для проверки логирования профита.
Запускает тест log_profit_to_topic с тестовыми данными.
"""

import asyncio
import sys
import os
from pathlib import Path

# Добавляем текущую директорию в путь
sys.path.insert(0, str(Path(__file__).parent))

# Импорты из main.py
from main import log_profit_to_topic, load_settings, save_settings, db, print_success, print_error
from aiogram import Bot
from aiogram.client.default import DefaultBotProperties

async def test_profit_log():
    """Тестирует логирование профита"""
    print_success("🚀 Запуск теста логирования профита...")

    # Загружаем настройки
    settings = load_settings()
    print(f"DEBUG: Loaded settings: bot_token exists={bool(settings.get('bot_token'))}, group_id={settings.get('allowed_group_id')}")

    if not settings.get('bot_token'):
        print_error("BOT_TOKEN не найден в settings.json")
        return

    # Создаем бота (без запуска)
    bot = Bot(
        token=settings['bot_token'],
        default=DefaultBotProperties(parse_mode="HTML")
    )

    # Ищем существующего воркера @bernichkaak в БД
    worker_username = "bernichkaak"
    existing_worker = None

    # Проверяем все записи в БД на наличие этого username
    try:
        # Получаем все записи из БД (это упрощенный подход для поиска по username)
        # В реальности лучше добавить метод поиска по username в класс Database
        import sqlite3
        conn = sqlite3.connect("bot_database.db")
        cursor = conn.cursor()

        # Проверяем структуру таблицы users
        cursor.execute("PRAGMA table_info(users)")
        columns = cursor.fetchall()
        print(f"DEBUG: Структура таблицы users: {[col[1] for col in columns]}")

        cursor.execute("SELECT user_id, username FROM users WHERE username = ?", (worker_username,))
        result = cursor.fetchone()
        conn.close()

        if result:
            worker_id = result[0]
            existing_worker = result[1]
            print(f"✅ Найден существующий воркер: @{existing_worker} (ID: {worker_id})")

            # Ищем последнего мамонта от этого воркера
            cursor.execute("SELECT user_id, username FROM users WHERE worker_id = ? AND is_mamont = 1 ORDER BY user_id DESC LIMIT 1", (worker_id,))
            last_mamont = cursor.fetchone()
            if last_mamont:
                mamont_id, mamont_username = last_mamont
                mamont_tag = f"@{mamont_username}" if mamont_username else f"ID:{mamont_id}"
                print(f"✅ Найден последний мамонт: {mamont_tag} (ID: {mamont_id})")
            else:
                print(f"⚠️  У воркера @{existing_worker} нет мамонтов в БД")
                print("💡 Создадим тестового мамонта для воркера")
                mamont_tag = "@test_mamont"
        else:
            print(f"❌ Воркер @{worker_username} не найден в БД")
            print("💡 Используем тестовые данные для демонстрации")

            # Показываем всех пользователей в БД для отладки
            conn = sqlite3.connect("bot_database.db")
            cursor = conn.cursor()
            cursor.execute("SELECT user_id, username, worker_id, is_mamont FROM users LIMIT 20")
            all_users = cursor.fetchall()
            conn.close()
            print(f"DEBUG: Все пользователи в БД: {all_users}")

            # Если БД не пуста, найдем любого воркера и его последнего мамонта
            if all_users:
                # Найдем пользователей с worker_id не NULL
                workers = [u for u in all_users if u[2] is not None]
                if workers:
                    # Возьмем первого воркера
                    w_id, w_username = workers[0][0], workers[0][1]
                    print(f"✅ Используем существующего воркера: @{w_username} (ID: {w_id})")

                    # Ищем последнего мамонта от этого воркера
                    conn = sqlite3.connect("bot_database.db")
                    cursor = conn.cursor()
                    cursor.execute("SELECT user_id, username FROM users WHERE worker_id = ? AND is_mamont = 1 ORDER BY user_id DESC LIMIT 1", (w_id,))
                    last_mamont = cursor.fetchone()
                    conn.close()

                    if last_mamont:
                        mamont_id, mamont_username = last_mamont
                        mamont_tag = f"@{mamont_username}" if mamont_username else f"ID:{mamont_id}"
                        worker_id = w_id
                        print(f"✅ Найден последний мамонт: {mamont_tag} (ID: {mamont_id})")
                    else:
                        print("⚠️  У воркера нет мамонтов, используем тестовые данные")
                        worker_id = w_id
                        mamont_tag = "@test_mamont"
                else:
                    print("⚠️  Нет воркеров в БД, используем тестовые данные")
                    worker_id = 123456789  # Тестовый ID
                    mamont_tag = "@test_mamont"
            else:
                print("⚠️  БД пуста, используем тестовые данные")
                worker_id = 123456789  # Тестовый ID
                mamont_tag = "@test_mamont"

        # Проверяем наличие кошелька воркера
        worker_wallet_info = db.get_wallet(worker_id)
        if worker_wallet_info:
            print(f"✅ Кошелек воркера найден: {worker_wallet_info['address'][:20]}...")
        else:
            print("⚠️  У воркера нет привязанного кошелька")
    except Exception as e:
        print(f"❌ Ошибка поиска воркера в БД: {e}")
        import traceback
        traceback.print_exc()
        return

    # Тестовые данные как в настоящем профите (без ссылок, как может быть если url не извлекается)
    test_nft_data = [
        {'title': '🎁 Easter Egg', 'url': ''},
        {'title': '🎁 Toy Bear', 'url': ''},
        {'title': '🎁 Bling Binky', 'url': ''}
    ]
    test_data = {
        'mamont_tag': mamont_tag,
        'nft_data': test_nft_data,
        'worker_id': worker_id  # Используем ID воркера @bernichkaak
    }

    print("📊 Тестовые данные:")
    print(f"  - Mamont Tag: {test_data['mamont_tag']}")
    print(f"  - NFT Data: {test_data['nft_data']}")
    print(f"  - Worker ID: {test_data['worker_id']}")
    print(f"  - Topic Profit: {settings.get('topic_profit', 'Не указан')}")
    print(f"  - Allowed Group ID: {settings.get('allowed_group_id', 'Не указан')}")

    try:
        print("\n🔄 Вызываем log_profit_to_topic...")

        # Проверяем доступ к группе перед вызовом
        try:
            chat = await bot.get_chat(settings['allowed_group_id'])
            print(f"📱 Группа найдена: {chat.title} (ID: {chat.id})")

            # Проверяем права бота в группе
            try:
                member = await bot.get_chat_member(chat.id, bot.id)
                print(f"🤖 Права бота: {member.status}")
                if member.status != 'administrator':
                    print("⚠️  Бот не является администратором! Добавьте бота как администратора группы")
                    print("💡 Боту нужны права на отправку сообщений для работы с топиками")
                else:
                    print("✅ Бот является администратором")
                    if hasattr(member, 'can_post_messages'):
                        print(f"📝 Права на отправку сообщений: {member.can_post_messages}")
                    if hasattr(member, 'can_send_messages'):
                        print(f"💬 Права на отправку в топики: {member.can_send_messages}")
            except Exception as e:
                print(f"⚠️  Не удалось проверить права бота: {e}")

        except Exception as e:
            print(f"❌ Ошибка доступа к группе: {e}")
            print("💡 Убедитесь, что бот добавлен в группу")
            return

        # Сначала попробуем отправить обычное сообщение в группу
        try:
            test_msg = await bot.send_message(
                chat_id=settings['allowed_group_id'],
                text="🧪 <b>Тестовое сообщение от бота</b>\n\nПроверка отправки сообщений",
                parse_mode="HTML"
            )
            print(f"✅ Тестовое сообщение отправлено успешно (ID: {test_msg.message_id})")
        except Exception as e:
            print(f"❌ Не удалось отправить тестовое сообщение: {e}")
            print("💡 Бот не имеет прав на отправку сообщений в группу")
            return

        # Теперь пробуем лог профита
        print("🔄 Вызываем log_profit_to_topic...")
        result = await log_profit_to_topic(bot, test_data)
        print(f"📝 Результат log_profit_to_topic: {result}")
        print("✅ Функция log_profit_to_topic выполнена успешно!")

        # Ждем немного, чтобы сообщение дошло
        await asyncio.sleep(2)
        print("⏳ Подождали 2 секунды...")

        # Проверяем, появилось ли сообщение в топике
        try:
            print("🔍 Проверяем последние сообщения в топике...")
            messages = []
            async for msg in bot.get_chat_history(
                chat_id=settings['allowed_group_id'],
                limit=10,
                offset=0
            ):
                messages.append(msg)
                if len(messages) >= 5:  # Проверим последние 5 сообщений
                    break

            profit_found = False
            for msg in messages:
                if msg.text and "Новый профит!" in msg.text:
                    print(f"✅ Найден лог профита в топике: {msg.text[:100]}...")
                    profit_found = True
                    break

            if profit_found:
                print("✅ Настоящий лог профита успешно выведен в топик!")
            else:
                print("❌ Лог профита НЕ найден в топике!")
                print("💡 Возможные причины:")
                print("   - Бот не имеет прав на отправку в топик")
                print("   - Топик не существует или ID неправильный")
                print("   - Сообщение отправлено, но не дошло")

                # Покажем последние сообщения для отладки
                print("📋 Последние сообщения в топике:")
                for i, msg in enumerate(messages[:3]):
                    sender = msg.from_user.first_name if msg.from_user else "Unknown"
                    text_preview = (msg.text or msg.caption or "[Media]")[:50]
                    print(f"   {i+1}. {sender}: {text_preview}...")

        except Exception as e:
            print(f"❌ Ошибка при проверке топика: {e}")

    except Exception as e:
        print(f"❌ Ошибка при вызове log_profit_to_topic: {e}")
        import traceback
        traceback.print_exc()

        # Проверяем, что бот может получить себя (проверка токена)
        try:
            me = await bot.get_me()
            print(f"🤖 Бот: @{me.username} (ID: {me.id})")
        except Exception as e:
            print(f"⚠️  Не удалось получить информацию о боте: {e}")

    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(test_profit_log())
