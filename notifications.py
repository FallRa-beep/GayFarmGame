import pygame
from config import SCREEN_HEIGHT, WHITE, RED, GREEN
import images
from fonts import initialize_fonts
from translations import get_text

class NotificationManager:
    def __init__(self, language):
        self.notifications = []
        self.language = language
        self.fonts = {"title_font_medium": pygame.font.Font(None, 24)}  # Заглушка
        self.font = self.fonts["title_font_medium"]
        self.max_text_width = 316  # 400 (ширина окна) - 64 (портрет) - 20 (отступ слева) - 10 (отступ справа)

    def add_notification(self, notification_type):
        """Добавляет уведомление в очередь по типу."""
        if notification_type == "level_up":
            message = get_text("Это у тебя зажигалка в кармане или просто твой уровень вырос?", self.language)
            color = GREEN
        elif notification_type == "no_resources":
            message = get_text("Чувак, мы не можем себе это позволить", self.language)
            color = RED
        else:
            return  # Игнорируем неизвестные типы

        notification = {
            "message": message,
            "color": color,
            "start_time": pygame.time.get_ticks(),
            "alpha": 0,
            "state": "fade_in"
        }
        self.notifications.append(notification)

    def update(self):
        current_time = pygame.time.get_ticks()
        if not self.notifications:
            return

        notification = self.notifications[0]
        elapsed_time = current_time - notification["start_time"]

        if notification["state"] == "fade_in":
            notification["alpha"] = min(255, (elapsed_time / 500) * 255)  # 500 мс на появление
            if elapsed_time >= 500:
                notification["state"] = "showing"
                notification["start_time"] = current_time
        elif notification["state"] == "showing":
            if elapsed_time >= 2000:  # 2000 мс показа
                notification["state"] = "fade_out"
                notification["start_time"] = current_time
        elif notification["state"] == "fade_out":
            notification["alpha"] = max(0, 255 - (elapsed_time / 500) * 255)  # 500 мс на исчезновение
            if elapsed_time >= 500:
                self.notifications.pop(0)  # Удаляем уведомление

    def draw(self, screen):
        if not self.notifications:
            return

        notification = self.notifications[0]
        screen_width = screen.get_width()
        menu_width, menu_height = 400, 84
        menu_x = (screen_width - menu_width) // 2
        menu_y = 10

        # Фон
        try:
            bg_image = images.GAME_IMAGES["notification_background"]
            bg_image = pygame.transform.scale(bg_image, (menu_width, menu_height))
        except KeyError:
            bg_image = pygame.Surface((menu_width, menu_height), pygame.SRCALPHA)
            bg_image.fill((0, 0, 0, 128))

        bg_image.set_alpha(int(notification["alpha"]))
        screen.blit(bg_image, (menu_x, menu_y))

        # Портрет
        try:
            portrait = images.GAME_IMAGES["hero_portrait"]
            portrait.set_alpha(int(notification["alpha"]))
            screen.blit(portrait, (menu_x + 10, menu_y + 10))
        except KeyError:
            portrait = pygame.Surface((64, 64), pygame.SRCALPHA)
            portrait.fill((255, 0, 0, 128))
            portrait.set_alpha(int(notification["alpha"]))
            screen.blit(portrait, (menu_x + 10, menu_y + 10))

        # Разбиваем текст на строки
        words = notification["message"].split()
        lines = []
        current_line = ""
        for word in words:
            test_line = current_line + " " + word if current_line else word
            text_width = self.font.size(test_line)[0]
            if text_width <= self.max_text_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)

        # Отрисовка текста построчно
        line_height = self.font.get_linesize()  # Высота строки текста
        total_text_height = len(lines) * line_height
        text_x = menu_x + 84  # 64 (портрет) + 20 (отступ)
        # Центрируем текст по вертикали в окне
        text_y_start = menu_y + (menu_height - total_text_height) // 2

        for i, line in enumerate(lines):
            text_surface = self.font.render(line, True, notification["color"])
            text_surface.set_alpha(int(notification["alpha"]))
            screen.blit(text_surface, (text_x, text_y_start + i * line_height))