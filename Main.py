import telebot
import requests
import random
import os
from bs4 import BeautifulSoup

TOKEN = os.environ.get("BOT_TOKEN")  # Токен будет из переменной окружения
bot = telebot.TeleBot(TOKEN)

# Локальная база рецептов
RECIPES_DB = {
    "борщ": {
        "title": "Борщ украинский",
        "ingredients": "• 500 г говядины\n• 1 свекла\n• 3 картофелины\n• 1 морковь\n• 1 луковица\n• 300 г капусты\n• 2 ст.л томатной пасты\n• 1 ст.л уксуса\n• Соль, перец, лавровый лист",
        "instructions": "1. Сварить бульон на мясе (2 часа).\n2. Свеклу натереть, обжарить с томатной пастой и уксусом.\n3. В бульон добавить нарезанный картофель и капусту, варить 15 мин.\n4. Обжарить лук с морковью, добавить в суп.\n5. Добавить свеклу, варить ещё 10 мин.\n6. Добавить специи, зелень. Подавать со сметаной.",
        "hacks": "Добавь уксус при обжарке свеклы — цвет останется ярким. Чеснок и зелень добавляй за 5 минут до готовности."
    },
    "пицца": {
        "title": "Пицца Маргарита",
        "ingredients": "• 300 г теста для пиццы\n• 4 ст.л томатного соуса\n• 150 г моцареллы\n• 2 помидора\n• Листья базилика\n• Оливковое масло",
        "instructions": "1. Раскатать тесто.\n2. Смазать томатным соусом.\n3. Выложить нарезанные помидоры и моцареллу.\n4. Выпекать 15 минут при 220°C.\n5. Готовую пиццу посыпать базиликом, сбрызнуть маслом.",
        "hacks": "Разогрей духовку до максимума вместе с противнем. Не перегружай тесто начинкой."
    },
    "омлет": {
        "title": "Омлет классический",
        "ingredients": "• 3 яйца\n• 50 мл молока\n• 1 ст.л сливочного масла\n• Соль, перец",
        "instructions": "1. Взбить яйца с молоком и солью.\n2. Разогреть сковороду с маслом.\n3. Вылить смесь, жарить на среднем огне 2-3 минуты.\n4. Сложить пополам, подержать ещё минуту.",
        "hacks": "Яйца должны быть комнатной температуры. Не взбивай слишком сильно — омлет будет нежнее."
    },
    "оливье": {
        "title": "Салат Оливье",
        "ingredients": "• 4 картофелины\n• 3 моркови\n• 4 яйца\n• 300 г вареной колбасы\n• 1 банка горошка\n• 3 соленых огурца\n• 1 луковица\n• Майонез, соль",
        "instructions": "1. Отварить картофель, морковь, яйца.\n2. Нарезать все ингредиенты кубиками.\n3. Смешать, добавить горошек, посолить.\n4. Заправить майонезом.",
        "hacks": "Нарежь все ингредиенты одинаковыми кубиками — салат будет красивее. Добавь немного лимонного сока в майонез для свежести."
    }
}

def search_recipe(query):
    # Поиск в локальной базе
    for key, recipe in RECIPES_DB.items():
        if key in query.lower() or query.lower() in key:
            return recipe["title"], recipe["ingredients"], recipe["instructions"], recipe["hacks"]
    # Если не нашли — создаём базовый
    return f"{query.capitalize()}", f"• Ингредиенты для {query}", f"1. Приготовьте {query}.", "Используй свежие продукты и готовь с любовью!"

def search_lifehacks(query):
    return search_recipe(query)[3]

@bot.message_handler(commands=['start', 'help'])
def start(message):
    bot.reply_to(message, 
                 "👩‍🍳 *ВкусноБот*\n\nПросто напиши название любого блюда, и я найду рецепт!\n\n📝 *Примеры:* борщ, пицца, оливье, сырники\n\n⭐ *Команды:* /help", 
                 parse_mode='Markdown')

@bot.message_handler(func=lambda message: True)
def handle_recipe(message):
    query = message.text.strip()
    msg = bot.reply_to(message, f"🔍 Ищу рецепт для «{query}»...")
    
    title, ingredients, instructions, hack = search_recipe(query)
    
    from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("📋 Копировать ингредиенты", callback_data=f"copy_{ingredients}"))
    
    response = (f"🍽 *{title}*\n\n"
                f"📝 *Ингредиенты:*\n{ingredients}\n\n"
                f"👨‍🍳 *Приготовление:*\n{instructions}\n\n"
                f"✨ *Лайфхак:*\n{hack}")
    
    bot.edit_message_text(response, message.chat.id, msg.message_id, reply_markup=keyboard, parse_mode='Markdown')

@bot.callback_query_handler(func=lambda call: True)
def handle_buttons(call):
    if call.data.startswith('copy_'):
        ingredients = call.data.replace('copy_', '')
        bot.answer_callback_query(call.id, "📋 Ингредиенты скопированы!")
        bot.send_message(call.message.chat.id, f"📋 *Ингредиенты:*\n```\n{ingredients}\n```", parse_mode='Markdown')

print("🍳 Бот запущен!")
bot.infinity_polling()
