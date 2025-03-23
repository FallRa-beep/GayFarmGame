import pygame
import os
from config import BROWN, YELLOW, GREEN, BLACK, GRAY, SEEDS, WHITE


def load_game_images():
    """Загружает и масштабирует все изображения игры."""
    IMAGES = {}

    def load_image(path, size, fallback_color, force_size=None):
        try:
            if not os.path.exists(path):
                print(f"File not found: {path}")
                raise FileNotFoundError(f"Image file {path} does not exist")
            image = pygame.image.load(path).convert_alpha()
            if force_size:
                image = pygame.transform.scale(image, force_size)
            else:
                image = pygame.transform.scale(image, size)
            return image
        except (pygame.error, FileNotFoundError) as e:
            surface = pygame.Surface(size)
            surface.fill(fallback_color)
            return surface

    # Динамическая загрузка спрайтов игрока из папки images/animation/player
    player_animation_dir = os.path.join("images", "animation", "player")
    player_states = {}
    if os.path.exists(player_animation_dir):
        for filename in os.listdir(player_animation_dir):
            if filename.endswith(".png"):
                # Разделяем имя файла на части
                parts = filename.rsplit("_", 1)  # Делим по последнему "_"
                if len(parts) == 2 and parts[1].replace(".png", "").isdigit():
                    state_name = parts[0]  # Например, "walking_down" из "walking_down_1.png"
                    frame_number = int(parts[1].replace(".png", ""))  # Например, "1" из "walking_down_1.png"
                else:
                    state_name = filename.replace(".png", "")  # Например, "processing" из "processing.png"
                    frame_number = 1  # Если номера нет, считаем это первым кадром

                frame_path = os.path.join(player_animation_dir, filename)
                image = load_image(frame_path, (64, 64), BROWN)

                if state_name not in player_states:
                    player_states[state_name] = []
                # Добавляем кадр в список, сортируя по номеру кадра
                player_states[state_name].append((frame_number, image))

        # Сортируем кадры по номеру
        for state in player_states:
            player_states[state].sort(key=lambda x: x[0])  # Сортируем по frame_number
            player_states[state] = [frame[1] for frame in player_states[state]]  # Оставляем только изображения
    else:
        print(f"Папка {player_animation_dir} не найдена, используются заглушки")
        # Заглушки для базовых состояний
        default_states = ["idle", "walking_up", "walking_down", "walking_left", "walking_right", "watering",
                          "harvesting", "processing"]
        for state in default_states:
            player_states[state] = [pygame.Surface((64, 64), pygame.SRCALPHA)]
            player_states[state][0].fill((255, 0, 0, 128))

    IMAGES["player_animations"] = player_states

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



    return IMAGES

GAME_IMAGES = {}