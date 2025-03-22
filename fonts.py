# fonts.py
import pygame
import os


FONT_PATH_TITLE = os.path.join("fonts", "nyashasans.ttf")
FONT_PATH_DESC = os.path.join("fonts", "Involve-Regular.ttf")

def initialize_fonts():
    """Инициализирует шрифты после pygame.init() и возвращает их."""
    if not os.path.exists(FONT_PATH_TITLE):
        print(f"Ошибка: шрифт {FONT_PATH_TITLE} не найден! Используется системный шрифт.")
        title_font_large = pygame.font.SysFont("monospace", 26)
        title_font_medium = pygame.font.SysFont("monospace", 16)
    else:
        title_font_large = pygame.font.Font(FONT_PATH_TITLE, 26)
        title_font_medium = pygame.font.Font(FONT_PATH_TITLE, 16)
        print(f"Шрифт {FONT_PATH_TITLE} успешно загружен: title_font_large = {title_font_large}")

    if not os.path.exists(FONT_PATH_DESC):
        print(f"Ошибка: шрифт {FONT_PATH_DESC} не найден! Используется системный шрифт.")
        desc_font_large = pygame.font.SysFont("arial", 18)
        desc_font_small = pygame.font.SysFont("arial", 14)
    else:
        desc_font_large = pygame.font.Font(FONT_PATH_DESC, 18)
        desc_font_small = pygame.font.Font(FONT_PATH_DESC, 14)
        print(f"Шрифт {FONT_PATH_DESC} успешно загружен: desc_font_large = {desc_font_large}")

    return {
        "title_font_large": title_font_large,
        "title_font_medium": title_font_medium,
        "desc_font_large": desc_font_large,
        "desc_font_small": desc_font_small
    }