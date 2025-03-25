import pygame
import os
from config import BROWN, YELLOW, GREEN, BLACK, GRAY, SEEDS, WHITE


def load_game_images():
    """Загружает и масштабирует все изображения игры."""
    IMAGES = {}

    def load_image(path, size=None, fallback_color=BLACK, force_size=None):
        """Вспомогательная функция для загрузки изображения."""
        try:
            if not os.path.exists(path):
                print(f"File not found: {path}")
                raise FileNotFoundError(f"Image file {path} does not exist")
            image = pygame.image.load(path).convert_alpha()
            if force_size:
                return pygame.transform.scale(image, force_size)
            if size:
                return pygame.transform.scale(image, size)
            return image  # Загружаем в оригинальном размере, если size не указан
        except (pygame.error, FileNotFoundError) as e:
            if force_size:
                surface = pygame.Surface(force_size)
            elif size:
                surface = pygame.Surface(size)
            else:
                surface = pygame.Surface((64, 64))  # Размер заглушки по умолчанию
            surface.fill(fallback_color)
            return surface

    # Загрузка изображений игрока (force_size не нужен, оставляем как есть)
    IMAGES["player_idle"] = load_image(os.path.join("images", "heroes", "player", "player_idle.png"), (64, 64), BROWN)
    IMAGES["player_walking"] = load_image(os.path.join("images", "heroes", "player", "player_walking.png"), (64, 64), BROWN)
    IMAGES["player_watering"] = load_image(os.path.join("images", "heroes", "player", "player_watering.png"), (64, 64), (0, 0, 255))
    IMAGES["player_harvesting"] = load_image(os.path.join("images", "heroes", "player", "player_harvesting.png"), (64, 64), GREEN)
    IMAGES["player_processing"] = load_image(os.path.join("images", "heroes", "player", "player_processing.png"), (64, 64), (255, 165, 0))

    # Загрузка тайлов травы с принудительным масштабированием до 32x32
    IMAGES["grass_tile_1"] = load_image(os.path.join("images", "tiles", "grass_1.png"), (32, 32), GREEN, force_size=(32, 32))
    IMAGES["grass_tile_2"] = load_image(os.path.join("images", "tiles", "grass_2.png"), (32, 32), GREEN, force_size=(32, 32))
    IMAGES["grass_tile_3"] = load_image(os.path.join("images", "tiles", "grass_3.png"), (32, 32), GREEN, force_size=(32, 32))

    # Остальные изображения (force_size не нужен)
    IMAGES["bed_dry"] = load_image(os.path.join("images", "map_objects", "bed_dry.png"), (32, 32), BROWN)
    IMAGES["bed_wet"] = load_image(os.path.join("images", "map_objects", "bed_wet.png"), (32, 32), (0, 0, 255))
    IMAGES["bed_ripe"] = load_image(os.path.join("images", "map_objects", "bed_ripe.png"), (32, 32), YELLOW)
    IMAGES["house"] = load_image(os.path.join("images", "map_objects", "house.png"), (128, 128), BLACK)
    IMAGES["market_stall"] = load_image(os.path.join("images", "map_objects", "market_stall.png"), (64, 64), (139, 69, 19))
    IMAGES["mill"] = load_image(os.path.join("images", "map_objects", "mill.png"), (64, 64), (160, 82, 45))
    IMAGES["background_menu"] = load_image(os.path.join("images", "ui", "background_menu.jpg"), (1280, 360), GRAY)
    IMAGES["coin_main"] = load_image(os.path.join("images", "ui", "coin.png"), (32, 32), YELLOW)
    IMAGES["coin_menu"] = load_image(os.path.join("images", "ui", "coin.png"), (16, 16), YELLOW)
    IMAGES["harvest"] = load_image(os.path.join("images", "ui", "harvest.png"), (32, 32), GREEN)
    IMAGES["product"] = load_image(os.path.join("images", "ui", "product.png"), (32, 32), (255, 165, 0))
    IMAGES["canning_cellar"] = load_image(os.path.join("images", "map_objects", "canning_cellar.png"), (64, 64), (128, 0, 128))
    IMAGES["button_normal"] = load_image(os.path.join("images", "ui", "button_normal.png"), (200, 60), GRAY)
    IMAGES["button_hover"] = load_image(os.path.join("images", "ui", "button_hover.png"), (200, 60), WHITE)
    IMAGES["return"] = load_image(os.path.join("images", "ui", "return.png"), (32, 32), WHITE)
    IMAGES["return_hover"] = load_image(os.path.join("images", "ui", "return_hover.png"), (32, 32), GRAY)
    IMAGES["close_button"] = load_image(os.path.join("images", "ui", "close_button.png"), (32, 32), GRAY)
    IMAGES["close_button_hover"] = load_image(os.path.join("images", "ui", "close_button_hover.png"), (32, 32), GRAY)
    IMAGES["arrow_left"] = load_image(os.path.join("images", "ui", "arrow_left.png"), (20, 20), GRAY)
    IMAGES["arrow_right"] = load_image(os.path.join("images", "ui", "arrow_right.png"), (20, 20), GRAY)
    IMAGES["construction_icon"] = load_image(os.path.join("images", "ui", "construction.png"), (32, 32), GRAY)
    IMAGES["planting_icon"] = load_image(os.path.join("images", "ui", "planting.png"), (32, 32), GRAY)
    IMAGES["wheel_background"] = load_image(os.path.join("images", "ui", "wheel_background.png"), (100, 100), GRAY)
    IMAGES["menu_background"] = load_image(os.path.join("images", "ui", "menu_background.png"), (200, 360), GRAY)
    IMAGES["move_normal"] = load_image(os.path.join("images", "ui", "move_normal.png"), (32, 32), GRAY)
    IMAGES["move_hover"] = load_image(os.path.join("images", "ui", "move_hover.png"), (32, 32), GRAY)
    IMAGES["move_active"] = load_image(os.path.join("images", "ui", "move_active.png"), (32, 32), GRAY)
    IMAGES["destroy_normal"] = load_image(os.path.join("images", "ui", "destroy_normal.png"), (32, 32), GRAY)
    IMAGES["destroy_hover"] = load_image(os.path.join("images", "ui", "destroy_hover.png"), (32, 32), GRAY)
    IMAGES["destroy_active"] = load_image(os.path.join("images", "ui", "destroy_active.png"), (32, 32), GRAY)
    IMAGES["tooltip_background"] = load_image(os.path.join("images", "ui", "tooltip_background.png"), (100, 120), GRAY)
    IMAGES["puck_seed"] = load_image(os.path.join("images", "ui", "puck_seed.png"), (64, 64), GRAY, force_size=(64, 64))
    IMAGES["clock_icon"] = load_image(os.path.join("images", "ui", "clock_icon.png"), (16, 16), GRAY)
    IMAGES["water_drop_icon"] = load_image(os.path.join("images", "ui", "water_drop_icon.png"), (16, 16), GRAY)
    IMAGES["hero_portrait"] = load_image(os.path.join("images", "heroes","player", "player_portrait.png"), (64, 64), GRAY)
    IMAGES["notification_background"] = load_image(os.path.join("images", "ui", "notification_background.png"),(400, 84), GRAY)

    for seed in SEEDS:
        plant_name = seed["name"]
        IMAGES[f"{plant_name}_seedling"] = load_image(
            os.path.join("images", "plants", f"{plant_name}_seedling.png"), (32, 32), GREEN
        )
        IMAGES[f"{plant_name}_sprout"] = load_image(
            os.path.join("images", "plants", f"{plant_name}_sprout.png"), (32, 32), (0, 128, 0)
        )
        IMAGES[f"{plant_name}_ripe"] = load_image(
            os.path.join("images", "plants", f"{plant_name}_ripe.png"), (32, 32), YELLOW
        )
        IMAGES[f"{plant_name}_seed"] = load_image(
            os.path.join("images", "plants", f"{plant_name}_seed.png"), (32, 32), YELLOW
        )

        # Новая динамическая загрузка для остальных категорий (map_objects, heroes)
        def get_fallback_color(category, obj_type):
            """Определяет цвет заглушки в зависимости от категории и типа объекта."""
            if category == "map_objects":
                if obj_type == "mill":
                    return (160, 82, 45)
                elif obj_type == "canning_cellar":
                    return (128, 0, 128)
                elif obj_type == "house":
                    return BLACK
                elif obj_type == "market_stall":
                    return (139, 69, 19)
                elif obj_type == "bed":
                    return BROWN
            elif category == "heroes":
                return BROWN
            return BLACK

        base_dir = "images"
        for category in os.listdir(base_dir):
            # Пропускаем ui, plants и tiles, так как они уже загружены
            if category in ["ui", "plants", "tiles"]:
                continue

            category_path = os.path.join(base_dir, category)
            if not os.path.isdir(category_path):
                continue

            for obj_type in os.listdir(category_path):
                obj_path = os.path.join(category_path, obj_type)
                if not os.path.isdir(obj_path):
                    continue

                # Определяем цвет заглушки
                fallback_color = get_fallback_color(category, obj_type)

                # Загружаем содержимое папки
                static_image = None
                states = {}  # Словарь для хранения анимаций и одиночных изображений
                for filename in os.listdir(obj_path):
                    if not filename.endswith(".png"):
                        continue
                    file_path = os.path.join(obj_path, filename)
                    name = filename.replace(".png", "")

                    # Разделяем имя файла на состояние и номер кадра (если есть)
                    parts = name.rsplit("_", 1)
                    if len(parts) == 2 and parts[1].isdigit():
                        state_name = parts[0]
                        frame_number = int(parts[1])
                        if state_name not in states:
                            states[state_name] = []
                        states[state_name].append(
                            (frame_number, load_image(file_path, size=None, fallback_color=fallback_color)))
                    else:
                        # Одиночное изображение (static или состояние без номера)
                        states[name] = load_image(file_path, size=None, fallback_color=fallback_color)
                        if name == "static":
                            static_image = states[name]

                # Сортируем анимации по номеру кадра
                for state in states:
                    if isinstance(states[state], list):
                        states[state].sort(key=lambda x: x[0])
                        states[state] = [frame[1] for frame in states[state]]

                # Сохраняем статичное изображение
                if "static" in states:
                    IMAGES[obj_type] = states["static"]
                    del states["static"]  # Удаляем из состояний, чтобы не дублировать
                    print(f"Loaded static image for {obj_type}")

                # Сохраняем состояния (анимации или одиночные изображения)
                if states:
                    if category == "map_objects" and obj_type == "bed":
                        # Для грядок сохраняем dry, wet, ripe отдельно
                        IMAGES["bed_dry"] = states.get("dry", load_image("", size=None, fallback_color=BROWN))
                        IMAGES["bed_wet"] = states.get("wet", load_image("", size=None, fallback_color=(0, 0, 255)))
                        IMAGES["bed_ripe"] = states.get("ripe", load_image("", size=None, fallback_color=YELLOW))
                    else:
                        # Для остальных объектов сохраняем состояния как анимации
                        IMAGES[f"{obj_type}_animations"] = states
                        print(f"Loaded states for {obj_type}: {list(states.keys())}")

        return IMAGES

    GAME_IMAGES = {}