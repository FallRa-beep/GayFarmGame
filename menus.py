import pygame
import math
from translations import get_text
from config import SCREEN_HEIGHT, SEEDS, BLACK, WHITE, GRAY, GREEN, BUILDING_CONFIG, YELLOW
import images
from entities import Bed, MapObject, Mill, CanningCellar, MarketStall
from notifications import NotificationManager


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


    def close(self):
        self.is_open = False


    def handle_input(self, event, camera_x):
        if not self.is_open:
            return None

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

            if not wheel_rect.collidepoint(mx, my):
                self.close()
                return None
        return None

    def draw(self, screen, camera_x):
        if not self.is_open:
            return
        screen_x = self.center_x - camera_x
        screen_y = self.center_y

        # Загружаем изображение фона колеса
        try:
            wheel_background = images.GAME_IMAGES["wheel_background"]
        except KeyError as e:

            # Заглушка на случай, если изображение не загрузилось
            wheel_background = pygame.Surface((self.radius * 2, self.radius * 2))
            wheel_background.fill(GRAY)

        # Определяем позицию для отображения фона (центрируем изображение)
        wheel_rect = wheel_background.get_rect(center=(int(screen_x), int(screen_y)))
        screen.blit(wheel_background, wheel_rect)

        # Остальной код для иконок остаётся без изменений
        build_angle = 0
        plant_angle = 180
        build_endpoint = (screen_x + self.radius * math.cos(math.radians(build_angle)),
                          screen_y - self.radius * math.sin(math.radians(build_angle)))
        plant_endpoint = (screen_x + self.radius * math.cos(math.radians(plant_angle)),
                          screen_y - self.radius * math.sin(math.radians(plant_angle)))

        try:
            build_icon = images.GAME_IMAGES["construction_icon"]
            plant_icon = images.GAME_IMAGES["planting_icon"]
        except KeyError as e:

            build_icon = pygame.Surface((32, 32))
            build_icon.fill((0, 0, 255))
            plant_icon = pygame.Surface((32, 32))
            plant_icon.fill((0, 255, 0))

        # Отрисовка иконок
        screen.blit(build_icon, (build_endpoint[0] + 5, build_endpoint[1] - build_icon.get_height() // 2))
        screen.blit(plant_icon,
                    (plant_endpoint[0] - plant_icon.get_width() - 5, plant_endpoint[1] - plant_icon.get_height() // 2))

class SeedMenu:
    def __init__(self, language, coins, level=1):
        self.is_open = False
        self.language = language
        self.coins = coins
        self.level = level
        self.current_seed = None
        self.current_index = 0
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.tooltip_font = pygame.font.Font(None, 18)
        self.hovered_buttons = {}
        self.error_message = None
        self.error_timer = 0

        # Формируем seed_options из SEEDS
        self.seed_options = []
        for seed in SEEDS:
            if level >= seed["unlock_level"]:
                translated_name = get_text(seed["name"].capitalize(), language)
                self.seed_options.append({
                    "name": translated_name,
                    "original_name": seed["name"],  # Для загрузки изображения плода (например, "wheat" или "corn")
                    "cost": seed["cost"],
                    "ripening_time": seed["ripening_time_minutes"],
                    "watering_interval": seed["watering_interval_minutes"],
                    "sprout_time": seed["sprout_time_minutes"],
                    "harvest_yield": seed["harvest_yield"],
                    "unlock_level": seed["unlock_level"]
                })

    def open(self):
        self.is_open = True
        self.planting = False
        self.selected_seed = None

    def close(self):
        self.is_open = False
        self.planting = False
        self.selected_seed = None

    def update(self, coins, level):
        self.coins = coins
        self.level = level

    def handle_input(self, event, screen_width, objects, camera_x):
        if not self.is_open:
            return None

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = pygame.mouse.get_pos()
            close_rect = pygame.Rect(screen_width - 30, 10, 20, 20)
            if close_rect.collidepoint(mx, my):
                self.close()
                return "close_seed_menu"
            available_seeds = [seed for seed in SEEDS if seed["unlock_level"] <= self.level]
            for i, seed in enumerate(available_seeds):
                row, col = i // 2, i % 2
                rect = pygame.Rect(screen_width - 180 + col * (64 + 10), 60 + row * (64 + 10), 64, 64)  # Новые размеры
                if rect.collidepoint(mx, my) and self.coins >= seed["cost"]:
                    self.selected_seed = {**seed, "language": self.language}
                    self.planting = True

                    return "seed_selected"
            if self.planting and self.selected_seed:
                world_x = mx + camera_x
                world_y = my

                planted = False
                for obj in objects:
                    if obj.obj_type == "bed":
                        bed_rect = pygame.Rect(obj.x, obj.y, obj.width, obj.height)

                        if bed_rect.collidepoint(world_x, world_y) and not obj.is_planted and self.coins >= \
                                self.selected_seed["cost"]:
                            obj.plant_seed(self.selected_seed)
                            planted = True

                            break
                if planted:
                    return {"action": "plant", "cost_coins": self.selected_seed["cost"]}

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
            mx, my = pygame.mouse.get_pos()
            menu_rect = pygame.Rect(screen_width - 200, 0, 200, SCREEN_HEIGHT)

            if not menu_rect.collidepoint(mx, my):
                self.close()
                return None
        return None

    def draw(self, screen):
        if not self.is_open:
            return
        screen_width = screen.get_width()
        menu_width, menu_height = 200, SCREEN_HEIGHT
        # Загружаем изображение фона меню
        try:
            background_image = images.GAME_IMAGES["menu_background"]
        except KeyError as e:

            # Заглушка на случай, если изображение не загрузилось
            background_image = pygame.Surface((menu_width, menu_height))
            background_image.fill((200, 200, 200))

        # Отрисовка фона
        screen.blit(background_image, (screen_width - menu_width, 0))

        seeds_per_row = 2
        seed_width = 64  # Новый размер кнопки
        seed_height = 64  # Новый размер кнопки
        start_y = 60

        available_seeds = [seed for seed in SEEDS if seed["unlock_level"] <= self.level]

        # Вычисляем общую ширину строки кнопок
        total_row_width = seeds_per_row * seed_width + (seeds_per_row - 1) * 10  # 138 пикселей для 2 кнопок
        # Центр меню
        menu_center_x = screen_width - menu_width // 2
        # Начальная позиция X для центрирования
        start_x = menu_center_x - (total_row_width // 2)

        # Отрисовка кнопки возврата
        mx, my = pygame.mouse.get_pos()
        return_rect = pygame.Rect(screen_width - 42, 10, 32, 32)  # 10 справа, 10 сверху
        return_image = images.GAME_IMAGES["return_hover"] if return_rect.collidepoint(mx, my) else images.GAME_IMAGES[
            "return"]
        screen.blit(return_image, (return_rect.x, return_rect.y))

        for i, seed in enumerate(available_seeds):
            row = i // seeds_per_row
            col = i % seeds_per_row
            rect_x = start_x + col * (seed_width + 10)
            rect_y = start_y + row * (seed_height + 10)
            rect = pygame.Rect(rect_x, rect_y, seed_width, seed_height)
            is_hovered = rect.collidepoint(pygame.mouse.get_pos())
            is_active = self.selected_seed and seed["name"] == self.selected_seed["name"]
        tooltip = None

        for i, seed in enumerate(available_seeds):
            row = i // seeds_per_row
            col = i % seeds_per_row
            rect_x = start_x + col * (seed_width + 10)  # Отступ 10 пикселей между кнопками
            rect_y = start_y + row * (seed_height + 10)  # Отступ 10 пикселей между строками
            rect = pygame.Rect(rect_x, rect_y, seed_width, seed_height)
            is_hovered = rect.collidepoint(pygame.mouse.get_pos())
            is_active = self.selected_seed and seed["name"] == self.selected_seed["name"]

            # Отрисовка фона кнопки (puck_seed)
            try:
                puck_seed_image = images.GAME_IMAGES["puck_seed"]
            except KeyError as e:

                puck_seed_image = pygame.Surface((seed_width, seed_height))
                puck_seed_image.fill(GRAY)

            screen.blit(puck_seed_image, (rect_x, rect_y))

            # Отрисовка изображения семени поверх фона
            try:
                seed_image = images.GAME_IMAGES[f"{seed['name']}_seed"]
            except KeyError as e:

                seed_image = pygame.Surface((seed_width, seed_height))
                seed_image.fill(YELLOW)

            # Центрируем семя на кнопке
            seed_x = rect_x + (seed_width - seed_image.get_width()) // 2
            seed_y = rect_y + (seed_height - seed_image.get_height()) // 2
            screen.blit(seed_image, (seed_x, seed_y))

            # Подсветка при наведении или выборе
            if is_active:
                pygame.draw.rect(screen, GREEN, rect, 2)  # Зеленая рамка для активной кнопки
            elif is_hovered:
                pygame.draw.rect(screen, WHITE, rect, 2)  # Белая рамка при наведении
                # Формируем текст подсказки
                tooltip_lines = [
                    f"{get_text(seed['name'].capitalize(), self.language)}",  # Название
                    "",  # Пустая строка для разделения (будет заменена иконками)
                    "",  # Место для стоимости
                    "",  # Место для времени созревания
                    "",  # Место для времени полива
                    ""  # Место для урожая
                ]
                tooltip = "\n".join(tooltip_lines)

        # Отрисовка подсказки (оставим текущую реализацию, если она уже настроена)
        if tooltip:
            # (Твой код подсказки остается без изменений, если ты доволен текущей реализацией)
            tooltip_lines = tooltip.split('\n')
            icon_size = 16
            line_height = 20
            padding = 10
            tooltip_width = 100
            tooltip_height = len(tooltip_lines) * line_height

            # Создаем поверхность для подсказки
            tooltip_surface = pygame.Surface((tooltip_width, tooltip_height), pygame.SRCALPHA)

            # Загружаем и масштабируем фон подсказки
            try:
                tooltip_background = images.GAME_IMAGES["tooltip_background"]
                tooltip_background = pygame.transform.scale(tooltip_background, (tooltip_width, tooltip_height))
            except KeyError as e:

                tooltip_background = pygame.Surface((tooltip_width, tooltip_height))
                tooltip_background.fill((0, 0, 0, 200))

            tooltip_surface.blit(tooltip_background, (0, 0))

            # Иконки
            coin_icon = pygame.transform.scale(images.GAME_IMAGES["coin_menu"], (icon_size, icon_size))
            clock_icon = pygame.transform.scale(images.GAME_IMAGES["clock_icon"], (icon_size, icon_size))
            water_drop_icon = pygame.transform.scale(images.GAME_IMAGES["water_drop_icon"], (icon_size, icon_size))
            harvest_icon = pygame.transform.scale(images.GAME_IMAGES["harvest"], (icon_size, icon_size))

            # Заполняем строки
            seed_index = next(i for i, seed in enumerate(available_seeds) if
                              get_text(seed['name'].capitalize(), self.language) == tooltip_lines[0])
            seed = available_seeds[seed_index]
            y_offset = padding+2
            x_offset = padding

            # Название
            name_text = self.tooltip_font.render(tooltip_lines[0], True, WHITE)
            tooltip_surface.blit(name_text, (x_offset, y_offset))
            y_offset += line_height

            # Функция для центрирования иконки относительно текста
            def center_icon_y(text_surface, y_position):
                text_height = text_surface.get_height()
                return y_position + (text_height - icon_size) // 2

            # Стоимость
            cost_text = self.tooltip_font.render(f"{seed['cost']}", True, WHITE)
            tooltip_surface.blit(coin_icon, (x_offset, center_icon_y(cost_text, y_offset)))
            tooltip_surface.blit(cost_text, (x_offset + icon_size + 5, y_offset))
            y_offset += line_height + 2

            # Время созревания
            ripening_text = self.tooltip_font.render(
                f"{seed['ripening_time_minutes']} {get_text('min', self.language)}", True, WHITE)
            tooltip_surface.blit(clock_icon, (x_offset, center_icon_y(ripening_text, y_offset)))
            tooltip_surface.blit(ripening_text, (x_offset + icon_size + 5, y_offset))
            y_offset += line_height

            # Время полива
            watering_text = self.tooltip_font.render(
                f"{seed['watering_interval_minutes']} {get_text('min', self.language)}", True, WHITE)
            tooltip_surface.blit(water_drop_icon, (x_offset, center_icon_y(watering_text, y_offset)))
            tooltip_surface.blit(watering_text, (x_offset + icon_size + 5, y_offset))
            y_offset += line_height

            # Урожай
            harvest_text = self.tooltip_font.render(f"{seed['harvest_yield']}", True, WHITE)
            tooltip_surface.blit(harvest_icon, (x_offset, center_icon_y(harvest_text, y_offset)))
            tooltip_surface.blit(harvest_text, (x_offset + icon_size + 5, y_offset))

            # Позиция подсказки на экране
            tooltip_rect = pygame.Rect(pygame.mouse.get_pos()[0] + 10, pygame.mouse.get_pos()[1], tooltip_width,
                                       tooltip_height)
            if tooltip_rect.right > screen_width:
                tooltip_rect.left = pygame.mouse.get_pos()[0] - tooltip_width - 10
            if tooltip_rect.bottom > SCREEN_HEIGHT:
                tooltip_rect.top = pygame.mouse.get_pos()[1] - tooltip_height - 10

            # Отрисовка подсказки на экране
            screen.blit(tooltip_surface, (tooltip_rect.x, tooltip_rect.y))

class BuildMenu:
    def __init__(self, language, coins, level=1,notification_manager=None):
        self.is_open = False
        self.language = language
        self.coins = coins
        self.level = level
        self.build_action = None
        self.preview_build = None
        self.moving_object = None
        self.current_index = 0
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.tooltip_font = pygame.font.Font(None, 18)
        self.hovered_buttons = {}
        self.error_message = None
        self.error_timer = 0
        # Динамическая генерация build_options из BUILDING_CONFIG
        self.build_options = []
        for building_key, building_data in BUILDING_CONFIG.items():
            translated_text = get_text(building_key.capitalize(), language)  # Предполагаем, что ключи — это имена
            cost_text = f"{get_text('Cost', language)}: {building_data['cost_coins']} {get_text('coins', language)}"
            if "cost_harvest" in building_data:
                cost_text += f" + {building_data['cost_harvest']} {get_text('Harvest', language)}"
            if "cost_products" in building_data:
                cost_text += f" + {building_data['cost_products']} {get_text('Products', language)}"
            self.build_options.append({
                "text": translated_text,
                "cost_coins": building_data["cost_coins"],
                "cost_harvest": building_data.get("cost_harvest", 0),
                "cost_products": building_data.get("cost_products", 0),
                "unlock_level": building_data["unlock_level"],
                "action": "new",
                "type": building_data.get("type", "functional"),  # По умолчанию "functional", если не указано
                "category": building_data["category"],
                "description": get_text(f"{building_key}_description", language),
                "cost_text": cost_text,
                "consume": building_data.get("consume", {}),
                "produce": building_data.get("produce", {}),
                "work_time": building_data.get("work_time", 0)
            })
        # Фильтр по умолчанию (пока только "functional")
        self.current_category = "functional"
        self.notification_manager = notification_manager

    def open(self):
        self.is_open = True
        self.build_action = None
        self.preview_build = None
        self.moving_object = None
        self.current_index = 0


    def close(self):
        self.is_open = False
        self.build_action = None
        self.preview_build = None
        self.moving_object = None


    def update(self, coins, level):
        self.coins = coins
        self.level = level
        available_options = [i for i, option in enumerate(self.build_options) if self.level >= option["unlock_level"]]
        if not available_options or self.current_index >= len(available_options):
            self.current_index = 0

    def handle_input(self, event, screen_width, map_width, objects, camera_x, harvest, products):
        from game_utils import snap_to_grid, check_collision
        if not self.is_open:
            return None

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = pygame.mouse.get_pos()
            build_rects = self.draw(pygame.display.get_surface(), harvest, products, return_rects=True)


            # Обработка кликов по кнопкам категорий
            for category in ["functional", "decor", "roads"]:
                if f"category_{category}" in build_rects and build_rects[f"category_{category}"].collidepoint(mx, my):
                    self.current_category = category
                    self.current_index = 0  # Сбрасываем индекс при смене категории
                    available_options = [option for option in self.build_options if
                                         self.level >= option["unlock_level"] and option[
                                             "category"] == self.current_category]
                    if not available_options:
                        self.current_index = 0  # Устанавливаем индекс на 0, если опции пусты

                    return None

            if build_rects["close"].collidepoint(mx, my):
                self.close()
                return "close_build_menu"
            elif build_rects["left_arrow"].collidepoint(mx, my):
                available_options = [i for i, option in enumerate(self.build_options) if
                                     self.level >= option["unlock_level"] and option[
                                         "category"] == self.current_category]
                if available_options:
                    self.current_index = (self.current_index - 1) % len(available_options)
            elif build_rects["right_arrow"].collidepoint(mx, my):
                available_options = [i for i, option in enumerate(self.build_options) if
                                     self.level >= option["unlock_level"] and option[
                                         "category"] == self.current_category]
                if available_options:
                    self.current_index = (self.current_index + 1) % len(available_options)
            elif build_rects["move"].collidepoint(mx, my):
                self.build_action = "move"

                return "set_move"
            elif build_rects["destroy"].collidepoint(mx, my):
                self.build_action = "destroy"

                return "set_destroy"
            elif build_rects["build_button"].collidepoint(mx, my):
                available_options = [option for option in self.build_options if
                                     self.level >= option["unlock_level"] and option[
                                         "category"] == self.current_category]
                if not available_options:
                    return None
                option = available_options[self.current_index]
                total_cost_coins = option["cost_coins"]
                cost_harvest = option.get("cost_harvest", 0)
                cost_products = option.get("cost_products", 0)
                if (self.coins >= total_cost_coins and
                        ("cost_harvest" not in option or harvest >= cost_harvest) and
                        ("cost_products" not in option or products >= cost_products)):
                    if option["text"] == get_text("Bed", self.language):
                        self.preview_build = Bed(0, 0, width=32, height=32)
                    elif option["text"] == get_text("Mill", self.language):
                        self.preview_build = Mill(0, 0)
                    elif option["text"] == get_text("Canning Cellar", self.language):
                        self.preview_build = CanningCellar(0, 0)
                    self.build_action = "build_preview"

                    return "start_build_preview"
                else:
                    if self.notification_manager:
                        self.notification_manager.add_notification("no_resources")

            elif self.build_action == "build_preview" and self.preview_build:
                mx, my = pygame.mouse.get_pos()
                new_x = snap_to_grid(mx + camera_x, grid_size=32)
                new_y = snap_to_grid(my, grid_size=32)
                new_x = max(0, min(new_x, map_width - self.preview_build.width))
                new_y = max(0, min(new_y, SCREEN_HEIGHT - self.preview_build.height))
                self.preview_build.x = new_x
                self.preview_build.y = new_y
                if not check_collision(self.preview_build, objects, grid_size=32, allow_touching=True):
                    objects.append(self.preview_build)
                    print(
                        f"Added {self.preview_build.obj_type} to objects at ({self.preview_build.x}, {self.preview_build.y})")
                    available_options = [option for option in self.build_options if
                                         self.level >= option["unlock_level"] and option[
                                             "category"] == self.current_category]
                    option = available_options[self.current_index]
                    cost = option["cost_coins"]
                    harvest_cost = option.get("cost_harvest", 0)
                    products_cost = option.get("cost_products", 0)

                    self.preview_build = None
                    self.build_action = None
                    print(
                    f"Build result: {{'action': 'build', 'cost_coins': {cost}, 'cost_harvest': {harvest_cost}, 'cost_products': {products_cost}}}")
                    return {"action": "build", "cost_coins": cost, "cost_harvest": harvest_cost,
                            "cost_products": products_cost}
            elif self.build_action == "move" and self.moving_object is None:
                ui_area = pygame.Rect(0, 0, 50, 50)
                if not ui_area.collidepoint(mx, my):
                    for obj in objects:
                        obj_rect = pygame.Rect(obj.x - camera_x, obj.y, obj.width, obj.height)
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

                            return "start_move_preview"
            elif self.build_action == "move_preview" and self.moving_object and self.preview_build:
                mx, my = pygame.mouse.get_pos()
                new_x = snap_to_grid(mx + camera_x, grid_size=32)
                new_y = snap_to_grid(my, grid_size=32)
                new_x = max(0, min(new_x, map_width - self.preview_build.width))
                new_y = max(0, min(new_y, SCREEN_HEIGHT - self.preview_build.height))
                self.preview_build.x = new_x
                self.preview_build.y = new_y
                temp_objects = [obj for obj in objects if obj != self.moving_object]
                if not check_collision(self.preview_build, temp_objects, grid_size=32, allow_touching=True):
                    self.moving_object.x = new_x
                    self.moving_object.y = new_y
                    moved_obj = self.moving_object
                    self.moving_object = None
                    self.preview_build = None
                    self.build_action = "move"

                    return {"action": "move_complete", "moved_obj": moved_obj}
            elif self.build_action == "destroy":
                for i, obj in enumerate(objects):
                    obj_rect = pygame.Rect(obj.x - camera_x, obj.y, obj.width, obj.height)

                    if obj_rect.collidepoint(mx, my) and obj.obj_type in ["bed", "mill",
                                                                          "canning_cellar"] and obj.obj_type not in [
                        "house"]:

                        destroyed_obj = objects.pop(i)
                        self.build_action = "destroy"

                        return {"action": "destroy_complete", "destroyed_obj": destroyed_obj}
        elif event.type == pygame.MOUSEMOTION:
            if self.build_action in ["build_preview", "move_preview"] and self.preview_build:
                mx, my = pygame.mouse.get_pos()
                new_x = snap_to_grid(mx + camera_x, grid_size=32)
                new_y = snap_to_grid(my, grid_size=32)
                new_x = max(0, min(new_x, map_width - self.preview_build.width))
                new_y = max(0, min(new_y, SCREEN_HEIGHT - self.preview_build.height))
                self.preview_build.x = new_x
                self.preview_build.y = new_y

                return {"action": self.build_action, "preview_obj": self.preview_build}
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
            mx, my = pygame.mouse.get_pos()
            menu_rect = pygame.Rect(screen_width - 240, 0, 240, SCREEN_HEIGHT)
            if not menu_rect.collidepoint(mx, my):
                self.close()

                return None
        return None

    def draw(self, screen, harvest, products, return_rects=False):
        if not self.is_open:
            return {} if return_rects else None
        screen_width = screen.get_width()
        menu_width, menu_height = 200, SCREEN_HEIGHT

        # Загружаем изображение фона меню
        try:
            background_image = images.GAME_IMAGES["menu_background"]
        except KeyError as e:

            background_image = pygame.Surface((menu_width, menu_height))
            background_image.fill((200, 200, 200))

        # Отрисовка фона
        screen.blit(background_image, (screen_width - menu_width, 0))

        # Получаем позицию мыши
        mx, my = pygame.mouse.get_pos()

        # Кнопки "Close", "Move" и "Destroy"
        close_rect = pygame.Rect(screen_width - menu_width + menu_width - 32 - 10, 10, 32, 32)  # Справа, отступ 10
        move_rect = pygame.Rect(screen_width - menu_width + 10, 10, 32, 32)  # Слева, отступ 10
        destroy_rect = pygame.Rect(screen_width - menu_width + 10 + 32 + 10, 10, 32, 32)  # Справа от Move, отступ 10
        close_image = images.GAME_IMAGES["return" if not close_rect.collidepoint(mx, my) else "return_hover"]
        move_state = "move_active" if self.build_action in ["move",
                                                            "move_preview"] else "move_hover" if move_rect.collidepoint(
            mx, my) else "move_normal"
        destroy_state = "destroy_active" if self.build_action == "destroy" else "destroy_hover" if destroy_rect.collidepoint(
            mx, my) else "destroy_normal"
        screen.blit(close_image, close_rect.topleft)
        screen.blit(images.GAME_IMAGES[move_state], move_rect.topleft)
        screen.blit(images.GAME_IMAGES[destroy_state], destroy_rect.topleft)
        self.hovered_buttons["close"] = close_rect.collidepoint(mx, my)
        self.hovered_buttons["move"] = move_rect.collidepoint(mx, my)
        self.hovered_buttons["destroy"] = destroy_rect.collidepoint(mx, my)

        # Кнопки категорий (на y=60, размер 32x32)
        category_rects = {}
        categories = ["functional", "decor", "roads"]
        category_width = 32
        category_height = 32
        category_start_x = screen_width - menu_width + 15
        for i, category in enumerate(categories):
            rect = pygame.Rect(category_start_x + i * (category_width + 10), 60, category_width, category_height)
            category_rects[category] = rect
            color = GREEN if self.current_category == category else GRAY
            pygame.draw.rect(screen, color, rect)
            category_text = self.tooltip_font.render(category.capitalize(), True, BLACK)
            screen.blit(category_text, category_text.get_rect(center=rect.center))
            self.hovered_buttons[f"category_{category}"] = rect.collidepoint(mx, my)

        # Отрисовка текущей выбранной постройки
        available_options = [option for option in self.build_options if
                             self.level >= option["unlock_level"] and option["category"] == self.current_category]
        current_option = available_options[self.current_index % len(available_options)] if available_options else None

        # Условие для отображения стрелок
        show_arrows = len(available_options) > 1 if available_options else False

        # Зона изображения объекта (уменьшаем высоту, чтобы поместить кнопку Build)
        build_rect = pygame.Rect(screen_width - menu_width + 15, 120, menu_width - 30, 150)  # Уменьшаем высоту до 150
        image_zone_width = 64
        image_zone_height = 64
        image_zone_x = build_rect.x + (build_rect.width - image_zone_width) // 2
        image_zone_y = build_rect.y + 10

        if current_option:
            if current_option["text"] == get_text("Bed", self.language):
                build_image = images.GAME_IMAGES["bed_wet"]
            elif current_option["text"] == get_text("Mill", self.language):
                build_image = images.GAME_IMAGES["mill"]
            elif current_option["text"] == get_text("Canning Cellar", self.language):
                build_image = images.GAME_IMAGES.get("canning_cellar", images.GAME_IMAGES["mill"])
            else:
                build_image = pygame.Surface((image_zone_width, image_zone_height))
                build_image.fill((255, 255, 255))
            scale_factor = min(image_zone_width / build_image.get_width(), image_zone_height / build_image.get_height())
            scaled_image = pygame.transform.scale(build_image, (
                int(build_image.get_width() * scale_factor), int(build_image.get_height() * scale_factor)))
            screen.blit(scaled_image, (image_zone_x + (image_zone_width - scaled_image.get_width()) // 2,
                                       image_zone_y + (image_zone_height - scaled_image.get_height()) // 2))

            # Название объекта
            title_text = self.font.render(current_option["text"], True, BLACK)
            screen.blit(title_text, (
                build_rect.x + (build_rect.width - title_text.get_width()) // 2, image_zone_y + image_zone_height + 10))

            # Стоимость
            coin_image = images.GAME_IMAGES["coin_menu"]
            harvest_image = pygame.transform.scale(images.GAME_IMAGES["harvest"], (16, 16))
            product_image = pygame.transform.scale(images.GAME_IMAGES["product"], (16, 16))
            cost_coins_text = self.tooltip_font.render(str(current_option["cost_coins"]), True, BLACK) if \
                current_option["cost_coins"] > 0 else None
            cost_harvest_text = self.tooltip_font.render(str(current_option["cost_harvest"]), True,
                                                         BLACK) if "cost_harvest" in current_option and current_option[
                "cost_harvest"] > 0 else None
            cost_products_text = self.tooltip_font.render(str(current_option["cost_products"]), True,
                                                          BLACK) if "cost_products" in current_option and \
                                                                    current_option["cost_products"] > 0 else None
            total_width = 0
            items = []
            if cost_coins_text:
                total_width += coin_image.get_width() + cost_coins_text.get_width() + 5
                items.append((coin_image, cost_coins_text))
            if cost_harvest_text:
                total_width += harvest_image.get_width() + cost_harvest_text.get_width() + 15
                items.append((harvest_image, cost_harvest_text))
            if cost_products_text:
                total_width += product_image.get_width() + cost_products_text.get_width() + 15
                items.append((product_image, cost_products_text))
            x_pos = build_rect.x + (build_rect.width - total_width) // 2
            y_pos = image_zone_y + image_zone_height + 40
            for icon, number_text in items:
                screen.blit(icon, (x_pos, y_pos))
                if number_text:
                    screen.blit(number_text, (x_pos + icon.get_width() + 5, y_pos))
                x_pos += icon.get_width() + number_text.get_width() + 15

            # Статическое описание с переносом
            description_lines = []
            current_line = ""
            for word in current_option["description"].split():
                test_line = current_line + " " + word if current_line else word
                if self.tooltip_font.size(test_line)[0] <= build_rect.width - 10:
                    current_line = test_line
                else:
                    description_lines.append(current_line)
                    current_line = word
            if current_line:
                description_lines.append(current_line)
            for i, line in enumerate(description_lines):
                description_text = self.tooltip_font.render(line, True, BLACK)
                description_rect = description_text.get_rect(
                    center=(build_rect.x + build_rect.width // 2, y_pos + 25 + i * 20))
                screen.blit(description_text, description_rect)

            # Кнопка "Build" (фиксированная позиция внизу)
            build_button_rect = pygame.Rect(build_rect.x + (build_rect.width - 100) // 2, SCREEN_HEIGHT - 60, 100, 40)
            total_cost_coins = current_option["cost_coins"]
            cost_harvest = current_option.get("cost_harvest", 0)
            cost_products = current_option.get("cost_products", 0)
            can_build = (self.coins >= total_cost_coins and
                         ("cost_harvest" not in current_option or harvest >= cost_harvest) and
                         ("cost_products" not in current_option or products >= cost_products))
            build_state = "button_hover" if can_build and build_button_rect.collidepoint(mx, my) else "button_normal"
            build_button_image = pygame.transform.scale(images.GAME_IMAGES[build_state], (100, 40))
            screen.blit(build_button_image, (build_button_rect.x, build_button_rect.y))
            build_text_color = GREEN if can_build and self.build_action == "build_preview" else WHITE if can_build and build_button_rect.collidepoint(
                mx, my) else (128, 128, 128)
            build_text = self.small_font.render(get_text("Build", self.language), True, build_text_color)
            screen.blit(build_text, build_text.get_rect(center=build_button_rect.center))
            self.hovered_buttons["build_button"] = build_button_rect.collidepoint(mx, my) and can_build

        # Стрелки с одинаковыми отступами
        left_arrow_rect = pygame.Rect(build_rect.x + 15, image_zone_y + (image_zone_height - 20) // 2, 20, 20)
        right_arrow_rect = pygame.Rect(build_rect.right - 15 - 20, image_zone_y + (image_zone_height - 20) // 2, 20, 20)
        if show_arrows:
            screen.blit(images.GAME_IMAGES["arrow_left"], left_arrow_rect.topleft)
            screen.blit(images.GAME_IMAGES["arrow_right"], right_arrow_rect.topleft)
            self.hovered_buttons["left_arrow"] = left_arrow_rect.collidepoint(mx, my)
            self.hovered_buttons["right_arrow"] = right_arrow_rect.collidepoint(mx, my)

        # Отрисовка сообщения об ошибке с переносом текста и плавным исчезновением
        if self.error_message and pygame.time.get_ticks() - self.error_timer < 2000:
            # Разбиваем текст на строки, чтобы он помещался в ширину меню
            max_width = menu_width - 20  # Учитываем небольшие отступы
            words = self.error_message.split()
            lines = []
            current_line = ""
            for word in words:
                test_line = current_line + " " + word if current_line else word
                if self.small_font.size(test_line)[0] <= max_width:
                    current_line = test_line
                else:
                    lines.append(current_line)
                    current_line = word
            if current_line:
                lines.append(current_line)

            # Вычисляем высоту текста
            line_height = self.small_font.size(" ")[1]  # Высота строки
            total_text_height = len(lines) * line_height

            # Создаем поверхность для текста
            text_surface = pygame.Surface((menu_width, total_text_height), pygame.SRCALPHA)

            # Отрисовываем строки текста
            for i, line in enumerate(lines):
                line_surface = self.small_font.render(line, True, (255, 0, 0))
                text_surface.blit(line_surface, (10, i * line_height))  # Отступ слева 10 пикселей

            # Вычисляем прозрачность (от 255 до 0 за 2 секунды)
            elapsed_time = pygame.time.get_ticks() - self.error_timer
            alpha = max(0, 255 - (255 * elapsed_time // 2000))  # Линейное уменьшение прозрачности
            text_surface.set_alpha(alpha)

            # Позиция текста внизу меню
            text_rect = text_surface.get_rect(
                center=(screen_width - menu_width // 2, SCREEN_HEIGHT - total_text_height - 20)
            )
            screen.blit(text_surface, text_rect)

        if return_rects:
            rects = {
                "close": close_rect,
                "move": move_rect,
                "destroy": destroy_rect,
                "build_button": build_button_rect if current_option else pygame.Rect(0, 0, 0, 0),
                "left_arrow": left_arrow_rect,
                "right_arrow": right_arrow_rect
            }
            rects.update({f"category_{category}": rect for category, rect in category_rects.items()})
            return rects


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
        self.error_message = None
        self.error_timer = 0
        self.sale_values = [0, 1, 5, 10, 25, 50, 100]
        self.animations = []

    def open(self):
        self.is_open = True
        self.error_message = None
        self.error_timer = 0
        self.animations = []


    def close(self):
        self.is_open = False
        self.error_message = None
        self.animations = []


    def update(self, coins, harvest, products):
        self.coins = coins
        self.harvest = harvest
        self.products = products
        for anim in self.animations[:]:
            anim["y"] -= 0.5  # Замедленный подъем
            anim["alpha"] -= 2  # Замедленное исчезновение
            if anim["alpha"] <= 0:
                self.animations.remove(anim)


    def handle_input(self, event, screen_width):
        if not self.is_open:
            return None

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = pygame.mouse.get_pos()
            rects = self.draw(pygame.display.get_surface(), return_rects=True)
            if rects["close"].collidepoint(mx, my):
                self.close()
                return "close_market_menu"
            elif rects["harvest_increase"].collidepoint(mx, my):
                current_index = self.sale_values.index(self.harvest_to_sell)
                next_index = (current_index + 1) % len(self.sale_values)
                while (next_index != current_index and self.sale_values[next_index] > self.harvest):
                    next_index = (next_index + 1) % len(self.sale_values)
                self.harvest_to_sell = self.sale_values[next_index]

            elif rects["harvest_decrease"].collidepoint(mx, my):
                current_index = self.sale_values.index(self.harvest_to_sell)
                prev_index = current_index - 1
                # Ограничиваем prev_index, чтобы не уходить ниже 0
                if prev_index < 0:
                    prev_index = 0  # Фиксируем на 0
                self.harvest_to_sell = self.sale_values[prev_index]

            elif rects["products_increase"].collidepoint(mx, my):
                current_index = self.sale_values.index(self.products_to_sell)
                next_index = (current_index + 1) % len(self.sale_values)
                while (next_index != current_index and self.sale_values[next_index] > self.products):
                    next_index = (next_index + 1) % len(self.sale_values)
                self.products_to_sell = self.sale_values[next_index]

            elif rects["products_decrease"].collidepoint(mx, my):
                current_index = self.sale_values.index(self.products_to_sell)
                prev_index = current_index - 1
                # Ограничиваем prev_index, чтобы не уходить ниже 0
                if prev_index < 0:
                    prev_index = 0  # Фиксируем на 0
                self.products_to_sell = self.sale_values[prev_index]

            elif rects["sell"].collidepoint(mx, my):
                if self.harvest_to_sell <= self.harvest and self.products_to_sell <= self.products:
                    harvest_value = self.harvest_to_sell * 2
                    products_value = self.products_to_sell * 15
                    total_value = harvest_value + products_value

                    sell_x = rects["sell"].centerx
                    sell_y = rects["sell"].top
                    if self.harvest_to_sell > 0:
                        harvest_image = images.GAME_IMAGES.get("harvest", pygame.Surface((32, 32))).copy()
                        self.animations.append(
                            {"type": "harvest", "value": -self.harvest_to_sell, "x": sell_x - 20, "y": sell_y,
                             "alpha": 255, "image": harvest_image})
                    if self.products_to_sell > 0:
                        product_image = images.GAME_IMAGES.get("product", pygame.Surface((32, 32))).copy()
                        self.animations.append(
                            {"type": "products", "value": -self.products_to_sell, "x": sell_x + 20, "y": sell_y,
                             "alpha": 255, "image": product_image})
                    if total_value > 0:
                        coin_image = images.GAME_IMAGES.get("coin_menu", pygame.Surface((16, 16))).copy()
                        self.animations.append(
                            {"type": "coins", "value": total_value, "x": sell_x, "y": sell_y - 20, "alpha": 255,
                             "image": coin_image})
                    result = {"action": "sell", "value": total_value, "harvest_sold": self.harvest_to_sell,
                              "products_sold": self.products_to_sell}
                    print(f"Sell result: {{'action': 'sell', 'value': {total_value}, 'harvest_sold': {self.harvest_to_sell}, 'products_sold': {self.products_to_sell}}}")
                    return result
                else:
                    self.error_message = get_text("Недостаточно ресурсов!", self.language)
                    self.error_timer = pygame.time.get_ticks()
                    print(self.error_message)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
            mx, my = pygame.mouse.get_pos()
            menu_rect = pygame.Rect((screen_width - 400) // 2, (SCREEN_HEIGHT - 250) // 2, 400, 250)

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

        harvest_image = images.GAME_IMAGES.get("harvest", pygame.Surface((32, 32)))
        product_image = images.GAME_IMAGES.get("product", pygame.Surface((32, 32)))
        coin_image = images.GAME_IMAGES.get("coin_menu", pygame.Surface((16, 16)))

        screen.blit(harvest_image, (menu_x + 20, menu_y + 50))
        harvest_rect = pygame.Rect(menu_x + 150, menu_y + 50, 50, 40)
        pygame.draw.rect(screen, WHITE, harvest_rect)
        harvest_text = self.small_font.render(str(self.harvest_to_sell), True, BLACK)
        screen.blit(harvest_text,
                    (harvest_rect.x + (harvest_rect.width - harvest_text.get_width()) // 2, harvest_rect.y + 10))

        screen.blit(product_image, (menu_x + 20, menu_y + 100))
        products_rect = pygame.Rect(menu_x + 150, menu_y + 100, 50, 40)
        pygame.draw.rect(screen, WHITE, products_rect)
        products_text = self.small_font.render(str(self.products_to_sell), True, BLACK)
        screen.blit(products_text,
                    (products_rect.x + (products_rect.width - products_text.get_width()) // 2, products_rect.y + 10))

        harvest_increase = pygame.Rect(menu_x + 205, menu_y + 50, 30, 20)
        harvest_decrease = pygame.Rect(menu_x + 205, menu_y + 70, 30, 20)
        products_increase = pygame.Rect(menu_x + 205, menu_y + 100, 30, 20)
        products_decrease = pygame.Rect(menu_x + 205, menu_y + 120, 30, 20)
        pygame.draw.rect(screen, GREEN, harvest_increase)
        pygame.draw.rect(screen, GREEN, harvest_decrease)
        pygame.draw.rect(screen, GREEN, products_increase)
        pygame.draw.rect(screen, GREEN, products_decrease)
        screen.blit(self.small_font.render("↑", True, BLACK), harvest_increase.move(10, 2))
        screen.blit(self.small_font.render("↓", True, BLACK), harvest_decrease.move(10, 2))
        screen.blit(self.small_font.render("↑", True, BLACK), products_increase.move(10, 2))
        screen.blit(self.small_font.render("↓", True, BLACK), products_decrease.move(10, 2))

        total_value = (self.harvest_to_sell * 2) + (self.products_to_sell * 15)
        screen.blit(coin_image, (menu_x + 150, menu_y + 150))
        value_text = self.small_font.render(str(total_value), True, BLACK)
        screen.blit(value_text, (menu_x + 190, menu_y + 152))
        sell_rect = pygame.Rect(menu_x + 150, menu_y + 180, 100, 40)
        pygame.draw.rect(screen, GREEN, sell_rect)
        sell_text = self.small_font.render(get_text("Sell", self.language), True, BLACK)
        screen.blit(sell_text, sell_text.get_rect(center=sell_rect.center))

        for anim in self.animations:
            image = anim["image"]
            if anim["type"] == "coins":
                text = self.small_font.render(f"+{anim['value']}", True, BLACK)
            else:
                text = self.small_font.render(str(anim["value"]), True, BLACK)
            image.set_alpha(anim["alpha"])
            text.set_alpha(anim["alpha"])
            screen.blit(text, (anim["x"] - text.get_width() - 5, anim["y"] - text.get_height() // 2))
            screen.blit(image, (anim["x"] + 5, anim["y"] - image.get_height() // 2))

        if self.error_message and pygame.time.get_ticks() - self.error_timer < 2000:
            error_surface = self.small_font.render(self.error_message, True, (255, 0, 0))
            error_rect = error_surface.get_rect(center=(menu_x + menu_width // 2, menu_y + menu_height - 30))
            screen.blit(error_surface, error_rect)

        if return_rects:
            return {
                "close": close_rect,
                "harvest_increase": harvest_increase, "harvest_decrease": harvest_decrease,
                "products_increase": products_increase, "products_decrease": products_decrease,
                "sell": sell_rect
            }

class MenuManager:
    def __init__(self, language, coins, harvest, products, level, notification_manager=None):
        self.menus = {
            "wheel": WheelMenu(language),
            "seed": SeedMenu(language, coins, level),
            "build": BuildMenu(language, coins, level, notification_manager),
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



    def close_all(self):
        for menu in self.menus.values():
            menu.close()
        self.active_menu = None

    def handle_input(self, event, camera_x, screen_width, map_width, objects, harvest, products):
        if self.active_menu:
            if self.active_menu == "wheel":
                result = self.menus[self.active_menu].handle_input(event, camera_x)
            elif self.active_menu == "seed":
                result = self.menus[self.active_menu].handle_input(event, screen_width, objects, camera_x)
            elif self.active_menu == "build":
                result = self.menus[self.active_menu].handle_input(event, screen_width, map_width, objects, camera_x,
                                                                   harvest, products)
                print(f"Результат из {self.active_menu}: {result}")
            elif self.active_menu == "market":
                result = self.menus[self.active_menu].handle_input(event, screen_width)
            else:
                result = None

            if result in ["close_seed_menu", "close_build_menu", "close_market_menu"]:
                self.close_all()
            elif result == "build":
                self.open_menu("build")
            elif result == "plant":
                self.open_menu("seed")

            return result  # Добавляем возврат результата

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
            self.close_all()
            return None
        return None


    def draw(self, screen, camera_x, harvest, products):
        if self.active_menu:

            if self.active_menu == "wheel":
                self.menus[self.active_menu].draw(screen, camera_x)
            elif self.active_menu == "market":
                self.menus[self.active_menu].update(self.menus[self.active_menu].coins, harvest, products)
                self.menus[self.active_menu].draw(screen)
            elif self.active_menu == "build":
                self.menus[self.active_menu].draw(screen, harvest, products)
            else:
                self.menus[self.active_menu].draw(screen)

    def update(self, coins, harvest, products, level):
        self.menus["seed"].update(coins, level)
        self.menus["build"].update(coins, level)
        self.menus["market"].update(coins, harvest, products)