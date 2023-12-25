import asyncio
from aiogram import Bot, Dispatcher, types, executor
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import geopy.distance

API_TOKEN = '6357761122:AAGDwB6thp4IEi3jAQr2x7co5CqilSrzgA0'

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Список всех кофеен с ценами и координатами
coffee_shops = [
    {
        'name': 'Кофейня 1',
        'prices': {'кофе': 30, 'чай': 25},
        'coordinates': {'latitude': 55.7539, 'longitude': 37.6204}
    },

]

@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    await message.reply("Привет! Я помогу тебе выбрать ближайшую кофейню с ценниками. Чтобы начать, введи свою геолокацию:")

@dp.message_handler(commands=['price'])
async def send_price(message: types.Message):
    await message.answer("Пожалуйста, отправьте свою геолокацию:")

@dp.message_handler(content_types=['location'])
async def handle_location(message: types.Message):
    user_coordinates = message.location.latitude, message.location.longitude
    closest_shop = await get_closest_shop(user_coordinates)
    prices = closest_shop['prices']
    keyboard = create_prices_keyboard(prices)
    await message.reply(f"Цены в {closest_shop['name']}:", reply_markup=keyboard)


async def get_user_coordinates(message):
    try:
        response = await bot.get_updates()
        for update in response:
            if 'message' in update and 'location' in update['message']:
                return update['message']['location']['latitude'], update['message']['location']['longitude']
    except asyncio.TimeoutError:
        await bot.send_message(message.chat.id, "Время ожидания истекло. Пожалуйста, попробуйте снова.")
        return



async def get_closest_shop(user_coordinates):
    closest_shop = None
    closest_distance = float('inf')
    for shop in coffee_shops:
        shop_coordinates = (shop['coordinates']['latitude'], shop['coordinates']['longitude'])
        distance = geopy.distance.distance(user_coordinates, shop_coordinates).km
        if distance < closest_distance:
            closest_distance = distance
            closest_shop = shop
    return closest_shop

def create_prices_keyboard(prices):
    keyboard = types.InlineKeyboardMarkup()
    for product, price in prices.items():
        button = types.InlineKeyboardButton(text=f"{product} - {price}₽", callback_data='none')
        keyboard.add(button)
    return keyboard

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
