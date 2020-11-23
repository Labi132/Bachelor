import pygame

class EventFire:
    def __init__(self):
        self.alive = True

    def tangible_move(self, tang):
        my_event = pygame.event.Event(pygame.USEREVENT+1, who=tang)
        pygame.event.post(my_event)

    def tangible_death(self, tang):
        my_event = pygame.event.Event(pygame.USEREVENT+2, who=tang)
        pygame.event.post(my_event)

