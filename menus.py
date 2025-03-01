import pygame
import math
from translations import get_text
from config import SCREEN_HEIGHT, SEEDS, BLACK, WHITE, GRAY, GREEN, BUILDING_CONFIG
import images
from entities import Bed, MapObject, Mill, CanningCellar, MarketStall

class WheelMenu:
    def __init__(self, language):
        self.is_open = False
        self.center_x = 0
        self.center_y = 0
        self.radius = 50
        self.language = language  # Убедимся, что language передаётся
        self.font = pygame.font.Font(None, 24)

    def open(self, x, y):
        self.is_open = True
        self.center_x = x
        self.center_y = y
        print(f"WheelMenu open at ({x}, {y}) with language: {self.language}")

    def close(self):
        self.is_open = False
        print("WheelMenu closed")

    def handle_input(self, event, camera_x):
        if not self.is_open:
            return None
        print(f"WheelMenu handling event: {event}, language: {self.language}")
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = pygame.mouse.get_pos()
            click_world_x = mx + camera_x
            click_world_y = my
            angle = math.atan2(click_world_y - self.center_y, click_world_x - self.center_x)
            angle = (angle / math.pi * 180 + 360) % 360
            if 270 <= angle < 360 or 0 <= angle < 90:
                self.close()
                return "build"
            elif 90 <= angle < 270:
                self.close()
                return "plant"
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
            mx, my = pygame.mouse.get_pos()
            screen_x = self.center_x - camera_x
            screen_y = self.center_y
            wheel_rect = pygame.Rect(screen_x - self.radius, screen_y - self.radius, 2 * self.radius, 2 * self.radius)
            print(f"WheelMenu right click at ({mx}, {my}), wheel_rect: {wheel_rect}, collide: {wheel_rect.collidepoint(mx, my)}, language: {self.language}")
            if not wheel_rect.collidepoint(mx, my):
                self.close()
                return None
        return None

    def draw(self, screen, camera_x):
        if not self.is_open:
            return
        screen_x = self.center_x - camera_x
        screen_y = self.center_y
        pygame.draw.circle(screen, (211, 211, 211), (int(screen_x), int(screen_y)), self.radius, 2)
        build_angle = 90
        plant_angle = 270
        build_endpoint = (screen_x + self.radius * math.cos(math.radians(build_angle)),
                          screen_y - self.radius * math.sin(math.radians(build_angle)))
        plant_endpoint = (screen_x + self.radius * math.cos(math.radians(plant_angle)),
                          screen_y - self.radius * math.sin(math.radians(plant_angle)))
        build_text = self.font.render(get_text("Construction", self.language), True, (0, 0, 255))
        plant_text = self.font.render(get_text("Planting", self.language), True, (0, 255, 0))
        screen.blit(build_text, (build_endpoint[0] + 5, build_endpoint[1] - 10))
        screen.blit(plant_text, (plant_endpoint[0] - plant_text.get_width() - 5, plant_endpoint[1] - 10))

class SeedMenu:
    def __init__(self, language, coins, level):
        self.is_open = False
        self.language = language
        self.coins = coins
        self.level = level
        self.selected_seed = None
        self.planting = False
        self.font = pygame.font.Font(None, 48)
        self.tooltip_font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 24)

    def open(self):
        self.is_open = True
        self.planting = False
        self.selected_seed = None
        print("SeedMenu open")

    def close(self):
        self.is_open = False
        self.planting = False
        self.selected_seed = None
        print("SeedMenu closed")

    def update(self, coins, level):
        self.coins = coins
        self.level = level

    def handle_input(self, event, screen_width, objects, camera_x):
        if not self.is_open:
            return None
        print(f"SeedMenu handling event: {event}, language: {self.language}")
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = pygame.mouse.get_pos()
            close_rect = pygame.Rect(screen_width - 30, 10, 20, 20)
            if close_rect.collidepoint(mx, my):
                self.close()
                return "close_seed_menu"
            available_seeds = [seed for seed in SEEDS if seed["unlock_level"] <= self.level]
            for i, seed in enumerate(available_seeds):
                row, col = i // 2, i % 2
                rect = pygame.Rect(screen_width - 190 + col * 90, 60 + row * 60, 80, 50)
                if rect.collidepoint(mx, my) and self.coins >= seed["cost"]:
                    self.selected_seed = {**seed, "language": self.language}
                    self.planting = True
                    print(f"Selected seed: {self.selected_seed['name']}, planting: {self.planting}")
                    return "seed_selected"
            if self.planting and self.selected_seed:
                print(f"Attempting to plant at screen position ({mx}, {my})")
                for obj in objects:
                    if obj.obj_type == "bed":
                        bed_rect = pygame.Rect(obj.x, obj.y, obj.width, obj.height)
                        print(f"Bed rect: {bed_rect}, is_planted: {obj.is_planted}")
                        world_x = mx + camera_x
                        world_y = my
                        if bed_rect.collidepoint(world_x, world_y) and not obj.is_planted and self.coins >= self.selected_seed["cost"]:
                            print(f"Planting {self.selected_seed['name']} at bed at ({obj.x}, {obj.y})")
                            obj.plant_seed(self.selected_seed)
                            return {"action": "plant", "cost": self.selected_seed["cost"]}
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
            mx, my = pygame.mouse.get_pos()
            menu_rect = pygame.Rect(screen_width - 200, 0, 200, SCREEN_HEIGHT)
            print(f"SeedMenu right click at ({mx}, {my}), menu_rect: {menu_rect}, collide: {menu_rect.collidepoint(mx, my)}, language: {self.language}")
            if not menu_rect.collidepoint(mx, my):
                self.close()
                return None
        return None

    def draw(self, screen):
        if not self.is_open:
            return
        screen_width = screen.get_width()
        menu_width, menu_height = 200, SCREEN_HEIGHT
        pygame.draw.rect(screen, (211, 211, 211), (screen_width - menu_width, 0, menu_width, menu_height))
        pygame.draw.rect(screen, GRAY, (screen_width - menu_width, 0, menu_width, menu_height), 2)
        close_rect = pygame.Rect(screen_width - 30, 10, 20, 20)
        pygame.draw.rect(screen, (173, 216, 230), close_rect)
        close_text = self.small_font.render("×", True, BLACK)
        screen.blit(close_text, close_text.get_rect(center=close_rect.center))

        seeds_per_row = 2
        seed_width = 90
        seed_height = 60
        start_x = screen_width - 190
        start_y = 60

        available_seeds = [seed for seed in SEEDS if seed["unlock_level"] <= self.level]

        tooltip = None
        for i, seed in enumerate(available_seeds):
            row = i // seeds_per_row
            col = i % seeds_per_row
            rect_x = start_x + col * seed_width
            rect_y = start_y + row * seed_height
            rect = pygame.Rect(rect_x, rect_y, 80, 50)
            color = (173, 216, 230) if self.coins >= seed["cost"] else GRAY
            is_hovered = rect.collidepoint(pygame.mouse.get_pos())
            is_active = self.selected_seed and seed["name"] == self.selected_seed["name"]
            menu_color = color
            if is_active:
                menu_color = GREEN
            elif is_hovered:
                menu_color = WHITE
                tooltip_lines = [
                    f"{get_text('Name', self.language)}: {get_text(seed['name'], self.language)}",
                    f"{get_text('Cost', self.language)}: {seed['cost']}",
                    f"{get_text('Growth Time', self.language)}: {seed['ripening_time_minutes']} {get_text('min', self.language)}",
                    f"{get_text('Watering Interval', self.language)}: {seed['watering_interval_minutes']} {get_text('min', self.language)}",
                    f"{get_text('Harvest Yield', self.language)}: {seed['harvest_yield']}"
                ]
                tooltip = "\n".join(tooltip_lines)

            pygame.draw.rect(screen, menu_color, rect)
            text = self.font.render(get_text(seed["name"], self.language)[0], True, BLACK)
            text_rect = text.get_rect(center=(rect_x + 40, rect_y + 25))
            screen.blit(text, text_rect)

        if tooltip:
            tooltip_lines = tooltip.split('\n')
            tooltip_height = len(tooltip_lines) * 20 + 10
            tooltip_width = 0
            for line in tooltip_lines:
                if line.startswith(get_text('Cost', self.language)):
                    parts = line.split(': ', 1)
                    if len(parts) == 2:
                        number = parts[1]
                        text_part = f"{parts[0]}: "
                        line_width = self.tooltip_font.size(text_part)[0] + self.tooltip_font.size(number)[0] + \
                                     images.GAME_IMAGES["coin_menu"].get_width() + 5
                    else:
                        line_width = self.tooltip_font.size(line)[0] + images.GAME_IMAGES["coin_menu"].get_width() + 5
                elif line.startswith(get_text('Harvest Yield', self.language)):
                    parts = line.split(': ', 1)
                    if len(parts) == 2:
                        number = parts[1]
                        text_part = f"{parts[0]}: "
                        line_width = self.tooltip_font.size(text_part)[0] + self.tooltip_font.size(number)[0] + \
                                     images.GAME_IMAGES["harvest"].get_width() + 5
                    else:
                        line_width = self.tooltip_font.size(line)[0] + images.GAME_IMAGES["harvest"].get_width() + 5
                else:
                    line_width = self.tooltip_font.size(line)[0]
                tooltip_width = max(tooltip_width, line_width + 10)

            tooltip_rect = pygame.Rect(pygame.mouse.get_pos()[0] + 10, pygame.mouse.get_pos()[1], tooltip_width,
                                       tooltip_height)
            if tooltip_rect.right > screen_width:
                tooltip_rect.left = pygame.mouse.get_pos()[0] - tooltip_width - 10
            if tooltip_rect.bottom > SCREEN_HEIGHT:
                tooltip_rect.top = pygame.mouse.get_pos()[1] - tooltip_height - 10

            pygame.draw.rect(screen, BLACK, tooltip_rect, border_radius=5)
            pygame.draw.rect(screen, WHITE, tooltip_rect, 2, border_radius=5)
            for i, line in enumerate(tooltip_lines):
                if line.startswith(get_text('Cost', self.language)):
                    parts = line.split(': ', 1)
                    if len(parts) == 2:
                        text_part, number = parts
                        text_surface = self.tooltip_font.render(f"{text_part}: ", True, WHITE)
                        number_surface = self.tooltip_font.render(number, True, WHITE)
                        coin_image = pygame.transform.scale(images.GAME_IMAGES["coin_menu"],
                                                            (16, 16))  # Убедились в размере
                        text_height = text_surface.get_height()
                        coin_height = coin_image.get_height()
                        y_offset = (text_height - coin_height) // 2
                        screen.blit(text_surface, (tooltip_rect.x + 5, tooltip_rect.y + 5 + i * 20))
                        screen.blit(number_surface, (
                        tooltip_rect.x + 5 + self.tooltip_font.size(f"{text_part}: ")[0], tooltip_rect.y + 5 + i * 20))
                        screen.blit(coin_image, (
                        tooltip_rect.x + 5 + self.tooltip_font.size(f"{text_part}: {number}")[0] + 5,
                        tooltip_rect.y + 5 + i * 20 + y_offset))
                elif line.startswith(get_text('Harvest Yield', self.language)):
                    parts = line.split(': ', 1)
                    if len(parts) == 2:
                        text_part, number = parts
                        text_surface = self.tooltip_font.render(f"{text_part}: ", True, WHITE)
                        number_surface = self.tooltip_font.render(number, True, WHITE)
                        harvest_image = pygame.transform.scale(images.GAME_IMAGES["harvest"],
                                                               (16, 16))  # Убедились в размере
                        text_height = text_surface.get_height()
                        harvest_height = harvest_image.get_height()
                        y_offset = (text_height - harvest_height) // 2
                        screen.blit(text_surface, (tooltip_rect.x + 5, tooltip_rect.y + 5 + i * 20))
                        screen.blit(number_surface, (
                        tooltip_rect.x + 5 + self.tooltip_font.size(f"{text_part}: ")[0], tooltip_rect.y + 5 + i * 20))
                        screen.blit(harvest_image, (
                        tooltip_rect.x + 5 + self.tooltip_font.size(f"{text_part}: {number}")[0] + 5,
                        tooltip_rect.y + 5 + i * 20 + y_offset))
                else:
                    text_surface = self.tooltip_font.render(line, True, WHITE)
                    screen.blit(text_surface, (tooltip_rect.x + 5, tooltip_rect.y + 5 + i * 20))


class BuildMenu:
    def __init__(self, language, coins, level=1):
        self.is_open = False
        self.language = language
        self.coins = coins
        self.level = level
        self.build_action = None
        self.preview_build = None
        self.moving_object = None
        self.current_index = 0  # Индекс текущего выбранного объекта в меню строительства
        self.font = pygame.font.Font(None, 48)
        self.tooltip_font = pygame.font.Font(None, 20)
        self.small_font = pygame.font.Font(None, 24)
        # Список доступных построек из конфига
        self.build_options = [
            {
                "text": get_text("Bed", language),
                "cost_coins": BUILDING_CONFIG["bed"]["cost_coins"],
                "unlock_level": BUILDING_CONFIG["bed"]["unlock_level"],
                "action": "new",
                "type": "functional",
                "description": get_text("Simple bed for planting plants", language),
                "cost_text": f"{get_text('Cost', language)}: {BUILDING_CONFIG['bed']['cost_coins']} {get_text('coins', language)}",
                "consume": BUILDING_CONFIG["bed"]["consume"],
                "produce": BUILDING_CONFIG["bed"]["produce"],
                "work_time": BUILDING_CONFIG["bed"]["work_time"]
            },
            {
                "text": get_text("Mill", language),
                "cost_coins": BUILDING_CONFIG["mill"]["cost_coins"],
                "cost_harvest": BUILDING_CONFIG["mill"]["cost_harvest"],
                "unlock_level": BUILDING_CONFIG["mill"]["unlock_level"],
                "action": "new",
                "type": "functional",
                "description": get_text("Converts 2 Harvest into 1 Product in 5 seconds", language),
                "cost_text": f"{get_text('Cost', language)}: {BUILDING_CONFIG['mill']['cost_coins']} {get_text('coins', language)} + {BUILDING_CONFIG['mill']['cost_harvest']} {get_text('Harvest', language)}",
                "consume": BUILDING_CONFIG["mill"]["consume"],
                "produce": BUILDING_CONFIG["mill"]["produce"],
                "work_time": BUILDING_CONFIG["mill"]["work_time"]
            },
            {
                "text": get_text("Canning Cellar", language),
                "cost_coins": BUILDING_CONFIG["canning_cellar"]["cost_coins"],
                "cost_harvest": BUILDING_CONFIG["canning_cellar"]["cost_harvest"],
                "cost_products": BUILDING_CONFIG["canning_cellar"]["cost_products"],
                "unlock_level": BUILDING_CONFIG["canning_cellar"]["unlock_level"],
                "action": "new",
                "type": "functional",
                "description": get_text("Converts 4 Harvest into 2 Products in 6 minutes", language),
                "cost_text": f"{get_text('Cost', language)}: {BUILDING_CONFIG['canning_cellar']['cost_coins']} {get_text('coins', language)} + {BUILDING_CONFIG['canning_cellar']['cost_harvest']} {get_text('Harvest', language)} + {BUILDING_CONFIG['canning_cellar']['cost_products']} {get_text('Products', language)}",
                "consume": BUILDING_CONFIG["canning_cellar"]["consume"],
                "produce": BUILDING_CONFIG["canning_cellar"]["produce"],
                "work_time": BUILDING_CONFIG["canning_cellar"]["work_time"]
            }
        ]

    def open(self):
        self.is_open = True
        self.build_action = None
        self.preview_build = None
        self.moving_object = None
        self.current_index = 0
        print("BuildMenu open")

    def close(self):
        self.is_open = False
        self.build_action = None
        self.preview_build = None
        self.moving_object = None
        print("BuildMenu closed")

    def update(self, coins, level):
        self.coins = coins
        self.level = level
        # Проверяем, чтобы current_index не выходил за пределы доступных опций
        available_options = [i for i, option in enumerate(self.build_options) if self.level >= option["unlock_level"]]
        if not available_options or self.current_index >= len(available_options):
            self.current_index = 0
        print(f"Updated current_index to: {self.current_index}")

    def handle_input(self, event, screen_width, map_width, objects, camera_x, harvest, products):
        from game_utils import snap_to_grid, check_collision
        if not self.is_open:
            return None
        print(f"BuildMenu handling event: {event}, language: {self.language}")
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = pygame.mouse.get_pos()
            build_rects = self.draw(pygame.display.get_surface(), return_rects=True)
            print(f"Mouse click at ({mx}, {my}), Rects: {build_rects.keys()}")

            # Закрытие меню
            if build_rects["close"].collidepoint(mx, my):
                self.close()
                print("Closing BuildMenu")
                return "close_build_menu"

            # Переключение между вариантами строительства (стрелки)
            elif build_rects["left_arrow"].collidepoint(mx, my):
                available_options = [i for i, option in enumerate(self.build_options) if
                                     self.level >= option["unlock_level"]]
                if available_options:
                    self.current_index = (self.current_index - 1) % len(available_options)
                    print(
                        f"Switched to previous option: {self.build_options[available_options[self.current_index]]['text']}")
            elif build_rects["right_arrow"].collidepoint(mx, my):
                available_options = [i for i, option in enumerate(self.build_options) if
                                     self.level >= option["unlock_level"]]
                if available_options:
                    self.current_index = (self.current_index + 1) % len(available_options)
                    print(
                        f"Switched to next option: {self.build_options[available_options[self.current_index]]['text']}")

            # Включение режима перемещения
            elif build_rects["move"].collidepoint(mx, my):
                self.build_action = "move"
                print("Set build_action to move")
                return "set_move"

            # Включение режима уничтожения
            elif build_rects["destroy"].collidepoint(mx, my):
                self.build_action = "destroy"
                print("Set build_action to destroy")
                return "set_destroy"

            # Начало строительства нового объекта
            elif build_rects["new"].collidepoint(mx, my):
                available_options = [option for option in self.build_options if self.level >= option["unlock_level"]]
                option = available_options[self.current_index]
                total_cost_coins = option["cost_coins"]
                cost_harvest = option.get("cost_harvest", 0)
                cost_products = option.get("cost_products", 0)
                if (self.coins >= total_cost_coins and
                        ("cost_harvest" not in option or harvest >= cost_harvest) and
                        ("cost_products" not in option or products >= cost_products)):
                    if option["text"] == get_text("Bed", self.language):
                        self.preview_build = Bed(0, 0)
                    elif option["text"] == get_text("Mill", self.language):
                        self.preview_build = Mill(0, 0)
                    elif option["text"] == get_text("Canning Cellar", self.language):
                        self.preview_build = CanningCellar(0, 0)
                    self.build_action = "build_preview"
                    print(f"Starting build preview for {option['text']}")
                    return "start_build_preview"

            # Завершение строительства нового объекта
            elif self.build_action == "build_preview" and self.preview_build:
                new_x = snap_to_grid(mx + camera_x, grid_size=32) - self.preview_build.width // 2
                new_y = snap_to_grid(my, grid_size=32) - self.preview_build.height // 2
                new_x = max(0, min(new_x, map_width - self.preview_build.width))
                new_y = max(0, min(new_y, SCREEN_HEIGHT - self.preview_build.height))
                self.preview_build.x = new_x
                self.preview_build.y = new_y
                if not check_collision(self.preview_build, objects, grid_size=32, allow_touching=True):
                    objects.append(self.preview_build)
                    available_options = [option for option in self.build_options if
                                         self.level >= option["unlock_level"]]
                    option = available_options[self.current_index]
                    cost = option["cost_coins"]
                    harvest_cost = option.get("cost_harvest", 0)
                    products_cost = option.get("cost_products", 0)
                    self.preview_build = None
                    self.build_action = None
                    print(f"Built {option['text']} at ({new_x}, {new_y})")
                    return {"action": "build", "cost_coins": cost, "cost_harvest": harvest_cost,
                            "cost_products": products_cost}

            # Выбор объекта для перемещения
            elif self.build_action == "move" and self.moving_object is None:
                ui_area = pygame.Rect(0, 0, 50, 50)  # Область интерфейса, чтобы не мешать выбору
                print(f"Checking UI area collision at ({mx}, {my}) with rect {ui_area}")
                if not ui_area.collidepoint(mx, my):
                    for obj in objects:
                        obj_rect = pygame.Rect(obj.x - camera_x, obj.y, obj.width, obj.height)
                        print(f"Checking object {obj.obj_type} at ({obj.x}, {obj.y}) with rect {obj_rect}, "
                              f"collides: {obj_rect.collidepoint(mx, my)}, camera_x: {camera_x}, "
                              f"screen_pos: ({obj.x - camera_x}, {obj.y})")
                        if obj_rect.collidepoint(mx, my) and obj.movable:
                            self.moving_object = obj
                            if obj.obj_type == "bed":
                                self.preview_build = Bed(obj.x, obj.y, obj.width, obj.height)
                            elif obj.obj_type == "mill":
                                self.preview_build = Mill(obj.x, obj.y, obj.width, obj.height)
                            elif obj.obj_type == "canning_cellar":
                                self.preview_build = CanningCellar(obj.x, obj.y, obj.width, obj.height)
                            elif obj.obj_type == "market_stall":
                                self.preview_build = MarketStall(obj.x, obj.y, obj.width, obj.height)
                            else:
                                self.preview_build = MapObject(obj.x, obj.y, obj.width, obj.height, obj.color,
                                                               obj.obj_type)
                            self.build_action = "move_preview"
                            print(f"Selected object for move: {obj.obj_type} at ({obj.x}, {obj.y})")
                            return "start_move_preview"

            # Завершение перемещения объекта
            elif self.build_action == "move_preview" and self.moving_object and self.preview_build:
                print(f"Moving object, current position: ({self.moving_object.x}, {self.moving_object.y})")
                new_x = snap_to_grid(mx + camera_x, grid_size=32) - self.preview_build.width // 2
                new_y = snap_to_grid(my, grid_size=32) - self.preview_build.height // 2
                new_x = max(0, min(new_x, map_width - self.preview_build.width))
                new_y = max(0, min(new_y, SCREEN_HEIGHT - self.preview_build.height))
                self.preview_build.x = new_x
                self.preview_build.y = new_y
                temp_objects = [obj for obj in objects if obj != self.moving_object]
                if not check_collision(self.preview_build, temp_objects, grid_size=32, allow_touching=True):
                    self.moving_object.x = new_x
                    self.moving_object.y = new_y
                    moved_obj = self.moving_object  # Сохраняем перемещённый объект
                    self.moving_object = None
                    self.preview_build = None
                    self.build_action = "move"  # Оставляем режим перемещения для следующего объекта
                    print(f"Successfully moved {moved_obj.obj_type} to ({new_x}, {new_y})")
                    return {"action": "move_complete", "moved_obj": moved_obj}

            # Уничтожение объекта
            elif self.build_action == "destroy":
                for i, obj in enumerate(objects):
                    obj_rect = pygame.Rect(obj.x - camera_x, obj.y, obj.width, obj.height)
                    print(f"Checking object {obj.obj_type} at ({obj.x}, {obj.y}) with rect {obj_rect} for destroy")
                    if obj_rect.collidepoint(mx, my) and obj.obj_type in ["bed", "mill",
                                                                          "canning_cellar"] and obj.obj_type not in [
                        "house"]:
                        print(f"Destroying object {obj.obj_type} at ({obj.x}, {obj.y})")
                        destroyed_obj = objects.pop(i)  # Сохраняем удалённый объект
                        self.build_action = "destroy"  # Оставляем режим уничтожения для следующего объекта
                        print("Destroy action completed, menu remains open")
                        return {"action": "destroy_complete", "destroyed_obj": destroyed_obj}

        # Закрытие меню правым кликом вне области
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
            mx, my = pygame.mouse.get_pos()
            menu_rect = pygame.Rect(screen_width - 240, 0, 240, SCREEN_HEIGHT)
            print(
                f"BuildMenu right click at ({mx}, {my}), menu_rect: {menu_rect}, collide: {menu_rect.collidepoint(mx, my)}, language: {self.language}")
            if not menu_rect.collidepoint(mx, my):
                self.close()
                print("Closing BuildMenu by right click outside")
                return None
        return None

    def draw(self, screen, return_rects=False):
        if not self.is_open:
            return {} if return_rects else None
        screen_width = screen.get_width()
        menu_width, menu_height = 240, SCREEN_HEIGHT
        pygame.draw.rect(screen, (211, 211, 211), (screen_width - menu_width, 0, menu_width, menu_height))
        pygame.draw.rect(screen, GRAY, (screen_width - menu_width, 0, menu_width, menu_height), 2)

        # Кнопка закрытия
        close_rect = pygame.Rect(screen_width - 30, 10, 20, 20)
        pygame.draw.rect(screen, (173, 216, 230), close_rect)
        close_text = self.small_font.render("×", True, BLACK)
        screen.blit(close_text, close_text.get_rect(center=close_rect.center))

        # Кнопки "Переместить" и "Уничтожить"
        action_width = (menu_width - 30) // 2
        move_rect = pygame.Rect(screen_width - menu_width + 15, 60, action_width, 50)
        destroy_rect = pygame.Rect(screen_width - action_width - 15, 60, action_width, 50)
        move_color = GREEN if self.build_action in ["move", "move_preview"] else (
        173, 216, 230) if self.coins >= 0 else GRAY
        destroy_color = GREEN if self.build_action == "destroy" else (173, 216, 230) if self.coins >= 0 else GRAY
        pygame.draw.rect(screen, move_color, move_rect)
        pygame.draw.rect(screen, destroy_color, destroy_rect)
        move_text = self.small_font.render(get_text("Move", self.language), True, BLACK)
        destroy_text = self.small_font.render(get_text("Destroy", self.language), True, (255, 0, 0))
        screen.blit(move_text, move_text.get_rect(center=(move_rect.x + action_width // 2, move_rect.y + 25)))
        screen.blit(destroy_text,
                    destroy_text.get_rect(center=(destroy_rect.x + action_width // 2, destroy_rect.y + 25)))

        # Отрисовка текущей выбранной постройки
        available_options = [option for option in self.build_options if self.level >= option["unlock_level"]]
        if not available_options:
            return {} if return_rects else None
        current_option = available_options[self.current_index]

        build_rect = pygame.Rect(screen_width - menu_width + 15, 120, menu_width - 30, 200)
        total_cost_coins = current_option["cost_coins"]
        cost_harvest = current_option.get("cost_harvest", 0)
        cost_products = current_option.get("cost_products", 0)
        color = (173, 216, 230) if (self.coins >= total_cost_coins and
                                    ("cost_harvest" not in current_option or self.coins >= cost_harvest) and
                                    ("cost_products" not in current_option or self.coins >= cost_products)) else GRAY
        pygame.draw.rect(screen, color, build_rect)

        # Зона изображения объекта
        image_zone_width = 64
        image_zone_height = 64
        image_zone_x = build_rect.x + (build_rect.width - image_zone_width) // 2
        image_zone_y = build_rect.y + 20
        pygame.draw.rect(screen, (255, 255, 255), (image_zone_x, image_zone_y, image_zone_width, image_zone_height), 2)

        # Выбор изображения для выбранного объекта
        if current_option["text"] == get_text("Bed", self.language):
            build_image = images.GAME_IMAGES["bed_wet"]
        elif current_option["text"] == get_text("Mill", self.language):
            build_image = images.GAME_IMAGES["mill"]
        elif current_option["text"] == get_text("Canning Cellar", self.language):
            build_image = images.GAME_IMAGES.get("canning_cellar", images.GAME_IMAGES["mill"])
        elif current_option["text"] == get_text("Market Stall", self.language):
            build_image = images.GAME_IMAGES["market_stall"]
        else:
            build_image = pygame.Surface((image_zone_width, image_zone_height))
            build_image.fill((255, 255, 255))

        scale_factor = min(image_zone_width / build_image.get_width(), image_zone_height / build_image.get_height())
        scaled_image = pygame.transform.scale(build_image, (
            int(build_image.get_width() * scale_factor), int(build_image.get_height() * scale_factor)))
        screen.blit(scaled_image, (image_zone_x + (image_zone_width - scaled_image.get_width()) // 2,
                                   image_zone_y + (image_zone_height - scaled_image.get_height()) // 2))

        # Название объекта
        title_text = self.tooltip_font.render(current_option["text"], True, BLACK)
        screen.blit(title_text, (
            build_rect.x + (build_rect.width - title_text.get_width()) // 2, image_zone_y + image_zone_height + 20))

        # Загрузка иконок ресурсов
        try:
            coin_image = images.GAME_IMAGES["coin_menu"]
            harvest_image = pygame.transform.scale(images.GAME_IMAGES["harvest"], (16, 16))
            product_image = pygame.transform.scale(images.GAME_IMAGES["product"], (16, 16))
        except KeyError:
            print("Error: coin_menu, harvest, or product not found in GAME_IMAGES")
            coin_image = pygame.Surface((16, 16))
            coin_image.fill((255, 255, 255))
            harvest_image = pygame.Surface((16, 16))
            harvest_image.fill((255, 255, 255))
            product_image = pygame.Surface((16, 16))
            product_image.fill((255, 255, 255))

        # Отрисовка стоимости
        cost_coins_text = self.tooltip_font.render(str(current_option["cost_coins"]), True, BLACK) if current_option[
                                                                                                          "cost_coins"] > 0 else None
        cost_harvest_text = self.tooltip_font.render(str(current_option["cost_harvest"]), True,
                                                     BLACK) if "cost_harvest" in current_option and current_option[
            "cost_harvest"] > 0 else None
        cost_products_text = self.tooltip_font.render(str(current_option["cost_products"]), True,
                                                      BLACK) if "cost_products" in current_option and current_option[
            "cost_products"] > 0 else None

        total_width = 0
        items = []
        if cost_coins_text:
            total_width += coin_image.get_width() + (cost_coins_text.get_width() if cost_coins_text else 0) + 5
            items.append((coin_image, cost_coins_text))
        if cost_harvest_text:
            total_width += harvest_image.get_width() + (cost_harvest_text.get_width() if cost_harvest_text else 0) + 15
            items.append((harvest_image, cost_harvest_text))
        if cost_products_text:
            total_width += product_image.get_width() + (
                cost_products_text.get_width() if cost_products_text else 0) + 15
            items.append((product_image, cost_products_text))

        x_pos = build_rect.x + (build_rect.width - total_width) // 2
        y_pos = image_zone_y + image_zone_height + 40
        for icon, number_text in items:
            screen.blit(icon, (x_pos, y_pos))
            if number_text:
                screen.blit(number_text, (x_pos + icon.get_width() + 5, y_pos))
            x_pos += icon.get_width() + (number_text.get_width() if number_text else 0) + 15

        # Стрелки для переключения объектов
        left_arrow_rect = pygame.Rect(build_rect.x + 10, image_zone_y + (image_zone_height - 40) // 2, 40, 40)
        right_arrow_rect = pygame.Rect(build_rect.right - 50, image_zone_y + (image_zone_height - 40) // 2, 40, 40)
        pygame.draw.polygon(screen, WHITE, [
            (left_arrow_rect.x + 10, left_arrow_rect.centery),
            (left_arrow_rect.x + 30, left_arrow_rect.centery - 10),
            (left_arrow_rect.x + 30, left_arrow_rect.centery + 10)
        ])
        pygame.draw.polygon(screen, WHITE, [
            (right_arrow_rect.x + 30, right_arrow_rect.centery),
            (right_arrow_rect.x + 10, right_arrow_rect.centery - 10),
            (right_arrow_rect.x + 10, right_arrow_rect.centery + 10)
        ])

        if return_rects:
            return {"close": close_rect, "move": move_rect, "destroy": destroy_rect, "new": build_rect,
                    "left_arrow": left_arrow_rect, "right_arrow": right_arrow_rect}
class MarketMenu:
    def __init__(self, language, coins, harvest, products):
        self.is_open = False
        self.language = language
        self.coins = coins
        self.harvest = harvest
        self.products = products
        self.harvest_to_sell = 0
        self.products_to_sell = 0
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.error_message = None  # Добавляем переменную для сообщения об ошибке
        self.error_timer = 0  # Таймер для отображения сообщения
        # Фиксированные значения для продажи
        self.sale_values = [0, 1, 5, 10, 25, 50, 100]

    def open(self):
        self.is_open = True
        self.harvest_to_sell = 0
        self.products_to_sell = 0
        self.error_message = None  # Сбрасываем сообщение при открытии
        self.error_timer = 0
        print("MarketMenu open")

    def close(self):
        self.is_open = False
        self.error_message = None  # Сбрасываем сообщение при закрытии
        print("MarketMenu closed")

    def update(self, coins, harvest, products):
        self.coins = coins
        self.harvest = harvest
        self.products = products

    def handle_input(self, event, screen_width):
        if not self.is_open:
            return None
        print(f"MarketMenu handling event: {event}, language: {self.language}")
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = pygame.mouse.get_pos()
            rects = self.draw(pygame.display.get_surface(), return_rects=True)
            if rects["close"].collidepoint(mx, my):
                self.close()
                return "close_market_menu"
            elif rects["harvest_increase"].collidepoint(mx, my):
                # Переключаем на следующее значение из sale_values, не превышающее harvest
                current_index = self.sale_values.index(self.harvest_to_sell)
                next_index = (current_index + 1) % len(self.sale_values)
                while (next_index != current_index and self.sale_values[next_index] > self.harvest):
                    next_index = (next_index + 1) % len(self.sale_values)
                self.harvest_to_sell = self.sale_values[next_index]
                print(f"Harvest to sell increased to: {self.harvest_to_sell}")
            elif rects["harvest_decrease"].collidepoint(mx, my):
                # Переключаем на предыдущее значение из sale_values
                current_index = self.sale_values.index(self.harvest_to_sell)
                prev_index = (current_index - 1) % len(self.sale_values)
                self.harvest_to_sell = self.sale_values[prev_index]
                print(f"Harvest to sell decreased to: {self.harvest_to_sell}")
            elif rects["products_increase"].collidepoint(mx, my):
                # Переключаем на следующее значение из sale_values, не превышающее products
                current_index = self.sale_values.index(self.products_to_sell)
                next_index = (current_index + 1) % len(self.sale_values)
                while (next_index != current_index and self.sale_values[next_index] > self.products):
                    next_index = (next_index + 1) % len(self.sale_values)
                self.products_to_sell = self.sale_values[next_index]
                print(f"Products to sell increased to: {self.products_to_sell}")
            elif rects["products_decrease"].collidepoint(mx, my):
                # Переключаем на предыдущее значение из sale_values
                current_index = self.sale_values.index(self.products_to_sell)
                prev_index = (current_index - 1) % len(self.sale_values)
                self.products_to_sell = self.sale_values[prev_index]
                print(f"Products to sell decreased to: {self.products_to_sell}")
            elif rects["sell"].collidepoint(mx, my):
                # Проверяем, достаточно ли ресурсов для продажи
                if self.harvest_to_sell <= self.harvest and self.products_to_sell <= self.products:
                    harvest_value = self.harvest_to_sell * 2
                    products_value = self.products_to_sell * 15
                    total_value = harvest_value + products_value
                    print(f"Selling {self.harvest_to_sell} harvest and {self.products_to_sell} products for {total_value} coins")
                    return {"action": "sell", "value": total_value, "harvest_sold": self.harvest_to_sell, "products_sold": self.products_to_sell}
                else:
                    # Устанавливаем сообщение об ошибке и таймер
                    self.error_message = get_text("Недостаточно ресурсов!", self.language)
                    self.error_timer = pygame.time.get_ticks()  # Записываем время ошибки
                    print(self.error_message)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
            mx, my = pygame.mouse.get_pos()
            menu_rect = pygame.Rect((screen_width - 400) // 2, (SCREEN_HEIGHT - 250) // 2, 400, 250)
            print(f"MarketMenu right click at ({mx}, {my}), menu_rect: {menu_rect}, collide: {menu_rect.collidepoint(mx, my)}, language: {self.language}")
            if not menu_rect.collidepoint(mx, my):
                self.close()
                return None
        return None

    def draw(self, screen, return_rects=False):
        if not self.is_open:
            return {} if return_rects else None
        screen_width = screen.get_width()
        menu_width, menu_height = 400, 250
        menu_x = (screen_width - menu_width) // 2
        menu_y = (SCREEN_HEIGHT - menu_height) // 2
        pygame.draw.rect(screen, (211, 211, 211), (menu_x, menu_y, menu_width, menu_height))
        pygame.draw.rect(screen, GRAY, (menu_x, menu_y, menu_width, menu_height), 2)
        close_rect = pygame.Rect(menu_x + menu_width - 30, menu_y + 10, 20, 20)
        pygame.draw.rect(screen, (173, 216, 230), close_rect)
        close_text = self.small_font.render("×", True, BLACK)
        screen.blit(close_text, close_text.get_rect(center=close_rect.center))
        try:
            harvest_image = images.GAME_IMAGES["harvest"]
            product_image = images.GAME_IMAGES["product"]
            coin_image = images.GAME_IMAGES["coin_menu"]
        except KeyError:
            print("Error: harvest, product, or coin_menu not found in GAME_IMAGES")
            harvest_image = pygame.Surface((32, 32))
            harvest_image.fill((255, 255, 255))
            product_image = pygame.Surface((32, 32))
            product_image.fill((255, 255, 255))
            coin_image = pygame.Surface((16, 16))
            coin_image.fill((255, 255, 255))

        harvest_rect = pygame.Rect(menu_x + 150, menu_y + 70, 50, 40)
        pygame.draw.rect(screen, WHITE, harvest_rect)
        harvest_text = self.small_font.render(str(self.harvest_to_sell), True, BLACK)
        screen.blit(harvest_text, (harvest_rect.x + (harvest_rect.width - harvest_text.get_width()) // 2, harvest_rect.y + 10))
        screen.blit(harvest_image, (menu_x + 20, menu_y + 70))
        harvest_increase = pygame.Rect(menu_x + 205, menu_y + 70, 30, 20)
        harvest_decrease = pygame.Rect(menu_x + 205, menu_y + 90, 30, 20)
        pygame.draw.rect(screen, GREEN, harvest_increase)
        pygame.draw.rect(screen, GREEN, harvest_decrease)
        screen.blit(self.small_font.render("↑", True, BLACK), harvest_increase.move(10, 2))
        screen.blit(self.small_font.render("↓", True, BLACK), harvest_decrease.move(10, 2))
        products_rect = pygame.Rect(menu_x + 150, menu_y + 130, 50, 40)
        pygame.draw.rect(screen, WHITE, products_rect)
        products_text = self.small_font.render(str(self.products_to_sell), True, BLACK)
        screen.blit(products_text, (products_rect.x + (products_rect.width - products_text.get_width()) // 2, products_rect.y + 10))
        screen.blit(product_image, (menu_x + 20, menu_y + 130))
        products_increase = pygame.Rect(menu_x + 205, menu_y + 130, 30, 20)
        products_decrease = pygame.Rect(menu_x + 205, menu_y + 150, 30, 20)
        pygame.draw.rect(screen, GREEN, products_increase)
        pygame.draw.rect(screen, GREEN, products_decrease)
        screen.blit(self.small_font.render("↑", True, BLACK), products_increase.move(10, 2))
        screen.blit(self.small_font.render("↓", True, BLACK), products_decrease.move(10, 2))
        total_value = (self.harvest_to_sell * 2) + (self.products_to_sell * 15)
        screen.blit(coin_image, (menu_x + 150, menu_y + 200))
        value_text = self.small_font.render(str(total_value), True, BLACK)
        screen.blit(value_text, (menu_x + 190, menu_y + 202))
        sell_rect = pygame.Rect(menu_x + 150, menu_y + 230, 100, 40)
        pygame.draw.rect(screen, GREEN, sell_rect)
        sell_text = self.small_font.render(get_text("Sell", self.language), True, BLACK)
        screen.blit(sell_text, sell_text.get_rect(center=sell_rect.center))

        # Отображение сообщения об ошибке, если оно есть
        if self.error_message and pygame.time.get_ticks() - self.error_timer < 2000:  # Показываем сообщение 2 секунды
            error_font = self.small_font
            error_surface = error_font.render(self.error_message, True, (255, 0, 0))  # Красный текст
            error_rect = error_surface.get_rect(center=(screen_width // 2, (SCREEN_HEIGHT - 250) // 2 + menu_height // 2))  # Центр меню
            screen.blit(error_surface, error_rect)

        if return_rects:
            return {
                "close": close_rect,
                "harvest_increase": harvest_increase, "harvest_decrease": harvest_decrease,
                "products_increase": products_increase, "products_decrease": products_decrease,
                "sell": sell_rect
            }

class MenuManager:
    def __init__(self, language, coins, harvest, products, level):
        self.menus = {
            "wheel": WheelMenu(language),
            "seed": SeedMenu(language, coins, level),
            "build": BuildMenu(language, coins, level),
            "market": MarketMenu(language, coins, harvest, products)
        }
        self.active_menu = None

    def open_menu(self, menu_name, *args):
        if menu_name in self.menus:
            self.close_all()
            self.active_menu = menu_name
            if menu_name == "wheel":
                self.menus[menu_name].open(*args)
            elif menu_name == "seed":
                self.menus[menu_name].open()
            elif menu_name == "build":
                self.menus[menu_name].open()
            elif menu_name == "market":
                self.menus[menu_name].open()
            print(f"Opened menu: {menu_name} with args: {args}, language: {self.menus[menu_name].language}")
        else:
            print(f"Menu {menu_name} not found")

    def close_all(self):
        for menu in self.menus.values():
            menu.close()
        self.active_menu = None
        print("All menus closed")

    def handle_input(self, event, camera_x, screen_width, map_width, objects, harvest, products):
        print(f"MenuManager handling event: {event}, language: {self.menus.get(self.active_menu, {}).language if self.active_menu else 'No active menu'}")
        if self.active_menu:
            if self.active_menu == "wheel":
                result = self.menus[self.active_menu].handle_input(event, camera_x)
            elif self.active_menu == "seed":
                result = self.menus[self.active_menu].handle_input(event, screen_width, objects, camera_x)
            elif self.active_menu == "build":
                result = self.menus[self.active_menu].handle_input(event, screen_width, map_width, objects, camera_x, harvest, products)
            elif self.active_menu == "market":
                result = self.menus[self.active_menu].handle_input(event, screen_width)
            else:
                result = None
            print(f"MenuManager result: {result}")  # Отладка результата
            if result in ["close_seed_menu", "close_build_menu", "close_market_menu"]:
                self.close_all()
            elif result == "build":
                self.open_menu("build")
                print("Opening BuildMenu from WheelMenu")
            elif result == "plant":
                self.open_menu("seed")
                print("Opening SeedMenu from WheelMenu")
            elif result:
                print(f"Результат от {self.active_menu}: {result}")
            return result
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
            self.close_all()
            print("Closed all menus by right click outside")
            return None
        return None

    def draw(self, screen, camera_x):
        if self.active_menu:
            if self.active_menu == "wheel":
                self.menus[self.active_menu].draw(screen, camera_x)
            else:
                self.menus[self.active_menu].draw(screen)

    def update(self, coins, harvest, products, level):
        self.menus["seed"].update(coins, level)
        self.menus["build"].update(coins, level)
        self.menus["market"].update(coins, harvest, products)