from bottle import route, run, get, post, request
import logging

logging.basicConfig(filename='log.txt',format='%(asctime)s %(message)s',
                    level=logging.INFO)


@get('/log/<content>') # or @route('/login')
def log(content):
    logging.info(content)
    return


run(host='192.168.0.92', port=8080, debug=True)
