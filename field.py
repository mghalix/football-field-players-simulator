from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import random
from threading import *
import threading
import time

from my_classes import *

def main():
    warmup()
    put_teams_in_the_field()
    start_match()


class Player():
    def __init__(self):
        self.x, self.y = generate_random_points()

    def update_position(self):
        self.x, self.y = generate_random_points()

class Team():
    def __init__(self, team_players_number):
        self.team = [Player() for _ in range(team_players_number)]

    def update_position(self):
        for player in self.team:
            player.update_position()

    def __iter__(self):
        return TeamIterator(self.team)

    def start_position_updater(self):
        thread = threading.Thread(target=self.position_updater)
        thread.daemon = True
        thread.start()

    def position_updater(self):
        while True:
            self.update_position()
            time.sleep(3)

class TeamIterator:
    def __init__(self, team):
        self.team = team
        self.index = 0

    def __next__(self):
        if self.index >= len(self.team):
            raise StopIteration

        player = self.team[self.index]
        self.index += 1
        return player

def generate_random_points():
    rx_min = RealCoordinates.x_min
    # rx_min += rx_min*0.1

    rx_max = RealCoordinates.x_max
    # rx_max -= rx_max*0.1

    ry_min= RealCoordinates.y_min
    # ry_min += ry_min*0.1

    ry_max = RealCoordinates.y_max
    # ry_max -= ry_max*0.1

    x = random.uniform(rx_min, rx_max)
    y = random.uniform(ry_min, ry_max)
    mapper = RealToDeviceMapping()
    return mapper.real_to_device(x, y)

def init():
    glutInit()
    glutInitDisplayMode(GLUT_SINGLE | GLUT_RGB)
    glutInitWindowSize(*DeviceProperties.get_window_size())
    glutInitWindowPosition(*DeviceProperties.get_center())
    glutCreateWindow('Field')

def canvas():
    glClearColor(0.0, 1.0, 0.0, 1.0)
    gluOrtho2D(
        DeviceCoordinates.x_min,
        DeviceCoordinates.x_max,
        DeviceCoordinates.y_min,
        DeviceCoordinates.y_max
    )

def draw_team(team, tshirt_color):
    player_border(team, border_color=RGB.color(0, 0.7, 1.0))

    set_color(tshirt_color)
    glBegin(GL_POINTS)
    for player in team:
        glVertex2f(player.x, player.y)
    glEnd()

def draw_mid_line(color):
    set_color(color)
    glBegin(GL_LINES)
    glVertex2f((DeviceCoordinates.x_max + DeviceCoordinates.x_min)/2, DeviceCoordinates.y_max)
    glVertex2f((DeviceCoordinates.x_max + DeviceCoordinates.x_min)/2, DeviceCoordinates.y_min)
    glEnd()

def set_color(color):
    glColor3f(*color)

def redraw():
    glutSwapBuffers()
    glutPostRedisplay()

def enhance_players_look():
    glEnable(GL_POINT_SMOOTH)
    glHint(GL_POINT_SMOOTH_HINT, GL_NICEST)

def customize_players_size(size):
    glPointSize(size)

def clear_field():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

def player_border(team, border_color):
    set_color(border_color)
    customize_players_size(default_player_size() * 1.3)
    glBegin(GL_POINTS)
    for player in team:
        glVertex2f(player.x, player.y)
    glEnd()
    default_player_size()

def default_player_size():
    customize_players_size(15)
    return 15

def draw():
    clear_field()

    enhance_players_look()

    draw_mid_line(RGB.WHITE)

    # team 1
    draw_team(team1, tshirt_color=RGB.color(0.0, 0.8, 1.0))

    # team 2
    draw_team(team2, tshirt_color=RGB.WHITE)

    redraw()

def put_teams_in_the_field():
    global team1, team2
    team1 = Team(5)
    team2 = Team(5)


    team1.start_position_updater()
    team2.start_position_updater()

def start_match():
    glutDisplayFunc(draw)
    glutMainLoop()

def setup_all_coordinates():
    xr_min, yr_min = 100, 200
    xr_max, yr_max = 700, 900

    RealCoordinates.set_closest_point(xr_min, yr_min)
    RealCoordinates.set_furthest_point(xr_max, yr_max)

    DeviceCoordinates.adapted(True)

    m, n = 1200, 1200
    w_width, w_height = 700, 400
    xd_min, yd_min = 300, 400

    DeviceProperties.set_resolution(m, n)
    DeviceProperties.set_window_size(w_width, w_height)

    DeviceCoordinates.set_closest_point(xd_min, yd_min)
    DeviceCoordinates.set_furthest_point(
        DeviceProperties.window_width + DeviceCoordinates.x_min,
        DeviceProperties.window_height + DeviceCoordinates.y_min,
    )

    Scale.setup_scale()
    Scale.check_distortion_and_fix()

def warmup():
    setup_all_coordinates()
    init()
    canvas()


main()
