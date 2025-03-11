# ui.py
import pygame
import math
import images
from config import SCREEN_HEIGHT, WHITE, BLACK, GRAY, GREEN, SEEDS
from translations import get_text

from save_load import list_saves  # Импортируем list_saves

class Menu:
    @staticmethod
    def is_save_exists():
        # Проверяем, есть ли хотя бы один сохраненный слот в папке saves
        return len(list_saves()) > 0

    def __init__(self, font):
        self.font = font
        self.current_language = "en"
        self.options = [
            {"text": get_text("New Game", self.current_language), "color": WHITE, "action": "new_game"},
            {"text": get_text("Continue", self.current_language), "color": GRAY if not self.is_save_exists() else WHITE,
             "action": "continue"},
            {"text": get_text("Settings", self.current_language), "color": WHITE, "action": "settings"},
            {"text": get_text("Exit", self.current_language), "color": WHITE, "action": "exit"}
        ]
        self.settings_open = False

    def draw(self, screen):
        screen_width = screen.get_width()
        screen_height = SCREEN_HEIGHT

        background = images.GAME_IMAGES["background_menu"]
        bg_width = background.get_width()
        bg_height = background.get_height()

        if bg_height != screen_height:
            scale_factor = screen_height / bg_height
            new_width = int(bg_width * scale_factor)
            background = pygame.transform.scale(background, (new_width, screen_height))
            bg_width = new_width
        else:
            background = background

        if bg_width < screen_width:
            scaled_background = pygame.transform.scale(background, (screen_width, screen_height))
            screen.blit(scaled_background, (0, 0))
        else:
            clip_x = (bg_width - screen_width) // 2
            clip_width = screen_width
            clipped_background = pygame.Surface((clip_width, screen_height))
            clipped_background.blit(background, (0, 0), (clip_x, 0, clip_width, screen_height))
            screen.blit(clipped_background, (0, 0))

        if not self.settings_open:
            for i, option in enumerate(self.options):
                text_surface = self.font.render(option["text"], True, option["color"])
                text_rect = text_surface.get_rect(center=(screen_width // 2, 100 + i * 60))
                screen.blit(text_surface, text_rect)
        else:
            settings_title = self.font.render(get_text("Settings", self.current_language), True, WHITE)
            screen.blit(settings_title, settings_title.get_rect(center=(screen_width // 2, 50)))

            language_text = self.font.render(get_text("Language", self.current_language), True, WHITE)
            screen.blit(language_text, language_text.get_rect(center=(screen_width // 2, 120)))

            ru_rect = pygame.Rect(screen_width // 2 - 100, 180, 80, 40)
            en_rect = pygame.Rect(screen_width // 2 + 20, 180, 80, 40)
            pygame.draw.rect(screen, GREEN if self.current_language == "ru" else WHITE, ru_rect)
            pygame.draw.rect(screen, GREEN if self.current_language == "en" else WHITE, en_rect)
            ru_text = self.font.render(get_text("Russian", self.current_language), True, BLACK)
            en_text = self.font.render(get_text("English", self.current_language), True, BLACK)
            screen.blit(ru_text, ru_text.get_rect(center=ru_rect.center))
            screen.blit(en_text, en_text.get_rect(center=en_rect.center))

            back_rect = pygame.Rect(screen_width // 2 - 50, 240, 100, 40)
            pygame.draw.rect(screen, WHITE, back_rect)
            back_text = self.font.render("Назад", True, BLACK)
            screen.blit(back_text, back_text.get_rect(center=back_rect.center))

    def handle_event(self, event, mx, my):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if not self.settings_open:
                for i, option in enumerate(self.options):
                    text_rect = self.font.render(option["text"], True, option["color"]).get_rect(
                        center=(pygame.display.get_surface().get_width() // 2, 100 + i * 60)
                    )
                    if text_rect.collidepoint(mx, my) and option["color"] != GRAY:
                        if option["action"] == "settings":
                            self.settings_open = True
                            return None
                        return option["action"]
            else:
                ru_rect = pygame.Rect(pygame.display.get_surface().get_width() // 2 - 100, 180, 80, 40)
                en_rect = pygame.Rect(pygame.display.get_surface().get_width() // 2 + 20, 180, 80, 40)
                back_rect = pygame.Rect(pygame.display.get_surface().get_width() // 2 - 50, 240, 100, 40)

                if ru_rect.collidepoint(mx, my):
                    self.current_language = "ru"
                    self.options = [
                        {"text": get_text("New Game", "ru"), "color": WHITE, "action": "new_game"},
                        {"text": get_text("Continue", "ru"), "color": GRAY if not self.is_save_exists() else WHITE,
                         "action": "continue"},
                        {"text": get_text("Settings", "ru"), "color": WHITE, "action": "settings"},
                        {"text": get_text("Exit", "ru"), "color": WHITE, "action": "exit"}
                    ]
                    self.settings_open = False
                    return None
                elif en_rect.collidepoint(mx, my):
                    self.current_language = "en"
                    self.options = [
                        {"text": get_text("New Game", "en"), "color": WHITE, "action": "new_game"},
                        {"text": get_text("Continue", "en"), "color": GRAY if not self.is_save_exists() else WHITE,
                         "action": "continue"},
                        {"text": get_text("Settings", "en"), "color": WHITE, "action": "settings"},
                        {"text": get_text("Exit", "en"), "color": WHITE, "action": "exit"}
                    ]
                    self.settings_open = False
                    return None
                elif back_rect.collidepoint(mx, my):
                    self.settings_open = False
                    return None
        return None
def draw_wheel(screen, game_context, camera_x, fonts):
    if not game_context.get("wheel_open"):
        return

    center_x = game_context["wheel_x"] - camera_x
    center_y = game_context["wheel_y"]
    radius = 50
    pygame.draw.circle(screen, (211, 211, 211), (int(center_x), int(center_y)), radius, 2)

    build_angle = 90
    plant_angle = 270

    build_endpoint = (
        center_x + radius * math.cos(math.radians(build_angle)),
        center_y - radius * math.sin(math.radians(build_angle))
    )
    plant_endpoint = (
        center_x + radius * math.cos(math.radians(plant_angle)),
        center_y - radius * math.sin(math.radians(plant_angle))
    )

    font = fonts["desc_font_large"]
    build_text = font.render(get_text("Construction", game_context["language"]), True, (0, 0, 255))
    plant_text = font.render(get_text("Planting", game_context["language"]), True, (0, 255, 0))

    screen.blit(build_text, (build_endpoint[0] + 5, build_endpoint[1] - 10))
    screen.blit(plant_text, (plant_endpoint[0] - plant_text.get_width() - 5, plant_endpoint[1] - 10))

    selected_action = game_context.get("selected_action")
    if selected_action:
        if selected_action == "build":
            pygame.draw.circle(screen, (0, 0, 255), (int(center_x), int(center_y)), 5)
        elif selected_action == "plant":
            pygame.draw.circle(screen, (0, 255, 0), (int(center_x), int(center_y)), 5)

def draw_seed_menu(game_context, coins, fonts, selected_seed=None, level=1):
    screen = game_context["screen"]
    language = game_context["language"]
    screen_width = screen.get_width()
    font = fonts["title_font_large"]
    tooltip_font = fonts["desc_font_large"]
    small_font = fonts["desc_font_large"]

    menu_width, menu_height = 200, SCREEN_HEIGHT
    pygame.draw.rect(screen, (211, 211, 211), (screen_width - menu_width, 0, menu_width, menu_height))
    pygame.draw.rect(screen, GRAY, (screen_width - menu_width, 0, menu_width, menu_height), 2)

    close_rect = pygame.Rect(screen_width - 30, 10, 20, 20)
    pygame.draw.rect(screen, (173, 216, 230), close_rect)
    close_text = small_font.render("×", True, BLACK)
    screen.blit(close_text, close_text.get_rect(center=close_rect.center))

    seeds_per_row = 2
    seed_width = 90
    seed_height = 60
    start_x = screen_width - 190
    start_y = 60

    available_seeds = [seed for seed in SEEDS if seed["unlock_level"] <= level]

    tooltip = None
    seed_lang = selected_seed.get("language", language) if selected_seed else language
    for i, seed in enumerate(available_seeds):
        row = i // seeds_per_row
        col = i % seeds_per_row
        rect_x = start_x + col * seed_width
        rect_y = start_y + row * seed_height
        rect = pygame.Rect(rect_x, rect_y, 80, 50)
        color = (173, 216, 230) if coins >= seed["cost"] else GRAY
        is_hovered = rect.collidepoint(pygame.mouse.get_pos())
        is_active = selected_seed and seed["name"] == selected_seed["name"]
        menu_color = color
        if is_active:
            menu_color = GREEN
        elif is_hovered:
            menu_color = WHITE
            tooltip = (
                f"{get_text('Name', language=seed_lang)}: {get_text(seed['name'], language=seed_lang)}\n"
                f"{get_text('Cost', language=seed_lang)}: {seed['cost']}\n"
                f"{get_text('Growth Time', language=seed_lang)}: {seed['ripening_time_minutes']} {get_text('min', language=seed_lang)}\n"
                f"{get_text('Watering Interval', language=seed_lang)}: {seed['watering_interval_minutes']} {get_text('min', language=seed_lang)}\n"
                f"{get_text('Harvest Yield', language=seed_lang)}: {seed['harvest_yield']}"
            )
        pygame.draw.rect(screen, menu_color, rect)
        text = font.render(get_text(seed["name"], language=seed_lang)[0], True, BLACK)
        text_rect = text.get_rect(center=(rect_x + 40, rect_y + 25))
        screen.blit(text, text_rect)

    if tooltip:
        tooltip_lines = tooltip.split('\n')
        tooltip_height = len(tooltip_lines) * 20 + 10
        tooltip_width = 0
        for line in tooltip_lines:
            if line.startswith(get_text('Cost', language=seed_lang)) or line.startswith(
                    get_text('Harvest Yield', language=seed_lang)):
                parts = line.split(': ', 1)
                if len(parts) == 2:
                    number = parts[1]
                    text_part = f"{parts[0]}: "
                    line_width = tooltip_font.size(text_part)[0] + tooltip_font.size(number)[0] + images.GAME_IMAGES[
                        "coin_menu"].get_width() + 5
                else:
                    line_width = tooltip_font.size(line)[0] + images.GAME_IMAGES["coin_menu"].get_width() + 5
            else:
                line_width = tooltip_font.size(line)[0]
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
            if line.startswith(get_text('Cost', language=seed_lang)) or line.startswith(
                    get_text('Harvest Yield', language=seed_lang)):
                parts = line.split(': ', 1)
                if len(parts) == 2:
                    text_part, number = parts
                    text_surface = tooltip_font.render(f"{text_part}: ", True, WHITE)
                    number_surface = tooltip_font.render(number, True, WHITE)
                    coin_image = images.GAME_IMAGES["coin_menu"]
                    text_height = text_surface.get_height()
                    coin_height = coin_image.get_height()
                    y_offset = (text_height - coin_height) // 2
                    screen.blit(text_surface, (tooltip_rect.x + 5, tooltip_rect.y + 5 + i * 20))
                    screen.blit(number_surface, (
                    tooltip_rect.x + 5 + tooltip_font.size(f"{text_part}: ")[0], tooltip_rect.y + 5 + i * 20))
                    screen.blit(coin_image, (tooltip_rect.x + 5 + tooltip_font.size(f"{text_part}: {number}")[0] + 5,
                                             tooltip_rect.y + 5 + i * 20 + y_offset))
            else:
                text_surface = tooltip_font.render(line, True, WHITE)
                screen.blit(text_surface, (tooltip_rect.x + 5, tooltip_rect.y + 5 + i * 20))

def draw_build_menu(game_context, coins, fonts, current_index=0, build_type="functional"):
    screen = game_context["screen"]
    language = game_context["language"]
    screen_width = screen.get_width()
    font = fonts["title_font_medium"]
    tooltip_font = fonts["desc_font_small"]
    small_font = fonts["desc_font_large"]

    build_options = [
        {"text": get_text("Bed", language=language), "cost": 10, "action": "new", "type": "functional",
         "description": get_text("Simple bed for planting plants", language=language),
         "cost_text": get_text("Cost: 10 coins", language=language)},
    ]

    filtered_options = [opt for opt in build_options if opt["type"] == build_type]

    menu_width, menu_height = 240, SCREEN_HEIGHT

    pygame.draw.rect(screen, (211, 211, 211), (screen_width - menu_width, 0, menu_width, menu_height))
    pygame.draw.rect(screen, GRAY, (screen_width - menu_width, 0, menu_width, menu_height), 2)

    close_rect = pygame.Rect(screen_width - 30, 10, 20, 20)
    pygame.draw.rect(screen, (173, 216, 230), close_rect)
    close_text = small_font.render("×", True, BLACK)
    screen.blit(close_text, close_text.get_rect(center=close_rect.center))

    action_width = (menu_width - 30) // 2
    move_rect = pygame.Rect(screen_width - menu_width + 15, 60, action_width, 50)
    destroy_rect = pygame.Rect(screen_width - action_width - 15, 60, action_width, 50)
    pygame.draw.rect(screen, (173, 216, 230) if coins >= 0 else GRAY, move_rect)
    pygame.draw.rect(screen, (173, 216, 230) if coins >= 0 else GRAY, destroy_rect)
    move_text = small_font.render(get_text("Move", language=language), True, BLACK)
    destroy_text = small_font.render(get_text("Destroy", language=language), True, (255, 0, 0))
    screen.blit(move_text, move_text.get_rect(center=(move_rect.x + action_width // 2, move_rect.y + 25)))
    screen.blit(destroy_text, destroy_text.get_rect(center=(destroy_rect.x + action_width // 2, destroy_rect.y + 25)))

    build_rect = None
    left_arrow_rect = None
    right_arrow_rect = None
    if filtered_options:
        current_build = filtered_options[current_index]
        build_rect = pygame.Rect(screen_width - menu_width + 15, 120, menu_width - 30, 200)
        pygame.draw.rect(screen, (173, 216, 230), build_rect)

        image_zone_width = 64
        image_zone_height = 64
        image_zone_x = build_rect.x + (build_rect.width - image_zone_width) // 2
        image_zone_y = build_rect.y + 20
        pygame.draw.rect(screen, (255, 255, 255), (image_zone_x, image_zone_y, image_zone_width, image_zone_height), 2)
        bed_image = images.GAME_IMAGES["bed_wet"]
        scale_factor = min(image_zone_width / bed_image.get_width(), image_zone_height / bed_image.get_height())
        scaled_width = int(bed_image.get_width() * scale_factor)
        scaled_height = int(bed_image.get_height() * scale_factor)
        scaled_bed_image = pygame.transform.scale(bed_image, (scaled_width, scaled_height))
        image_x = image_zone_x + (image_zone_width - scaled_width) // 2
        image_y = image_zone_y + (image_zone_height - scaled_height) // 2
        screen.blit(scaled_bed_image, (image_x, image_y))

        title_text = tooltip_font.render(current_build["text"], True, BLACK)
        title_x = build_rect.x + (build_rect.width - title_text.get_width()) // 2
        title_y = image_zone_y + image_zone_height + 20
        screen.blit(title_text, (title_x, title_y))

        coin_image = images.GAME_IMAGES["coin_menu"]
        cost_value = current_build["cost"]
        cost_text = tooltip_font.render(str(cost_value), True, BLACK)
        total_width = cost_text.get_width() + coin_image.get_width() + 5
        cost_x = build_rect.x + (build_rect.width - total_width) // 2
        cost_y = title_y + title_text.get_height() + 10
        screen.blit(cost_text, (cost_x, cost_y))
        screen.blit(coin_image, (cost_x + cost_text.get_width() + 5, cost_y))

        description = current_build["description"]
        words = description.split()
        lines = []
        current_line = ""
        for word in words:
            if tooltip_font.size(current_line + " " + word)[0] <= menu_width - 60:
                current_line += (" " if current_line else "") + word
            else:
                lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)

        description_start_y = cost_y + tooltip_font.get_height() + 10
        for i, line in enumerate(lines[:4]):
            desc_text = tooltip_font.render(line, True, BLACK)
            screen.blit(desc_text, (build_rect.x + 15, description_start_y + i * 20))

        left_arrow_rect = pygame.Rect(build_rect.x + 10, image_zone_y + (image_zone_height - 40) // 2, 40, 40)
        right_arrow_rect = pygame.Rect(build_rect.right - 50, image_zone_y + (image_zone_height - 40) // 2, 40, 40)
        pygame.draw.polygon(screen, WHITE, [(left_arrow_rect.x + 10, left_arrow_rect.centery),
                                            (left_arrow_rect.x + 30, left_arrow_rect.centery - 10),
                                            (left_arrow_rect.x + 30, left_arrow_rect.centery + 10)])
        pygame.draw.polygon(screen, WHITE, [(right_arrow_rect.x + 30, right_arrow_rect.centery),
                                            (right_arrow_rect.x + 10, right_arrow_rect.centery - 10),
                                            (right_arrow_rect.x + 10, right_arrow_rect.centery + 10)])

    building_types = [
        {"text": "Функциональные", "type": "functional", "color": GREEN},
        {"text": "Декоративные", "type": "decorative", "color": (255, 165, 0)}
    ]
    type_height = 40
    type_y = 10
    for i, btype in enumerate(building_types):
        type_rect = pygame.Rect(screen_width - menu_width + 15 + i * ((menu_width - 30) // 2), type_y,
                                (menu_width - 30) // 2, type_height)
        pygame.draw.rect(screen, btype["color"], type_rect)
        type_text = small_font.render(btype["text"][0], True, BLACK)
        screen.blit(type_text, type_text.get_rect(
            center=(type_rect.x + type_rect.width // 2, type_rect.y + type_rect.height // 2)))

    return {
        "close": close_rect,
        "move": move_rect,
        "destroy": destroy_rect,
        "new": build_rect if build_rect else pygame.Rect(0, 0, 0, 0),
        "left_arrow": left_arrow_rect if left_arrow_rect else pygame.Rect(0, 0, 0, 0),
        "right_arrow": right_arrow_rect if right_arrow_rect else pygame.Rect(0, 0, 0, 0),
        "building_types": [(btype["type"], rect) for i, btype in enumerate(building_types) for rect in [
            pygame.Rect(screen_width - menu_width + 15 + i * ((menu_width - 30) // 2), type_y, (menu_width - 30) // 2,
                        type_height)]]
    }

def confirm_dialog(screen, message, fonts):
    font = fonts["title_font_medium"]
    dialog_running = True
    while dialog_running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                yes_rect = pygame.Rect(screen.get_width() // 2 - 100, SCREEN_HEIGHT // 2 + 20, 80, 40)
                no_rect = pygame.Rect(screen.get_width() // 2 + 20, SCREEN_HEIGHT // 2 + 20, 80, 40)
                if yes_rect.collidepoint(mx, my):
                    return True
                elif no_rect.collidepoint(mx, my):
                    return False

        screen.fill(BLACK)
        text = font.render(message, True, WHITE)
        text_rect = text.get_rect(center=(screen.get_width() // 2, SCREEN_HEIGHT // 2 - 20))
        screen.blit(text, text_rect)
        pygame.draw.rect(screen, GREEN, (screen.get_width() // 2 - 100, SCREEN_HEIGHT // 2 + 20, 80, 40))
        pygame.draw.rect(screen, GRAY, (screen.get_width() // 2 + 20, SCREEN_HEIGHT // 2 + 20, 80, 40))
        yes_text = font.render("Да", True, WHITE)
        no_text = font.render("Нет", True, WHITE)
        screen.blit(yes_text, yes_text.get_rect(center=(screen.get_width() // 2 - 60, SCREEN_HEIGHT // 2 + 40)))
        screen.blit(no_text, no_text.get_rect(center=(screen.get_width() // 2 + 60, SCREEN_HEIGHT // 2 + 40)))
        pygame.display.flip()
        pygame.time.Clock().tick(60)

def draw_market_menu(game_context, coins, harvest, products, fonts):
    screen = game_context["screen"]
    language = game_context["language"]
    screen_width = screen.get_width()
    font = fonts["title_font_medium"]
    small_font = fonts["desc_font_large"]

    menu_width, menu_height = 400, 250
    menu_x = (screen_width - menu_width) // 2
    menu_y = (SCREEN_HEIGHT - menu_height) // 2
    pygame.draw.rect(screen, (211, 211, 211), (menu_x, menu_y, menu_width, menu_height))
    pygame.draw.rect(screen, GRAY, (menu_x, menu_y, menu_width, menu_height), 2)

    close_rect = pygame.Rect(menu_x + menu_width - 30, menu_y + 10, 20, 20)
    pygame.draw.rect(screen, (173, 216, 230), close_rect)
    close_text = small_font.render("×", True, BLACK)
    screen.blit(close_text, close_text.get_rect(center=close_rect.center))

    harvest_image = images.GAME_IMAGES["harvest"]
    product_image = images.GAME_IMAGES["product"]
    coin_image = images.GAME_IMAGES["coin_menu"]

    harvest_count = game_context["market_harvest_to_sell"]
    harvest_rect = pygame.Rect(menu_x + 150, menu_y + 70, 50, 40)
    pygame.draw.rect(screen, WHITE, harvest_rect)
    harvest_text = small_font.render(str(harvest_count), True, BLACK)
    screen.blit(harvest_text, (harvest_rect.x + (harvest_rect.width - harvest_text.get_width()) // 2, harvest_rect.y + 10))
    screen.blit(harvest_image, (menu_x + 20, menu_y + 70))

    harvest_increase = pygame.Rect(menu_x + 205, menu_y + 70, 30, 20)
    harvest_decrease = pygame.Rect(menu_x + 205, menu_y + 90, 30, 20)
    pygame.draw.rect(screen, GREEN, harvest_increase)
    pygame.draw.rect(screen, GREEN, harvest_decrease)
    screen.blit(small_font.render("↑", True, BLACK), harvest_increase.move(10, 2))
    screen.blit(small_font.render("↓", True, BLACK), harvest_decrease.move(10, 2))

    products_count = game_context["market_products_to_sell"]
    products_rect = pygame.Rect(menu_x + 150, menu_y + 130, 50, 40)
    pygame.draw.rect(screen, WHITE, products_rect)
    products_text = small_font.render(str(products_count), True, BLACK)
    screen.blit(products_text, (products_rect.x + (products_rect.width - products_text.get_width()) // 2, products_rect.y + 10))
    screen.blit(product_image, (menu_x + 20, menu_y + 130))

    products_increase = pygame.Rect(menu_x + 205, menu_y + 130, 30, 20)
    products_decrease = pygame.Rect(menu_x + 205, menu_y + 150, 30, 20)
    pygame.draw.rect(screen, GREEN, products_increase)
    pygame.draw.rect(screen, GREEN, products_decrease)
    screen.blit(small_font.render("↑", True, BLACK), products_increase.move(10, 2))
    screen.blit(small_font.render("↓", True, BLACK), products_decrease.move(10, 2))

    total_value = (game_context["market_harvest_to_sell"] * 2) + (game_context["market_products_to_sell"] * 15)
    screen.blit(coin_image, (menu_x + 150, menu_y + 200))
    value_text = small_font.render(str(total_value), True, BLACK)
    screen.blit(value_text, (menu_x + 190, menu_y + 202))

    sell_rect = pygame.Rect(menu_x + 150, menu_y + 230, 100, 40)
    pygame.draw.rect(screen, GREEN, sell_rect)
    sell_text = small_font.render(get_text("Sell", language), True, BLACK)
    screen.blit(sell_text, sell_text.get_rect(center=sell_rect.center))

    return {
        "close": close_rect,
        "harvest_increase": harvest_increase, "harvest_decrease": harvest_decrease,
        "products_increase": products_increase, "products_decrease": products_decrease,
        "sell": sell_rect
    }