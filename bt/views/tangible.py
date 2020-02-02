import pygame


class Tangible(pygame.sprite.Sprite):
    offset = -50

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((150, 150))
        self.image.fill((255, 0, 255))
        self.rect = self.image.get_rect()

    def set_center(self, coords):
        self.rect.center = (coords[0], coords[1])


    def move(self, x_move, y_move):
        self.rect.move_ip(x_move, y_move)
