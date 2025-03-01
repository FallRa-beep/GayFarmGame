import pygame
import json
from config import MAP_WIDTH, SCREEN_HEIGHT
from entities import Player, MapObject, Bed, MarketStall, Mill, CanningCellar
from game_utils import snap_to_grid

OBJECT_TYPE_TO_CLASS = {
    "bed": Bed,
    "market_stall": MarketStall,
    "mill": Mill,
    "canning_cellar": CanningCellar
}

def save_game(player, house, objects, camera_x, screen, harvest_count, level, coins, harvest, products, language):
    data = {
        "player": {k: v for k, v in player.__dict__.items() if k != "images"},
        "house": house.to_dict(),
        "objects": [obj.to_dict() for obj in objects],
        "camera_x": camera_x,
        "harvest_count": harvest_count,
        "level": level,
        "coins": coins,
        "harvest": harvest,
        "products": products,
        "language": language
    }
    with open("save_game.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    print("Game saved successfully")

def load_game(screen):
    try:
        with open("save_game.json", "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print("No save file found, returning default values")
        return None, None, [], 0, 0, 1, 10, 0, 0, "en"
    except json.JSONDecodeError as e:
        print(f"Error decoding save_game.json: {e}")
        return None, None, [], 0, 0, 1, 10, 0, 0, "en"

    player_data = data["player"]
    house_data = data["house"]
    objects_data = data["objects"]
    camera_x = data["camera_x"]
    harvest_count = data["harvest_count"]
    level = data["level"]
    coins = data["coins"]
    harvest = data["harvest"]
    products = data["products"]
    language = data["language"]

    player = Player(player_data["x"], player_data["y"], player_data["width"], player_data["height"],
                    player_data["speed"], language)
    player.__dict__.update(player_data)

    house = MapObject(house_data["x"], house_data["y"], house_data["width"], house_data["height"],
                      house_data["color"], house_data["obj_type"])
    house.__dict__.update(house_data)  # Включает movable

    objects = []
    for obj_data in objects_data:
        obj_type = obj_data["obj_type"]
        if obj_type in OBJECT_TYPE_TO_CLASS:
            obj_class = OBJECT_TYPE_TO_CLASS[obj_type]
            obj = obj_class(obj_data["x"], obj_data["y"], obj_data["width"], obj_data["height"])
        else:
            obj = MapObject(obj_data["x"], obj_data["y"], obj_data["width"], obj_data["height"],
                            obj_data["color"], obj_type)
        obj.__dict__.update(obj_data)  # Включает movable и другие параметры
        objects.append(obj)

    for obj in objects:
        obj.x = max(0, min(obj.x, MAP_WIDTH - obj.width))
        obj.y = max(0, min(obj.y, SCREEN_HEIGHT - obj.height))

    return player, house, objects, camera_x, harvest_count, level, coins, harvest, products, language