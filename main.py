# main.py
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
from fonts import initialize_fonts

def load_menu_language():
    if os.path.exists("menu_language.json"):
        with open("menu_language.json", "r", encoding="utf-8") as f:
            return json.load(f).get("language", "en")
    return "en"

def save_menu_language(language):
    with open("menu_language.json", "w", encoding="utf-8") as f:
        json_str = json.dumps({"language": language}, indent=4, ensure_ascii=False)
        f.write(json_str)

def show_save_dialog(screen, game_context, language, fonts):
    font = fonts["title_font_medium"]
    small_font = fonts["desc_font_large"]
    clock = pygame.time.Clock()
    save_slot = None
    confirmation_text = None
    show_slot_selection = False

    while True:
        screen.fill((0, 0, 0))
        mx, my = pygame.mouse.get_pos()

        display_text = confirmation_text if confirmation_text else get_text("Do you want to save the game?", language)
        text = font.render(display_text, True, WHITE)
        text_rect = text.get_rect(center=(screen.get_width() // 2, 50))
        screen.blit(text, text_rect)

        buttons = []
        if not show_slot_selection:
            buttons = [
                {"text": get_text("Yes", language), "rect": None, "action": "yes"},
                {"text": get_text("No", language), "rect": None, "action": "no"},
                {"text": get_text("Cancel", language), "rect": None, "action": "cancel"}
            ]
            button_width = 100
            button_spacing = 20
            total_width = len(buttons) * button_width + (len(buttons) - 1) * button_spacing
            start_x = (screen.get_width() - total_width) // 2
            for i, button in enumerate(buttons):
                button["rect"] = pygame.Rect(start_x + i * (button_width + button_spacing), 150, button_width, 50)

        slot_buttons = []
        if show_slot_selection:
            y_offset = 200
            max_slots = 3
            save_slots = list_saves()
            for i in range(max_slots):
                slot_name = f"Slot {i+1} (Empty)"
                if i < len(save_slots):
                    slot_name = f"Slot {i+1} ({time.strftime('%Y-%m-%d %H:%M', time.localtime(save_slots[i]['timestamp']))})"
                rect = pygame.Rect((screen.get_width() - 340) // 2, y_offset + i * 60, 340, 50)
                slot_buttons.append({"text": slot_name, "rect": rect, "action": "save", "slot": save_slots[i]["filename"] if i < len(save_slots) else f"save_new_{i+1}.json"})

        for button in buttons:
            pygame.draw.rect(screen, GRAY if button["rect"].collidepoint(mx, my) else WHITE, button["rect"])
            text_surf = small_font.render(button["text"], True, BLACK)
            text_rect = text_surf.get_rect(center=button["rect"].center)
            screen.blit(text_surf, text_rect)

        for slot_button in slot_buttons:
            pygame.draw.rect(screen, GRAY if slot_button["rect"].collidepoint(mx, my) else WHITE, slot_button["rect"])
            text_surf = small_font.render(slot_button["text"], True, BLACK)
            text_rect = text_surf.get_rect(center=slot_button["rect"].center)
            screen.blit(text_surf, text_rect)

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
                                save_context = {k: v for k, v in game_context.items() if k != "screen"}
                                save_game(game_context["player"], game_context["house"], game_context["objects"],
                                          game_context["camera_x"], game_context["harvest_count"],
                                          game_context["level"], game_context["coins"], game_context["harvest"],
                                          game_context["products"], language, save_context, save_slot)
                                return "main_menu"
                            else:
                                confirmation_text = get_text("Please select a slot!", language)
                                show_slot_selection = True
                        elif button["action"] == "no":
                            return "main_menu"
                        elif button["action"] == "cancel":
                            return None
                for slot_button in slot_buttons:
                    if slot_button["rect"].collidepoint(mx, my):
                        save_slot = slot_button["slot"]
                        confirmation_text = get_text("Save to", language) + f" {save_slot}?"
                        show_slot_selection = False

def show_load_dialog(screen, language, fonts):
    font = fonts["title_font_medium"]
    small_font = fonts["desc_font_large"]
    clock = pygame.time.Clock()

    while True:
        screen.fill((0, 0, 0))
        mx, my = pygame.mouse.get_pos()

        text = font.render(get_text("Select a save to load:", language), True, WHITE)
        text_rect = text.get_rect(center=(screen.get_width() // 2, 50))
        screen.blit(text, text_rect)

        cancel_button = {"text": get_text("Cancel", language), "rect": None}
        cancel_button["rect"] = pygame.Rect((screen.get_width() - 100) // 2, SCREEN_HEIGHT // 2 - 50, 100, 50)

        save_slots = list_saves()
        slot_buttons = []
        y_offset = SCREEN_HEIGHT // 2 + 50
        max_slots = 3
        for i in range(max_slots):
            slot_name = f"Slot {i+1} (Empty)"
            if i < len(save_slots):
                slot_name = f"Slot {i+1} - {time.strftime('%Y-%m-%d %H:%M', time.localtime(save_slots[i]['timestamp']))}"
            rect = pygame.Rect((screen.get_width() - 340) // 2, y_offset + i * 60, 340, 50)
            slot_buttons.append({"text": slot_name, "rect": rect, "action": "load", "slot": save_slots[i]["filename"] if i < len(save_slots) else None})

        pygame.draw.rect(screen, GRAY if cancel_button["rect"].collidepoint(mx, my) else WHITE, cancel_button["rect"])
        text_surf = small_font.render(cancel_button["text"], True, BLACK)
        text_rect = text_surf.get_rect(center=cancel_button["rect"].center)
        screen.blit(text_surf, text_rect)

        for slot_button in slot_buttons:
            if slot_button["slot"]:
                pygame.draw.rect(screen, GRAY if slot_button["rect"].collidepoint(mx, my) else WHITE, slot_button["rect"])
                text_surf = small_font.render(slot_button["text"], True, BLACK)
                text_rect = text_surf.get_rect(center=slot_button["rect"].center)
                screen.blit(text_surf, text_rect)

        pygame.display.flip()
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if cancel_button["rect"].collidepoint(mx, my):
                    return None
                for slot_button in slot_buttons:
                    if slot_button["rect"].collidepoint(mx, my) and slot_button["slot"]:
                        loaded_data = load_game(screen, slot_button["slot"])
                        if loaded_data:
                            return loaded_data

def main():
    pygame.init()
    fonts = initialize_fonts()
    print(f"Шрифты после initialize_fonts(): {fonts}")

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
    print(f"GAME_IMAGES keys after loading: {list(images.GAME_IMAGES.keys())}")

    menu_language = load_menu_language()
    saved_data = load_game(screen)  # Проверяем наличие сохранений при старте
    game_language = "ru" if saved_data and saved_data[-2] == "ru" else "en" if saved_data else "en"

    menu = Menu(fonts["title_font_large"])
    menu.current_language = menu_language
    update_menu_options(menu)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                action = menu.handle_event(event, mx, my)
                print(f"Действие выбрано: {action}")  # Отладочный вывод
                if action == "new_game":
                    loop_result = game_loop(screen, language=game_language)
                    while True:
                        if isinstance(loop_result, tuple):
                            result, game_context = loop_result
                        else:
                            result, game_context = loop_result, None
                        if result in ["exit", "main_menu"]:
                            if result == "main_menu" and game_context:
                                dialog_result = show_save_dialog(screen, game_context, game_language, fonts)
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
                elif action == "continue":
                    print("Нажата кнопка Continue")  # Отладочный вывод
                    loaded_data = load_game(screen)  # Загружаем самый последний слот
                    print(f"Загруженные данные: {loaded_data}")  # Отладочный вывод
                    if loaded_data:
                        player, house, objects, camera_x, harvest_count, level, coins, harvest, products, game_language, map_tiles = loaded_data
                        game_language = menu.current_language
                        print(f"Запуск game_loop с данными: player={player}, language={game_language}")  # Отладочный вывод
                        loop_result = game_loop(screen, player, house, objects, camera_x, harvest_count, level, coins,
                                                harvest, products, game_language, map_tiles)
                        while True:
                            if isinstance(loop_result, tuple):
                                result, game_context = loop_result
                            else:
                                result, game_context = loop_result, None
                            if result in ["exit", "main_menu"]:
                                if result == "main_menu" and game_context:
                                    dialog_result = show_save_dialog(screen, game_context, game_language, fonts)
                                    if dialog_result == "main_menu":
                                        update_menu_options(menu)
                                        break
                                    elif dialog_result == "exit":
                                        running = False
                                        break
                                    elif dialog_result is None:
                                        loop_result = game_loop(screen,
                                                                player,
                                                                house,
                                                                objects,
                                                                camera_x,
                                                                harvest_count,
                                                                level,
                                                                coins,
                                                                harvest,
                                                                products,
                                                                game_language,
                                                                map_tiles)
                                        continue
                                elif result == "exit":
                                    running = False
                                    break
                            break
                    else:
                        print("Нет сохранённой игры для продолжения!")
                elif action == "load":
                    loaded_data = show_load_dialog(screen, menu.current_language, fonts)
                    if loaded_data:
                        player, house, objects, camera_x, harvest_count, level, coins, harvest, products, game_language, map_tiles = loaded_data
                        game_language = menu.current_language
                        loop_result = game_loop(screen, player, house, objects, camera_x, harvest_count, level, coins,
                                                harvest, products, game_language, map_tiles)
                        while True:
                            if isinstance(loop_result, tuple):
                                result, game_context = loop_result
                            else:
                                result, game_context = loop_result, None
                            if result in ["exit", "main_menu"]:
                                if result == "main_menu" and game_context:
                                    dialog_result = show_save_dialog(screen, game_context, game_language, fonts)
                                    if dialog_result == "main_menu":
                                        update_menu_options(menu)
                                        break
                                    elif dialog_result == "exit":
                                        running = False
                                        break
                                    elif dialog_result is None:
                                        loop_result = game_loop(screen,
                                                                player,
                                                                house,
                                                                objects,
                                                                camera_x,
                                                                harvest_count,
                                                                level,
                                                                coins,
                                                                harvest,
                                                                products,
                                                                game_language,
                                                                map_tiles)
                                        continue
                                elif result == "exit":
                                    running = False
                                    break
                            break
                elif action == "exit":
                    running = False
                elif action == "settings":
                    update_menu_options(menu)

        menu.draw(screen)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

def update_menu_options(menu):
    menu.options = [
        {"text": get_text("New Game", menu.current_language), "color": WHITE, "action": "new_game"},
        {"text": get_text("Continue", menu.current_language), "color": WHITE if Menu.is_save_exists() else GRAY, "action": "continue"},
        {"text": get_text("Load", menu.current_language), "color": WHITE, "action": "load"},
        {"text": get_text("Settings", menu.current_language), "color": WHITE, "action": "settings"},
        {"text": get_text("Exit", menu.current_language), "color": WHITE, "action": "exit"}
    ]
    print(f"Menu options updated: {menu.options}")

if __name__ == "__main__":
    main()