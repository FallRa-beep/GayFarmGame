import pygame
import math
class QuadTree:
    def __init__(self, boundary, capacity=4):
        self.boundary = boundary
        self.capacity = capacity
        self.objects = []
        self.divided = False
        self.northwest = None
        self.northeast = None
        self.southwest = None
        self.southeast = None

    def subdivide(self):
        x, y, w, h = self.boundary.x, self.boundary.y, self.boundary.width, self.boundary.height
        half_w, half_h = w // 2, h // 2
        self.northwest = QuadTree(pygame.Rect(x, y, half_w, half_h), self.capacity)
        self.northeast = QuadTree(pygame.Rect(x + half_w, y, half_w, half_h), self.capacity)
        self.southwest = QuadTree(pygame.Rect(x, y + half_h, half_w, half_h), self.capacity)
        self.southeast = QuadTree(pygame.Rect(x + half_w, y + half_h, half_w, half_h), self.capacity)
        self.divided = True

    def insert(self, obj):
        obj_center = (obj.x + obj.width // 2, obj.y + obj.height // 2)
        if not self.boundary.collidepoint(obj_center):
            return False
        if len(self.objects) < self.capacity and not self.divided:
            self.objects.append(obj)
            return True
        if not self.divided:
            self.subdivide()
            for existing_obj in self.objects[:]:
                self.insert(existing_obj)
            self.objects.clear()
        return (self.northwest.insert(obj) or self.northeast.insert(obj) or
                self.southwest.insert(obj) or self.southeast.insert(obj))

    def remove(self, obj):
        obj_center = (obj.x + obj.width // 2, obj.y + obj.height // 2)
        if not self.boundary.collidepoint(obj_center):
            return False
        if obj in self.objects:
            self.objects.remove(obj)
            return True
        if self.divided:
            return (self.northwest.remove(obj) or self.northeast.remove(obj) or
                    self.southwest.remove(obj) or self.southeast.remove(obj))
        return False

    def update_position(self, obj, new_x, new_y):
        if self.remove(obj):
            obj.x = new_x
            obj.y = new_y
            self.insert(obj)
            return True
        return False

    def query(self, rect):
        found = []
        if not self.boundary.colliderect(rect):
            print(f"Boundary {self.boundary} does not collide with {rect}")
            return found
        for obj in self.objects:
            obj_center = (obj.x + obj.width // 2, obj.y + obj.height // 2)
            if rect.collidepoint(obj_center):
                found.append(obj)
        if self.divided:
            found.extend(self.northwest.query(rect))
            found.extend(self.northeast.query(rect))
            found.extend(self.southwest.query(rect))
            found.extend(self.southeast.query(rect))
        return found

    def find_nearest(self, point, condition=None, max_range=3000):  # Ограничим до размера карты
        nearest = None
        min_dist = max_range
        range_rect = pygame.Rect(point[0] - max_range, point[1] - max_range, max_range * 2, max_range * 2)
        print(f"Searching in range_rect: {range_rect}")
        candidates = self.query(range_rect)
        print(f"Candidates found: {[f'({obj.x}, {obj.y}) type={obj.obj_type}' for obj in candidates]}")
        for obj in candidates:
            if condition:
                condition_result = condition(obj)
                print(f"Checking {obj.obj_type} at ({obj.x}, {obj.y}): condition={condition_result}")
                if not condition_result:
                    continue
            obj_center = (obj.x + obj.width // 2, obj.y + obj.height // 2)
            dist = math.hypot(point[0] - obj_center[0], point[1] - obj_center[1])
            if dist < min_dist:
                min_dist = dist
                nearest = obj
        print(f"Nearest selected: {nearest.obj_type if nearest else 'None'} at distance {min_dist}")
        return nearest, min_dist

    def clear(self):
        self.objects.clear()
        self.divided = False
        self.northwest = None
        self.northeast = None
        self.southwest = None
        self.southeast = None