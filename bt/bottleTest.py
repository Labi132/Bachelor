from bottle import route, run, get, post, request
import waitress
import threading
import logging

logging.basicConfig(filename='log.txt',format='%(asctime)s %(message)s',
                    level=logging.INFO)


class Bottle:
    def __init__(self, eventsource):
        self.event_source = eventsource

    @get('/log/<content>')  # or @route('/login')
    def log(self, content):
        self.event_source.tangible_switch(content)
        logging.info(content)
        pass

    def run(self):
        run(server='waitress')

