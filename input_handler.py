import pygame
from config import SCREEN_HEIGHT
from menus import WheelMenu, SeedMenu, BuildMenu, MarketMenu
from game_utils import snap_to_grid  # Добавляем импорт snap_to_grid

def handle_input(player, objects, camera_x, screen_width, map_width, screen_height, game_context, coins, harvest,
                 harvest_count, level, products, event):
    menu_manager = game_context["menu_manager"]

    # Инициализируем last_click_time, если его ещё нет в game_context
    if "last_click_time" not in game_context:
        game_context["last_click_time"] = 0

    if event.type == pygame.MOUSEBUTTONDOWN:
        mx, my = pygame.mouse.get_pos()
        current_time = pygame.time.get_ticks()

        # Проверяем двойной клик для движения персонажа (левый клик, кнопка 1)
        if event.button == 1:
            print(f"Mouse button down at ({mx}, {my}), button={event.button}, time={current_time}, last_click_time={game_context.get('last_click_time', 'Not set')}")
            double_click_threshold = 300  # Порог в миллисекундах для двойного клика
            is_double_click = (current_time - game_context["last_click_time"]) <= double_click_threshold
            print(f"Is double click: {is_double_click}")

            if is_double_click:
                # Разрешаем движение по обеим осям, используя snap_to_grid для стабильности
                target_x = snap_to_grid(mx + camera_x, grid_size=32) - player.width // 2
                target_y = snap_to_grid(my, grid_size=32) - player.height // 2  # Вертикальное движение
                target_x = max(0, min(target_x, map_width - player.width))
                target_y = max(0, min(target_y, screen_height - player.height))
                player.target_x = target_x
                player.target_y = target_y
                player.state = "walking"  # Устанавливаем состояние для движения
                print(f"Double click detected, moving player to ({target_x}, {target_y})")
                return None

            # Сохраняем время текущего клика для проверки следующего
            game_context["last_click_time"] = current_time
            print(f"Updated last_click_time to {current_time}")

            # Проверяем взаимодействие с объектами в зависимости от режима
            build_menu = menu_manager.menus.get("build")
            is_move_mode = build_menu and build_menu.build_action == "move" if build_menu else False

            for obj in objects:
                obj_rect = pygame.Rect(obj.x - camera_x, obj.y, obj.width, obj.height)
                if obj_rect.collidepoint(mx, my):
                    if obj.obj_type == "market_stall":
                        if not is_move_mode:  # Открываем меню только если не в режиме перемещения
                            menu_manager.open_menu("market")
                            print(f"Market stall clicked at ({obj.x}, {obj.y}), opening MarketMenu")
                            return None
                        else:  # В режиме перемещения обрабатываем как перемещаемый объект
                            print(f"Attempting to move market_stall at ({obj.x}, {obj.y})")
                            result = menu_manager.handle_input(event, camera_x, screen_width, map_width, objects, harvest, products)
                            print(f"Result of move attempt: {result}")
                            if result in ["start_move_preview", "move_complete"]:
                                return result
                            return None
                    elif obj.obj_type in ["bed", "mill", "house", "canning_cellar"]:  # Обрабатываем только эти объекты
                        if is_move_mode:
                            print(f"Attempting to move {obj.obj_type} at ({obj.x}, {obj.y})")
                            result = menu_manager.handle_input(event, camera_x, screen_width, map_width, objects, harvest, products)
                            print(f"Result of move attempt: {result}")
                            if result in ["start_move_preview", "move_complete"]:
                                return result
                            return None

        # Проверяем правый клик для открытия WheelMenu
        elif event.button == 3:
            for menu in menu_manager.menus.values():
                if menu.is_open:
                    menu_rect = None
                    if isinstance(menu, WheelMenu):
                        screen_x = menu.center_x - camera_x
                        screen_y = menu.center_y
                        menu_rect = pygame.Rect(screen_x - menu.radius, screen_y - menu.radius, 2 * menu.radius,
                                                2 * menu.radius)
                    elif isinstance(menu, (SeedMenu, BuildMenu, MarketMenu)):
                        if isinstance(menu, SeedMenu):
                            menu_rect = pygame.Rect(screen_width - 200, 0, 200, SCREEN_HEIGHT)
                        elif isinstance(menu, BuildMenu):
                            menu_rect = pygame.Rect(screen_width - 240, 0, 240, SCREEN_HEIGHT)
                        elif isinstance(menu, MarketMenu):
                            menu_rect = pygame.Rect((screen_width - 400) // 2, (SCREEN_HEIGHT - 250) // 2, 400, 250)
                    if menu_rect and not menu_rect.collidepoint(mx, my):
                        menu_manager.close_all()
                        print("Closed all menus by right click outside")
                        return None

            world_x = mx + camera_x
            world_y = my
            menu_manager.open_menu("wheel", world_x, world_y)
            print(f"Opening WheelMenu at world position ({world_x}, {world_y})")
            return None

    # Обработка меню с отладкой
    print(f"Handling menu input: event={event}, camera_x={camera_x}, screen_width={screen_width}")
    menu_result = menu_manager.handle_input(event, camera_x, screen_width, map_width, objects, harvest, products)
    print(f"Menu result: {menu_result}")
    if menu_result in ["build", "plant"]:
        menu_manager.open_menu(menu_result)
        print(f"Opening menu: {menu_result}")
        return None
    elif menu_result == "close_seed_menu":
        return "close_seed_menu"
    elif menu_result == "close_build_menu":
        return "close_build_menu"
    elif menu_result == "close_market_menu":
        return "close_market_menu"
    elif menu_result == "set_move":
        return "set_move"
    elif menu_result == "set_destroy":
        return "set_destroy"
    elif menu_result == "start_build_preview":
        return "start_build_preview"
    elif menu_result == "start_move_preview":
        return "start_move_preview"
    elif menu_result == "move_complete":
        return "move_complete"
    elif menu_result == "destroy_complete":
        return "destroy_complete"
    elif isinstance(menu_result, dict) and menu_result.get("action") in ["build", "plant", "sell"]:
        if menu_result["action"] == "build":
            # Проверяем наличие 'cost_coins', используем 'cost' как резервный вариант
            cost_coins = menu_result.get("cost_coins", menu_result.get("cost", 0))
            coins -= cost_coins
            if "cost_harvest" in menu_result:
                harvest -= menu_result["cost_harvest"]
            if "cost_products" in menu_result:
                products -= menu_result["cost_products"]
            return coins, harvest, products
        elif menu_result["action"] == "plant":
            # Проверяем наличие 'cost_coins', используем 'cost' как резервный вариант
            cost_coins = menu_result.get("cost_coins", menu_result.get("cost", 0))
            coins -= cost_coins
            return coins, harvest, products
        elif menu_result["action"] == "sell":
            coins += menu_result["value"]
            harvest -= menu_result["harvest_sold"]
            products -= menu_result["products_sold"]
            return coins, harvest, products
    return None