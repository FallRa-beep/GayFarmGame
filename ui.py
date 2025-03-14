import pygame
import math
import images
from config import SCREEN_HEIGHT, WHITE, BLACK, GRAY, GREEN, SEEDS
from translations import get_text

class Menu:
    @staticmethod
    def is_save_exists():
        from save_load import list_saves
        saves = list_saves()
        return len(saves) > 0

    def __init__(self):
        self.font = pygame.font.Font(None, 36)
        self.current_language = "en"
        self.button_normal = images.GAME_IMAGES.get("button_normal")
        self.button_hover = images.GAME_IMAGES.get("button_hover")
        if not self.button_normal or not self.button_hover:

            self.button_normal = pygame.Surface((200, 60))
            self.button_normal.fill(GRAY)
            self.button_hover = pygame.Surface((200, 60))
            self.button_hover.fill(WHITE)
        self.close_button = images.GAME_IMAGES.get("close_button")
        self.close_hover = images.GAME_IMAGES.get("close_button_hover")
        if not self.close_button:

            self.close_button = pygame.Surface((30, 30))
            self.close_button.fill((255, 0, 0))
        self.arrow_left = images.GAME_IMAGES.get("arrow_left")
        self.arrow_right = images.GAME_IMAGES.get("arrow_right")
        if not self.arrow_left or not self.arrow_right:

            self.arrow_left = pygame.Surface((20, 20))
            self.arrow_left.fill(GRAY)
            self.arrow_right = pygame.Surface((20, 20))
            self.arrow_right.fill(GRAY)
        else:
            self.arrow_left = pygame.transform.scale(self.arrow_left, (20, 20))
            self.arrow_right = pygame.transform.scale(self.arrow_right, (20, 20))

        has_saves = self.is_save_exists()
        self.options = [
            {"text": get_text("New Game", self.current_language), "image_normal": self.button_normal, "image_hover": self.button_hover, "color": WHITE, "action": "new_game"},
            {"text": get_text("Continue", self.current_language), "image_normal": self.button_normal, "image_hover": self.button_hover, "color": WHITE if has_saves else GRAY, "action": "continue"},
            {"text": get_text("Load", self.current_language), "image_normal": self.button_normal, "image_hover": self.button_hover, "color": WHITE if has_saves else GRAY, "action": "load"},
            {"text": get_text("Settings", self.current_language), "image_normal": self.button_normal, "image_hover": self.button_hover, "color": WHITE, "action": "settings"},
        ]
        self.settings_open = False
        self.option_rects = []
        self.music_volume = 0.5
        self.sound_volume = 0.5
        self.dragging_music = False
        self.dragging_sound = False

        # Инициализация прямоугольников как None
        self.close_rect = None
        self.back_rect = None
        self.left_arrow_rect = None
        self.right_arrow_rect = None
        self.lang_switch_rect = None
        self.music_slider_rect = None
        self.sound_slider_rect = None
        self.slider_width = 200  # Ширина слайдера
        self.music_slider_x = 0  # Будет обновлено в update_rects
        self.sound_slider_x = 0  # Будет обновлено в update_rects

    def update_rects(self, screen):
        """Обновляет прямоугольники для элементов меню."""
        screen_width = screen.get_width()
        button_width, button_height = self.button_normal.get_size()
        base_x = screen_width * 2 // 3
        base_y = 50
        spacing = 80
        arrow_size = (20, 20)
        slider_width = self.slider_width
        slider_height = 10
        knob_radius = 8

        if not self.settings_open:
            self.option_rects = []
            for i, _ in enumerate(self.options):
                button_x = base_x
                button_y = base_y + i * 80
                button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
                self.option_rects.append(button_rect)
            close_width, close_height = self.close_button.get_size()
            self.close_rect = pygame.Rect(screen_width - close_width - 10, 10, close_width, close_height)
        else:
            self.back_rect = pygame.Rect(screen_width - 32 - 10, 10, 32, 32)

            # Прямоугольники для переключения языка
            lang_text = "English" if self.current_language == "en" else "Russian"
            lang_switch_text = self.font.render(lang_text, True, WHITE)
            text_width = lang_switch_text.get_width()
            padding = 20
            lang_switch_width = text_width + padding
            lang_switch_height = button_height
            left_arrow_x = base_x + button_width + 40
            self.left_arrow_rect = pygame.Rect(left_arrow_x, base_y + spacing + (button_height - arrow_size[1]) // 2,
                                               arrow_size[0], arrow_size[1])
            gap = 10
            lang_switch_x = left_arrow_x + arrow_size[0] + gap
            self.lang_switch_rect = pygame.Rect(lang_switch_x, base_y + spacing, lang_switch_width, lang_switch_height)
            right_arrow_x = lang_switch_x + lang_switch_width + gap
            self.right_arrow_rect = pygame.Rect(right_arrow_x, base_y + spacing + (button_height - arrow_size[1]) // 2,
                                                arrow_size[0], arrow_size[1])

            # Прямоугольники для слайдеров
            self.music_slider_x = base_x + button_width + 20
            music_slider_y = base_y + 2 * spacing + (button_height - slider_height) // 2
            self.music_slider_rect = pygame.Rect(self.music_slider_x - knob_radius, music_slider_y - knob_radius,
                                                 slider_width + 2 * knob_radius, slider_height + 2 * knob_radius)

            self.sound_slider_x = base_x + button_width + 20
            sound_slider_y = base_y + 3 * spacing + (button_height - slider_height) // 2
            self.sound_slider_rect = pygame.Rect(self.sound_slider_x - knob_radius, sound_slider_y - knob_radius,
                                                 slider_width + 2 * knob_radius, slider_height + 2 * knob_radius)

    def draw(self, screen):

        self.update_rects(screen)

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
        if bg_width < screen_width:
            scaled_background = pygame.transform.scale(background, (screen_width, screen_height))
            screen.blit(scaled_background, (0, 0))
        else:
            clip_x = (bg_width - screen_width) // 2
            clip_width = screen_width
            clipped_background = pygame.Surface((clip_width, screen_height))
            clipped_background.blit(background, (0, 0), (clip_x, 0, clip_width, screen_height))
            screen.blit(clipped_background, (0, 0))

        mx, my = pygame.mouse.get_pos()

        if not self.settings_open:
            for i, option in enumerate(self.options):
                button_rect = self.option_rects[i]
                image_to_draw = option["image_hover"] if button_rect.collidepoint(mx, my) and option["color"] != GRAY else option["image_normal"]
                screen.blit(image_to_draw, (button_rect.x, button_rect.y))
                text_surface = self.font.render(option["text"], True, option["color"])
                text_rect = text_surface.get_rect(center=button_rect.center)
                screen.blit(text_surface, text_rect)

            close_image = self.close_hover if self.close_rect.collidepoint(mx, my) else self.close_button
            screen.blit(close_image, (self.close_rect.x, self.close_rect.y))

        else:
            back_button = images.GAME_IMAGES.get("return")
            back_hover = images.GAME_IMAGES.get("return_hover")
            if not back_button:
                back_button = pygame.Surface((32, 32))
                back_button.fill(GRAY)
            if not back_hover:
                back_hover = back_button
            image_to_draw = back_hover if self.back_rect.collidepoint(mx, my) else back_button
            screen.blit(image_to_draw, (self.back_rect.x, self.back_rect.y))

            button_width, button_height = self.button_normal.get_size()
            base_x = screen_width * 2 // 3
            base_y = 50
            spacing = 80

            settings_rect = pygame.Rect(base_x, base_y, button_width, button_height)
            screen.blit(self.button_normal, (settings_rect.x, settings_rect.y))
            settings_title = self.font.render(get_text("Settings", self.current_language), True, WHITE)
            settings_text_rect = settings_title.get_rect(center=settings_rect.center)
            screen.blit(settings_title, settings_text_rect)

            language_rect = pygame.Rect(base_x, base_y + spacing, button_width, button_height)
            screen.blit(self.button_normal, (language_rect.x, language_rect.y))
            language_title = self.font.render(get_text("Language", self.current_language), True, WHITE)
            language_text_rect = language_title.get_rect(center=language_rect.center)
            screen.blit(language_title, language_text_rect)

            lang_text = "English" if self.current_language == "en" else "Russian"
            lang_switch_text = self.font.render(lang_text, True, WHITE)
            # Заменяем условие на постоянное использование self.button_normal
            lang_switch_image = self.button_normal  # Убрано активное состояние
            lang_switch_image = pygame.transform.scale(lang_switch_image,
                                                       (self.lang_switch_rect.width, self.lang_switch_rect.height))
            screen.blit(lang_switch_image, (self.lang_switch_rect.x, self.lang_switch_rect.y))
            lang_switch_text_rect = lang_switch_text.get_rect(center=self.lang_switch_rect.center)
            screen.blit(lang_switch_text, lang_switch_text_rect)

            screen.blit(self.arrow_left, self.left_arrow_rect)
            screen.blit(self.arrow_right, self.right_arrow_rect)

            music_rect = pygame.Rect(base_x, base_y + 2 * spacing, button_width, button_height)
            screen.blit(self.button_normal, (music_rect.x, music_rect.y))
            music_title = self.font.render(get_text("Music Volume", self.current_language), True, WHITE)
            music_text_rect = music_title.get_rect(center=music_rect.center)
            screen.blit(music_title, music_text_rect)
            pygame.draw.rect(screen, GRAY, (self.music_slider_x, music_rect.y + (button_height - 10) // 2, self.slider_width, 10))
            knob_x = self.music_slider_x + int(self.music_volume * self.slider_width)
            pygame.draw.circle(screen, BLACK, (knob_x, music_rect.y + (button_height - 10) // 2 + 5), 8)


            sound_rect = pygame.Rect(base_x, base_y + 3 * spacing, button_width, button_height)
            screen.blit(self.button_normal, (sound_rect.x, sound_rect.y))
            sound_title = self.font.render(get_text("Sound Volume", self.current_language), True, WHITE)
            sound_text_rect = sound_title.get_rect(center=sound_rect.center)
            screen.blit(sound_title, sound_text_rect)
            pygame.draw.rect(screen, GRAY, (self.sound_slider_x, sound_rect.y + (button_height - 10) // 2, self.slider_width, 10))
            knob_x = self.sound_slider_x + int(self.sound_volume * self.slider_width)
            pygame.draw.circle(screen, BLACK, (knob_x, sound_rect.y + (button_height - 10) // 2 + 5), 8)



    def handle_event(self, event, mx, my, screen):
        self.update_rects(screen)  # Обновляем прямоугольники перед обработкой событий

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if not self.settings_open:
                if self.close_rect and self.close_rect.collidepoint(mx, my):
                    return "exit"
                for i, option in enumerate(self.options):
                    if self.option_rects[i].collidepoint(mx, my) and option["color"] != GRAY:
                        if option["action"] == "settings":
                            self.settings_open = True
                            return None
                        return option["action"]
            else:
                if self.back_rect and self.back_rect.collidepoint(mx, my):
                    self.settings_open = False
                    return None
                if self.left_arrow_rect and self.left_arrow_rect.collidepoint(mx, my):
                    self.current_language = "ru" if self.current_language == "en" else "en"
                    has_saves = self.is_save_exists()
                    self.options = [
                        {"text": get_text("New Game", self.current_language), "image_normal": self.button_normal,
                         "image_hover": self.button_hover, "color": WHITE, "action": "new_game"},
                        {"text": get_text("Continue", self.current_language), "image_normal": self.button_normal,
                         "image_hover": self.button_hover, "color": WHITE if has_saves else GRAY, "action": "continue"},
                        {"text": get_text("Load", self.current_language), "image_normal": self.button_normal,
                         "image_hover": self.button_hover, "color": WHITE if has_saves else GRAY, "action": "load"},
                        {"text": get_text("Settings", self.current_language), "image_normal": self.button_normal,
                         "image_hover": self.button_hover, "color": WHITE, "action": "settings"},
                    ]
                    return None
                elif self.right_arrow_rect and self.right_arrow_rect.collidepoint(mx, my):
                    self.current_language = "en" if self.current_language == "ru" else "ru"
                    has_saves = self.is_save_exists()
                    self.options = [
                        {"text": get_text("New Game", self.current_language), "image_normal": self.button_normal,
                         "image_hover": self.button_hover, "color": WHITE, "action": "new_game"},
                        {"text": get_text("Continue", self.current_language), "image_normal": self.button_normal,
                         "image_hover": self.button_hover, "color": WHITE if has_saves else GRAY, "action": "continue"},
                        {"text": get_text("Load", self.current_language), "image_normal": self.button_normal,
                         "image_hover": self.button_hover, "color": WHITE if has_saves else GRAY, "action": "load"},
                        {"text": get_text("Settings", self.current_language), "image_normal": self.button_normal,
                         "image_hover": self.button_hover, "color": WHITE, "action": "settings"},
                    ]
                    return None
                if self.music_slider_rect.collidepoint(mx, my):

                    self.dragging_music = True
                elif self.sound_slider_rect.collidepoint(mx, my):

                    self.dragging_sound = True

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:

            self.dragging_music = False
            self.dragging_sound = False

        elif event.type == pygame.MOUSEMOTION:
            if self.dragging_music:
                new_volume = max(0.0, min(1.0, (mx - self.music_slider_x) / self.slider_width))
                if new_volume != self.music_volume:  # Избегаем избыточных обновлений
                    self.music_volume = new_volume
                    pygame.mixer.music.set_volume(self.music_volume)

            elif self.dragging_sound:
                new_volume = max(0.0, min(1.0, (mx - self.sound_slider_x) / self.slider_width))
                if new_volume != self.sound_volume:  # Избегаем избыточных обновлений
                    self.sound_volume = new_volume


        return None

# Оставляем остальные функции в ui.py без изменений


# ui.py (фрагмент draw_wheel)
def draw_wheel(screen, game_context, camera_x):
    """Отрисовка колеса действий в месте клика."""
    if not game_context.get("wheel_open"):
        return

    center_x = game_context["wheel_x"] - camera_x  # Используем координаты клика, преобразованные в экранные
    center_y = game_context["wheel_y"]  # Используем экранные Y координаты клика
    radius = 50
    pygame.draw.circle(screen, (211, 211, 211), (int(center_x), int(center_y)), radius, 2)

    # "Строительство" справа (0 градусов), "Посадки" слева (180 градусов)
    build_angle = 90  # Справа (0 градусов)
    plant_angle = 270  # Слева (180 градусов)

    build_endpoint = (
        center_x + radius * math.cos(math.radians(build_angle)),
        center_y - radius * math.sin(math.radians(build_angle))
    )
    plant_endpoint = (
        center_x + radius * math.cos(math.radians(plant_angle)),
        center_y - radius * math.sin(math.radians(plant_angle))
    )

    font = pygame.font.Font(None, 24)  # Определяем font здесь для использования
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

def draw_seed_menu(game_context, coins, selected_seed=None, level=1):
    screen = game_context["screen"]
    language = game_context["language"]
    screen_width = screen.get_width()
    font = pygame.font.Font(None, 48)  # Определяем font здесь
    tooltip_font = pygame.font.Font(None, 24)
    small_font = pygame.font.Font(None, 24)

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


def draw_build_menu(game_context, coins, current_index=0, build_type="functional"):
    screen = game_context["screen"]
    language = game_context["language"]
    screen_width = screen.get_width()
    font = pygame.font.Font(None, 48)  # Определяем font здесь
    tooltip_font = pygame.font.Font(None, 20)
    small_font = pygame.font.Font(None, 24)

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


def confirm_dialog(screen, message):
    font = pygame.font.Font(None, 36)
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

def draw_market_menu(game_context, coins, harvest, products):
    screen = game_context["screen"]
    language = game_context["language"]
    screen_width = screen.get_width()
    font = pygame.font.Font(None, 36)
    small_font = pygame.font.Font(None, 24)

    menu_width, menu_height = 400, 250
    menu_x = (screen_width - menu_width) // 2
    menu_y = (SCREEN_HEIGHT - menu_height) // 2
    pygame.draw.rect(screen, (211, 211, 211), (menu_x, menu_y, menu_width, menu_height))
    pygame.draw.rect(screen, GRAY, (menu_x, menu_y, menu_width, menu_height), 2)

    close_rect = pygame.Rect(menu_x + menu_width - 30, menu_y + 10, 20, 20)
    pygame.draw.rect(screen, (173, 216, 230), close_rect)
    close_text = small_font.render("×", True, BLACK)
    screen.blit(close_text, close_text.get_rect(center=close_rect.center))

    # Иконки без названий
    harvest_image = images.GAME_IMAGES["harvest"]
    product_image = images.GAME_IMAGES["product"]
    coin_image = images.GAME_IMAGES["coin_menu"]

    # Окошко для Урожая с двумя стрелочками
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

    # Окошко для Продуктов с двумя стрелочками
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

    # Иконка монетки вместо "Итого"
    total_value = (game_context["market_harvest_to_sell"] * 2) + (game_context["market_products_to_sell"] * 15)
    screen.blit(coin_image, (menu_x + 150, menu_y + 200))
    value_text = small_font.render(str(total_value), True, BLACK)
    screen.blit(value_text, (menu_x + 190, menu_y + 202))

    # Кнопка "Продать"
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