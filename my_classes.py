from OpenGL.GLUT import glutGet, GLUT_SCREEN_HEIGHT, GLUT_SCREEN_WIDTH
from abc import ABC, abstractmethod
from enum import Enum


class Adaption:
    @classmethod
    def y_adapted(cls, y_na):
        return ((DeviceProperties.device_height - 1) - y_na)

class Coordinates:
    x_min = y_min = x_max = y_max = -1

    @classmethod
    def set_max_point(cls, x, y):
        cls.x_max = x
        cls.y_max = y

    @classmethod
    def set_min_point(cls, x, y):
        cls.x_min = x
        cls.y_min = y

    @classmethod
    @property
    def furthest_point(cls):
        return (cls.x_max, cls.y_max)

    @classmethod
    @property
    def closest_point(cls):
        return (cls.x_min, cls.y_min)

    @classmethod
    def set_furthest_point(cls, x, y):
        cls.set_max_point(x, y)

    @classmethod
    def set_closest_point(cls, x, y):
        cls.set_min_point(x, y)

    @classmethod
    def find_min_max_point_and_set(cls, vertices):
        cls.x_min = cls.y_min= 1e10
        for vertex in vertices:
            x, y = vertex[0], vertex[1]
            cls.x_max = max(cls.x_max, x)
            cls.x_min = min(cls.x_min, x)
            cls.y_min = min(cls.y_min, y)
            cls.y_max = max(cls.y_max, y)

    @classmethod
    def show_info(cls):
        return f'x_min: {cls.x_min}\nx_max: {cls.x_max}\ny_min: {cls.y_min}\ny_max: {cls.y_max}'

class RealCoordinates(Coordinates):
    pass

class DeviceCoordinates(Coordinates):
    _adapted = True

    @classmethod
    def adapted(cls, flag):
        cls._adapted = flag

    @classmethod
    def is_adapted(cls):
        return cls._adapted

    @classmethod
    def post_adaption_fix(cls):
        # correctly adapted
        if (cls.y_max >= cls.y_min):
            return

        cls.y_max, cls.y_min = cls.y_min, cls.y_max

    @classmethod
    def check_and_fix_adaption(cls, y):
        yA = (y if cls.is_adapted() else Adaption.y_adapted(y))
        return yA;

    @classmethod
    def set_max_point(cls, x, y):
        super().set_max_point(x, cls.check_and_fix_adaption(y))
        if cls.y_max != -1 and cls.y_min != -1:
            cls.post_adaption_fix()

    @classmethod
    def set_min_point(cls, x, y):
        super().set_min_point(x, cls.check_and_fix_adaption(y))

        if cls.y_max != -1 and cls.y_min != -1:
            cls.post_adaption_fix()

    @classmethod
    def set_closest_point(cls, x, y):
        cls.set_min_point(x, y)

    @classmethod
    def set_furthest_point(cls, x, y):
        cls.set_max_point(x, y)

class DeviceProperties:
    device_width = device_height = window_width = window_height = 0

    @classmethod
    def set_window_size(cls, width, height):
        cls.window_width = width
        cls.window_height = height

    @classmethod
    def set_resolution(cls, m, n):
        cls.device_width = m
        cls.device_height = n

    @classmethod
    def get_window_size(cls):
        return (cls.window_width, cls.window_height)

    @classmethod
    def get_resolution(cls):
        return (cls.device_width, cls.device_height)

    @classmethod
    def get_center(cls):
        screen_width = glutGet(GLUT_SCREEN_WIDTH)
        screen_height = glutGet(GLUT_SCREEN_HEIGHT)

        return (
            (int((screen_width - cls.window_width) / 2),
             int((screen_height - cls.window_height) / 2))
        )

class MappingTypes(Enum):
    REAL_TO_DEVICE = 1
    DEVICE_TO_REAL = 2

class Scale:
    x_scale = y_scale = 0

    @classmethod
    def setup_scale(cls):
        cls.calculate_x_and_y_scale()

    @classmethod
    def get_x_scale(cls):
        return cls.x_scale

    @classmethod
    def get_y_scale(cls):
        return cls.y_scale

    @classmethod
    def calculate_x_and_y_scale(cls):
        cls.calculate_x_scale()
        cls.calculate_y_scale()

    # x_scale = (x_device_max - x_device_min) / (x_real_max - x_real_min)
    @classmethod
    def calculate_x_scale(cls):
        cls.x_scale = (DeviceCoordinates.x_max - DeviceCoordinates.x_min) \
                    / (RealCoordinates.x_max - RealCoordinates.x_min)

        if(Mapping.type == MappingTypes.DEVICE_TO_REAL):
            cls.x_scale = cls.x_scale ** -1

    @classmethod
    def show_info(cls):
        return f'x_scale: {cls.x_scale}\ny_scale: {cls.y_scale}'


    # y_scale = (y_device_max - y_device_min) / (y_real_max - y_real_min)
    @classmethod
    def calculate_y_scale(cls):
        cls.y_scale = (DeviceCoordinates.y_max - DeviceCoordinates.y_min) \
                    / (RealCoordinates.y_max - RealCoordinates.y_min)

        if(Mapping.type is MappingTypes.DEVICE_TO_REAL):
            cls.y_scale = cls.y_scale ** -1


    @classmethod
    def check_distortion_and_fix(cls):
        cls.calculate_x_and_y_scale()
        if cls.x_scale == cls.y_scale:
            return

        cls.fix_distortion()

    @classmethod
    def fix_distortion(cls):
        cls.x_scale = cls.y_scale = min(cls.x_scale, cls.y_scale)

    @classmethod
    def is_distorted(cls):
        return cls.x_scale != cls.y_scale

class Mapping(ABC):
    type = MappingTypes(1)

    @abstractmethod
    def map_x(self, x_real):
        pass

    @abstractmethod
    def map_y(self, y_real):
        pass

    @abstractmethod
    def map_points(self, vertices):
        pass

class RealToDeviceMapping(Mapping):
    # x_device = x_device_min + x_scale * (x_real - x_real_min)
    def real_to_device(self, x_real, y_real):
        return (int(self.map_x(x_real)), int(self.map_y(y_real)))

    # x_device = x_device_min + x_scale * (x_real - x_real_min)
    def map_x(self, x_real):
        return DeviceCoordinates.x_min + Scale.get_x_scale() * (x_real - RealCoordinates.x_min)

    # y_device = y_device_min + y_scale * (y_real - y_real_min)
    def map_y(self, y_real):
        return DeviceCoordinates.y_min + Scale.get_y_scale() * (y_real - RealCoordinates.y_min)

    def map_points(self, vertices):
        mapped_points = []
        for vertex in vertices:
            mapped_points.append(self.real_to_device(*vertex))

        return mapped_points

class DeviceToRealMapping(Mapping):
    # x_real = x_real_min + x_scale * (x_device - x_device_min)
    def device_to_real(self, x_device, y_device):
        return (int(self.map_x(x_device)), int(self.map_y(y_device)))

    # x_real = x_real_min + x_scale * (x_device - x_device_min)
    def map_x(self, x_device):
        return RealCoordinates.x_min + Scale.get_x_scale() * (x_device - DeviceCoordinates.x_min)

    # y_real = y_real_min + y_scale * (y_device - y_device_min)
    def map_y(self, y_device):
        return RealCoordinates.y_min + Scale.get_y_scale() * (y_device - DeviceCoordinates.y_min)

    def map_points(self, vertices):
        mapped_points = []
        for vertex in vertices:
            mapped_points.append(self.device_to_real(*vertex))

        return mapped_points

class RGB:
    WHITE = (1.0, 1.0, 1.0)
    BLACK = (0.0, 0.0, 0.0)
    RED   = (1.0, 0.0, 0.0)
    GREEN = (0.0, 1.0, 0.0)
    BLUE  = (0.0, 0.0, 1.0)

    @classmethod
    def convert_0_255(cls, r, g, b):
        return r/255, g/255, b/255

    # todo
    @classmethod
    def convert_hex_to_rgb(cls, hex):
        start = 0
        end = len(hex)
        if hex[start] == '#':
            start += 1

        for i in range(start, end, 2):
            # value = to_rgb(hex[i], hex[i + 1])
            value = 0
            if i == 2:
                r = value
            elif i == 4:
                g = value
            elif i == 6:
                b = value

        raise NotImplementedError
        return (r, g, b)

    @classmethod
    def color(cls, r, g, b):
        return (r, g, b)

def main():
    pass

if __name__ == '__main__':
    main()
