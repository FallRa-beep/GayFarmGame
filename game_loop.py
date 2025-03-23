import pygame
import time
import random  # Оставляем только используемые импорты
from config import MAP_WIDTH, SCREEN_HEIGHT, LEVEL_THRESHOLDS, SEEDS
from translations import get_text
from entities import Player, Bed, MapObject, MarketStall, Mill, CanningCellar
from menus import MenuManager
from rendering import render_game
from input_handler import handle_input
from game_utils import snap_to_grid
from save_load import save_game
from quadtree import QuadTree
from notifications import NotificationManager
import fonts

def game_loop(screen, player=None, house=None, objects=None, initial_camera_x=0, harvest_count=0, level=1, coins=10,
              harvest=0, products=0, language="en", map_tiles=None,fonts=None):
    clock = pygame.time.Clock()
    screen_width = screen.get_width()
    screen_height = SCREEN_HEIGHT

    # Инициализируем NotificationManager
    notification_manager = NotificationManager(language,fonts)
    menu_manager = MenuManager(language, coins, harvest, products, level, notification_manager=notification_manager, fonts=fonts)
    boundary = pygame.Rect(0, 0, MAP_WIDTH, SCREEN_HEIGHT)
    quad_tree = QuadTree(boundary, capacity=4)


    # Инициализация game_context до его использования
    game_context = {
        "language": language,
        "screen": screen,
        "menu_manager": menu_manager,
        "target_bed": None,
        "target_mill": None,
        "target_canning_cellar": None,
        "last_click_time": 0,
        "window_active": True,
        "window_minimized": False,
        "map_tiles": map_tiles if map_tiles is not None else [],
        "player": player,  # Добавляем данные для сохранения
        "house": house,
        "objects": objects,
        "camera_x": initial_camera_x,
        "harvest_count": harvest_count,
        "level": level,
        "coins": coins,
        "harvest": harvest,
        "products": products,
        "dragging_obj": None,  # Для отслеживания перетаскиваемого объекта
        "preview_obj": None
    }

    if player is None:
        house_x = snap_to_grid(screen_width // 2 - 64, grid_size=32)
        house_y = snap_to_grid(10, grid_size=32)
        house = MapObject(house_x, house_y, 128, 128, (0, 0, 0), "house")
        market_x = snap_to_grid(house_x - 150, grid_size=32)
        market_y = snap_to_grid(house_y + 120, grid_size=32)
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
        objects = [Bed(bed1_x, bed1_y, width=32, height=32), Bed(bed2_x, bed2_y, width=32, height=32),
                   Bed(bed3_x, bed3_y, width=32, height=32), house, market_stall,
                   Mill(mill_x, mill_y), CanningCellar(cellar_x, cellar_y)]
        for obj in objects:
            quad_tree.insert(obj)

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

        # Генерация тайлов травы для фона
        tile_size = 32
        map_tiles = []
        for x in range(0, MAP_WIDTH, tile_size):
            for y in range(0, SCREEN_HEIGHT, tile_size):
                tile_type = random.choice(["grass_tile_1", "grass_tile_2", "grass_tile_3"])
                map_tiles.append({"x": x, "y": y, "type": tile_type})
        game_context["map_tiles"] = map_tiles

        # Обновляем game_context для новой игры
        game_context.update({
            "player": player,
            "house": house,
            "objects": objects,
            "camera_x": camera_x,
            "harvest_count": harvest_count,
            "level": level,
            "coins": coins,
            "harvest": harvest,
            "products": products
        })
    else:
        camera_x = initial_camera_x
        if objects is None:
            objects = []
        has_market_stall = any(obj.obj_type == "market_stall" for obj in objects)
        if not has_market_stall:
            market_x = snap_to_grid(house.x - 150, grid_size=32)  # Правее дома
            market_y = snap_to_grid(house.y + 120, grid_size=32)  # Ниже дома
            market_stall = MarketStall(market_x, market_y)
            objects.append(market_stall)
        for obj in objects:
            quad_tree.insert(obj)

        player.language = language
        player.x = max(0, min(player.x, MAP_WIDTH - player.width))
        player.y = max(0, min(player.y, SCREEN_HEIGHT - player.height))

        # Обновляем game_context для загруженной игры
        game_context.update({
            "player": player,
            "house": house,
            "objects": objects,
            "camera_x": camera_x,
            "harvest_count": harvest_count,
            "level": level,
            "coins": coins,
            "harvest": harvest,
            "products": products
        })

    app_mouse_focus = 1
    app_input_focus = 2
    app_active = 4

    running = True


    def find_nearest_bed_quad(p, condition=None):  # Изменяем имя параметра, чтобы избежать затенения
        player_pos = (p.x + p.width // 2, p.y + p.height // 2)
        nearest, dist = quad_tree.find_nearest(player_pos, condition)
        return nearest

    def find_nearest_mill_quad(p, condition=None):  # Изменяем имя параметра
        player_pos = (p.x + p.width // 2, p.y + p.height // 2)
        nearest, dist = quad_tree.find_nearest(player_pos, condition)
        return nearest

    def find_nearest_canning_cellar_quad(p, condition=None):  # Изменяем имя параметра
        player_pos = (p.x + p.width // 2, p.y + p.height // 2)
        nearest, dist = quad_tree.find_nearest(player_pos, condition)
        return nearest

    result = None  # Инициализируем result, чтобы избежать ошибки
    while running:

        game_context["language"] = language
        menu_manager.update(coins, harvest, products, level)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                result = "exit"
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                if menu_manager.active_menu:
                    menu_manager.close_all()
                else:
                    result = "main_menu"
            elif event.type == pygame.ACTIVEEVENT:
                if event.state & app_active:
                    if event.gain == 0:
                        game_context["window_minimized"] = True
                        game_context["window_active"] = False
                    else:
                        game_context["window_minimized"] = False
                        game_context["window_active"] = True
                elif event.state & (app_mouse_focus | app_input_focus):
                    if event.gain == 0:
                        game_context["window_active"] = False
                    else:
                        game_context["window_active"] = True
            elif event.type == pygame.MOUSEBUTTONDOWN:
                result = handle_input(player, objects, camera_x, screen_width, MAP_WIDTH, screen_height, game_context, coins,
                                      harvest, harvest_count, level, products, event)
                print(f"Handle input result: {result}")  # Отладка
                print(f"Game loop result: {result}")
                if result in ["exit", "main_menu"]:
                    break
                elif isinstance(result, dict):
                    if "updated_resources" in result:
                        coins = result["updated_resources"]["coins"]
                        harvest = result["updated_resources"]["harvest"]
                        products = result["updated_resources"]["products"]
                        print(f"Updated resources: coins={coins}, harvest={harvest}, products={products}")
                        game_context.update({
                            "coins": coins,
                            "harvest": harvest,
                            "products": products
                        })
                    if result.get("action") == "build":
                        if objects:
                            new_obj = objects[-1]
                            if isinstance(new_obj, Bed):
                                grid_x = snap_to_grid(new_obj.x, grid_size=32)
                                grid_y = snap_to_grid(new_obj.y, grid_size=32)
                                new_obj.x = grid_x
                                new_obj.y = grid_y
                            if new_obj not in quad_tree.get_all_objects():
                                quad_tree.insert(new_obj)
                                print(f"Inserted into QuadTree: {new_obj.obj_type} at ({new_obj.x}, {new_obj.y})")
                    elif result.get("action") == "plant":
                        for obj in objects:
                            if obj.obj_type == "bed" and obj.is_planted and not obj.is_watered:
                                quad_tree.remove(obj)
                                quad_tree.insert(obj)
                                break
                    elif result.get("action") == "sell":
                        pass
                    elif result.get("action") == "start_move_preview":
                        game_context["dragging_obj"] = result.get("moved_obj")
                        game_context["preview_obj"] = result.get("preview_obj")  # Сохраняем предпросмотр
                    elif result.get("action") == "move_complete":
                        moved_obj = result.get("moved_obj")
                        if moved_obj and isinstance(moved_obj, Bed):
                            grid_x = snap_to_grid(moved_obj.x, grid_size=32)
                            grid_y = snap_to_grid(moved_obj.y, grid_size=32)
                            moved_obj.x = grid_x
                            moved_obj.y = grid_y
                            quad_tree.update_position(moved_obj, moved_obj.x, moved_obj.y)
                        game_context["dragging_obj"] = None
                        game_context["preview_obj"] = None
                    elif result.get("action") == "destroy_complete":
                        destroyed_obj = result.get("destroyed_obj")
                        if destroyed_obj:
                            quad_tree.remove(destroyed_obj)

        notification_manager.update()

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

            if player.state == "idle":
                game_context["target_canning_cellar"] = None
                game_context["target_mill"] = None
                game_context["target_bed"] = None

                if harvest >= 4:
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
                        else:
                            player.target_x = target_cellar.x + target_cellar.width // 2 - player.width // 2
                            player.target_y = target_cellar.y + target_cellar.height // 2 - player.height // 2
                            player.target_x = max(0, min(player.target_x, MAP_WIDTH - player.width))
                            player.target_y = max(0, min(player.target_y, SCREEN_HEIGHT - player.height))
                            player.state = "walking"
                        continue

                if harvest >= 2:
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
                        else:
                            player.target_x = target_mill.x + target_mill.width // 2 - player.width // 2
                            player.target_y = target_mill.y + target_mill.height // 2 - player.height // 2
                            player.target_x = max(0, min(player.target_x, MAP_WIDTH - player.width))
                            player.target_y = max(0, min(player.target_y, SCREEN_HEIGHT - player.height))
                            player.state = "walking"
                        continue

                target_bed = find_nearest_bed_quad(
                    player,
                    lambda b: b.obj_type == "bed" and b.is_planted and not b.is_watered and b.watering_start_time is None
                )
                if not target_bed:
                    target_bed = find_nearest_bed_quad(
                        player,
                        lambda b: b.obj_type == "bed" and b.is_ripe
                    )
                if target_bed:
                    game_context["target_bed"] = target_bed
                    player_rect = pygame.Rect(player.x, player.y, player.width, player.height)
                    bed_rect = pygame.Rect(target_bed.x, target_bed.y, target_bed.width, target_bed.height)
                    if player_rect.colliderect(bed_rect):
                        if target_bed.is_planted and not target_bed.is_watered and not target_bed.is_ripe and target_bed.watering_start_time is None:
                            target_bed.water()
                            player.start_action("watering")
                            player.direction = "right"
                        elif target_bed.is_ripe:
                            seed = next((s for s in SEEDS if s["name"] == target_bed.plant_type), SEEDS[0])
                            harvest_yield = seed["harvest_yield"]
                            target_bed.harvest()
                            player.start_action("harvesting")
                            player.direction = "right"
                            harvest += harvest_yield
                            harvest_count += 1
                            harvest_threshold = LEVEL_THRESHOLDS.get(level, float('inf'))
                            if harvest_count >= harvest_threshold:
                                level = min(level + 1, max(LEVEL_THRESHOLDS.keys()))
                                game_context["level"] = level
                                notification_manager.add_notification("level_up")
                                print(get_text("Level up! New level: {level}", language).format(level=level))
                    else:
                        player.target_x = target_bed.x - player.width // 2
                        player.target_y = target_bed.y - player.height // 2
                        player.target_x = max(0, min(player.target_x, MAP_WIDTH - player.width))
                        player.target_y = max(0, min(player.target_y, SCREEN_HEIGHT - player.height))
                        player.state = "walking"

            if player.state != "walking" or game_context["target_canning_cellar"] is None:
                game_context["target_canning_cellar"] = None
            if player.state != "walking" or game_context["target_mill"] is None:
                game_context["target_mill"] = None
            if player.state != "walking" or game_context["target_bed"] is None:
                game_context["target_bed"] = None

        player.x = max(0, min(player.x, MAP_WIDTH - player.width))
        player.y = max(0, min(player.y, SCREEN_HEIGHT - player.height))
        player.move()

        clock.tick(60)  # Убираем зависимость от window_minimized
        camera_x = render_game(screen , game_context["language"], player, objects, camera_x, screen_width, MAP_WIDTH, coins, harvest, products,
                               level, game_context,fonts=fonts)
        menu_manager.draw(screen, camera_x, harvest, products)  # Рисуем меню
        notification_manager.draw(screen)
        # Обновляем camera_x в game_context
        game_context["camera_x"] = camera_x

        pygame.display.flip()

        if result in ["exit", "main_menu"]:
            game_context.update({
                "player": player,
                "house": house,
                "objects": objects,
                "camera_x": camera_x,
                "harvest_count": harvest_count,
                "level": level,
                "coins": coins,
                "harvest": harvest,
                "products": products
            })
            break

    if result == "main_menu":
        return result, game_context
    return result