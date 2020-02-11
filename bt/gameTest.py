import argparse
import threading

from lib.pythonosc import dispatcher
from lib.pythonosc import osc_server

from parsers.MessageParser import MessageParser
from parsers.MessageTypes import MessageTypes

from EventFire import EventFire

import pygame
import sys
import time
import logging
import random
from views.images import Images, ImageList
from views.tangible import Tangible

white = [255, 255, 255]
red = [255, 0, 0]

HIGHLIGHT = 0
DRAG = 1
GROUP = 2
PAN = 3

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
    (200, 100), (200, 400), (200, 700), (200, 1000), (200, 1300), (200, 1600),
    (650, 100), (650, 400), (650, 700), (650, 1000), (650, 1300), (650, 1600),
    (1100, 100), (1100, 400), (1100, 700), (1100, 1000), (1100, 1300),
    (1550, 100), (1550, 400), (1550, 700), (1550, 1000), (1550, 1300),
    (2000, 100), (2000, 400), (2000, 700), (2000, 1000), (2000, 1300)}

tangibles = {HIGHLIGHT: 0, DRAG: 1, GROUP: 2, PAN: 3}
tang = {}


def create_tangibles(tangl):
    for key in tangibles:
        new_tang = Tangible([], key)
        tang[key] = new_tang
        tangl.add(new_tang)


def create_images(imgl):
    # muss der screenshot volle größe / größer als 300, 150 sein / screenshot hochformat?
    position_list = list(positions)
    random.shuffle(position_list)
    k = 0

    for x in images:
        new_image = Images(x)
        new_image.set_center(position_list[k][0], position_list[k][1])
        k = k + 1
        imgl.add(new_image)


"""
def move_all_images(imgl, amount):
    for x in imgl:
        x.move(amount[0], amount[1])
"""


# define a main function
def main():
    logging.basicConfig(filename='log.txt', format='%(asctime)s %(message)s',
                        level=logging.INFO)
    highlight_coll = []
    old_offset = [0, 0]
    current_offset = [0, 0]
    offset_rate = 3
    offset_changed = False
    # zoomed_img = None

    event_source = EventFire()
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

    clock = pygame.time.Clock()
    # create a surface on screen that has the size of 240 x 180
    screen = pygame.display.set_mode((0, 0), pygame.NOFRAME)

    tangible_list = pygame.sprite.LayeredUpdates()
    create_tangibles(tangible_list)
    tang[DRAG].set_lockable(True)

    image_list = ImageList()
    create_images(image_list)

    """
    control_rect = Tangible([], 4)
    tang[4] = control_rect  # TODO: ENTFERNEN; NUR ZUM TESTEN
    tangible_list.add(control_rect)
    control_rect.set_center(pygame.mouse.get_pos())
    """

    lockList = []

    """Flags und Timer um zu schnelles bewegen als Fehler etwas zu vermindern"""
    timer_drag = time.perf_counter()
    timer_highlight = time.perf_counter()
    timer_pan = time.perf_counter()
    timer_group = time.perf_counter()
    deaths = {DRAG: False, HIGHLIGHT: False, PAN: False, GROUP: False}
    timer_delay = 0.5

    """Timer fürs Logging"""
    timer_log = time.perf_counter()
    logging_delay = 1

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

            if event.type == TANGIBLEMOVE:
                if event.who.get_class_id() == DRAG:
                    deaths[DRAG] = False
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

                    """
                    tangible_list.remove(control_rect)
                    control_rect = Tangible(event.who.get_bounds_component(), 4)
                    control_rect.recolor(tangibles[event.who.get_class_id()])
                    tangible_list.add(control_rect)
                    """

                if event.who.get_class_id() == HIGHLIGHT:  # HIGHLIGHTING GEHT
                    deaths[HIGHLIGHT] = False
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

                if event.who.get_class_id() == GROUP:  # Funktioniert, allerdings noch ohne offset und nicht animiert
                    deaths[GROUP] = False
                    tang[GROUP].set_center(
                        event.who.get_bounds_component().get_position())
                    group_center = tang[GROUP].get_center()
                    k = 0
                    for x in image_list:
                        if x.get_highlight():
                            img_center = x.get_center()
                            group_delta = (group_center[0] - img_center[0] + k,
                                           group_center[1] - img_center[1] + k)
                            x.rect.move_ip(group_delta)
                            k += 40  # offset vielleicht differenzieren
                """
                # Zoom
                if event.who.get_class_id() == PAN:
                    pan_death = False
                    tang[PAN].set_center(event.who.get_bounds_component().get_position())
                    pan_center = tang[PAN].get_center()
                    if pan_center[0] < 900:
                        align_right = True
                    else:
                        align_right = False
                    if collisions[PAN]:
                        if len(collisions[PAN])>1:
                            print(collisions[PAN])
                            # TODO: make sure only biggest overlap is used
                            pass
                        else:
                            print(collisions[PAN])
                            if align_right:
                                zoomed_img = collisions[PAN][0]
                                zoomed_img.zoom(pan_center, align_right)
                """

                # PAN
                if event.who.get_class_id() == PAN:
                    deaths[PAN] = False
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
                    timer_drag = time.perf_counter()

                if event.who.get_class_id() == HIGHLIGHT:
                    deaths[HIGHLIGHT] = True
                    timer_highlight = time.perf_counter()

                if event.who.get_class_id() == PAN:
                    deaths[PAN] = True
                    timer_pan = time.perf_counter()

                if event.who.get_class_id() == GROUP:
                    deaths[GROUP] = True
                    timer_group = time.perf_counter()

        # Handle all death flags
        if deaths[DRAG] and time.perf_counter() - timer_drag > timer_delay:
            delta = (0, 0)
            tang[DRAG].set_lockable(False)
            for x in lockList:
                x.unlock()
                lockList.remove(x)
        if deaths[
            HIGHLIGHT] and time.perf_counter() - timer_highlight > timer_delay:
            collisions[HIGHLIGHT] = []
        # if group_death and time.perf_counter() - timer_group > 0.5: # nötig?

        for x in tang.keys():
            collisions[x] = pygame.sprite.spritecollide(tang[x],
                                                        image_list, False)

        # DRAW
        screen.fill(white)

        # tangible_list.update()
        if offset_changed:
            offset_delta = [current_offset[0] - old_offset[0],
                            current_offset[1] - old_offset[1]]
            for x in image_list:
                x.move(offset_delta[0], offset_delta[1])
            offset_changed = False
            old_offset[0] += offset_delta[0]
            old_offset[1] += offset_delta[1]
        tangible_list.draw(screen)
        image_list.draw(screen)
        # for x in image_list:
        #    x.draw_highlight(screen)
        pygame.display.flip()
        if time.perf_counter() - timer_log > logging_delay:
            for y in tangible_list:
                message = "ID: " + str(y.get_id()) + ", "
                message += "Alive: " + str(deaths[y.get_id()]) + ", "
                message += "Center: " + str(y.get_center())

                # message += y.get_center
                print(y.get_id())
                print(y.get_center())
                # TODO: Logging; ID, location, (mode), death
                # TODO Tangible Logging: Beschleunigung, modus, ID
                logging.info(message)
            timer_log = time.perf_counter()
        clock.tick(30)


# run the main function only if this module is executed as the main script
# (if you import this as a module then nothing is executed)
# if __name__ == "__main__":
# call the main function
main()
