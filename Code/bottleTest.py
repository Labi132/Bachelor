from bottle import route, run, get, post, request, Bottle
import threading
import pygame


class LogBottle(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.host = '132.199.132.227'
        self.port = 3030
        self.daemon = True

    @staticmethod
    @get('/log/<content>')
    def log(content):
        my_event = pygame.event.Event(pygame.USEREVENT + 3, mode=content)
        pygame.event.post(my_event)
        pass

    def run(self):
            run(server='waitress', host=self.host, port=self.port)
