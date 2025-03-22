# translations.py
TRANSLATIONS = {
    "en": {
        "New Game": "New Game",
        "Continue": "Continue",
        "Settings": "Settings",
        "Exit": "Exit",
        "Language": "Language",
        "Russian": "Russian",
        "English": "English",
        "Auto-save completed!": "Auto-save completed!",

        "Level up! New level: {level}": "Level up! New level: {level}",
        "Save the game?": "Save the game?",
        "Game saved!": "Game saved!",
        "Coins": "Coins",
        "Level": "Level",
        "Construction": "Construction",
        "Planting": "Planting",
        "Wheat": "Wheat",
        "corn": "Corn",
        "Name": "Name",
        "Cost": "Cost",
        "Growth Time": "Growth Time",
        "Watering Interval": "Watering Interval",
        "Income": "Income",
        "Move": "Move",
        "Destroy": "Destroy",
        "Bed": "Bed",
        "bed_description": "Simple bed for planting plants",
        "min": "min",
        "Market Stall": "Market Stall",
        "Harvest": "Harvest",
        "Products": "Products",
        "Total": "Total",
        "Sell": "Sell",
        "Mill": "Mill",
        "Canning Cellar": "Cellar",
        "Harvest Yield": "Harvest Yield",
        "Load": "Load",
        "Build": "Build",
        "Your path to the top. A hot and passionate climb to success!":"Your path to the top. A hot and passionate climb to success!",
        "Tasty delicacies to seduce anyone!": "Tasty delicacies to seduce anyone!",
        "The juicy fruits of your labor — a sweetness you can't resist...": "The juicy fruits of your labor — a sweetness you can't resist...",
        "Golden sparks that make hearts beat faster!": "Golden sparks that make hearts beat faster!",
        "Music Volume": "Music",
        "Sound Volume": "Sound"
    },
    "ru": {
        "New Game": "Новая игра",
        "Continue": "Продолжить",
        "Settings": "Настройки",
        "Exit": "Выйти",
        "Language": "Язык",
        "Russian": "Русский",
        "English": "Английский",
        "Auto-save completed!": "Автосохранение выполнено!",

        "Save the game?": "Сохранить игру?",
        "Game saved!": "Игра сохранена!",
        "Coins": "Монеты",
        "Level": "Уровень",
        "Construction": "Строительство",
        "Planting": "Посадки",
        "Wheat": "Пшеница",
        "corn": "Кукуруза",
        "Name": "Название",
        "Cost": "Стоимость",
        "Growth Time": "Время роста",
        "Watering Interval": "Интервал полива",
        "Income": "Доход",
        "Move": "Переместить",
        "Destroy": "×",
        "Bed": "Грядка",
        "bed_description": "Простая грядка для посадки растений",
        "Cost: 10 coins": "Стоимость: 10 монет",
        "min": "мин",
        "Planted": "Посажено",
        "at bed at": "на грядку в",
        "coin_symbol": "",
        "Market Stall": "Ларек",
        "Harvest": "Урожай",
        "Products": "Продукты",
        "Total": "Итого",
        "Sell": "Продать",
        "Mill": "Мельница",
        "Converts 2 Harvest into 1 Product in 5 seconds": "Преобразует 2 Урожая в 1 Продукт за 5 секунд",
        "Cost: 25 coins + 1 Harvest": "Стоимость: 25 монет + 1 Урожай",
        "Canning Cellar": "Погреб",  # Добавляем перевод для Canning Cellar
        "Harvest Yield": "Получаемый урожай",
        "Load": "Загрузка", # Добавляем перевод для Harvest Yield
        "Build": "Построить",
        "Your path to the top. A hot and passionate climb to success!":"Твой путь к вершине — горячий и страстный подъем к успеху!",
        "Tasty delicacies to seduce anyone!": "Вкусные деликатесы, чтобы соблазнить любого!!",
        "The juicy fruits of your labor — a sweetness you can't resist...": "Сочные плоды твоих трудов — сладость, которую хочется попробовать...",
        "Golden sparks that make hearts beat faster!": "Золотые искры, которые заставляют сердца биться чаще!",
        "Music Volume": "Музыка",
        "Sound Volume": "Звуки",
        "Do you want to save the game?": "Вы хотите сохранить игру?",
        "No": "Нет",
        "Yes": "Да",
        "Cancel": "Отмена",
        "Please select a slot!": "Выберите слот для сохранения",
        "Save to": "Сохранить в",
        "Select a save to load:": "Выберите сохранение",
    }
}

def get_text(key, language="en"):
    """
    Возвращает перевод строки для указанного языка.
    Если перевод не найден, возвращает исходный ключ.
    """
    return TRANSLATIONS.get(language, {}).get(key, key)