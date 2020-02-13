import argparse
import threading
import sys
import time
import logging
import random

import pygame

from lib.pythonosc import dispatcher
from lib.pythonosc import osc_server

from parsers.MessageParser import MessageParser
from parsers.MessageTypes import MessageTypes

from EventFire import EventFire

from bottleTest import Bottle

from views.images import Images, ImageList
from views.tangible import Tangible

white = [255, 255, 255]

HIGHLIGHT = 0
DRAG = 1
GROUP = 2
PAN = 3
ZOOM = 4

images = {'views/Bilder/city/c1.jpg', 'views/Bilder/city/c2.jpg',
          'views/Bilder/city/c3.jpg', 'views/Bilder/food/f1.jpg',
          'views/Bilder/food/f2.jpg', 'views/Bilder/food/f3.jpg',
          'views/Bilder/food/f4.jpg', 'views/Bilder/food/f5.jpg',
          'views/Bilder/food/f6.jpg', 'views/Bilder/food/f7.jpg',
          'views/Bilder/pet/p1.jpg', 'views/Bilder/pet/p2.jpg',
          'views/Bilder/pet/p3.jpg', 'views/Bilder/pet/p4.jpg',
          'views/Bilder/pet/p5.jpg', 'views/Bilder/pet/p6.jpg',
          'views/Bilder/pet/p7.jpg', 'views/Bilder/vacation/v1.jpg',
          'views/Bilder/vacation/v2.jpg', 'views/Bilder/vacation/v3.jpg',
          'views/Bilder/vacation/v4.jpg', 'views/Bilder/vacation/v5.jpg',
          'views/Bilder/vacation/v6.jpg', 'views/Bilder/vacation/v7.jpg',
          'views/Bilder/screenshot/s1.PNG', 'views/Bilder/screenshot/s2.PNG',
          'views/Bilder/screenshot/s3.PNG'}

positions = {
    (200, 100), (200, 350), (200, 600), (200, 850),
    (450, 100), (450, 350), (450, 600), (450, 850),
    (700, 100), (700, 350), (700, 600), (700, 850),
    (950, 100), (950, 350), (950, 600), (950, 850),
    (1200, 100), (1200, 350), (1200, 600), (1200, 850),
    (1450, 100), (1450, 350), (1450, 600), (1450, 850),
    (1700, 100), (1700, 350), (1700, 600)}

"""positions = {
    (200, 100), (200, 350), (200, 600), (200, 850), (200, 1100), (200, 1350),
    (450, 100), (450, 350), (450, 600), (450, 850), (450, 1100), (450, 1350),
    (700, 100), (700, 350), (700, 600), (700, 850), (700, 1100),
    (950, 100), (950, 350), (950, 600), (950, 850), (950, 1100),
    (1200, 100), (1200, 350), (1200, 600), (1200, 850), (1200, 1100)}"""

tangibles = {HIGHLIGHT: 0, DRAG: 1, GROUP: 2, PAN: 3, ZOOM: 4}
tang = {}

PID = None
MODE = "Multiple"

logging.basicConfig(filename='log.txt', format='%(asctime)s %(message)s',
                    level=logging.INFO)


# Stacking oder kleinere kacheln, dateiname, programmatisches ende

def create_tangibles(tangl):
    for key in tangibles:
        new_tang = Tangible([], key)
        tang[key] = new_tang
        tangl.add(new_tang)


def create_images(imgl):
    position_list = list(positions)
    random.shuffle(position_list)
    k = 0

    for x in images:
        new_image = Images(x)
        new_image.set_center(position_list[k][0], position_list[k][1])
        k = k + 1
        imgl.add(new_image)


def log(tangible):
    message = "PID: " + str(PID) + ", "
    message += "Mode: " + MODE + ", "
    message += "ID: " + str(tangible.get_id()) + ", "
    message += "Dead: " + str(tangible.get_alive()) + ", "
    message += "Center: " + str(tangible.get_center())
    logging.info(message)


# define a main function
def main():
    highlight_coll = []
    old_offset = [0, 0]
    current_offset = [0, 0]
    offset_rate = 3
    offset_changed = False
    zoomed_img = None
    event_source = EventFire()
    bottle = Bottle(event_source)
    # bottle.run()
    threading.Thread(target=bottle.run).start()
    # threading.Thread(target=bottle.run()).start()
    # Aus Jürgens Code
    sys.setrecursionlimit(10000)
    mp = MessageParser(event_source)

    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", default="127.0.0.1", help="The ip to listen on")
    parser.add_argument("--port", type=int, default=3333,
                        help="The port to listen on")
    args = parser.parse_args()

    dispatch = dispatcher.Dispatcher()
    dispatch.map(MessageTypes.POINTER.value, mp.parse)
    dispatch.map(MessageTypes.TOKEN.value, mp.parse)
    dispatch.map(MessageTypes.BOUNDS.value, mp.parse)
    dispatch.map(MessageTypes.FRAME.value, mp.parse)
    dispatch.map(MessageTypes.ALIVE.value, mp.parse)
    dispatch.map(MessageTypes.SYMBOL.value, mp.parse)

    server = osc_server.ThreadingOSCUDPServer((args.ip, args.port), dispatch)

    print("Serving on {}".format(server.server_address))

    server_ = threading.Thread(target=server.serve_forever)

    server_.start()
    # ENDE KOPIERTER CODE HIER

    # initialize the pygame module
    pygame.init()

    TANGIBLEMOVE = pygame.USEREVENT + 1  # custom events für tangible aktionen
    TANGIBLEDEATH = pygame.USEREVENT + 2
    TANGIBLESWITCH = pygame.USEREVENT + 3

    clock = pygame.time.Clock()
    # create a surface on screen that has the size of 240 x 180
    screen = pygame.display.set_mode((0, 0), pygame.NOFRAME)

    tangible_list = pygame.sprite.LayeredUpdates()
    create_tangibles(tangible_list)
    tang[DRAG].set_lockable(True)

    image_list = ImageList()
    create_images(image_list)

    lockList = []

    """Flags und Timer um zu schnelles bewegen als Fehler etwas zu vermindern"""
    timer_drag = time.perf_counter()
    timer_highlight = time.perf_counter()
    timer_pan = time.perf_counter()
    timer_group = time.perf_counter()
    timer_zoom = time.perf_counter()
    deaths = {HIGHLIGHT: True, DRAG: True, GROUP: True, PAN: True, ZOOM: True}
    timer_delay = 0.5

    """Flags damit die endgültigen death events nur einmal pro death ausgelöst 
    werden"""
    once_drag = False
    once_highlight = False

    collisions = [None, None, None, None, None]
    # define a variable to control the main loop
    running = True

    # main loop
    while running:
        # event handling, gets all event from the event queue
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # change the value to False, to exit the main loop
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                    server.shutdown()
                    pygame.quit()
                    sys.exit()

            if event.type == TANGIBLESWITCH:
                pass

            if event.type == TANGIBLEMOVE:
                # Drag
                if event.who.get_class_id() == DRAG:
                    deaths[DRAG] = False
                    once_drag = False
                    tang[DRAG].set_alive(deaths[DRAG])
                    log(tang[DRAG])
                    move_pos = tang[DRAG].get_center()
                    tang[DRAG].set_center(
                        event.who.get_bounds_component().get_position())
                    current_center = tang[DRAG].get_center()
                    delta = (move_pos[0] - current_center[0],
                             move_pos[1] - current_center[1])
                    for x in lockList:
                        image_center = x.get_center()
                        x.set_center(image_center[0] - delta[0],
                                     image_center[1] - delta[1])
                    if collisions[DRAG] != [] and tang[DRAG].get_lockable():
                        for x in collisions[DRAG]:
                            if not x.get_locked():
                                x.lock()
                                lockList.append(x)
                                for y in lockList:
                                    if y not in collisions[DRAG]:
                                        y.unlock()
                                        lockList.remove(y)
                    tang[DRAG].set_lockable(True)

                # Highlight
                if event.who.get_class_id() == HIGHLIGHT:  # HIGHLIGHTING GEHT
                    deaths[HIGHLIGHT] = False
                    once_highlight = False
                    tang[HIGHLIGHT].set_alive(deaths[HIGHLIGHT])
                    log(tang[HIGHLIGHT])
                    tang[HIGHLIGHT].set_center(
                        event.who.get_bounds_component().get_position())
                    if highlight_coll:
                        for x in highlight_coll:
                            if x not in collisions[HIGHLIGHT]:
                                x.set_light_changed(False)
                                highlight_coll.remove(x)
                    if collisions[HIGHLIGHT]:
                        for x in collisions[HIGHLIGHT]:
                            x.invert_highlight()
                            x.set_light_changed(True)
                            highlight_coll.append(x)

                # Group
                if event.who.get_class_id() == GROUP:  # Funktioniert, allerdings noch ohne offset und nicht animiert
                    deaths[GROUP] = False
                    tang[GROUP].set_alive(deaths[GROUP])
                    log(tang[GROUP])
                    tang[GROUP].set_center(
                        event.who.get_bounds_component().get_position())
                    group_center = tang[GROUP].get_center()
                    k = 0
                    for x in image_list:
                        if x.get_highlight():
                            img_center = x.get_center()
                            group_delta = (group_center[0] - img_center[0] + k,
                                           group_center[1] - img_center[1] + k)
                            x.move(group_delta[0], group_delta[1])
                            k += 60  # offset vielleicht differenzieren

                # Zoom
                if event.who.get_class_id() == ZOOM:
                    zoom_death = False
                    tang[ZOOM].set_alive(deaths[ZOOM])
                    log(tang[ZOOM])
                    tang[ZOOM].set_center(
                        event.who.get_bounds_component().get_position())
                    zoom_center = tang[ZOOM].get_center()
                    if zoom_center[0] < 900:
                        align_right = True
                    else:
                        align_right = False
                    if collisions[ZOOM]:
                        if len(collisions[ZOOM]) > 1:
                            # TODO: make sure only biggest overlap is used
                            pass
                        else:
                            zoomed_img = collisions[ZOOM][0]
                            if align_right:
                                # zoomed_img.zoom(zoom_center, align_right)
                                pass
                            else:
                                pass
                    else:
                        zoomed_img = None

                # PAN
                if event.who.get_class_id() == PAN:
                    deaths[PAN] = False
                    tang[PAN].set_alive(deaths[PAN])
                    log(tang[PAN])
                    tang[PAN].set_center(
                        event.who.get_bounds_component().get_position())
                    pan_center = tang[PAN].get_center()
                    if pan_center[0] < 200 and pan_center[
                        1] < 200:  # LEFT AND UP
                        current_offset[0] = current_offset[0] + offset_rate
                        current_offset[1] = current_offset[1] + offset_rate
                        offset_changed = True
                    if pan_center[0] > 1800 and pan_center[
                        1] < 200:  # RIGHT AND UP
                        current_offset[0] = current_offset[0] - offset_rate
                        current_offset[1] = current_offset[1] + offset_rate
                        offset_changed = True
                    if pan_center[0] > 1800 and pan_center[
                        1] > 950:  # RIGHT AND DOWN
                        current_offset[0] = current_offset[0] - offset_rate
                        current_offset[1] = current_offset[1] - offset_rate
                        offset_changed = True
                    if pan_center[0] < 200 and pan_center[
                        1] > 950:  # LEFT AND DOWN
                        current_offset[0] = current_offset[0] + offset_rate
                        current_offset[1] = current_offset[1] - offset_rate
                        offset_changed = True
                    if pan_center[0] < 200:  # LEFT
                        current_offset[0] = current_offset[0] + offset_rate
                        offset_changed = True
                    if pan_center[0] > 1800:  # RIGHT
                        current_offset[0] = current_offset[0] - offset_rate
                        offset_changed = True
                    if pan_center[1] < 200:  # UP
                        current_offset[1] = current_offset[1] + offset_rate
                        offset_changed = True
                    if pan_center[1] > 950:  # DOWN
                        current_offset[1] = current_offset[1] - offset_rate
                        offset_changed = True

            if event.type == TANGIBLEDEATH:
                if event.who.get_class_id() == DRAG:
                    deaths[DRAG] = True
                    tang[DRAG].set_alive(deaths[DRAG])
                    log(tang[DRAG])
                    timer_drag = time.perf_counter()

                if event.who.get_class_id() == HIGHLIGHT:
                    deaths[HIGHLIGHT] = True
                    tang[HIGHLIGHT].set_alive(deaths[HIGHLIGHT])
                    log(tang[HIGHLIGHT])
                    timer_highlight = time.perf_counter()

                if event.who.get_class_id() == PAN:
                    deaths[PAN] = True
                    tang[PAN].set_alive(deaths[PAN])
                    log(tang[PAN])
                    timer_pan = time.perf_counter()

                if event.who.get_class_id() == ZOOM:
                    deaths[ZOOM] = True
                    tang[ZOOM].set_alive(deaths[ZOOM])
                    log(tang[ZOOM])
                    zoomed_img = None
                    timer_zoom = time.perf_counter()

                if event.who.get_class_id() == GROUP:
                    deaths[GROUP] = True
                    tang[GROUP].set_alive(deaths[GROUP])
                    log(tang[GROUP])
                    timer_group = time.perf_counter()

        # Collision
        for x in tang.keys():
            collisions[x] = pygame.sprite.spritecollide(tang[x],
                                                        image_list, False)

        # Handle all death flags
        if deaths[
            DRAG] and time.perf_counter() - timer_drag > timer_delay and not once_drag:
            delta = (0, 0)
            tang[DRAG].set_lockable(False)
            once_drag = True
            for x in lockList:
                x.unlock()
                lockList.remove(x)
        if deaths[HIGHLIGHT] and time.perf_counter() - \
                timer_highlight > timer_delay and not once_highlight:
            once_highlight = True
            collisions[HIGHLIGHT] = []

            # PAN offset application
        if offset_changed:
            offset_delta = [current_offset[0] - old_offset[0],
                            current_offset[1] - old_offset[1]]
            for x in image_list:
                x.move(offset_delta[0], offset_delta[1])
            offset_changed = False
            old_offset[0] += offset_delta[0]
            old_offset[1] += offset_delta[1]

        # DRAW
        screen.fill(white)
        tangible_list.draw(screen)
        image_list.draw(screen)
        if zoomed_img is not None:
            zoomed_img.draw_unscaled(screen, zoom_center)
        pygame.display.flip()
        clock.tick(30)


# run the main function only if this module is executed as the main script
# (if you import this as a module then nothing is executed)
# if __name__ == "__main__":
# call the main function
main()
