import os
import sys
import random
import collections
import pygame as pg
import queue

from pygame.draw import rect


caption = "Jim's snake"
screen_size_x = 544*3  # 544
screen_size_y = 544*2  # 544
screen_size = (screen_size_x, screen_size_y)
cell_x = cell_y = screen_size_y / (34)
cell = pg.Rect(0, 0, cell_x, cell_y)
play_rect = pg.Rect(cell.w, cell.h, screen_size_x - 2 *
                    cell.w, screen_size_y - 2 * cell.h)
board_size = (play_rect.w//cell.w, play_rect.h//cell.h)
growth_per_apple = 2


colours = {"background": (30, 40, 50), "walls": pg.Color("lightslategrey"),
           "snake": pg.Color("limegreen"), "head": pg.Color("darkgreen"),
           "apple": pg.Color("tomato")}

direct_dict = {"left": (-1, 0), "right": (1, 0),
               "up": (0, -1), "down": (0, 1)}

opposites = {"left": "right", "right": "left",
             "up": "down", "down": "up"}

move_keys = {(pg.K_LEFT, pg.K_a): "left", (pg.K_RIGHT, pg.K_d): "right",
             (pg.K_UP, pg.K_w): "up", (pg.K_DOWN, pg.K_s): "down"}


class apple():
    def __init__(self, walls, snake):
        self.colour = colours["apple"]
        self.walls = walls.pos
        self.pos = self.respawn(snake.body_set | self.walls)

    def collide_with(self, snake):
        self.pos = self.respawn(snake.body_set | self.walls)

    def respawn(self, obstacles):
        pos = tuple(random.randrange(board_size[i]) for i in (0, 1))
        while pos in obstacles:
            pos = tuple(random.randrange(board_size[i]) for i in (0, 1))
        return pos


class walls():
    def __init__(self):
        self.colour = colours["walls"]
        self.pos = self.make_walls()

    def make_walls(self):
        walls = set()
        for i in range(-1, board_size[0]+1):
            walls.add((i, -1))
            walls.add((i, board_size[1]))
        for j in range(-1, board_size[1]+1):
            walls.add((-1, j))
            walls.add((board_size[0], j))
        return walls


class snake():
    def __init__(self):
        self.body_colour = colours["snake"]
        self.head_colour = colours["head"]
        self.speed = 8  # Cells per second
        self.direction = "up"
        self.vector = direct_dict[self.direction]
        self.body = [(10, 25), (10, 24), (10, 23)]
        self.body_set = set(self.body)
        self.growing = False
        self.grow_number = 0
        self.timer = 0
        self.dead = False
        self.direction_queue = queue.Queue(5)

    def update(self, now):
        if not self.dead and now-self.timer >= 1000.0/self.speed:
            self.timer = now
            self.change_direction()
            next_cell = [self.body[-1][i]+self.vector[i] for i in (0, 1)]
            self.body.append(tuple(next_cell))
            if not self.growing:
                del self.body[0]
            else:
                self.grow()
            self.body_set = set(self.body)

    def change_direction(self):
        try:
            new = self.direction_queue.get(block=False)
        except queue.Empty:
            new = self.direction
        if new not in (self.direction, opposites[self.direction]):
            self.vector = direct_dict[new]
            self.direction = new

    def grow(self):
        self.grow_number += 1
        if self.grow_number == growth_per_apple:
            self.grow_number = 0
            self.growing = False

    def check_collisions(self, apple, walls):
        if self.body[-1] == apple.pos:
            apple.collide_with(self)
            self.growing = True
        elif self.body[-1] in walls.pos:
            self.dead = True
        elif any(val > 1 for val in collections.Counter(self.body).values()):
            self.dead = True

    def get_key_press(self, key):
        for keys in move_keys:
            if key in keys:
                try:
                    self.direction_queue.put(move_keys[keys], block=False)
                    break
                except queue.Full:
                    pass

    def draw(self, surface, offset=(0, 0)):
        for cell in self.body:
            draw_cell(surface, cell, self.body_colour, offset)
        draw_cell(surface, self.body[-1], self.head_colour, offset)


class scene():
    def __init__(self, next_state=None):
        self.next = next_state
        self.done = False
        self.start_time = None
        self.screen_copy = None

    def startup(self, now):
        self.start_time = now
        self.screen_copy = pg.display.get_surface().copy()

    def reset(self):
        self.done = False
        self.start_time = None
        self.screen_copy = None

    def get_event(self, event):
        pass

    def update(self, now):
        if not self.start_time:
            self.startup(now)


class anykey(scene):
    def __init__(self, title):
        scene.__init__(self, "GAME")
        self.blink_timer = 0.0
        self.blink = False
        self.make_text(title)
        self.reset()

    def make_text(self, title):
        self.main = FONTS["BIG"].render(title, True, pg.Color("white"))
        self.main_rect = self.main.get_rect(centerx=play_rect.centerx,
                                            centery=play_rect.centery-150)
        text = "Press any key"
        self.ne_key = FONTS["SMALL"].render(text, True, pg.Color("white"))
        self.ne_key_rect = self.ne_key.get_rect(centerx=play_rect.centerx,
                                                centery=play_rect.centery+150)

    def get_event(self, event):
        if event.type == pg.KEYDOWN:
            self.done = True

    def update(self, now):
        scene.update(self, now)
        if now-self.blink_timer > 1000.0/5:
            self.blink = not self.blink
            self.blink_timer = now

    def draw(self, surface):
        surface.blit(self.screen_copy, (0, 0))
        surface.blit(self.main, self.main_rect)
        if self.blink:
            surface.blit(self.ne_key, self.ne_key_rect)


class game(scene):
    def __init__(self):
        scene.__init__(self, "DEAD")
        self.reset()

    def reset(self):
        scene.reset(self)
        self.snake = snake()
        self.walls = walls()
        self.apple = apple(self.walls, self.snake)

    def get_event(self, event):
        if event.type == pg.KEYDOWN:
            self.snake.get_key_press(event.key)

    def update(self, now):
        scene.update(self, now)
        self.snake.update(now)
        self.snake.check_collisions(self.apple, self.walls)
        if self.snake.dead:
            self.done = True

    def draw(self, surface):
        surface.fill(colours["background"])
        draw_cell(surface, self.apple.pos,
                  self.apple.colour, play_rect.topleft)
        for wall in self.walls.pos:
            draw_cell(surface, wall, self.walls.colour, play_rect.topleft)
        self.snake.draw(surface, offset=play_rect.topleft)


class control():
    def __init__(self):
        self.screen = pg.display.get_surface()
        self.clock = pg.time.Clock()
        self.fps = 60.0
        self.done = False
        self.state_dict = {"START": anykey("START"),
                           "GAME": game(),
                           "DEAD": anykey("GAME OVER")}
        self.state = self.state_dict["START"]

    def event_loop(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.done = True
            self.state.get_event(event)

    def update(self):
        now = pg.time.get_ticks()
        self.state.update(now)
        if self.state.done:
            self.state.reset()
            self.state = self.state_dict[self.state.next]

    def draw(self):
        if self.state.start_time:
            self.state.draw(self.screen)

    def main_loop(self):
        self.screen.fill(colours["background"])
        while not self.done:
            self.event_loop()
            self.update()
            self.draw()
            pg.display.update()
            self.clock.tick(self.fps)


def draw_cell(surface, cells, color, offset=(0, 0)):
    pos = [cells[i]*cell.size[i] for i in (0, 1)]
    rect = pg.Rect(pos, cell.size)
    rect.move_ip(*offset)
    surface.fill(color, rect)


def main():
    global FONTS, LEVELS
    os.environ["SDL_VIDEO_CENTERED"] = "True"
    pg.init()
    pg.display.set_caption(caption)
    pg.display.set_mode(screen_size)
    FONTS = {"BIG": pg.font.SysFont("helvetica", 70, True),
             "SMALL": pg.font.SysFont("helvetica", 35, True)}
    control().main_loop()
    pg.quit()
    sys.exit()


if __name__ == "__main__":
    main()
