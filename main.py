import pygame
import win32gui
import win32con
import json
from config import SCREEN_HEIGHT, WHITE, GRAY
from game_loop import game_loop
from ui import Menu
from save_load import load_game, save_game
from translations import get_text
import images
import os

def load_menu_language():
    """Загружает язык меню из файла, если он существует, или возвращает 'en' по умолчанию."""
    if os.path.exists("menu_language.json"):
        with open("menu_language.json", "r", encoding="utf-8") as f:
            return json.load(f).get("language", "en")
    return "en"

def save_menu_language(language):
    """Сохраняет язык меню в файл."""
    with open("menu_language.json", "w", encoding="utf-8") as f:
        json.dump({"language": language}, f, indent=4)

def main():
    pygame.init()

    # Получаем информацию об экране и создаём окно без рамки
    info = pygame.display.Info()
    screen_width = info.current_w
    screen = pygame.display.set_mode((screen_width, SCREEN_HEIGHT), pygame.NOFRAME)

    # Устанавливаем позицию окна внизу экрана
    hwnd = pygame.display.get_wm_info()['window']
    x = 0
    y = info.current_h - SCREEN_HEIGHT - 40
    width = screen_width
    height = SCREEN_HEIGHT
    win32gui.SetWindowPos(hwnd, win32con.HWND_TOP, x, y, width, height, win32con.SWP_SHOWWINDOW)

    pygame.display.set_caption("Gay Farm Game")
    clock = pygame.time.Clock()

    # Загружаем изображения игры
    images.GAME_IMAGES = images.load_game_images()
    print(f"GAME_IMAGES keys after loading: {list(images.GAME_IMAGES.keys())}")

    # Загружаем язык меню (независимо от игры)
    menu_language = load_menu_language()
    # Загружаем сохранённые данные игры для определения языка игры
    saved_data = load_game(screen)
    game_language = "ru" if saved_data and saved_data[-1] == "ru" else "en" if saved_data else "en"

    # Создаём меню с языком меню (независимым от языка игры)
    menu = Menu()
    menu.current_language = menu_language  # Язык меню
    update_menu_options(menu)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                action = menu.handle_event(event, mx, my)
                if action == "new_game":
                    result = game_loop(screen, language=game_language)  # Используем язык игры
                    if result in ["exit", "main_menu"]:
                        if result == "exit":
                            running = False
                        update_menu_options(menu)  # Обновляем опции меню
                elif action == "continue":
                    loaded_data = load_game(screen)
                    if loaded_data:
                        # Распаковываем все 11 значений, включая map_tiles
                        player, house, objects, camera_x, harvest_count, level, coins, harvest, products, game_language, map_tiles = loaded_data
                        # Обновляем язык игры до текущего языка меню
                        game_language = menu.current_language
                        result = game_loop(screen, player, house, objects, camera_x, harvest_count, level, coins,
                                           harvest, products, game_language, map_tiles)
                        if result in ["exit", "main_menu"]:
                            if result == "exit":
                                running = False
                            update_menu_options(menu)  # Обновляем опции меню
                    else:
                        print("Нет сохранённой игры для продолжения!")
                elif action == "exit":
                    running = False
                elif action == "settings":
                    # Здесь можно добавить логику настроек, но для простоты пока просто обновляем опции
                    update_menu_options(menu)

        menu.draw(screen)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

def update_menu_options(menu):
    """Обновляет опции меню, проверяя наличие сохранённой игры и язык меню."""
    menu.options = [
        {"text": get_text("New Game", menu.current_language), "color": WHITE, "action": "new_game"},
        {"text": get_text("Continue", menu.current_language), "color": WHITE if Menu.is_save_exists() else GRAY, "action": "continue"},
        {"text": get_text("Settings", menu.current_language), "color": WHITE, "action": "settings"},
        {"text": get_text("Exit", menu.current_language), "color": WHITE, "action": "exit"}
    ]
    print(f"Menu options updated: {menu.options}")

if __name__ == "__main__":
    main()