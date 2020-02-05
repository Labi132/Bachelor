import pygame


class Images(pygame.sprite.Sprite):
    locked = False
    highlighted = False
    coll_list = []

    def __init__(self, image):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(pygame.image.load(image),
                                            (300, 150))
        self.rect = self.image.get_rect()
        self.light_changed = False

    def draw_highlight(self, screen):
        if self.highlighted:
            pygame.draw.rect(screen, (255, 0, 0), self.rect, 2)

    def highlight(self):
        self.highlighted = True

    def un_highlight(self):
        self.highlighted = False

    def invert_highlight(self):
        if not self.light_changed:
            if not self.highlighted:
                self.highlight()
            else:
                self.un_highlight()

    def lock(self):
        print("IM LOCKED")
        self.locked = True

    def unlock(self):
        self.locked = False

    def get_locked(self):
        return self.locked

    def set_center(self, x_coord, y_coord):
        self.rect.center = (x_coord, y_coord)
        
    def get_center(self):
        return self.rect.center    

    def get_rect(self):
        return self.rect

    def get_image(self):
        return self.image

    def move(self, x_move, y_move):
        self.rect.move_ip(x_move, y_move)

    def set_light_changed(self, changed):
        self.light_changed = changed

    def get_light_changed(self):
        return self.light_changed
