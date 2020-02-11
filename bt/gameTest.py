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
from views.images import Images, ImageList
from views.tangible import Tangible

white = [255, 255, 255]
red = [255, 0, 0]

HIGHLIGHT = 0
DRAG = 1
GROUP = 2
PAN = 3

images = {('views/Bilder/city/c1.jpg', (200, 100)),
          ('views/Bilder/city/c2.jpg', (550, 100)),
          ('views/Bilder/city/c3.jpg', (900, 100)),
          ('views/Bilder/food/f1.jpg', (1250, 100)),
          ('views/Bilder/food/f2.jpg', (1600, 100)),
          ('views/Bilder/food/f3.jpg', (200, 300)),
          ('views/Bilder/food/f4.jpg', (550, 300)),
          ('views/Bilder/food/f5.jpg', (900, 300)),
          ('views/Bilder/food/f6.jpg', (1250, 300)),
          ('views/Bilder/food/f7.jpg', (1600, 300)),
          ('views/Bilder/pet/p1.jpg', (200, 500)),
          ('views/Bilder/pet/p2.jpg', (550, 500)),
          ('views/Bilder/pet/p3.jpg', (900, 500)),
          ('views/Bilder/pet/p4.jpg', (1250, 500)),
          ('views/Bilder/pet/p5.jpg', (1600, 500)),
          ('views/Bilder/pet/p6.jpg', (200, 700)),
          ('views/Bilder/pet/p7.jpg', (550, 700)),
          ('views/Bilder/vacation/v1.jpg', (900, 700)),
          ('views/Bilder/vacation/v2.jpg', (1250, 700)),
          ('views/Bilder/vacation/v3.jpg', (1600, 700)),
          ('views/Bilder/vacation/v4.jpg', (200, 900)),
          ('views/Bilder/vacation/v5.jpg', (550, 900)),
          ('views/Bilder/vacation/v6.jpg', (900, 900)),
          ('views/Bilder/vacation/v7.jpg', (1250, 900)),
          ('views/Bilder/screenshot/s1.PNG', (1600, 900))}

tangibles = {HIGHLIGHT: [100, 0, 100], DRAG: [0, 255, 0], GROUP: [255, 0, 0],
             PAN: [255, 255, 0]}
tang = {}


def create_tangibles(tangl):
    for key in tangibles:
        new_tang = Tangible([], key)
        tang[key] = new_tang
        tangl.add(new_tang)


def create_images(imgl):
    for x in images:
        new_image = Images(x[0])
        new_image.set_center(x[1][0], x[1][1])
        imgl.add(new_image)


def move_all_images(imgl, amount):
    for x in imgl:
        x.move(amount[0], amount[1])

    # , , , , , ,


# 'img10.jpg', 'img11.jpg', 'img12.jpg'}

# TODO: Loggen von aktuellen tangible positionen auf der Oberfläche


# define a main function
def main():
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

    control_rect = Tangible([], 4)
    tang[4] = control_rect  # TODO: ENTFERNEN; NUR ZUM TESTEN
    tangible_list.add(control_rect)
    control_rect.set_center(pygame.mouse.get_pos())

    lockList = []

    """Flags und Timer um zu schnelles bewegen als Fehler etwas zu vermindern"""
    timer_drag = time.perf_counter()
    timer_highlight = time.perf_counter()
    timer_pan = time.perf_counter()
    timer_group = time.perf_counter()
    drag_death = False
    highlight_death = False
    pan_death = False
    group_death = False
    timer_delay = 0.5

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
                    drag_death = False
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
                    highlight_death = False
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
                    group_death = False
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

                if event.who.get_class_id() == PAN:
                    pan_death = False
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
                    drag_death = True
                    timer_drag = time.perf_counter()

                if event.who.get_class_id() == HIGHLIGHT:
                    highlight_death = True
                    timer_highlight = time.perf_counter()

                if event.who.get_class_id() == PAN:
                    pan_death = True
                    timer_pan = time.perf_counter()

                if event.who.get_class_id() == GROUP:
                    group_death = True
                    timer_group = time.perf_counter()

        # Handle all death flags
        if drag_death and time.perf_counter() - timer_drag > timer_delay:
            delta = (0, 0)
            tang[DRAG].set_lockable(False)
            for x in lockList:
                x.unlock()
                lockList.remove(x)
        if highlight_death and time.perf_counter() - timer_highlight > timer_delay:
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
        for y in tangible_list:
            print(y.get_id())
            print(y.get_center())
            # TODO: Logging; ID, location, (mode), death
            # TODO Tangible Logging: Beschleunigung, modus, ID
        clock.tick(30)


# run the main function only if this module is executed as the main script
# (if you import this as a module then nothing is executed)
# if __name__ == "__main__":
# call the main function
main()
