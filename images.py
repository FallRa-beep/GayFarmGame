import pygame
import os
from config import BROWN, YELLOW, GREEN, BLACK, GRAY, SEEDS

def load_game_images():
    """Загружает и масштабирует все изображения игры."""
    IMAGES = {}

    def load_image(path, size, fallback_color, force_size=None):
        try:
            print(f"Attempting to load image from {path}")
            if not os.path.exists(path):
                print(f"File not found: {path}")
                raise FileNotFoundError(f"Image file {path} does not exist")
            image = pygame.image.load(path).convert_alpha()
            print(f"Successfully loaded image from {path}")
            # Если указан force_size, масштабируем изображение до этого размера
            if force_size:
                image = pygame.transform.scale(image, force_size)
            else:
                image = pygame.transform.scale(image, size)
            return image
        except (pygame.error, FileNotFoundError) as e:
            print(f"Error loading {path}: {e}. Using fallback color {fallback_color}.")
            surface = pygame.Surface(size)
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
    IMAGES["bed_dry"] = load_image(os.path.join("images", "map_objects", "bed_dry.png"), (64, 64), BROWN)
    IMAGES["bed_wet"] = load_image(os.path.join("images", "map_objects", "bed_wet.png"), (64, 64), (0, 0, 255))
    IMAGES["bed_ripe"] = load_image(os.path.join("images", "map_objects", "bed_ripe.png"), (64, 64), YELLOW)
    IMAGES["house"] = load_image(os.path.join("images", "map_objects", "house.png"), (128, 128), BLACK)
    IMAGES["market_stall"] = load_image(os.path.join("images", "map_objects", "market_stall.png"), (64, 64), (139, 69, 19))
    IMAGES["mill"] = load_image(os.path.join("images", "map_objects", "mill.png"), (64, 64), (160, 82, 45))
    IMAGES["background_menu"] = load_image(os.path.join("images", "ui", "background_menu.jpg"), (1280, 360), GRAY)
    IMAGES["coin_main"] = load_image(os.path.join("images", "ui", "coin.png"), (32, 32), YELLOW)
    IMAGES["coin_menu"] = load_image(os.path.join("images", "ui", "coin.png"), (16, 16), YELLOW)
    IMAGES["harvest"] = load_image(os.path.join("images", "ui", "harvest.png"), (32, 32), GREEN)
    IMAGES["product"] = load_image(os.path.join("images", "ui", "product.png"), (32, 32), (255, 165, 0))
    IMAGES["canning_cellar"] = load_image(os.path.join("images", "map_objects", "canning_cellar.png"), (64, 64), (128, 0, 128))

    for seed in SEEDS:
        plant_name = seed["name"]
        IMAGES[f"{plant_name}_seedling"] = load_image(
            os.path.join("images", "plants", f"{plant_name}_seedling.png"), (64, 64), GREEN
        )
        IMAGES[f"{plant_name}_sprout"] = load_image(
            os.path.join("images", "plants", f"{plant_name}_sprout.png"), (64, 64), (0, 128, 0)
        )
        IMAGES[f"{plant_name}_ripe"] = load_image(
            os.path.join("images", "plants", f"{plant_name}_ripe.png"), (64, 64), YELLOW
        )

    print("Images loaded or replaced with fallbacks!")
    for key, img in IMAGES.items():
        print(f"Size of {key}: {img.get_size()}")

    return IMAGES

GAME_IMAGES = {}