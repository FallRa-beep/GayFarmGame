from config import MAP_WIDTH, SCREEN_HEIGHT
import math
import pygame


def snap_to_grid(value, grid_size=32):
    return (value // grid_size) * grid_size


def check_collision(obj, objects, grid_size=32, allow_touching=False):
    obj_rect = pygame.Rect(obj.x, obj.y, obj.width, obj.height)
    for other in objects:
        if obj == other:
            continue
        other_rect = pygame.Rect(other.x, other.y, other.width, other.height)
        if obj_rect.colliderect(other_rect):
            if not allow_touching:
                return True
            # Проверяем, пересекаются ли объекты более чем на 1 пиксель
            intersection = obj_rect.clip(other_rect)
            if intersection.width > 1 or intersection.height > 1:
                return True
    return False


def find_nearest_bed(player, beds, condition=None):
    nearest_bed = None
    min_distance = float('inf')
    player_rect = pygame.Rect(player.x, player.y, player.width, player.height)

    for bed in beds:
        if condition and not condition(bed):
            continue
        bed_rect = pygame.Rect(bed.x, bed.y, bed.width, bed.height)
        if not player_rect.colliderect(bed_rect):
            distance = math.hypot(bed.x - player.x, bed.y - player.y)
            if distance < min_distance:
                min_distance = distance
                nearest_bed = bed
    return nearest_bed