import pygame

white = [255, 255, 255]
red = [255, 0, 0]


class ImageList(pygame.sprite.Group):
    def draw(self, surface, current_screen):
        sprites = self.sprites()
        for spr in sprites:
            self.spritedict[spr] = spr.draw(surface, current_screen)
        self.lostsprites = []


class Images(pygame.sprite.Sprite):
    locked = False
    highlighted = False
    scalesize = (110, 110)
    active = True

    def __init__(self, image, screen):
        pygame.sprite.Sprite.__init__(self)

        self.image = pygame.image.load(image[0])
        self.image = pygame.transform.scale(self.image, self.scalesize)
        self.rect = self.image.get_rect()
        self.tag = image[1]
        self.name = image[0][-11:]
        self.has_changed = False

        self.font = pygame.font.SysFont('Arial', 14)
        self.textSurf = self.font.render(self.name, 1, [0, 0, 0])
        self.text_rect = self.textSurf.get_rect()
        self.text_rect.center = self.rect.center
        self.current_screen = screen

    def draw(self, screen, current_s):
        if self.active:
            screen.blit(self.image, self.rect)
            screen.blit(self.textSurf, self.text_rect)
            if self.highlighted:
                pygame.draw.rect(screen, (255, 0, 0), self.rect, 2)

    def change_screen(self, screen):
        if self.active and not self.has_changed:
            self.current_screen = screen
            self.has_changed = True

    def get_active(self):
        return self.active

    def get_screen(self):
        return self.current_screen

    def set_center(self, x_coord, y_coord):
        if self.active:
            self.rect.center = (x_coord, y_coord)
            self.text_rect.center = (x_coord, y_coord + 60)

    def set_center_reset(self, x_coord, y_coord):
        self.rect.center = (x_coord, y_coord)
        self.text_rect.center = (x_coord, y_coord + 60)

    def get_center(self):
        if self.active:
            return self.rect.center

    def get_rect(self):
        return self.rect

    def get_image(self):
        return self.image

    def update(self, current_s):
        self.has_changed = False
        if self.current_screen == current_s:
            self.active = True
        else:
            self.active = False

    def get_correct(self):
        if self.current_screen == self.tag:
            return True
        else:
            return False


class ImageFolder(pygame.sprite.Sprite):
    locked = False

    def __init__(self, tag, pos_list):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('/home/lab/Desktop/Eder-Bachelor/Bachelor/bt/views/folder.png')
        self.image = pygame.transform.smoothscale(self.image, (120, 100))
        self.tag = tag
        self.rect = self.image.get_rect()

        self.images = list()
        self.positions = pos_list
        self.counter = 0
        self.original_text = tag
        self.current_text = tag

        self.font = pygame.font.SysFont('Arial', 14)
        self.textSurf = self.font.render(self.original_text, 1, [0, 0, 0])
        self.text_rect = self.textSurf.get_rect()
        self.text_rect.center = (self.rect.center[0], self.rect.center[1] + 60)

    def update_text(self, tag):
        self.textSurf = self.font.render(tag, 1, [0, 0, 0])
        self.text_rect = self.textSurf.get_rect()
        self.text_rect.center = (self.rect.center[0], self.rect.center[1] + 60)

    def draw(self, screen):
        screen.blit(self.image, self.rect)
        screen.blit(self.textSurf, self.text_rect)

    def move(self, x_move, y_move):
        self.rect.move_ip(x_move, y_move)
        self.text_rect.move_ip(x_move, y_move)

    def set_left(self, left):
        self.rect.left = left

    def set_right(self, right):
        self.rect.right = right

    def set_bottom(self, bottom):
        self.rect.bottom = bottom

    def set_top(self, top):
        self.rect.top = top

    def set_center(self, x_coord, y_coord):
        self.rect.center = (x_coord, y_coord)
        self.text_rect.center = (x_coord, y_coord + 60)

    def get_center(self):
        return self.rect.center

    def get_tag(self):
        return self.tag

    def lock(self):
        self.locked = True

    def unlock(self):
        self.locked = False

    def get_locked(self):
        return self.locked

    def increase_counter(self):
        self.counter += 1

    def decrease_counter(self):
        self.counter -= 1

    def add_item(self): # (self, item):
        # item.set_center(self.positions[self.counter][0],
        #                 self.positions[self.counter][1])
        # self.images.append(item)
        self.increase_counter()

    def remove_item(self):  # (self, item):
            # self.images.remove(item)
            self.decrease_counter()

    def reset_positions(self, image_list):
        k = 0
        for x in image_list:
            if x.get_screen() == self.tag:
                x.set_center_reset(self.positions[k][0], self.positions[k][1])
                k += 1
        """k = 0
        for x in self.images:
            x.set_center(self.positions[k][0], self.positions[k][1])
            k += 0
            """

    def update(self, current_s):
        if self.tag == current_s:
            self.current_text = 'back to top'
            self.update_text(self.current_text)
        else:
            if self.current_text != self.original_text:
                self.current_text = self.original_text
                self.update_text(self.current_text)
