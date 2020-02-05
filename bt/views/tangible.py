import pygame

white = [255, 255, 255]
red = [255, 0, 0]

class Tangible(pygame.sprite.Sprite):
    offset = -50

    def __init__(self, bounds, id):
        pygame.sprite.Sprite.__init__(self)
        self.id = id
        if bounds != []:
            self.image = pygame.Surface((bounds.width, bounds.height))
            self.image.fill(white)
            self.rect = self.image.get_rect()
            self.rect.center = (bounds.get_position())
            self.lockable = False
        else:
            self.image = pygame.Surface((90, 90))
            self.image.fill(white)
            self.rect = self.image.get_rect()
            self.rect.center = (500, 500)
            self.lockable = False

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

    def get_id(self):
        return self.id

    def set_color(self, color):
        self.image.fill(color)
