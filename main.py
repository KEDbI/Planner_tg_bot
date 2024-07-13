import asyncio
from aiogram import Dispatcher, Bot
from aiogram.client.bot import DefaultBotProperties
from config_data.config import load_bot_config, BotConfig
from handlers import user_handlers


async def main() -> None:
    # Инициализируем конфиг
    config: BotConfig = load_bot_config()

    # Инициализируем бот и корневой роутер
    bot: Bot = Bot(token=config.tgbot.token, default=DefaultBotProperties(parse_mode='HTML'))
    dp: Dispatcher = Dispatcher()

    # Регистрируем роутеры в диспетчере
    dp.include_router(user_handlers.router)

    # Пропускаем накопившиеся апдейты и запускаем polling1
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())