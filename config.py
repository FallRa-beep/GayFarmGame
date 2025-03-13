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
        "cost_coins": 10,
        "unlock_level": 1,
        "category": "functional",  # Категория
        "consume": {},
        "produce": {},
        "work_time": 0
    },
    "mill": {
        "cost_coins": 25,
        "cost_harvest": 1,
        "unlock_level": 2,
        "category": "functional",
        "consume": {"harvest": 2},
        "produce": {"products": 1},
        "work_time": 5000
    },
    "canning_cellar": {
        "cost_coins": 30,
        "cost_harvest": 1,
        "cost_products": 1,
        "unlock_level": 2,
        "category": "functional",
        "consume": {"harvest": 4},
        "produce": {"products": 2},
        "work_time": 60000
    },
    # Пример декора (можно добавить позже)
    "fence": {
        "cost_coins": 5,
        "unlock_level": 1,
        "category": "decor",
        "consume": {},
        "produce": {},
        "work_time": 0
    }
}