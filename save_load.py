# save_load.py
import json
import os
import time
import pygame
from entities import Player, Bed, MarketStall, Mill, CanningCellar, MapObject  # Импортируем классы

def filter_dict(data, exclude_types=(pygame.Surface, pygame.Rect, pygame.Color)):
    """Рекурсивно фильтрует словарь, исключая несохраняемые объекты."""
    if isinstance(data, dict):
        return {k: filter_dict(v, exclude_types) for k, v in data.items()
                if not isinstance(v, exclude_types)}
    elif isinstance(data, list):
        return [filter_dict(item, exclude_types) for item in data]
    elif isinstance(data, (int, float, str, bool, type(None))):
        return data
    return str(data)  # Преобразуем несохраняемые объекты в строку (для отладки)

def list_saves():
    """Возвращает список сохранений с информацией о файлах и временных метках."""
    saves_dir = "saves"
    if not os.path.exists(saves_dir):
        os.makedirs(saves_dir)
        print(f"Создана папка {saves_dir}")
    save_files = [f for f in os.listdir(saves_dir) if f.endswith(".json")]
    save_data = []
    print(f"Найденные файлы в {saves_dir}: {save_files}")
    for file_name in save_files:
        file_path = os.path.join(saves_dir, file_name)
        timestamp = os.path.getmtime(file_path)
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            save_data.append({"filename": file_name, "timestamp": timestamp, "data": data})

        except json.JSONDecodeError as e:
            print(f"Ошибка при декодировании файла {file_name}: {e}. Файл будет пропущен.")
            continue  # Пропускаем повреждённый файл
    return sorted(save_data, key=lambda x: x["timestamp"], reverse=True)  # Сортируем по убыванию времени

def load_game(screen, filename=None):
    """Загружает игру из указанного файла или последнего сохранения, если filename не задан."""
    saves_dir = "saves"
    if not os.path.exists(saves_dir):
        print(f"Папка {saves_dir} не существует")
        return None

    if filename is None:
        save_files = list_saves()

        if not save_files:
            print("Нет доступных сохранений")
            return None
        filename = save_files[0]["filename"]  # Берем файл с максимальным timestamp (последнее сохранение)

    file_path = os.path.join(saves_dir, filename)
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Восстановление данных
            player_data = data.get("player", {})
            house_data = data.get("house", {})
            objects_data = data.get("objects", [])
            camera_x = data.get("camera_x", 0)
            harvest_count = data.get("harvest_count", 0)
            level = data.get("level", 1)
            coins = data.get("coins", 10)
            harvest = data.get("harvest", 0)
            products = data.get("products", 0)
            language = data.get("language", "en")
            map_tiles = data.get("map_tiles", [])

            # Восстановление Player
            player = Player(player_data.get("x", 0), player_data.get("y", 0), player_data.get("width", 64),
                           player_data.get("height", 64), player_data.get("speed", 5), language=language)
            player.__dict__.update(player_data)  # Восстанавливаем остальные атрибуты
            player.reload_images()  # Перезагружаем изображения

            # Восстановление MapObject (house)
            house = MapObject(house_data.get("x", 0), house_data.get("y", 0), house_data.get("width", 128),
                             house_data.get("height", 128), house_data.get("color", (0, 0, 0)), house_data.get("obj_type", "house"))
            house.__dict__.update(house_data)
            house.reload_images()

            # Восстановление других объектов
            objects = []
            for obj_data in objects_data:
                obj_type = obj_data.get("obj_type")
                if obj_type == "bed":
                    obj = Bed(obj_data.get("x", 0), obj_data.get("y", 0))
                elif obj_type == "market_stall":
                    obj = MarketStall(obj_data.get("x", 0), obj_data.get("y", 0))
                elif obj_type == "mill":
                    obj = Mill(obj_data.get("x", 0), obj_data.get("y", 0))
                elif obj_type == "canning_cellar":
                    obj = CanningCellar(obj_data.get("x", 0), obj_data.get("y", 0))
                else:
                    obj = MapObject(obj_data.get("x", 0), obj_data.get("y", 0), obj_data.get("width", 64),
                                   obj_data.get("height", 64), obj_data.get("color", (0, 0, 0)), obj_type)
                obj.__dict__.update(obj_data)
                obj.reload_images()  # Перезагружаем изображения
                objects.append(obj)

            print(f"Успешно загружено: player={player}, house={house}, objects={len(objects)}")
            return player, house, objects, camera_x, harvest_count, level, coins, harvest, products, language, map_tiles
        except json.JSONDecodeError as e:
            print(f"Ошибка при загрузке файла {filename}: {e}. Файл повреждён.")
            return None
    print(f"Файл {file_path} не существует")
    return None

def save_game(player, house, objects, camera_x, harvest_count, level, coins, harvest, products, language, game_context, filename):
    """Сохраняет игру в указанный файл."""
    saves_dir = "saves"
    if not os.path.exists(saves_dir):
        os.makedirs(saves_dir)
        print(f"Создана папка {saves_dir}")

    file_path = os.path.join(saves_dir, filename)
    # Фильтруем данные перед сохранением
    filtered_player = player.to_dict()  # Используем to_dict для игрока
    filtered_house = house.to_dict()    # Используем to_dict для дома
    filtered_objects = [obj.to_dict() for obj in objects]  # Используем to_dict для объектов
    filtered_game_context = {
        k: filter_dict(v) for k, v in game_context.items()
        if k not in ["screen", "menu_manager", "target_bed", "target_mill", "target_canning_cellar"]
    }

    save_data = {
        "player": filtered_player,
        "house": filtered_house,
        "objects": filtered_objects,
        "camera_x": camera_x,
        "harvest_count": harvest_count,
        "level": level,
        "coins": coins,
        "harvest": harvest,
        "products": products,
        "language": language,
        "map_tiles": filter_dict(game_context["map_tiles"])
    }
    save_data["game_context"] = filtered_game_context  # Сохраняем отфильтрованный game_context
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(save_data, f, indent=4, ensure_ascii=False)
        print(f"Игра успешно сохранена в {file_path}")