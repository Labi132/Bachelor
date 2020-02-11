import pygame

class ImageList(pygame.sprite.Group):

    def draw(self, surface):
        """draw all sprites onto the surface
        Group.draw(surface): return None
        Draws all of the member sprites onto the given surface.
        """
        sprites = self.sprites()
        for spr in sprites:
            self.spritedict[spr] = spr.draw(surface)
        self.lostsprites = []

class Images(pygame.sprite.Sprite):
    locked = False
    highlighted = False
    coll_list = []
    offset = [0, 0]
    scalesize = (300, 150)


    def __init__(self, image):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(image)
        self.width = self.image.get_rect().width
        self.height = self.image.get_rect().height
        self.image = pygame.transform.scale(self.image,
                                            self.scalesize)
        self.rect = self.image.get_rect()
        # self.unzoomed_center = self.rect.center
        self.light_changed = False

    def draw(self, screen):
        screen.blit(self.image, self.rect)
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

    def get_highlight(self):
        return self.highlighted

    def lock(self):
        self.locked = True

    def unlock(self):
        self.locked = False

    def get_locked(self):
        return self.locked

    def set_center(self, x_coord, y_coord):
        self.rect.center = (x_coord+self.offset[0], y_coord+self.offset[1])
        # self.unzoomed_center = self.rect.center
        
    def get_center(self):
        return self.rect.center    

    def get_rect(self):
        return self.rect

    def get_image(self):
        return self.image

    def move(self, x_move, y_move):
        self.rect.move_ip(x_move, y_move)
        # self.unzoomed_center = self.rect.center

    def set_light_changed(self, changed):
        self.light_changed = changed

    def get_light_changed(self):
        return self.light_changed
    """
    def zoom(self, center_zoom, align_right):
        self.image = pygame.transform.scale(self.image, (self.width, self.height))
        self.rect = self.image.get_rect()
        self._layer = 1
        if align_right:
            self.rect.center = (center_zoom[0] + 45, center_zoom[1])
        else:
            self.rect.center = (center_zoom[0] - 45, center_zoom[1])

    def unzoom(self):
        self.image = pygame.transform.scale(self.image, self.scalesize)
        self.rect = self.image.get_rect()
        self.rect.center = self.unzoomed_center
    """

    """
    def update(self, new_offset):
        temp_offset = self.offset
        self.move(new_offset[0]-temp_offset[0], new_offset[1]-temp_offset[1])
        self.offset = new_offset
    """
