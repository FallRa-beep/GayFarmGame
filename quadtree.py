import pygame
import math

class QuadTree:
    def __init__(self, boundary, capacity=4):
        """
        Инициализация QuadTree.
        :param boundary: pygame.Rect - прямоугольник, определяющий границы области
        :param capacity: int - максимальное количество объектов в узле до разделения
        """
        self.boundary = boundary
        self.capacity = capacity
        self.objects = []
        self.divided = False
        self.northwest = None
        self.northeast = None
        self.southwest = None
        self.southeast = None

    def subdivide(self):
        """
        Разделяет текущий узел на четыре дочерних узла.
        """
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
            print(f"Object {obj.obj_type} at ({obj.x}, {obj.y}) outside boundary {self.boundary}")
            return False
        if len(self.objects) < self.capacity and not self.divided:
            self.objects.append(obj)
            print(f"Inserted {obj.obj_type} at ({obj.x}, {obj.y}) into leaf node")
            return True
        if not self.divided:
            self.subdivide()
            print(f"Subdivided node at {self.boundary}")
            for existing_obj in self.objects[:]:
                self.insert(existing_obj)
            self.objects.clear()
        success = (self.northwest.insert(obj) or
                   self.northeast.insert(obj) or
                   self.southwest.insert(obj) or
                   self.southeast.insert(obj))
        if not success:
            print(f"Failed to insert {obj.obj_type} at ({obj.x}, {obj.y}) into any child node")
        return success

    def remove(self, obj):
        """
        Удаляет объект из QuadTree.
        :param obj: объект для удаления
        :return: bool - успешно ли удален объект
        """
        obj_center = (obj.x + obj.width // 2, obj.y + obj.height // 2)
        if not self.boundary.collidepoint(obj_center):
            return False
        if obj in self.objects:
            self.objects.remove(obj)
            return True
        if self.divided:
            return (self.northwest.remove(obj) or
                    self.northeast.remove(obj) or
                    self.southwest.remove(obj) or
                    self.southeast.remove(obj))
        return False

    def update_position(self, obj, new_x, new_y):
        """
        Обновляет позицию объекта в QuadTree.
        :param obj: объект для обновления
        :param new_x: новая координата x
        :param new_y: новая координата y
        :return: bool - успешно ли обновлена позиция
        """
        if self.remove(obj):
            old_x, old_y = obj.x, obj.y
            obj.x, obj.y = new_x, new_y
            if not self.insert(obj):
                obj.x, obj.y = old_x, old_y
                self.insert(obj)
                return False
            return True
        return False

    def query(self, rect):
        """
        Находит все объекты, пересекающиеся с заданным прямоугольником.
        :param rect: pygame.Rect - область запроса
        :return: list - список объектов в области
        """
        found = []
        if not self.boundary.colliderect(rect):
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

    def find_nearest(self, point, condition=None, max_range=3000):
        """
        Находит ближайший объект к заданной точке.
        :param point: tuple (x, y) - точка поиска
        :param condition: callable - опциональное условие для фильтрации объектов
        :param max_range: float - максимальная дистанция поиска
        :return: tuple (object, distance) - ближайший объект и расстояние до него
        """
        nearest = None
        min_dist = max_range
        range_rect = pygame.Rect(point[0] - max_range, point[1] - max_range, max_range * 2, max_range * 2)
        candidates = self.query(range_rect)
        for obj in candidates:
            if condition and not condition(obj):
                continue
            obj_center = (obj.x + obj.width // 2, obj.y + obj.height // 2)
            dist = math.hypot(point[0] - obj_center[0], point[1] - obj_center[1])
            if dist < min_dist:
                min_dist = dist
                nearest = obj
        return nearest, min_dist

    def clear(self):
        """
        Очищает QuadTree, удаляя все объекты и дочерние узлы.
        """
        self.objects.clear()
        self.divided = False
        self.northwest = None
        self.northeast = None
        self.southwest = None
        self.southeast = None

    def get_all_objects(self):
        """
        Возвращает все объекты в QuadTree (для отладки).
        :return: list - список всех объектов
        """
        all_objects = self.objects.copy()
        if self.divided:
            all_objects.extend(self.northwest.get_all_objects())
            all_objects.extend(self.northeast.get_all_objects())
            all_objects.extend(self.southwest.get_all_objects())
            all_objects.extend(self.southeast.get_all_objects())
        return all_objects