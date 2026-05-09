import asyncio
import random
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import aiohttp
from aiogram.exceptions import TelegramBadRequest

# ==================== КОНФИГУРАЦИЯ MERCH ====================
BOT_TOKEN = "8248718556:AAGyxQyL-q8iCy34ChBJ5CWQ1SYcT7X8gps"
CACTUS_API_URL = "https://lk.cactuspay.pro/api/?method=create"
CACTUS_TOKEN = "5c687699511aa6201a12fd2d"

# ==================== БАЗА ОТЗЫВОВ ====================
FAKE_REVIEWS = [
    "заказал мерч качество огонь доставка быстрая",
    "пацаны реально крутые шмотки прислали",
    "первый раз заказывал переживал но всё чётко",
    "толстовка пришла за пару дней размер подошёл",
    "скинули трек на след день я в шоке",
    "заказываю не первый раз всегда стабильно",
    "лучше чем в офлайн магазах и дешевле",
    "думал развод а нет реально тема",
    "спасибо за оперативность",
    "качество печати на высоте не стирается",
    "рекомендую всем кто шарит за шмот",
    "ещё закажу жду новые дропы",
    "по цене норм по качеству тоже",
    "мерч пришёл упакован отлично",
    "в Москве лучший магаз",
    "третий заказ и всё чётко парни",
    "футболка села идеально",
    "реальные челы не кидалы",
    "стиль реально индивидуальный",
    "не верьте если пишут что лохотрон",
    "оператор вежливый подсказал по размерам",
    "можно предзаказ делать",
    "пять звёзд ставлю",
    "магаз проверенный временем",
    "всё на высоте",
    "изи заказ оформил",
    "мерч пришёл прям как на фото",
    "размерная сетка точная",
    "заказываю только тут",
    "чисто пацанам респект",
    "на районе все заказывают",
    "вкусный дизайн",
    "худи огонь",
    "качество хлопка топ",
    "всем советую",
]

# ==================== ТОВАРЫ (МЕРЧ) ====================
CATEGORIES = {
    "hoodies": "🧥 Худи и Свитшоты",
    "tshirts": "👕 Футболки",
    "accessories": "🎒 Аксессуары",
    "exclusive": "💎 Эксклюзивный мерч",
}

PRODUCTS = {
    "hoodie_black": {
        "name": "🧥 Худи ICE Чёрное",
        "cat": "hoodies",
        "desc": "Премиальное худи из плотного футера. Качественная вышивка, не линяет. Размеры S-XXL.",
        "prices": {1: 4500, 2: 8500, 3: 12000},
    },
    "hoodie_white": {
        "name": "🧥 Худи AK-47 Белое",
        "cat": "hoodies",
        "desc": "Лимитированная серия. Плотный материал, вышивка высокой детализации.",
        "prices": {1: 4900, 2: 9200, 3: 13000},
    },
    "tshirt_premium": {
        "name": "👕 Футболка 3.0 Premium",
        "cat": "tshirts",
        "desc": "Премиальный хлопок. Не садится после стирки. Яркий принт.",
        "prices": {1: 2900, 2: 5500, 3: 7800},
    },
    "tshirt_alpha": {
        "name": "👕 Футболка Alpha",
        "cat": "tshirts",
        "desc": "Уникальный дизайн. Ограниченный тираж. Высокое качество печати.",
        "prices": {1: 3200, 2: 6000, 3: 8500},
    },
    "exclusive_rolls": {
        "name": "💎 Лонгслив Rolls Royce",
        "cat": "exclusive",
        "desc": "Эксклюзивный лонгслив из премиального материала. Ручная работа.",
        "prices": {1: 6500, 2: 12000, 3: 17000},
    },
    "tshirt_muka": {
        "name": "👕 Футболка Muka VIP",
        "cat": "tshirts",
        "desc": "Высокое качество печати. Премиальный крой.",
        "prices": {1: 2800, 2: 5300, 3: 7500},
    },
    "tshirt_crystal": {
        "name": "👕 Футболка Crystal VIP",
        "cat": "tshirts",
        "desc": "Наша гордость. Уникальный дизайн с кристаллами.",
        "prices": {1: 3500, 2: 6600, 3: 9200},
    },
    "accessory_punisher": {
        "name": "🎒 Рюкзак Punisher",
        "cat": "accessories",
        "desc": "Качественный рюкзак из Нидерландов. Прочные материалы, удобные лямки.",
        "prices": {1: 4200, 2: 8000, 3: 11000},
    },
    "accessory_case": {
        "name": "🎒 Чехол для телефона 300",
        "cat": "accessories",
        "desc": "Ударопрочный чехол. Точная подгонка под модели iPhone и Samsung.",
        "prices": {1: 1900, 2: 3500, 3: 5000},
    },
    "exclusive_jeeter": {
        "name": "💎 Стикер-пак Jeeter Juice",
        "cat": "exclusive",
        "desc": "Эксклюзивный набор стикеров. Лимитированная серия для ценителей.",
        "prices": {1: 1500, 2: 2800, 3: 4000},
    },
    "test": {
        "name": "🧪 Тестовый платёж 100₽",
        "cat": "accessories",
        "desc": "Пробный платёж для проверки.",
        "prices": {1: 100},
    },
}

CITIES = [
    "Москва", "Санкт-Петербург", "Екатеринбург", "Казань",
    "Нижний Новгород", "Новосибирск", "Краснодар", "Ростов-на-Дону",
    "Челябинск", "Уфа", "Самара", "Омск", "Красноярск",
    "Воронеж", "Пермь", "Волгоград",
]

USDT_RATE = 90

def rub_to_usdt(rub):
    return round(rub / USDT_RATE, 1)

# ==================== ИНИЦИАЛИЗАЦИЯ ====================
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# ==================== КЛАВИАТУРЫ ====================
def main_menu():
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📦 КАТАЛОГ", callback_data="menu_catalog")],
        [InlineKeyboardButton(text="💬 ПОДДЕРЖКА", callback_data="menu_support")],
        [InlineKeyboardButton(text="⭐️ ОТЗЫВЫ", callback_data="menu_reviews")],
    ])
    return kb

def reviews_menu():
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👁 ПОСМОТРЕТЬ ОТЗЫВЫ", callback_data="show_reviews")],
        [InlineKeyboardButton(text="◀️ НАЗАД", callback_data="back_main")],
    ])
    return kb

def cities_menu():
    buttons = []
    row = []
    for city in CITIES:
        row.append(InlineKeyboardButton(text=city, callback_data=f"city_{city}"))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    buttons.append([InlineKeyboardButton(text="◀️ НАЗАД", callback_data="back_main")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def categories_menu():
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🧥 Худи и Свитшоты", callback_data="cat_hoodies")],
        [InlineKeyboardButton(text="👕 Футболки", callback_data="cat_tshirts")],
        [InlineKeyboardButton(text="🎒 Аксессуары", callback_data="cat_accessories")],
        [InlineKeyboardButton(text="💎 Эксклюзивный мерч", callback_data="cat_exclusive")],
        [InlineKeyboardButton(text="◀️ ВЫБРАТЬ ДРУГОЙ ГОРОД", callback_data="menu_catalog")],
        [InlineKeyboardButton(text="◀️ ГЛАВНОЕ МЕНЮ", callback_data="back_main")],
    ])
    return kb

def products_menu(cat_key):
    buttons = []
    for key, prod in PRODUCTS.items():
        if prod["cat"] == cat_key:
            buttons.append([InlineKeyboardButton(text=prod["name"], callback_data=f"prod_{key}")])
    buttons.append([InlineKeyboardButton(text="◀️ НАЗАД К КАТЕГОРИЯМ", callback_data="show_categories")])
    buttons.append([InlineKeyboardButton(text="◀️ ГЛАВНОЕ МЕНЮ", callback_data="back_main")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def weights_menu(product_key):
    prod = PRODUCTS[product_key]
    buttons = []
    for weight, price in prod["prices"].items():
        buttons.append([InlineKeyboardButton(
            text=f"{weight}шт — {price:,} ₽",
            callback_data=f"weight_{product_key}_{weight}"
        )])
    buttons.append([InlineKeyboardButton(
        text="◀️ НАЗАД К ТОВАРАМ",
        callback_data=f"back_to_cat_{PRODUCTS[product_key]['cat']}"
    )])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def back_to_main_btn():
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ ГЛАВНОЕ МЕНЮ", callback_data="back_main")],
    ])
    return kb

# ==================== ОБРАБОТЧИКИ ====================
@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    await message.answer(
        "🛍 <b>MERCH STORE 24/7</b> 🛍\n\n"
        "🏙️ Доставка по РФ\n"
        "🕒 Работаем круглосуточно\n\n"
        "<i>Выберите действие:</i>",
        reply_markup=main_menu(),
        parse_mode="html",
    )

@dp.callback_query(lambda c: c.data == "back_main")
async def back_main(call: CallbackQuery, state: FSMContext):
    await state.clear()
    try:
        await call.message.edit_text(
            "🛍 <b>MERCH STORE 24/7</b> 🛍\n\n"
            "🕒 Работаем круглосуточно\n\n"
            "<i>Выберите действие:</i>",
            reply_markup=main_menu(),
            parse_mode="html",
        )
    except:
        await call.message.answer(
            "🛍 <b>MERCH STORE 24/7</b> 🛍\n\n"
            "🕒 Работаем круглосуточно\n\n"
            "<i>Выберите действие:</i>",
            reply_markup=main_menu(),
            parse_mode="html",
        )
    await call.answer()

@dp.callback_query(lambda c: c.data == "menu_catalog")
async def show_cities(call: CallbackQuery):
    await call.message.edit_text(
        "📍 <b>Выберите ваш город:</b>",
        reply_markup=cities_menu(),
        parse_mode="html",
    )
    await call.answer()

@dp.callback_query(lambda c: c.data.startswith("city_"))
async def city_selected(call: CallbackQuery):
    city = call.data.split("_", 1)[1]
    await call.message.edit_text(
        f"✅ <b>Город: {city}</b>\n\n<i>Выберите категорию:</i>",
        reply_markup=categories_menu(),
        parse_mode="html",
    )
    await call.answer()

@dp.callback_query(lambda c: c.data == "show_categories")
async def show_categories(call: CallbackQuery):
    await call.message.edit_text(
        "<i>Выберите категорию:</i>",
        reply_markup=categories_menu(),
        parse_mode="html",
    )
    await call.answer()

@dp.callback_query(lambda c: c.data.startswith("cat_"))
async def show_products(call: CallbackQuery):
    cat_key = call.data.replace("cat_", "")
    await call.message.edit_text(
        f"📦 <b>{CATEGORIES.get(cat_key, 'Товары')}</b>\n\n<i>Выберите товар:</i>",
        reply_markup=products_menu(cat_key),
        parse_mode="html",
    )
    await call.answer()

@dp.callback_query(lambda c: c.data.startswith("back_to_cat_"))
async def back_to_category(call: CallbackQuery):
    cat_key = call.data.replace("back_to_cat_", "")
    await call.message.edit_text(
        f"📦 <b>{CATEGORIES.get(cat_key, 'Товары')}</b>\n\n<i>Выберите товар:</i>",
        reply_markup=products_menu(cat_key),
        parse_mode="html",
    )
    await call.answer()

@dp.callback_query(lambda c: c.data.startswith("prod_"))
async def show_product(call: CallbackQuery):
    prod_key = call.data.replace("prod_", "")
    prod = PRODUCTS[prod_key]
    prices_str = "\n".join([
        f"▪️ {k} шт — {v:,} ₽"
        for k, v in prod["prices"].items()
    ])
    await call.message.edit_text(
        f"{prod['name']}\n\n{prod['desc']}\n\n💵 <b>ЦЕНА:</b>\n{prices_str}\n\n⬇️ <i>Выберите количество:</i>",
        reply_markup=weights_menu(prod_key),
        parse_mode="html",
        disable_web_page_preview=True,
    )
    await call.answer()

@dp.callback_query(lambda c: c.data.startswith("weight_"))
async def start_payment(call: CallbackQuery, state: FSMContext):
    parts = call.data.split("_")
    if len(parts) < 3:
        return
    prod_key = parts[1]
    try:
        qty = int(parts[2])
    except ValueError:
        return
    prod = PRODUCTS[prod_key]
    price_rub = prod["prices"][qty]
    order_id = f"MERCH_{call.from_user.id}_{int(datetime.now().timestamp())}"

    await call.message.edit_text("⏳ Создаю платёж...")

    body = {
        "token": CACTUS_TOKEN,
        "amount": price_rub,
        "order_id": order_id,
        "description": f"Order {order_id}",
    }

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(CACTUS_API_URL, json=body) as resp:
                data = await resp.json()
        except:
            await call.message.edit_text("❌ Ошибка. Попробуйте позже.", reply_markup=back_to_main_btn())
            return

    if data.get("status") != "success":
        await call.message.edit_text("❌ Ошибка создания платежа.", reply_markup=back_to_main_btn())
        return

    payment_url = data["response"]["url"]

    caption = (
        f"🛒 <b>ЗАКАЗ СФОРМИРОВАН</b>\n\n"
        f"📦 <b>Товар:</b> {prod['name']}\n"
        f"📦 <b>Количество:</b> {qty} шт\n"
        f"💵 <b>Сумма:</b> {price_rub:,} ₽\n\n"
        f"<i>Нажмите кнопку ниже для перехода к оплате.</i>"
    )

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 ОПЛАТИТЬ", url=payment_url)],
        [InlineKeyboardButton(text="◀️ ГЛАВНОЕ МЕНЮ", callback_data="back_main")],
    ])

    await call.message.edit_text(caption, reply_markup=kb, parse_mode="html")

# ==================== ПОДДЕРЖКА ====================
SUPPORT_USERNAME = "liqvidoff"

@dp.callback_query(lambda c: c.data == "menu_support")
async def support(call: CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💬 НАПИСАТЬ В ПОДДЕРЖКУ", url=f"https://t.me/{SUPPORT_USERNAME}")],
        [InlineKeyboardButton(text="◀️ НАЗАД", callback_data="back_main")],
    ])
    await call.message.edit_text(
        "💬 <b>ПОДДЕРЖКА</b>\n\nНажмите кнопку для связи с оператором.\n\n<i>Время ответа: до 10 минут.</i>",
        reply_markup=kb,
        parse_mode="html",
    )
    await call.answer()

# ==================== ОТЗЫВЫ ====================
@dp.callback_query(lambda c: c.data == "menu_reviews")
async def reviews(call: CallbackQuery):
    selected = random.sample(FAKE_REVIEWS, 5)
    msg = "⭐️ <b>ОТЗЫВЫ ПОКУПАТЕЛЕЙ</b>\n\n"
    for review in selected:
        fake_time = datetime.now() - timedelta(minutes=random.randint(2, 5))
        time_str = fake_time.strftime("%H:%M")
        msg += f"🕐 {time_str} МСК — {review}\n\n"
    msg += "<i>🔒 Все отзывы анонимны.</i>"

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ НАЗАД", callback_data="back_main")],
    ])
    await call.message.edit_text(msg, reply_markup=kb, parse_mode="html", disable_web_page_preview=True)
    await call.answer()

# ==================== ЗАПУСК ====================
async def main():
    print("⚡ MERCH BOT ЗАПУЩЕН")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())