import pygame

white = [255, 255, 255]
red = [255, 0, 0]


class Tangible(pygame.sprite.Sprite):
    offset = -50

    def __init__(self, id):
        pygame.sprite.Sprite.__init__(self)
        self.id = id
        self.image = pygame.Surface((90, 90))
        self.image.fill(white)
        self.rect = self.image.get_rect()
        self.rect.center = (-500, -500)
        self.lockable = False
        self.alive = False

    def set_center(self, coords):
        self.rect.center = (coords[0], coords[1])

    def get_center(self):
        return self.rect.center

    def move(self, x_move, y_move):
        self.rect.move_ip(x_move, y_move)

    def set_lockable(self, lock):
        self.lockable = lock

    def get_lockable(self):
        return self.lockable

    def invert_lockable(self):
        self.lockable = not self.lockable

    def get_id(self):
        return self.id

    def set_color(self, color):
        self.image.fill(color)

    def set_alive(self, living):
        self.alive = living

    def get_alive(self):
        return self.alive


class Circle:
    def __init__(self):
        self.x = -500
        self.y = -500
        self.radius = 200
        self.color = [0, 0, 255]

    def set_center(self, new_coords):
        self.x, self.y = new_coords

    def get_center(self):
        return (self.x, self.y)

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius, 5)
