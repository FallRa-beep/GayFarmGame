import pygame
import win32gui
import win32con
import json
import os
import time
from config import SCREEN_HEIGHT, WHITE, GRAY, BLACK
from game_loop import game_loop
from ui import Menu
from save_load import load_game, save_game, list_saves
from translations import get_text
import images
import random
from notifications import NotificationManager
import fonts
from fonts import initialize_fonts



def load_menu_language():
    """Загружает язык меню из файла, если он существует, или возвращает 'en' по умолчанию."""
    if os.path.exists("menu_language.json"):
        with open("menu_language.json", "r", encoding="utf-8") as f:
            return json.load(f).get("language", "en")
    return "en"

def save_menu_language(language):
    """Сохраняет язык меню в файл."""
    with open("menu_language.json", "w", encoding="utf-8") as f:
        json_str = json.dumps({"language": language}, indent=4, ensure_ascii=False)
        f.write(json_str)

def show_save_dialog(screen, game_context, language, fonts=None):
    """Показывает диалоговое окно для сохранения игры."""
    font = fonts["title_font_large"]  # 36 pt
    small_font = fonts["title_font_medium"]
    clock = pygame.time.Clock()
    save_slot = None
    confirmation_text = None
    show_slot_selection = False  # Флаг для отображения слотов

    while True:
        screen.fill((0, 0, 0))  # Черный фон для диалога
        mx, my = pygame.mouse.get_pos()

        # Текст запроса
        display_text = confirmation_text if confirmation_text else get_text("Do you want to save the game?", language)
        text = font.render(display_text, True, WHITE)
        text_rect = text.get_rect(center=(screen.get_width() // 2, 50))
        screen.blit(text, text_rect)

        # Кнопки (отображаем только если не в режиме выбора слотов)
        buttons = []
        if not show_slot_selection:
            buttons = [
                {"text": get_text("Yes", language), "rect": None, "action": "yes"},
                {"text": get_text("No", language), "rect": None, "action": "no"},
                {"text": get_text("Cancel", language), "rect": None, "action": "cancel"}
            ]
            # Центрируем кнопки горизонтально
            button_width = 100
            button_spacing = 20
            total_width = len(buttons) * button_width + (len(buttons) - 1) * button_spacing
            start_x = (screen.get_width() - total_width) // 2
            for i, button in enumerate(buttons):
                button["rect"] = pygame.Rect(start_x + i * (button_width + button_spacing), 150, button_width, 50)

        # Список слотов для сохранения (отображаем только при show_slot_selection)
        slot_buttons = []
        if show_slot_selection:
            y_offset = 200
            max_slots = 3  # Ограничиваем до 3 слотов
            save_slots = list_saves()
            for i in range(max_slots):
                slot_name = f"Slot {i+1} (Empty)"  # По умолчанию пустой слот
                if i < len(save_slots):
                    slot_name = f"Slot {i+1} ({time.strftime('%Y-%m-%d %H:%M', time.localtime(save_slots[i]['timestamp']))})"
                rect = pygame.Rect((screen.get_width() - 340) // 2, y_offset + i * 60, 340, 50)  # Центрируем слоты
                slot_buttons.append({"text": slot_name, "rect": rect, "action": "save", "slot": save_slots[i]["filename"] if i < len(save_slots) else f"save_new_{i+1}.json"})

        # Отображаем кнопки
        for button in buttons:
            pygame.draw.rect(screen, GRAY if button["rect"].collidepoint(mx, my) else WHITE, button["rect"])
            text_surf = small_font.render(button["text"], True, BLACK)
            screen.blit(text_surf, (button["rect"].x + 10, button["rect"].y + 10))

        # Отображаем слоты
        for slot_button in slot_buttons:
            pygame.draw.rect(screen, GRAY if slot_button["rect"].collidepoint(mx, my) else WHITE, slot_button["rect"])
            text_surf = small_font.render(slot_button["text"], True, BLACK)
            screen.blit(text_surf, (slot_button["rect"].x + 10, slot_button["rect"].y + 10))

        pygame.display.flip()
        clock.tick(60)

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                return "exit"
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for button in buttons:
                    if button["rect"] and button["rect"].collidepoint(mx, my):
                        if button["action"] == "yes":
                            if save_slot:
                                # Создаём копию game_context без "screen"
                                save_context = {k: v for k, v in game_context.items() if k != "screen"}
                                save_game(game_context["player"], game_context["house"], game_context["objects"],
                                          game_context["camera_x"], game_context["harvest_count"],
                                          game_context["level"], game_context["coins"], game_context["harvest"],
                                          game_context["products"], language, save_context, save_slot)
                                return "main_menu"
                            else:
                                confirmation_text = get_text("Please select a slot!", language)
                                show_slot_selection = True  # Показываем слоты для выбора
                        elif button["action"] == "no":
                            return "main_menu"  # Возвращаемся в меню без сохранения
                        elif button["action"] == "cancel":
                            return None
                for slot_button in slot_buttons:
                    if slot_button["rect"].collidepoint(mx, my):
                        save_slot = slot_button["slot"]  # Только устанавливаем слот, сохранение при "Yes"
                        confirmation_text = get_text("Save to", language) + f" {save_slot}?"
                        show_slot_selection = False  # Возвращаемся к основным кнопкам после выбора

def show_load_dialog(screen, language, menu, fonts=None):
    font = pygame.font.Font(None, 36)
    small_font = pygame.font.Font(None, 24)
    clock = pygame.time.Clock()

    while True:
        # Загружаем фон из images
        background = images.GAME_IMAGES["background_menu"]
        bg_width = background.get_width()
        bg_height = background.get_height()
        if bg_height != SCREEN_HEIGHT:
            scale_factor = SCREEN_HEIGHT / bg_height
            new_width = int(bg_width * scale_factor)
            background = pygame.transform.scale(background, (new_width, SCREEN_HEIGHT))
            bg_width = new_width
        if bg_width < screen.get_width():
            scaled_background = pygame.transform.scale(background, (screen.get_width(), SCREEN_HEIGHT))
            screen.blit(scaled_background, (0, 0))
        else:
            clip_x = (bg_width - screen.get_width()) // 2
            clip_width = screen.get_width()
            clipped_background = pygame.Surface((clip_width, SCREEN_HEIGHT))
            clipped_background.blit(background, (0, 0), (clip_x, 0, clip_width, SCREEN_HEIGHT))
            screen.blit(clipped_background, (0, 0))

        mx, my = pygame.mouse.get_pos()

        # Текст запроса на уровне текста "New Game" из главного меню
        button_width = 340  # Ширина кнопок
        text = font.render(get_text("Select a save to load:", language), True, WHITE)
        text_x = screen.get_width() * 2 //3 + button_width // 2-70  # Центр группы кнопок
        text_rect = text.get_rect(center=(text_x, 50))  # На уровне "New Game"
        screen.blit(text, text_rect)

        # Кнопка возврата (в правом верхнем углу)
        back_button = images.GAME_IMAGES.get("return")
        back_hover = images.GAME_IMAGES.get("return_hover")
        if not back_button:

            back_button = pygame.Surface((32, 32))  # Заглушка
            back_button.fill(GRAY)
        if not back_hover:

            back_hover = back_button
        back_x = screen.get_width() - 32 - 10
        back_y = 10
        back_rect = pygame.Rect(back_x, back_y, 32, 32)
        back_image = back_hover if back_rect.collidepoint(mx, my) else back_button
        screen.blit(back_image, (back_x, back_y))

        # Список слотов для загрузки
        save_slots = list_saves()
        slot_buttons = []
        y_offset = 80  # Начинаем ниже текста
        max_slots = 3
        button_width, button_height = 340, 80  # Размер кнопок
        button_x = screen.get_width() * 2 // 3  # Расположение на 2/3 ширины
        for i in range(max_slots):
            slot_name = "Empty"
            if i < len(save_slots):
                slot_name = time.strftime('%Y-%m-%d %H:%M', time.localtime(save_slots[i]['timestamp']))
            rect = pygame.Rect(button_x, y_offset + i * 90, button_width, button_height)  # Интервал 90
            slot_buttons.append({"text": slot_name, "rect": rect, "action": "load", "slot": save_slots[i]["filename"] if i < len(save_slots) else None})

        # Рисуем кнопки слотов с фоном и иконками ресурсов
        for slot_button in slot_buttons:
            if slot_button["slot"]:  # Отображаем только слоты с файлами
                # Переключение на button_hover при наведении
                button_image = menu.button_hover if slot_button["rect"].collidepoint(mx, my) else menu.button_normal
                screen.blit(button_image, (slot_button["rect"].x, slot_button["rect"].y))  # Фоновое изображение
                # Текст даты, начинается слева
                date_text = small_font.render(slot_button["text"], True, BLACK)
                date_text_rect = date_text.get_rect(topleft=(slot_button["rect"].x + 20, slot_button["rect"].y + 10))  # Слева с отступом
                screen.blit(date_text, date_text_rect)
                # Иконки ресурсов (под датой), 16x16, с расстоянием, внутри кнопки
                data = save_slots[slot_buttons.index(slot_button)]["data"]
                coin_icon = pygame.transform.scale(images.GAME_IMAGES["coin_main"], (16, 16))
                harvest_icon = pygame.transform.scale(images.GAME_IMAGES["harvest"], (16, 16))
                product_icon = pygame.transform.scale(images.GAME_IMAGES["product"], (16, 16))
                resource_y = slot_button["rect"].y + 30  # Вторая строка под датой
                coin_x = slot_button["rect"].x + 15  # Начало слева
                screen.blit(coin_icon, (coin_x, resource_y))
                coin_value = small_font.render(str(data.get("coins", 0)), True, BLACK)
                screen.blit(coin_value, (coin_x + 20, resource_y))
                screen.blit(harvest_icon, (coin_x + 60, resource_y))
                harvest_value = small_font.render(str(data.get("harvest", 0)), True, BLACK)
                screen.blit(harvest_value, (coin_x + 80, resource_y))
                screen.blit(product_icon, (coin_x + 120, resource_y))
                product_value = small_font.render(str(data.get("products", 0)), True, BLACK)
                screen.blit(product_value, (coin_x + 140, resource_y))

        pygame.display.flip()
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Только левый клик
                    if back_rect.collidepoint(mx, my):
                        return None
                    for slot_button in slot_buttons:
                        if slot_button["rect"].collidepoint(mx, my) and slot_button["slot"]:
                            loaded_data = load_game(screen, slot_button["slot"])
                            if loaded_data:
                                return loaded_data

def load_music_tracks():
    """Загружает все музыкальные файлы из папки music/background."""
    # Убедимся, что Pygame инициализирован
    if not pygame.mixer.get_init():
        pygame.mixer.init()

    music_dir = os.path.join("music", "background")
    if not os.path.exists(music_dir):
        os.makedirs(music_dir)

        return []

    tracks = [os.path.join(music_dir, f) for f in os.listdir(music_dir)
              if f.endswith(('.mp3', '.ogg'))]

    return tracks


def play_next_track(tracks):
    """Воспроизводит следующий случайный трек из списка."""
    if not tracks:

        return
    next_track = random.choice(tracks)  # Случайный выбор трека
    pygame.mixer.music.load(next_track)
    pygame.mixer.music.set_volume(0.5)  # Устанавливаем громкость по умолчанию
    pygame.mixer.music.play()


def main():
    pygame.init()
    pygame.mixer.init()

    # Инициализируем шрифты и сохраняем результат в переменную fonts
    fonts_dict = initialize_fonts()  # Переименуем для ясности, чтобы не путать с модулем fonts

    info = pygame.display.Info()
    screen_width = info.current_w
    screen = pygame.display.set_mode((screen_width, SCREEN_HEIGHT), pygame.NOFRAME)

    hwnd = pygame.display.get_wm_info()['window']
    x = 0
    y = info.current_h - SCREEN_HEIGHT - 40
    width = screen_width
    height = SCREEN_HEIGHT
    win32gui.SetWindowPos(hwnd, win32con.HWND_TOP, x, y, width, height, win32con.SWP_SHOWWINDOW)

    pygame.display.set_caption("Gay Farm Game")
    clock = pygame.time.Clock()

    images.GAME_IMAGES = images.load_game_images()

    menu_language = load_menu_language()
    saved_data = load_game(screen)
    game_language = menu_language

    # Передаем fonts_dict в NotificationManager
    notification_manager = NotificationManager(game_language, fonts_dict)

    # Создаем меню, передавая fonts_dict
    menu = Menu(fonts=fonts_dict)
    menu.current_language = menu_language
    menu.font = fonts_dict["title_font_large"]  # Устанавливаем кастомный шрифт для меню
    update_menu_options(menu)

    music_tracks = load_music_tracks()
    MUSIC_END = pygame.USEREVENT + 1
    pygame.mixer.music.set_endevent(MUSIC_END)
    if music_tracks:
        play_next_track(music_tracks)

    settings_file = "settings.json"
    if os.path.exists(settings_file):
        with open(settings_file, "r", encoding="utf-8") as f:
            settings = json.load(f)
            pygame.mixer.music.set_volume(settings.get("music_volume", 0.5))
            menu.music_volume = settings.get("music_volume", 0.5)
            menu.sound_volume = settings.get("sound_volume", 0.5)
    else:
        pygame.mixer.music.set_volume(0.5)
        menu.music_volume = 0.5
        menu.sound_volume = 0.5

    running = True
    while running:
        mx, my = pygame.mouse.get_pos()

        # Обрабатываем события
        action = None
        for event in pygame.event.get():
            try:
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    running = False
                elif event.type == MUSIC_END:
                    play_next_track(music_tracks)
                temp_action = menu.handle_event(event, mx, my, screen)
                if temp_action:  # Сохраняем последнее действие
                    action = temp_action
            except Exception as e:
                running = False

        # Обрабатываем действие за пределами цикла событий
        if action == "new_game":
            # Начальные значения для новой игры
            player = None
            house = None
            objects = None
            initial_camera_x = 0
            harvest_count = 0
            level = 1
            coins = 10
            harvest = 0
            products = 0
            map_tiles = None

            # Передаем fonts_dict в game_loop
            loop_result = game_loop(screen, player, house, objects, initial_camera_x, harvest_count, level, coins,
                                    harvest, products, language=game_language, map_tiles=map_tiles, fonts=fonts_dict)
            while True:
                if isinstance(loop_result, tuple):
                    result, game_context = loop_result
                else:
                    result, game_context = loop_result, None
                if result in ["exit", "main_menu"]:
                    if result == "main_menu" and game_context:
                        dialog_result = show_save_dialog(screen, game_context,
                                                         game_language, fonts=fonts_dict)  # Убедись, что fonts_dict передаётся сюда, если нужно
                        if dialog_result == "main_menu":
                            update_menu_options(menu)
                            break
                        elif dialog_result == "exit":
                            running = False
                            break
                        elif dialog_result is None:
                            loop_result = game_loop(screen,
                                                    game_context["player"],
                                                    game_context["house"],
                                                    game_context["objects"],
                                                    game_context["camera_x"],
                                                    game_context["harvest_count"],
                                                    game_context["level"],
                                                    game_context["coins"],
                                                    game_context["harvest"],
                                                    game_context["products"],
                                                    menu.current_language,
                                                    game_context["map_tiles"],
                                                    fonts=fonts_dict)
                            continue
                    elif result == "exit":
                        running = False
                        break
                break
        elif action == "continue":
            loaded_data = show_load_dialog(screen, menu.current_language, menu, fonts=fonts_dict)
            if loaded_data:
                player, house, objects, camera_x, harvest_count, level, coins, harvest, products, game_language, map_tiles = loaded_data
                game_language = menu.current_language
                loop_result = game_loop(screen, player, house, objects, camera_x, harvest_count, level, coins,
                                        harvest, products, game_language, map_tiles, fonts=fonts_dict)
                while True:
                    if isinstance(loop_result, tuple):
                        result, game_context = loop_result
                    else:
                        result, game_context = loop_result, None
                    if result in ["exit", "main_menu"]:
                        if result == "main_menu" and game_context:
                            dialog_result = show_save_dialog(screen, game_context, game_language, fonts=fonts_dict)
                            if dialog_result == "main_menu":
                                update_menu_options(menu)
                                break
                            elif dialog_result == "exit":
                                running = False
                                break
                            elif dialog_result is None:
                                loop_result = game_loop(screen,
                                                        game_context["player"],
                                                        game_context["house"],
                                                        game_context["objects"],
                                                        game_context["camera_x"],
                                                        game_context["harvest_count"],
                                                        game_context["level"],
                                                        game_context["coins"],
                                                        game_context["harvest"],
                                                        game_context["products"],
                                                        menu.current_language,
                                                        game_context["map_tiles"],
                                                        fonts=fonts)
                                continue
                        elif result == "exit":
                            running = False
                            break
                    break
        elif action == "load":
            loaded_data = show_load_dialog(screen, menu.current_language, menu, fonts)
            if loaded_data:
                player, house, objects, camera_x, harvest_count, level, coins, harvest, products, game_language, map_tiles = loaded_data
                game_language = menu.current_language
                loop_result = game_loop(screen, player, house, objects, camera_x, harvest_count, level, coins,
                                        harvest, products, game_language, map_tiles, fonts=fonts_dict)
                while True:
                    if isinstance(loop_result, tuple):
                        result, game_context = loop_result
                    else:
                        result, game_context = loop_result, None
                    if result in ["exit", "main_menu"]:
                        if result == "main_menu" and game_context:
                            dialog_result = show_save_dialog(screen, game_context, game_language, fonts=fonts_dict)
                            if dialog_result == "main_menu":
                                update_menu_options(menu)
                                break
                            elif dialog_result == "exit":
                                running = False
                                break
                            elif dialog_result is None:
                                loop_result = game_loop(screen,
                                                        game_context["player"],
                                                        game_context["house"],
                                                        game_context["objects"],
                                                        game_context["camera_x"],
                                                        game_context["harvest_count"],
                                                        game_context["level"],
                                                        game_context["coins"],
                                                        game_context["harvest"],
                                                        game_context["products"],
                                                        game_language,
                                                        game_context["map_tiles"])
                                continue
                        elif result == "exit":
                            running = False
                            break
                    break
        elif action == "exit":
            running = False
        elif action == "settings":
            update_menu_options(menu)

        # Отрисовка

        notification_manager.update()
        menu.draw(screen)
        notification_manager.draw(screen)
        pygame.display.flip()
        clock.tick(60)


    pygame.quit()

def update_menu_options(menu):
    """Обновляет опции меню, проверяя наличие сохранённой игры и язык меню."""
    has_saves = Menu.is_save_exists()
    menu.options = [
        {"text": get_text("New Game", menu.current_language), "image_normal": menu.button_normal, "image_hover": menu.button_hover, "color": WHITE, "action": "new_game"},
        {"text": get_text("Continue", menu.current_language), "image_normal": menu.button_normal, "image_hover": menu.button_hover, "color": WHITE if has_saves else GRAY, "action": "continue"},
        {"text": get_text("Load", menu.current_language), "image_normal": menu.button_normal, "image_hover": menu.button_hover, "color": WHITE if has_saves else GRAY, "action": "load"},
        {"text": get_text("Settings", menu.current_language), "image_normal": menu.button_normal, "image_hover": menu.button_hover, "color": WHITE, "action": "settings"},
    ]


if __name__ == "__main__":
    main()