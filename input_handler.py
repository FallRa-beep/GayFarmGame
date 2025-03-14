import pygame
from config import SCREEN_HEIGHT
from menus import WheelMenu, SeedMenu, BuildMenu, MarketMenu
from game_utils import snap_to_grid
from entities import Bed

def handle_input(player, objects, camera_x, screen_width, map_width, screen_height, game_context, coins, harvest,
                 harvest_count, level, products, event):
    menu_manager = game_context["menu_manager"]

    if "last_click_time" not in game_context:
        game_context["last_click_time"] = 0

    if event.type == pygame.MOUSEBUTTONDOWN:
        mx, my = pygame.mouse.get_pos()
        print(f"Mouse click at ({mx}, {my})")

        if event.button == 1:
            double_click_threshold = 300
            is_double_click = (pygame.time.get_ticks() - game_context["last_click_time"]) <= double_click_threshold

            if is_double_click:
                target_x = snap_to_grid(mx + camera_x, grid_size=32) - player.width // 2
                target_y = snap_to_grid(my, grid_size=32) - player.height // 2
                target_x = max(0, min(target_x, map_width - player.width))
                target_y = max(0, min(target_y, screen_height - player.height))
                player.target_x = target_x
                player.target_y = target_y
                player.state = "walking"
                return None

            game_context["last_click_time"] = pygame.time.get_ticks()

            build_menu = menu_manager.menus.get("build")
            is_move_mode = build_menu and build_menu.build_action == "move" if build_menu else False
            print(f"Is move mode active: {is_move_mode}")

            for obj in objects:
                obj_rect = pygame.Rect(obj.x - camera_x, obj.y, obj.width, obj.height)
                print(f"Checking object {obj.obj_type} at ({obj.x}, {obj.y}), rect: {obj_rect}")
                if obj_rect.collidepoint(mx, my):
                    if obj.obj_type == "market_stall":
                        if not is_move_mode:
                            print("Opening MarketMenu")
                            menu_manager.open_menu("market")
                            return None
                        else:
                            result = menu_manager.handle_input(event, camera_x, screen_width, map_width, objects, harvest, products)
                            if result in ["start_move_preview", "move_complete"]:
                                return result
                            return None
                    elif obj.obj_type in ["bed", "mill", "house", "canning_cellar"]:
                        if is_move_mode:
                            result = menu_manager.handle_input(event, camera_x, screen_width, map_width, objects, harvest, products)
                            if result in ["start_move_preview", "move_complete"]:
                                return result
                            return None

        elif event.button == 3:
            for menu in menu_manager.menus.values():
                if menu.is_open:
                    menu_rect = None
                    if isinstance(menu, WheelMenu):
                        screen_x = menu.center_x - camera_x
                        screen_y = menu.center_y
                        menu_rect = pygame.Rect(screen_x - menu.radius, screen_y - menu.radius, 2 * menu.radius, 2 * menu.radius)
                    elif isinstance(menu, (SeedMenu, BuildMenu, MarketMenu)):
                        if isinstance(menu, SeedMenu):
                            menu_rect = pygame.Rect(screen_width - 200, 0, 200, SCREEN_HEIGHT)
                        elif isinstance(menu, BuildMenu):
                            menu_rect = pygame.Rect(screen_width - 240, 0, 240, SCREEN_HEIGHT)
                        elif isinstance(menu, MarketMenu):
                            menu_rect = pygame.Rect((screen_width - 400) // 2, (SCREEN_HEIGHT - 250) // 2, 400, 250)
                    if menu_rect and not menu_rect.collidepoint(mx, my):
                        menu_manager.close_all()
                        return None
            world_x = mx + camera_x
            world_y = my
            menu_manager.open_menu("wheel", world_x, world_y)
            return None

    # Обрабатываем результат от menu_manager
    menu_result = menu_manager.handle_input(event, camera_x, screen_width, map_width, objects, harvest, products)
    print(f"Menu result before processing: {menu_result}")
    if menu_result:
        # Если это предварительный просмотр перемещения, выравниваем объект по сетке
        if isinstance(menu_result, dict) and menu_result.get("action") == "start_move_preview":
            moved_obj = menu_result.get("moved_obj")
            if moved_obj and isinstance(moved_obj, Bed):  # Проверяем, что это грядка
                grid_x = snap_to_grid(moved_obj.x, grid_size=32)
                grid_y = snap_to_grid(moved_obj.y, grid_size=32)
                moved_obj.x = grid_x
                moved_obj.y = grid_y

        # Обработка других действий (build, plant, sell)
        if isinstance(menu_result, dict) and menu_result.get("action") in ["build", "plant", "sell"]:
            if menu_result["action"] == "build":
                cost_coins = menu_result.get("cost_coins", 0)
                coins -= cost_coins
                if "cost_harvest" in menu_result:
                    harvest -= menu_result["cost_harvest"]
                if "cost_products" in menu_result:
                    products -= menu_result["cost_products"]
            elif menu_result["action"] == "plant":
                cost_coins = menu_result.get("cost_coins", 0)
                coins -= cost_coins
            elif menu_result["action"] == "sell":
                coins += menu_result["value"]
                harvest -= menu_result["harvest_sold"]
                products -= menu_result["products_sold"]
                print(f"Sell processed: coins={coins}, harvest={harvest}, products={products}")
            menu_result["updated_resources"] = {"coins": coins, "harvest": harvest, "products": products}
        print(f"Updated resources in input_handler: {menu_result}")

        return menu_result
    return None