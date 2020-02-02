import pygame


class Images(pygame.sprite.Sprite):
    locked = False
    highlighted = False

    def __init__(self, image):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(pygame.image.load(image), (300, 150))
        self.rect = self.image.get_rect()


    def draw_highlight(self, screen):
        if self.highlighted:
            pygame.draw.rect(screen, (255, 0, 0), self.rect, 2)

    def highlight(self):
        self.highlighted = True

    def un_highlight(self):
        self.highlighted = False

    def invert_highlight(self):
        if not self.highlighted:
            self.highlight()
        else:
            self.un_highlight()

    def lock(self):
        self.locked = True
        print("locked")

    def unlock(self):
        self.locked = False
        print("unlocked")

    def get_locked(self):
        return self.locked

    def set_center(self, x_coord, y_coord):
        self.rect.center = (x_coord, y_coord)

    def get_rect(self):
        return self.rect

    def get_image(self):
        return self.image

    def move(self, x_move, y_move):
        self.rect.move_ip(x_move, y_move)
