from dataclasses import dataclass

@dataclass
class MapConfig:
    MAP_NAME: str
    MAP_FILE_NAME: str
    MAP_WIDTH_CM: float
    MAP_HEIGHT_CM: float
    MAP_MARGIN_CM: float
    MAP_CM_PER_PIXELS: float
    
    ROBOT_INIT_POS_X_CM: float
    ROBOT_INIT_POS_Y_CM: float
    ROBOT_INIT_ANGLE: float
    
    MIN_LEFT_MARKER_COUNTER: int


map0 = MapConfig(
    MAP_NAME = "map0",
    MAP_FILE_NAME = "map0.png",
    MAP_WIDTH_CM = 96.0,
    MAP_HEIGHT_CM = 301.0,
    MAP_MARGIN_CM = 25.0,
    MAP_CM_PER_PIXELS = 3.0,
    ROBOT_INIT_POS_X_CM = 11.0,
    ROBOT_INIT_POS_Y_CM = 200.0,
    ROBOT_INIT_ANGLE = 90.0,
    MIN_LEFT_MARKER_COUNTER = 20,
)

map1 = MapConfig(
    MAP_NAME = "map1",
    MAP_FILE_NAME = "map1.png",
    MAP_WIDTH_CM = 230.0,
    MAP_HEIGHT_CM = 395.0,
    MAP_MARGIN_CM = 25.0,
    MAP_CM_PER_PIXELS = 2.0,
    ROBOT_INIT_POS_X_CM = 11.0,
    ROBOT_INIT_POS_Y_CM = 125.0,
    ROBOT_INIT_ANGLE = 90.0,
    MIN_LEFT_MARKER_COUNTER = 20,
)

map2 = MapConfig(
    MAP_NAME = "map2",
    MAP_FILE_NAME = "map2.png",
    MAP_WIDTH_CM = 186.0,
    MAP_HEIGHT_CM = 354.0,
    MAP_MARGIN_CM = 25.0,
    MAP_CM_PER_PIXELS = 2.0,
    ROBOT_INIT_POS_X_CM = 178.0,
    ROBOT_INIT_POS_Y_CM = 75.0,
    ROBOT_INIT_ANGLE = 270.0,
    MIN_LEFT_MARKER_COUNTER = 26,
)

map3 = MapConfig(
    MAP_NAME = "map3",
    MAP_FILE_NAME = "map3.png",
    MAP_WIDTH_CM = 545.0,
    MAP_HEIGHT_CM = 595.0,
    MAP_MARGIN_CM = 25.0,
    MAP_CM_PER_PIXELS = 1.5,
    ROBOT_INIT_POS_X_CM = 175.0,
    ROBOT_INIT_POS_Y_CM = 12.0,
    ROBOT_INIT_ANGLE = 180.0,
    MIN_LEFT_MARKER_COUNTER = 40,
)

map4 = MapConfig(
    MAP_NAME = "map4",
    MAP_FILE_NAME = "map4.png",
    MAP_WIDTH_CM = 600.0,
    MAP_HEIGHT_CM = 378.0,
    MAP_MARGIN_CM = 25.0,
    MAP_CM_PER_PIXELS = 2.0,
    ROBOT_INIT_POS_X_CM = 9.0,
    ROBOT_INIT_POS_Y_CM = 155.0,
    ROBOT_INIT_ANGLE = 90.0,
    MIN_LEFT_MARKER_COUNTER = 50,
)

map5 = MapConfig(
    MAP_NAME = "map5",
    MAP_FILE_NAME = "map5.png",
    MAP_WIDTH_CM = 651.0,
    MAP_HEIGHT_CM = 317.0,
    MAP_MARGIN_CM = 25.0,
    MAP_CM_PER_PIXELS = 2.0,
    ROBOT_INIT_POS_X_CM = 125.0,
    ROBOT_INIT_POS_Y_CM = 308.0,
    ROBOT_INIT_ANGLE = 180.0,
    MIN_LEFT_MARKER_COUNTER = 33,
)

map6 = MapConfig(
    MAP_NAME = "map6",
    MAP_FILE_NAME = "map6.png",
    MAP_WIDTH_CM = 303.0,
    MAP_HEIGHT_CM = 227.0,
    MAP_MARGIN_CM = 25.0,
    MAP_CM_PER_PIXELS = 3.0,
    ROBOT_INIT_POS_X_CM = 9.0,
    ROBOT_INIT_POS_Y_CM = 135.0,
    ROBOT_INIT_ANGLE = 90.0,
    MIN_LEFT_MARKER_COUNTER = 40,
)

map7 = MapConfig(
    MAP_NAME = "map7",
    MAP_FILE_NAME = "map7.png",
    MAP_WIDTH_CM = 688.0,
    MAP_HEIGHT_CM = 430.0,
    MAP_MARGIN_CM = 25.0,
    MAP_CM_PER_PIXELS = 2.0,
    ROBOT_INIT_POS_X_CM = 675.0,
    ROBOT_INIT_POS_Y_CM = 325.0,
    ROBOT_INIT_ANGLE = 90.0,
    MIN_LEFT_MARKER_COUNTER = 60,
)

map8 = MapConfig(
    MAP_NAME = "map8",
    MAP_FILE_NAME = "map8.png",
    MAP_WIDTH_CM = 665.0,
    MAP_HEIGHT_CM = 309.0,
    MAP_MARGIN_CM = 25.0,
    MAP_CM_PER_PIXELS = 2.0,
    ROBOT_INIT_POS_X_CM = 5.0,
    ROBOT_INIT_POS_Y_CM = 165.0,
    ROBOT_INIT_ANGLE = 90.0,
    MIN_LEFT_MARKER_COUNTER = 60,
)

map17 = MapConfig(
    MAP_NAME = "map17",
    MAP_FILE_NAME = "map17.png",
    MAP_WIDTH_CM = 405.0,
    MAP_HEIGHT_CM = 132.0,
    MAP_MARGIN_CM = 25.0,
    MAP_CM_PER_PIXELS = 3.0,
    ROBOT_INIT_POS_X_CM = 195.0,
    ROBOT_INIT_POS_Y_CM = 20.0,
    ROBOT_INIT_ANGLE = 180.0,
    MIN_LEFT_MARKER_COUNTER = 40,
)

map19 = MapConfig(
    MAP_NAME = "map19",
    MAP_FILE_NAME = "map19.png",
    MAP_WIDTH_CM = 653.0,
    MAP_HEIGHT_CM = 255.0,
    MAP_MARGIN_CM = 25.0,
    MAP_CM_PER_PIXELS = 2.0,
    ROBOT_INIT_POS_X_CM = 640.0,
    ROBOT_INIT_POS_Y_CM = 100.0,
    ROBOT_INIT_ANGLE = 90.0,
    MIN_LEFT_MARKER_COUNTER = 53,
)