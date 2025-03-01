# config.py
SCREEN_HEIGHT = 360
MAP_WIDTH = 3000
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (211, 211, 211)
GREEN = (0, 255, 0)
BROWN = (165, 42, 42)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)

SEEDS = [
    {"name": "wheat", "cost": 0, "ripening_time_minutes": 0.2, "watering_interval_minutes": 0.1, "sprout_time_minutes": 0.1, "harvest_yield": 5, "unlock_level": 1},
    {"name": "corn", "cost": 1, "ripening_time_minutes": 0.2, "watering_interval_minutes": 0.1, "sprout_time_minutes": 0.1, "harvest_yield": 8, "unlock_level": 2}
]

LEVEL_THRESHOLDS = {1: 5, 2: 10, 3: 20, 4: 40}

BUILDING_CONFIG = {
    "bed": {
        "cost_coins": 10,  # Стоимость в монетах
        "unlock_level": 1,  # Уровень, на котором здание становится доступным
        "consume": {},  # Потребляемые ресурсы (пусто для грядки)
        "produce": {},  # Производимые ресурсы (пусто для грядки)
        "work_time": 0  # Время работы (0, так как грядка не требует работы)
    },
    "mill": {
        "cost_coins": 25,  # Стоимость в монетах
        "cost_harvest": 1,  # Потребление Harvest для постройки
        "unlock_level": 2,  # Уровень открытия
        "consume": {"harvest": 2},  # Потребляет 2 Harvest за цикл
        "produce": {"products": 1},  # Производит 1 Product за цикл
        "work_time": 5000  # Время работы (5 секунд для обработки)
    },
    "canning_cellar": {
        "cost_coins": 30,  # Стоимость в монетах
        "cost_harvest": 1,  # Потребление 1 Harvest для постройки
        "cost_products": 1,  # Потребление 1 Product для постройки
        "unlock_level": 2,  # Уровень открытия
        "consume": {"harvest": 4},  # Потребляет 4 Harvest за цикл
        "produce": {"products": 2},  # Производит 2 Products за цикл
        "work_time": 60000  # Время работы (6 минут = 360000 мс)
    }
}