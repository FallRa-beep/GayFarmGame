import pygame
import time
import math
from config import MAP_WIDTH, SCREEN_HEIGHT, LEVEL_THRESHOLDS, SEEDS
from translations import get_text
from entities import Player, Bed, MapObject, MarketStall, Mill, CanningCellar
from menus import MenuManager
from rendering import render_game
from input_handler import handle_input
from game_utils import snap_to_grid
from save_load import save_game
from quadtree import QuadTree

def game_loop(screen, player=None, house=None, objects=None, initial_camera_x=0, harvest_count=0, level=1, coins=10,
              harvest=0, products=0, language="en"):
    clock = pygame.time.Clock()
    screen_width = screen.get_width()
    screen_height = SCREEN_HEIGHT

    menu_manager = MenuManager(language, coins, harvest, products, level)
    boundary = pygame.Rect(0, 0, MAP_WIDTH, SCREEN_HEIGHT)
    quad_tree = QuadTree(boundary, capacity=4)

    if player is None:
        house_x = snap_to_grid(screen_width // 2 - 64, grid_size=32)
        house_y = snap_to_grid(10, grid_size=32)
        house = MapObject(house_x, house_y, 128, 128, (0, 0, 0), "house")
        market_x = snap_to_grid(64, grid_size=32)
        market_y = snap_to_grid(house_y, grid_size=32)
        market_stall = MarketStall(market_x, market_y)
        bed1_x = snap_to_grid(screen_width // 2 - 96, grid_size=32)
        bed1_y = snap_to_grid(screen_height - 128, grid_size=32)
        bed2_x = snap_to_grid(screen_width // 2 - 32, grid_size=32)
        bed2_y = snap_to_grid(screen_height - 128, grid_size=32)
        bed3_x = snap_to_grid(screen_width // 2 + 32, grid_size=32)
        bed3_y = snap_to_grid(screen_height - 128, grid_size=32)
        mill_x = snap_to_grid(screen_width // 2 + 100, grid_size=32)
        mill_y = snap_to_grid(100, grid_size=32)
        cellar_x = snap_to_grid(screen_width // 2 + 164, grid_size=32)
        cellar_y = snap_to_grid(100, grid_size=32)
        objects = [Bed(bed1_x, bed1_y), Bed(bed2_x, bed2_y), Bed(bed3_x, bed3_y), house, market_stall,
                   Mill(mill_x, mill_y), CanningCellar(cellar_x, cellar_y)]
        for obj in objects:
            quad_tree.insert(obj)
        print(f"Objects in QuadTree: {len(quad_tree.query(pygame.Rect(0, 0, MAP_WIDTH, SCREEN_HEIGHT)))}")
        player = Player(snap_to_grid(screen_width // 2 + 100, grid_size=32),
                        snap_to_grid(screen_height - 128, grid_size=32), 64, 64, 5, language=language)
        camera_x = 0
        player.x = max(0, min(player.x, MAP_WIDTH - player.width))
        player.y = max(0, min(player.y, SCREEN_HEIGHT - player.height))
        coins = 10
        harvest = 0
        products = 0
        level = 1
        harvest_count = 0
    else:
        camera_x = initial_camera_x
        if objects is None:
            objects = []
        has_market_stall = any(obj.obj_type == "market_stall" for obj in objects)
        if not has_market_stall:
            market_x = snap_to_grid(64, grid_size=32)
            market_y = snap_to_grid(10, grid_size=32)
            market_stall = MarketStall(market_x, market_y)
            objects.append(market_stall)
        for obj in objects:
            quad_tree.insert(obj)
        print(f"Objects in QuadTree after load: {len(quad_tree.query(pygame.Rect(0, 0, MAP_WIDTH, SCREEN_HEIGHT)))}")
        player.language = language
        player.x = max(0, min(player.x, MAP_WIDTH - player.width))
        player.y = max(0, min(player.y, SCREEN_HEIGHT - player.height))

    app_mouse_focus = 1
    app_input_focus = 2
    app_active = 4

    game_context = {
        "language": language,
        "screen": screen,
        "menu_manager": menu_manager,
        "target_bed": None,
        "target_mill": None,
        "target_canning_cellar": None,
        "last_click_time": 0,
        "window_active": True,
        "window_minimized": False
    }
    running = True
    last_save_time = time.time()
    auto_save_interval = 600

    print(f"Pygame version: {pygame.ver}")
    print(f"Initial player position: ({player.x}, {player.y}), state: {player.state}")

    def find_nearest_bed_quad(player, condition=None):
        player_pos = (player.x + player.width // 2, player.y + player.height // 2)
        all_beds = quad_tree.query(pygame.Rect(0, 0, MAP_WIDTH, SCREEN_HEIGHT))
        print(f"All beds in QuadTree: {[f'({b.x}, {b.y}) planted={b.is_planted} watered={b.is_watered} ripe={b.is_ripe}' for b in all_beds if b.obj_type == 'bed']}")
        nearest, dist = quad_tree.find_nearest(player_pos, condition)
        if nearest:
            print(f"Nearest bed found via QuadTree: {nearest.obj_type} at distance {dist}, "
                  f"planted: {nearest.is_planted}, watered: {nearest.is_watered}, ripe: {nearest.is_ripe}, "
                  f"watering_start_time: {nearest.watering_start_time}")
        else:
            print("No suitable bed found via QuadTree")
        return nearest

    def find_nearest_mill_quad(player, condition=None):
        player_pos = (player.x + player.width // 2, player.y + player.height // 2)
        all_mills = quad_tree.query(pygame.Rect(0, 0, MAP_WIDTH, SCREEN_HEIGHT))
        print(f"All mills in QuadTree: {[f'({m.x}, {m.y}) processing={m.is_processing}' for m in all_mills if m.obj_type == 'mill']}")
        nearest, dist = quad_tree.find_nearest(player_pos, condition)
        if nearest:
            print(f"Nearest mill found via QuadTree: {nearest.obj_type} at distance {dist}, processing: {nearest.is_processing}")
        else:
            print("No suitable mill found via QuadTree")
        return nearest

    def find_nearest_canning_cellar_quad(player, condition=None):
        player_pos = (player.x + player.width // 2, player.y + player.height // 2)
        all_cellars = quad_tree.query(pygame.Rect(0, 0, MAP_WIDTH, SCREEN_HEIGHT))
        print(f"All canning cellars in QuadTree: {[f'({c.x}, {c.y}) processing={c.is_processing}' for c in all_cellars if c.obj_type == 'canning_cellar']}")
        nearest, dist = quad_tree.find_nearest(player_pos, condition)
        if nearest:
            print(f"Nearest canning cellar found via QuadTree: {nearest.obj_type} at distance {dist}, processing: {nearest.is_processing}")
        else:
            print("No suitable canning cellar found via QuadTree")
        return nearest

    while running:
        current_time = time.time()
        if current_time - last_save_time >= auto_save_interval:
            save_game(player, house, objects, camera_x, screen, harvest_count, level, coins, harvest, products, language)
            last_save_time = current_time
            print(get_text("Auto-save completed!", language))

        menu_manager.update(coins, harvest, products, level)

        for event in pygame.event.get():
            print(f"Game loop received event: {event}")
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                if menu_manager.active_menu:
                    menu_manager.close_all()
                else:
                    save_game(player, house, objects, camera_x, screen, harvest_count, level, coins, harvest, products, language)
                    return "main_menu"
            elif event.type == pygame.ACTIVEEVENT:
                if event.state & app_active:
                    if event.gain == 0:
                        game_context["window_minimized"] = True
                        game_context["window_active"] = False
                        print("Window minimized (using ACTIVEEVENT), continuing in background")
                    else:
                        game_context["window_minimized"] = False
                        game_context["window_active"] = True
                        print("Window restored (using ACTIVEEVENT)")
                elif event.state & (app_mouse_focus | app_input_focus):
                    if event.gain == 0:
                        game_context["window_active"] = False
                        print("Window lost focus (using ACTIVEEVENT), continuing in background")
                    else:
                        game_context["window_active"] = True
                        print("Window gained focus (using ACTIVEEVENT)")
            elif event.type == pygame.MOUSEBUTTONDOWN:
                print(f"Processing MOUSEBUTTONDOWN event: button={event.button}, pos={pygame.mouse.get_pos()}")
                result = handle_input(player, objects, camera_x, screen_width, MAP_WIDTH, screen_height, game_context, coins,
                                      harvest, harvest_count, level, products, event)
                print(f"Objects after handle_input: {[obj.obj_type for obj in objects]}")
                if result in ["exit", "main_menu"]:
                    return result
                elif isinstance(result, tuple) and len(result) == 3:
                    coins, harvest, products = result
                elif isinstance(result, dict):
                    if result.get("action") == "build":
                        coins -= result["cost_coins"]
                        if "cost_harvest" in result:
                            harvest -= result["cost_harvest"]
                        if "cost_products" in result:
                            products -= result["cost_products"]
                        quad_tree.insert(objects[-1])
                    elif result.get("action") == "plant":
                        coins -= result["cost_coins"]
                    elif result.get("action") == "sell":
                        coins += result["value"]
                        harvest -= result["harvest_sold"]
                        products -= result["products_sold"]
                    elif result.get("action") == "move_complete":
                        moved_obj = result.get("moved_obj")
                        if moved_obj:
                            quad_tree.update_position(moved_obj, moved_obj.x, moved_obj.y)
                    elif result.get("action") == "destroy_complete":
                        destroyed_obj = result.get("destroyed_obj")
                        if destroyed_obj:
                            quad_tree.remove(destroyed_obj)

        target_beds = [obj for obj in objects if obj.obj_type == "bed"]
        mills = [obj for obj in objects if obj.obj_type == "mill"]
        canning_cellars = [obj for obj in objects if obj.obj_type == "canning_cellar"]
        for bed in target_beds:
            bed.update()
        for mill in mills:
            products += mill.update()
        for cellar in canning_cellars:
            products += cellar.update()

        if player.state in ["idle", "walking", "watering", "harvesting"]:
            current_time_ms = pygame.time.get_ticks()
            if player.state in ["watering", "harvesting"]:
                action_duration = 2000
                if current_time_ms - player.action_start_time >= action_duration:
                    player.state = "idle"
                    if player.state == "watering":
                        print(f"Completed watering action, returning to idle at ({player.x}, {player.y})")
                    elif player.state == "harvesting":
                        print(f"Completed harvesting action, returning to idle at ({player.x}, {player.y}), harvest now: {harvest}")

            if player.state == "idle":
                print(f"Player is idle at ({player.x}, {player.y}), harvest: {harvest}, products: {products}")
                # Сбрасываем все цели перед новой проверкой
                game_context["target_canning_cellar"] = None
                game_context["target_mill"] = None
                game_context["target_bed"] = None

                # Проверка переработки с приоритетом
                if harvest >= 4:
                    print(f"Player has {harvest} harvest, looking for canning cellar")
                    target_cellar = find_nearest_canning_cellar_quad(
                        player,
                        lambda c: c.obj_type == "canning_cellar" and not c.is_processing
                    )
                    if target_cellar:
                        game_context["target_canning_cellar"] = target_cellar
                        player_rect = pygame.Rect(player.x, player.y, player.width, player.height)
                        cellar_rect = pygame.Rect(target_cellar.x, target_cellar.y, target_cellar.width, target_cellar.height)
                        if player_rect.colliderect(cellar_rect):
                            harvest_used = target_cellar.start_processing(harvest, products)
                            harvest -= harvest_used
                            print(f"Started processing at canning cellar, used {harvest_used} harvest, returning to idle")
                        else:
                            player.target_x = target_cellar.x + target_cellar.width // 2 - player.width // 2
                            player.target_y = target_cellar.y + target_cellar.height // 2 - player.height // 2
                            player.target_x = max(0, min(player.target_x, MAP_WIDTH - player.width))
                            player.target_y = max(0, min(player.target_y, SCREEN_HEIGHT - player.height))
                            player.state = "walking"
                            print(f"Player moving to canning cellar at ({player.target_x}, {player.target_y})")
                        continue  # Переходим к следующей итерации цикла

                if harvest >= 2:
                    print(f"Player has {harvest} harvest, looking for mill")
                    target_mill = find_nearest_mill_quad(
                        player,
                        lambda m: m.obj_type == "mill" and not m.is_processing
                    )
                    if target_mill:
                        game_context["target_mill"] = target_mill
                        player_rect = pygame.Rect(player.x, player.y, player.width, player.height)
                        mill_rect = pygame.Rect(target_mill.x, target_mill.y, target_mill.width, target_mill.height)
                        if player_rect.colliderect(mill_rect):
                            harvest_used = target_mill.start_processing(harvest)
                            harvest -= harvest_used
                            print(f"Started processing at mill, used {harvest_used} harvest, returning to idle")
                        else:
                            player.target_x = target_mill.x + target_mill.width // 2 - player.width // 2
                            player.target_y = target_mill.y + target_mill.height // 2 - player.height // 2
                            player.target_x = max(0, min(player.target_x, MAP_WIDTH - player.width))
                            player.target_y = max(0, min(player.target_y, SCREEN_HEIGHT - player.height))
                            player.state = "walking"
                            print(f"Player moving to mill at ({player.target_x}, {player.target_y})")
                        continue  # Переходим к следующей итерации цикла

                # Если нет переработки, проверяем грядки
                print(f"Player is idle at ({player.x}, {player.y}), looking for a bed to water")
                target_bed = find_nearest_bed_quad(
                    player,
                    lambda b: b.obj_type == "bed" and b.is_planted and not b.is_watered and not b.is_ripe and b.watering_start_time is None
                )
                if not target_bed:
                    print("No bed to water found, checking for ripe beds")
                    target_bed = find_nearest_bed_quad(
                        player,
                        lambda b: b.obj_type == "bed" and b.is_ripe
                    )
                if target_bed:
                    game_context["target_bed"] = target_bed
                    player_rect = pygame.Rect(player.x, player.y, player.width, player.height)
                    bed_rect = pygame.Rect(target_bed.x, target_bed.y, target_bed.width, target_bed.height)
                    print(f"Target bed at ({target_bed.x}, {target_bed.y}), planted: {target_bed.is_planted}, watered: {target_bed.is_watered}, ripe: {target_bed.is_ripe}")
                    if player_rect.colliderect(bed_rect):
                        if target_bed.is_planted and not target_bed.is_watered and not target_bed.is_ripe and target_bed.watering_start_time is None:
                            target_bed.water()
                            player.start_action("watering")
                            print(f"Started watering bed at ({target_bed.x}, {target_bed.y})")
                        elif target_bed.is_ripe:
                            seed = next((s for s in SEEDS if s["name"] == target_bed.plant_type), SEEDS[0])
                            harvest_yield = seed["harvest_yield"]
                            target_bed.harvest()
                            player.start_action("harvesting")
                            harvest += harvest_yield
                            harvest_count += 1
                            harvest_threshold = LEVEL_THRESHOLDS.get(level, float('inf'))
                            if harvest_count >= harvest_threshold:
                                level = min(level + 1, max(LEVEL_THRESHOLDS.keys()))
                                print(get_text("Level up! New level: {level}", language).format(level=level))
                            print(f"Harvested bed at ({target_bed.x}, {target_bed.y}), earned {harvest_yield} harvest, harvest count: {harvest_count}")
                    else:
                        player.target_x = target_bed.x + target_bed.width // 2 - player.width // 2
                        player.target_y = target_bed.y + target_bed.height // 2 - player.height // 2
                        player.target_x = max(0, min(player.target_x, MAP_WIDTH - player.width))
                        player.target_y = max(0, min(player.target_y, SCREEN_HEIGHT - player.height))
                        player.state = "walking"
                        print(f"Player moving to bed at ({player.target_x}, {player.target_y})")

            # Сбрасываем неиспользованные цели
            if player.state != "walking" or game_context["target_canning_cellar"] is None:
                game_context["target_canning_cellar"] = None
            if player.state != "walking" or game_context["target_mill"] is None:
                game_context["target_mill"] = None
            if player.state != "walking" or game_context["target_bed"] is None:
                game_context["target_bed"] = None

        player.x = max(0, min(player.x, MAP_WIDTH - player.width))
        player.y = max(0, min(player.y, SCREEN_HEIGHT - player.height))
        player.move()

        print(f"Player state: {player.state}, Position: ({player.x}, {player.y}), Target bed: {game_context['target_bed']}, "
              f"Target mill: {game_context['target_mill']}, Target canning cellar: {game_context['target_canning_cellar']}")

        if game_context["window_minimized"]:
            clock.tick(10)
        else:
            clock.tick(60)
            camera_x = render_game(screen, player, objects, camera_x, screen_width, MAP_WIDTH, coins, harvest, products,
                                   level, game_context)

        pygame.display.flip()

    return "main_menu"