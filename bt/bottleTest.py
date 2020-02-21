from bottle import route, run, get, post, request, Bottle
import waitress
import logging
import threading
import pygame

logging.basicConfig(filename='log.txt',format='%(asctime)s %(message)s',
                    level=logging.INFO)


class LogBottle(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.app = Bottle()
        self.host = '132.199.132.227'
        self.port = 3030

    @staticmethod
    @get('/log/<content>')  # or @route('/login')
    def log(content):
        my_event = pygame.event.Event(pygame.USEREVENT + 3, mode=content)
        pygame.event.post(my_event)
        logging.info(content)
        pass

    def run(self):
        run(server='waitress', host=self.host, port=self.port)
