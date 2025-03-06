import pygame
from config import SCREEN_HEIGHT, WHITE, BLACK, GRAY, GREEN
import images
from translations import get_text
from game_utils import snap_to_grid, check_collision

def render_game(screen, player, objects, camera_x, screen_width, map_width, coins, harvest, products, level, game_context):
    mx, my = pygame.mouse.get_pos()
    # Убираем screen.fill(WHITE), так как теперь у нас есть фон из тайлов

    # Отрисовка тайлов
    tile_size = 32
    if "map_tiles" in game_context:
        for tile in game_context["map_tiles"]:
            tile_image = images.GAME_IMAGES[tile["type"]]
            screen_x = tile["x"] - camera_x
            # Отрисовываем только видимые тайлы для оптимизации
            if -tile_size <= screen_x <= screen_width:
                screen.blit(tile_image, (screen_x, tile["y"]))

    # Отрисовка объектов и игрока
    for obj in objects:
        obj.draw(screen, camera_x)
    player.draw(screen, camera_x)

    # Отрисовка меню
    game_context["menu_manager"].draw(screen, camera_x, harvest, products)  # Добавляем harvest и products

    # Отрисовка интерфейса ресурсов
    small_font = pygame.font.Font(None, 24)  # Меньший шрифт (24)
    tooltip_font = pygame.font.Font(None, 18)  # Ещё меньший шрифт для подсказок

    # Уменьшаем иконки до 16x16
    coin_image = pygame.transform.scale(images.GAME_IMAGES["coin_main"], (16, 16))
    harvest_image = pygame.transform.scale(images.GAME_IMAGES["harvest"], (16, 16))
    product_image = pygame.transform.scale(images.GAME_IMAGES["product"], (16, 16))

    # Рисуем фон для показателей (полупрозрачный серый прямоугольник)
    icon_height = coin_image.get_height()  # Высота иконок (16 пикселей)
    background_height = 26  # Высота фона (16 пикселей иконки + 5 сверху + 5 снизу для центрирования)
    background_width = (coin_image.get_width() + 5 + small_font.size(str(coins))[0] + 30 +  # Монеты
                       harvest_image.get_width() + 5 + small_font.size(str(harvest))[0] + 30 +  # Урожай
                       product_image.get_width() + 5 + small_font.size(str(products))[0] + 30 +  # Продукты
                       small_font.size(f"{get_text('Level', game_context['language'])}: {level}")[0] + 10)  # Уровень
    background_rect = pygame.Rect(0, 0, background_width, background_height)
    pygame.draw.rect(screen, (211, 211, 211, 128), background_rect)  # Полупрозрачный светло-серый фон

    # Рисуем показатели с минимальным отступом 5 пикселей слева и расстоянием 30 пикселей справа от текста
    y_offset = (background_height - icon_height) // 2
    x_offset = 0

    # Монеты
    screen.blit(coin_image, (x_offset + 5, y_offset))
    coins_text = small_font.render(str(coins), True, BLACK)
    screen.blit(coins_text, (x_offset + 5 + coin_image.get_width() + 5, y_offset))
    coins_rect = pygame.Rect(x_offset + 5, y_offset, coin_image.get_width() + coins_text.get_width() + 5 + 30,
                            coin_image.get_height())

    # Урожай
    x_offset += coin_image.get_width() + 5 + coins_text.get_width() + 30
    screen.blit(harvest_image, (x_offset + 5, y_offset))
    harvest_text = small_font.render(str(harvest), True, BLACK)
    screen.blit(harvest_text, (x_offset + 5 + harvest_image.get_width() + 5, y_offset))
    harvest_rect = pygame.Rect(x_offset + 5, y_offset, harvest_image.get_width() + harvest_text.get_width() + 5 + 30,
                              harvest_image.get_height())

    # Продукты
    x_offset += harvest_image.get_width() + 5 + harvest_text.get_width() + 30
    screen.blit(product_image, (x_offset + 5, y_offset))
    products_text = small_font.render(str(products), True, BLACK)
    screen.blit(products_text, (x_offset + 5 + product_image.get_width() + 5, y_offset))
    products_rect = pygame.Rect(x_offset + 5, y_offset, product_image.get_width() + products_text.get_width() + 5 + 30,
                               product_image.get_height())

    # Уровень
    x_offset += product_image.get_width() + 5 + products_text.get_width() + 30
    level_text = get_text("Level", game_context["language"])
    level_display = f"{level_text}: {level}"
    level_surface = small_font.render(level_display, True, BLACK)
    screen.blit(level_surface, (x_offset + 5, y_offset))
    level_rect = pygame.Rect(x_offset + 5, y_offset, level_surface.get_width(), level_surface.get_height())

    # Отрисовка предпросмотра строительства/перемещения
    build_menu = game_context["menu_manager"].menus["build"]
    if build_menu.build_action in ["build_preview", "move_preview"] and build_menu.preview_build:
        build_menu.preview_build.x = snap_to_grid(mx + camera_x, grid_size=32) - build_menu.preview_build.width // 2
        build_menu.preview_build.y = snap_to_grid(my, grid_size=32) - build_menu.preview_build.height // 2
        build_menu.preview_build.x = max(0, min(build_menu.preview_build.x, map_width - build_menu.preview_build.width))
        build_menu.preview_build.y = max(0, min(build_menu.preview_build.y,
                                                SCREEN_HEIGHT - build_menu.preview_build.height))

        preview_surface = pygame.Surface((build_menu.preview_build.width, build_menu.preview_build.height),
                                        pygame.SRCALPHA)
        obj_type = build_menu.preview_build.obj_type
        if obj_type == "bed":
            base_image = images.GAME_IMAGES["bed_dry"]
            preview_surface.blit(base_image, (0, 0))
        elif obj_type == "house":
            house_image = images.GAME_IMAGES["house"]
            scaled_house = pygame.transform.scale(house_image,
                                                 (build_menu.preview_build.width, build_menu.preview_build.height))
            preview_surface.blit(scaled_house, (0, 0))
        elif obj_type == "mill":
            mill_image = images.GAME_IMAGES["mill"]
            scaled_mill = pygame.transform.scale(mill_image,
                                                (build_menu.preview_build.width, build_menu.preview_build.height))
            preview_surface.blit(scaled_mill, (0, 0))
        elif obj_type == "market_stall":
            stall_image = images.GAME_IMAGES["market_stall"]
            scaled_stall = pygame.transform.scale(stall_image,
                                                 (build_menu.preview_build.width, build_menu.preview_build.height))
            preview_surface.blit(scaled_stall, (0, 0))
        else:
            pygame.draw.rect(preview_surface, build_menu.preview_build.color,
                            (0, 0, build_menu.preview_build.width, build_menu.preview_build.height))

        preview_surface.set_alpha(128)
        collision = check_collision(build_menu.preview_build,
                                    [obj for obj in objects if obj != build_menu.moving_object], grid_size=32,
                                    allow_touching=True)

        glow_surface = pygame.Surface((build_menu.preview_build.width + 20, build_menu.preview_build.height + 20),
                                     pygame.SRCALPHA)
        glow_color = (0, 255, 0, 100) if not collision else (255, 0, 0, 100)
        pygame.draw.rect(glow_surface, glow_color,
                        (10, 10, build_menu.preview_build.width, build_menu.preview_build.height), 4)

        screen.blit(glow_surface, (build_menu.preview_build.x - camera_x - 10, build_menu.preview_build.y - 10))
        screen.blit(preview_surface, (build_menu.preview_build.x - camera_x, build_menu.preview_build.y))

    if build_menu.build_action == "destroy":
        for obj in objects:
            if obj.obj_type in ["bed", "mill"]:
                obj_rect = pygame.Rect(obj.x - camera_x, obj.y, obj.width, obj.height)
                if obj_rect.collidepoint(mx, my):
                    destroy_glow_surface = pygame.Surface((obj.width + 20, obj.height + 20), pygame.SRCALPHA)
                    destroy_glow_color = (255, 0, 0, 100)
                    pygame.draw.rect(destroy_glow_surface, destroy_glow_color, (10, 10, obj.width, obj.height), 4)
                    screen.blit(destroy_glow_surface, (obj.x - camera_x - 10, obj.y - 10))

    # Отрисовка tooltip поверх всех элементов
    tooltip = None
    if coins_rect.collidepoint(mx, my):
        tooltip = tooltip_font.render("Золотые искры, которые заставляют сердца биться чаще!", True, WHITE)
    elif harvest_rect.collidepoint(mx, my):
        tooltip = tooltip_font.render("Сочные плоды твоих трудов — сладость, которую хочется попробовать...", True,
                                     WHITE)
    elif products_rect.collidepoint(mx, my):
        tooltip = tooltip_font.render("Вкусные деликатесы, чтобы соблазнить любого поклонника!", True, WHITE)
    elif level_rect.collidepoint(mx, my):
        tooltip = tooltip_font.render("Твой путь к вершине — горячий и страстный подъем к успеху!", True, WHITE)

    if tooltip:
        tooltip_rect = pygame.Rect(mx + 10, my, tooltip.get_width() + 10, tooltip.get_height() + 10)
        if tooltip_rect.right > screen_width:
            tooltip_rect.left = mx - tooltip_rect.width - 10
        if tooltip_rect.bottom > SCREEN_HEIGHT:
            tooltip_rect.top = my - tooltip_rect.height - 10
        if tooltip_rect.left < 0:
            tooltip_rect.left = 10
        if tooltip_rect.top < 0:
            tooltip_rect.top = 10

        pygame.draw.rect(screen, BLACK, tooltip_rect)
        screen.blit(tooltip, (tooltip_rect.x + 5, tooltip_rect.y + 5))

    # Обработка движения камеры
    if mx < 50 and camera_x > 0:
        camera_x -= 5
    elif mx > screen_width - 50 and camera_x < map_width - screen_width:
        camera_x += 5

    return camera_x