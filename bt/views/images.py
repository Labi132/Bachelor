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
        self.unscaled_image = self.image
        self.unscaled_image = pygame.transform.smoothscale(self.unscaled_image, (960, 1080))
        self.unscaled_rect = self.unscaled_image.get_rect()
        self.image = pygame.transform.scale(self.image, self.scalesize)
        self.rect = self.image.get_rect()
        self.tag = image[1]
        self.name = image[0]

        self.font = pygame.font.SysFont('Arial', 14)
        self.textSurf = self.font.render(self.name, 1, [0, 0, 0])
        self.text_rect = self.textSurf.get_rect()
        self.text_rect.center = self.rect.center
        self.current_screen = screen
        self.light_changed = False

    def draw(self, screen, current_s):
        if self.active:
            screen.blit(self.image, self.rect)
            screen.blit(self.textSurf, self.text_rect)
            if self.highlighted:
                pygame.draw.rect(screen, (255, 0, 0), self.rect, 2)

    def draw_unscaled(self, screen, alignment, current_s):
        if self.active:
            self.unscaled_rect.top = 0
            if alignment:
                self.unscaled_rect.left = 960
            else:
                self.unscaled_rect.left = 0
            screen.blit(self.unscaled_image, self.unscaled_rect)

    def change_screen(self, screen, pos):
        if self.active:
            print("SELF CURRENT: " + str(self.current_screen))
            print("TAG:" + str(self.tag))
            print(screen)
            self.current_screen = screen
            self.set_center(pos[0], pos[1])

    def highlight(self):
        if self.active:
            self.highlighted = True

    def un_highlight(self):
        if self.active:
            self.highlighted = False

    def invert_highlight(self):
        if self.active:
            if not self.light_changed:
                if not self.highlighted:
                    self.highlight()
                else:
                    self.un_highlight()

    def get_highlight(self):
        if self.active:
            return self.highlighted

    def lock(self):
        if self.active:
            self.locked = True

    def unlock(self):
        if self.active:
            self.locked = False

    def get_locked(self):
        if self.active:
            return self.locked

    def set_center(self, x_coord, y_coord):
        if self.active:
            self.rect.center = (x_coord, y_coord)
            self.text_rect.center = (x_coord, y_coord + 60)

    def get_center(self):
        if self.active:
            return self.rect.center

    def get_rect(self):
        return self.rect

    def get_image(self):
        return self.image

    def move(self, x_move, y_move):
        if self.active:
            self.rect.move_ip(x_move, y_move)
            self.text_rect.move_ip(x_move, y_move)

    def set_light_changed(self, changed):
        if self.active:
            self.light_changed = changed

    def get_light_changed(self):
        if self.active:
            return self.light_changed

    def update(self, current_s):
        if self.current_screen == current_s:
            self.active = True
        else:
            self.un_highlight()
            self.unlock()
            self.active = False

    def get_correct(self):
        if self.current_screen == self.tag:
            return True
        else:
            return False



class ImageFolder(pygame.sprite.Sprite):
    locked = False

    def __init__(self, tag):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('views/folder.png')
        self.image = pygame.transform.smoothscale(self.image, (150, 100))
        self.tag = tag
        self.rect = self.image.get_rect()

        self.font = pygame.font.SysFont('Arial', 14)
        self.textSurf = self.font.render(tag, 1, [0, 0, 0])
        self.text_rect = self.textSurf.get_rect()
        self.text_rect.center = (self.rect.center[0], self.rect.center[1]+60)

    def draw(self, screen):
        screen.blit(self.image, self.rect)
        screen.blit(self.textSurf, self.text_rect)

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
        self.text_rect.center = (x_coord, y_coord+60)

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
