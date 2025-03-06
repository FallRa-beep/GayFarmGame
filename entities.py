import pygame
from config import BROWN, YELLOW, GREEN, BLACK, MAP_WIDTH, SCREEN_HEIGHT, SEEDS, BUILDING_CONFIG
import images
import math

class MapObject:
    def __init__(self, x, y, width, height, color, obj_type="generic"):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.obj_type = obj_type
        self.movable = False  # По умолчанию объект нельзя перемещать
        self.image = None
        if self.obj_type == "house":
            try:
                self.image = images.GAME_IMAGES["house"]
            except KeyError:
                self.image = pygame.Surface((self.width, self.height))
                self.image.fill(BLACK)

    def reload_images(self):
        """Перезагружает изображения объекта."""
        if self.obj_type == "house":
            try:
                self.image = images.GAME_IMAGES["house"]
            except KeyError:
                self.image = pygame.Surface((self.width, self.height))
                self.image.fill(BLACK)

    def draw(self, screen, camera_x):
        if self.image and self.obj_type == "house":
            screen.blit(self.image, (self.x - camera_x, self.y))
        else:
            pygame.draw.rect(screen, self.color, (self.x - camera_x, self.y, self.width, self.height))

    def to_dict(self):
        return {
            "x": self.x, "y": self.y, "width": self.width, "height": self.height,
            "color": self.color, "obj_type": self.obj_type, "movable": self.movable
        }

class MarketStall(MapObject):
    def __init__(self, x, y, width=64, height=64):
        super().__init__(x, y, width, height, (139, 69, 19), "market_stall")
        self.movable = True  # Ларек можно перемещать
        try:
            self.image = images.GAME_IMAGES["market_stall"]
        except KeyError:
            print("Ошибка: изображение ларька не найдено")
            self.image = pygame.Surface((self.width, self.height))
            self.image.fill((139, 69, 19))

    def reload_images(self):
        """Перезагружает изображение ларька."""
        try:
            self.image = images.GAME_IMAGES["market_stall"]
        except KeyError:
            print("Ошибка: изображение ларька не найдено")
            self.image = pygame.Surface((self.width, self.height))
            self.image.fill((139, 69, 19))

    def draw(self, screen, camera_x):
        screen.blit(self.image, (self.x - camera_x, self.y))

    def to_dict(self):
        return {
            "x": self.x, "y": self.y, "width": self.width, "height": self.height,
            "color": self.color, "obj_type": "market_stall", "movable": self.movable
        }

class Bed(MapObject):
    def __init__(self, x, y, width=64, height=64):
        super().__init__(x, y, width, height, BROWN, "bed")
        self.movable = True  # Грядку можно перемещать
        self.is_planted = False
        self.plant_type = None
        self.is_watered = False
        self.is_sprouted = False
        self.last_watered_time = 0
        self.ripening_start_time = None
        self.is_ripe = False
        self.total_ripening_time = 0
        self.first_watering_time = None
        self.watering_start_time = None
        self.watering_duration = 2000
        try:
            self.image_dry = images.GAME_IMAGES["bed_dry"]
            self.image_wet = images.GAME_IMAGES["bed_wet"]
            self.image_ripe = images.GAME_IMAGES["bed_ripe"]
        except KeyError as e:
            print(f"Ошибка: изображение грядки не найдено - {e}")
            self.image_dry = pygame.Surface((self.width, self.height))
            self.image_dry.fill(BROWN)
            self.image_wet = pygame.Surface((self.width, self.height))
            self.image_wet.fill((0, 0, 255))
            self.image_ripe = pygame.Surface((self.width, self.height))
            self.image_ripe.fill(YELLOW)

    def reload_images(self):
        """Перезагружает изображения грядки."""
        try:
            self.image_dry = images.GAME_IMAGES["bed_dry"]
            self.image_wet = images.GAME_IMAGES["bed_wet"]
            self.image_ripe = images.GAME_IMAGES["bed_ripe"]
        except KeyError as e:
            print(f"Ошибка: изображение грядки не найдено - {e}")
            self.image_dry = pygame.Surface((self.width, self.height))
            self.image_dry.fill(BROWN)
            self.image_wet = pygame.Surface((self.width, self.height))
            self.image_wet.fill((0, 0, 255))
            self.image_ripe = pygame.Surface((self.width, self.height))
            self.image_ripe.fill(YELLOW)

    def draw(self, screen, camera_x):
        if self.is_ripe:
            screen.blit(self.image_ripe, (self.x - camera_x, self.y))
        elif self.is_watered and pygame.time.get_ticks() - self.last_watered_time < 10000:
            screen.blit(self.image_wet, (self.x - camera_x, self.y))
        else:
            screen.blit(self.image_dry, (self.x - camera_x, self.y))

        if self.is_planted and self.plant_type:
            try:
                if self.is_ripe:
                    plant_image = images.GAME_IMAGES[f"{self.plant_type}_ripe"]
                elif self.is_sprouted:
                    plant_image = images.GAME_IMAGES[f"{self.plant_type}_sprout"]
                else:
                    plant_image = images.GAME_IMAGES[f"{self.plant_type}_seedling"]
                plant_x = self.x + (self.width - plant_image.get_width()) // 2 - camera_x
                plant_y = self.y + (self.height - plant_image.get_height()) // 2
                screen.blit(plant_image, (plant_x, plant_y))
            except KeyError as e:
                print(f"Ошибка: изображение для {self.plant_type} не найдено - {e}")

    def plant_seed(self, seed):
        if not self.is_planted:
            self.is_planted = True
            self.plant_type = seed["name"]
            self.is_watered = False
            self.is_sprouted = False
            self.last_watered_time = 0
            self.ripening_start_time = None
            self.is_ripe = False
            self.total_ripening_time = 0
            self.first_watering_time = None
            self.watering_start_time = None

    def water(self):
        if not self.is_watered and self.is_planted and self.watering_start_time is None:
            self.watering_start_time = pygame.time.get_ticks()

    def update(self):
        current_time = pygame.time.get_ticks()
        if self.is_planted and self.plant_type:
            seed = next((s for s in SEEDS if s["name"] == self.plant_type), None)
            if seed:
                watering_interval = seed["watering_interval_minutes"] * 60000
                sprout_time = seed["sprout_time_minutes"] * 60000
                ripening_time = seed["ripening_time_minutes"] * 60000
            else:
                watering_interval = 300000
                sprout_time = 15000
                ripening_time = 300000

            if self.watering_start_time is not None:
                if current_time - self.watering_start_time >= self.watering_duration:
                    self.is_watered = True
                    self.last_watered_time = current_time
                    self.watering_start_time = None
                    if self.first_watering_time is None:
                        self.first_watering_time = current_time
                    if self.ripening_start_time is None:
                        self.ripening_start_time = current_time

            if not self.is_sprouted and self.first_watering_time is not None:
                time_since_first_water = current_time - self.first_watering_time
                if time_since_first_water >= sprout_time:
                    self.is_sprouted = True

            if current_time - self.last_watered_time > watering_interval:
                self.is_watered = False
                if self.ripening_start_time is not None:
                    elapsed_time = current_time - self.ripening_start_time
                    self.total_ripening_time += elapsed_time
                    self.ripening_start_time = None

            if self.is_watered and self.ripening_start_time is not None:
                total_time = self.total_ripening_time + (current_time - self.ripening_start_time)
                if total_time >= ripening_time and not self.is_ripe:
                    self.is_ripe = True

    def harvest(self):
        self.is_planted = False
        self.plant_type = None
        self.is_watered = False
        self.is_sprouted = False
        self.last_watered_time = 0
        self.ripening_start_time = None
        self.is_ripe = False
        self.total_ripening_time = 0
        self.first_watering_time = None
        self.watering_start_time = None

    def to_dict(self):
        base_dict = super().to_dict()
        base_dict.update({
            "is_planted": self.is_planted,
            "plant_type": self.plant_type,
            "is_watered": self.is_watered,
            "is_sprouted": self.is_sprouted,
            "last_watered_time": self.last_watered_time,
            "ripening_start_time": self.ripening_start_time,
            "is_ripe": self.is_ripe,
            "total_ripening_time": self.total_ripening_time,
            "first_watering_time": self.first_watering_time,
            "watering_start_time": self.watering_start_time
        })
        return base_dict

class Mill(MapObject):
    def __init__(self, x, y, width=64, height=64):
        super().__init__(x, y, width, height, (160, 82, 45), "mill")
        self.movable = True  # Мельницу можно перемещать
        self.is_processing = False
        self.process_start_time = 0
        self.process_duration = BUILDING_CONFIG["mill"]["work_time"]
        self.harvest_stored = 0
        try:
            self.image = images.GAME_IMAGES["mill"]
        except KeyError:
            print("Ошибка: изображение мельницы не найдено")
            self.image = pygame.Surface((self.width, self.height))
            self.image.fill((160, 82, 45))

    def reload_images(self):
        """Перезагружает изображение мельницы."""
        try:
            self.image = images.GAME_IMAGES["mill"]
        except KeyError:
            print("Ошибка: изображение мельницы не найдено")
            self.image = pygame.Surface((self.width, self.height))
            self.image.fill((160, 82, 45))

    def start_processing(self, harvest):
        if not self.is_processing and harvest >= BUILDING_CONFIG["mill"]["consume"].get("harvest", 0):
            self.is_processing = True
            self.process_start_time = pygame.time.get_ticks()
            self.harvest_stored = BUILDING_CONFIG["mill"]["consume"].get("harvest", 0)
            return BUILDING_CONFIG["mill"]["consume"].get("harvest", 0)
        return 0

    def update(self):
        if self.is_processing:
            current_time = pygame.time.get_ticks()
            if current_time - self.process_start_time >= self.process_duration:
                self.is_processing = False
                self.harvest_stored = 0
                return BUILDING_CONFIG["mill"]["produce"].get("products", 0)
        return 0

    def draw(self, screen, camera_x):
        screen.blit(self.image, (self.x - camera_x, self.y))
        if self.is_processing:
            progress = (pygame.time.get_ticks() - self.process_start_time) / self.process_duration
            bar_width = int(self.width * progress)
            pygame.draw.rect(screen, GREEN, (self.x - camera_x, self.y - 10, bar_width, 5))

    def to_dict(self):
        return {
            "x": self.x, "y": self.y, "width": self.width, "height": self.height,
            "color": self.color, "obj_type": "mill", "movable": self.movable,
            "is_processing": self.is_processing,
            "process_start_time": self.process_start_time,
            "harvest_stored": self.harvest_stored
        }

class CanningCellar(MapObject):
    def __init__(self, x, y, width=64, height=64):
        super().__init__(x, y, width, height, (128, 0, 128), "canning_cellar")
        self.movable = True  # Погреб можно перемещать
        self.is_processing = False
        self.process_start_time = 0
        self.process_duration = BUILDING_CONFIG["canning_cellar"]["work_time"]
        self.harvest_stored = 0
        self.products_stored = 0
        try:
            self.image = images.GAME_IMAGES.get("canning_cellar", images.GAME_IMAGES["mill"])
        except KeyError:
            print("Ошибка: изображение Canning Cellar не найдено")
            self.image = pygame.Surface((self.width, self.height))
            self.image.fill((128, 0, 128))

    def reload_images(self):
        """Перезагружает изображение погреба."""
        try:
            self.image = images.GAME_IMAGES.get("canning_cellar", images.GAME_IMAGES["mill"])
        except KeyError:
            print("Ошибка: изображение Canning Cellar не найдено")
            self.image = pygame.Surface((self.width, self.height))
            self.image.fill((128, 0, 128))

    def start_processing(self, harvest, products):
        if not self.is_processing and harvest >= BUILDING_CONFIG["canning_cellar"]["consume"].get("harvest", 0) and products >= 0:
            self.is_processing = True
            self.process_start_time = pygame.time.get_ticks()
            self.harvest_stored = BUILDING_CONFIG["canning_cellar"]["consume"].get("harvest", 0)
            self.products_stored = 0
            return BUILDING_CONFIG["canning_cellar"]["consume"].get("harvest", 0)
        return 0

    def update(self):
        if self.is_processing:
            current_time = pygame.time.get_ticks()
            if current_time - self.process_start_time >= self.process_duration:
                self.is_processing = False
                self.harvest_stored = 0
                self.products_stored = 0
                return BUILDING_CONFIG["canning_cellar"]["produce"].get("products", 0)
        return 0

    def draw(self, screen, camera_x):
        screen.blit(self.image, (self.x - camera_x, self.y))
        if self.is_processing:
            progress = (pygame.time.get_ticks() - self.process_start_time) / self.process_duration
            bar_width = int(self.width * progress)
            pygame.draw.rect(screen, GREEN, (self.x - camera_x, self.y - 10, bar_width, 5))

    def to_dict(self):
        return {
            "x": self.x, "y": self.y, "width": self.width, "height": self.height,
            "color": self.color, "obj_type": "canning_cellar", "movable": self.movable,
            "is_processing": self.is_processing,
            "process_start_time": self.process_start_time,
            "harvest_stored": self.harvest_stored,
            "products_stored": self.products_stored
        }

# Класс Player
class Player:
    def __init__(self, x, y, width, height, speed, language="en"):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.speed = speed
        self.state = "idle"
        self.action_start_time = 0
        self.target_x = x
        self.target_y = y
        self.language = language
        try:
            self.images = {
                "idle": pygame.transform.scale(images.GAME_IMAGES["player_idle"], (width, height)),
                "walking": pygame.transform.scale(images.GAME_IMAGES["player_walking"], (width, height)),
                "watering": pygame.transform.scale(images.GAME_IMAGES["player_watering"], (width, height)),
                "harvesting": pygame.transform.scale(images.GAME_IMAGES["player_harvesting"], (width, height)),
                "processing": pygame.transform.scale(images.GAME_IMAGES["player_processing"], (width, height))
            }
        except KeyError as e:
            self.images = {
                "idle": pygame.Surface((width, height), pygame.SRCALPHA),
                "walking": pygame.Surface((width, height), pygame.SRCALPHA),
                "watering": pygame.Surface((width, height), pygame.SRCALPHA),
                "harvesting": pygame.Surface((width, height), pygame.SRCALPHA),
                "processing": pygame.Surface((width, height), pygame.SRCALPHA)
            }
            for state in self.images:
                self.images[state].fill((255, 0, 0, 128))

    def reload_images(self):
        """Перезагружает изображения игрока."""
        try:
            self.images = {
                "idle": pygame.transform.scale(images.GAME_IMAGES["player_idle"], (self.width, self.height)),
                "walking": pygame.transform.scale(images.GAME_IMAGES["player_walking"], (self.width, self.height)),
                "watering": pygame.transform.scale(images.GAME_IMAGES["player_watering"], (self.width, self.height)),
                "harvesting": pygame.transform.scale(images.GAME_IMAGES["player_harvesting"], (self.width, self.height)),
                "processing": pygame.transform.scale(images.GAME_IMAGES["player_processing"], (self.width, self.height))
            }
        except KeyError as e:
            self.images = {
                "idle": pygame.Surface((self.width, self.height), pygame.SRCALPHA),
                "walking": pygame.Surface((self.width, self.height), pygame.SRCALPHA),
                "watering": pygame.Surface((self.width, self.height), pygame.SRCALPHA),
                "harvesting": pygame.Surface((self.width, self.height), pygame.SRCALPHA),
                "processing": pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            }
            for state in self.images:
                self.images[state].fill((255, 0, 0, 128))

    def start_action(self, action):
        self.state = action
        self.action_start_time = pygame.time.get_ticks()

    def move(self):
        if self.state == "walking":
            dx = self.target_x - self.x
            dy = self.target_y - self.y
            distance = math.hypot(dx, dy)
            if distance > 0:
                if distance < self.speed:
                    self.x = self.target_x
                    self.y = self.target_y
                    self.state = "idle"
                else:
                    direction_x = dx / distance if dx != 0 else 0
                    direction_y = dy / distance if dy != 0 else 0
                    self.x += direction_x * self.speed
                    self.y += direction_y * self.speed
            else:
                self.state = "idle"
        elif self.state in ["idle", "watering", "harvesting", "processing"]:
            pass

    def draw(self, screen, camera_x):
        screen_x = self.x - camera_x
        if 0 <= screen_x <= screen.get_width() and 0 <= self.y <= screen.get_height():
            try:
                image = self.images[self.state]
                screen.blit(image, (screen_x, self.y))
            except KeyError as e:
                default_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
                default_surface.fill((255, 0, 0, 128))
                screen.blit(default_surface, (screen_x, self.y))

    def __str__(self):
        return f"Player(x={self.x}, y={self.y}, state={self.state})"

    def to_dict(self):
        """Возвращает словарь с данными игрока для сохранения."""
        return {
            "x": self.x, "y": self.y, "width": self.width, "height": self.height,
            "speed": self.speed, "state": self.state, "action_start_time": self.action_start_time,
            "target_x": self.target_x, "target_y": self.target_y, "language": self.language
        }