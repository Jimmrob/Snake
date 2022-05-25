import pygame, sys, random
from collections import namedtuple
from enum import Enum

pygame.init()
clock = pygame.time.Clock()

Point = namedtuple("Point", "x, y")

grid_size = 30
cell_size = 20
screen_x = grid_size * cell_size
screen_y = grid_size * cell_size
speed = 10

colours =   {"background"   : (30, 40, 50), 
            "text"         : pygame.Color("lightslategrey"),
            "snake_body"    : pygame.Color("limegreen"), 
            "snake_head"    : pygame.Color("darkgreen"),
            "apple"         : pygame.Color("tomato")}


screen = pygame.display.set_mode((screen_x, screen_y))
caption = pygame.display.set_caption("snake")

class Apple:
    def __init__(self, snake):
        self.colour = colours["apple"]
        self.food = None
        self.spawn_food(snake)


    def spawn_food(self, snake):
        x = random.randint(0, (screen_x - cell_size)//cell_size) * cell_size
        y = random.randint(0, (screen_y - cell_size)//cell_size) * cell_size
        self.food = Point(x, y)
        if self.food in snake:
            self.spawn_food(snake)


    def draw(self):
        pygame.draw.rect(screen, colours["apple"], pygame.Rect(self.food.x, self.food.y, cell_size, cell_size))


class Snake:
    def __init__(self):
        self.head_colour = colours["snake_head"]
        self.body_colour = colours["snake_body"]
        self.head = Point(screen_x / 2, screen_y / 2)
        self.snake = [self.head,
                      Point(self.head.x - cell_size, self.head.y),
                      Point(self.head.x - 2 * cell_size, self.head.y)]
        self.direction = "right"

    
    def move(self):
        x = self.head.x
        y = self.head.y
        if self.direction == "right":
            x += cell_size
        elif self.direction == "left":
            x -= cell_size
        elif self.direction == "up":
            y -= cell_size
        elif self.direction == "down":
            y += cell_size
        
        self.head = Point(x, y)
        self.snake.insert(0, self.head)
        self.snake.pop()


    def collision(self, pt=None):
        if pt is None:
            pt = self.head
        if pt.x < 0 or screen_x - cell_size < pt.x or pt.y < 0 or screen_y - cell_size < pt.y:
            return True
        if pt in self.snake[1:]:
            return True
        return False
        

    def draw(self):
        for pt in self.snake:
            pygame.draw.rect(screen, colours["snake_body"], pygame.Rect(pt.x, pt.y, cell_size, cell_size))

        pygame.draw.rect(screen, colours["snake_head"], pygame.Rect(self.snake[0].x, self.snake[0].y, cell_size, cell_size))


snake = Snake()
apple = Apple(snake.snake)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    if snake.direction != "right":
                        snake.direction = "left"
                    else:
                        snake.direction = snake.direction
                elif event.key == pygame.K_RIGHT:
                    if snake.direction != "left":
                        snake.direction = "right"
                    else:
                        snake.direction = snake.direction
                elif event.key == pygame.K_UP:
                    if snake.direction != "down":
                        snake.direction = "up"
                    else:
                        snake.direction = snake.direction
                elif event.key == pygame.K_DOWN:
                    if snake.direction != "up":
                        snake.direction = "down"
                    else:
                        snake.direction = snake.direction

    snake.move() # update the head
    snake.snake.insert(0, snake.head)
        
    # 3. check if game over
    if snake.collision():
        pygame.quit()
        sys.exit()
            
    # 4. place new food or just move
    if snake.head == apple.food:
        snake.score += 1
        apple.spawn_food()
    else:
        snake.snake.pop()
        

    screen.fill(colours["background"])
    apple.draw()
    snake.draw()
    snake.move()

    pygame.display.update()
    clock.tick(speed)