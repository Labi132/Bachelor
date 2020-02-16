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

from views.images import Images, ImageList, ImageFolder
from views.tangible import Tangible, Circle

white = [255, 255, 255]

HIGHLIGHT = 0
DRAG = 1
GROUP = 2
PAN = 3
ZOOM = 4

images = {('views/Bilder/city/c1.jpg', 'city'),
          ('views/Bilder/city/c2.jpg', 'city'),
          ('views/Bilder/city/c3.jpg', 'city'),
          ('views/Bilder/food/f1.jpg', 'food'),
          ('views/Bilder/food/f2.jpg', 'food'),
          ('views/Bilder/food/f3.jpg', 'food'),
          ('views/Bilder/food/f4.jpg', 'food'),
          ('views/Bilder/food/f5.jpg', 'food'),
          ('views/Bilder/food/f6.jpg', 'food'),
          ('views/Bilder/food/f7.jpg', 'food'),
          ('views/Bilder/pet/p1.jpg', 'pet'),
          ('views/Bilder/pet/p2.jpg', 'pet'),
          ('views/Bilder/pet/p3.jpg', 'pet'),
          ('views/Bilder/pet/p4.jpg', 'pet'),
          ('views/Bilder/pet/p5.jpg', 'pet'),
          ('views/Bilder/pet/p6.jpg', 'pet'),
          ('views/Bilder/pet/p7.jpg', 'pet'),
          ('views/Bilder/vacation/v1.jpg', 'vacation'),
          ('views/Bilder/vacation/v2.jpg', 'vacation'),
          ('views/Bilder/vacation/v3.jpg', 'vacation'),
          ('views/Bilder/vacation/v4.jpg', 'vacation'),
          ('views/Bilder/vacation/v5.jpg', 'vacation'),
          ('views/Bilder/vacation/v6.jpg', 'vacation'),
          ('views/Bilder/vacation/v7.jpg', 'vacation'),
          ('views/Bilder/screenshot/s1.PNG', 'screen'),
          ('views/Bilder/screenshot/s2.PNG', 'screen'),
          ('views/Bilder/screenshot/s3.PNG', 'screen')}

positions = {
    (100, 100), (100, 350), (100, 600), (100, 850),
    (350, 100), (350, 350), (350, 600), (350, 850),
    (600, 100), (600, 350), (600, 600), (600, 850),
    (850, 100), (850, 350), (850, 600),  # (850, 850),
    (1100, 100), (1100, 350), (1100, 600),  # (1150, 850),
    (1350, 100), (1350, 350), (1350, 600),  # (1400, 850),
    (1600, 100), (1600, 350), (1600, 600),
    (1850, 100), (1850, 350), (1850, 600)}

tangibles = {HIGHLIGHT: 0, DRAG: 1, GROUP: 2, PAN: 3, ZOOM: 4}
tang = {}

folders = {}

screens = {0: 'city', 1: 'vacation', 2: 'pet', 3: 'food',
           4: 'screen', 5: 'main'}

events = {25: "Movement", 26: "Death", 27: "Switch"}

image_counts = {'screen': 3, 'city': 3, 'vacation': 7, 'pet': 7, 'food': 7}

PID = None
INTERACTION = "Multiple"

logging.basicConfig(filename='log.txt', format='%(asctime)s %(message)s',
                    level=logging.INFO)


# Stacking oder kleinere kacheln, dateiname, programmatisches ende

def create_tangibles(tangl):
    for key in tangibles:
        new_tang = Tangible([], key)
        tang[key] = new_tang
        tangl.add(new_tang)


def create_images(imgl, dragl):
    position_list = list(positions)
    random.shuffle(position_list)
    k = 0

    for x in images:
        new_image = Images(x, screens[5])
        new_image.set_center(position_list[k][0], position_list[k][1])
        k = k + 1
        imgl.add(new_image)
        dragl.add(new_image)


def log(tangible, eventtype, mode):
    message = str(PID) + ", "
    # "PID: " + str(PID) + ", "
    message += str(INTERACTION) + ", "
    # "Interaction Style: " + str(INTERACTION) + ", "
    """if INTERACTION == "Multiple":"""
    message += str(mode) + ", "
    # "Mode: " + str(MODE) + ", "
    message += str(events[eventtype]) + ", "
    # "Eventtype: " + str(events[eventtype]) + ", "
    message += str(tangible.get_id()) + ", "
    # "ID: " + str(tangible.get_id()) + ", "
    message += str(tangible.get_alive()) + ", "
    # "Dead: " + str(tangible.get_alive()) + ", "
    message += str(tangible.get_center())
    # "Center: " + str(tangible.get_center())
    logging.info(message)


# define a main function
def main():
    pos_list = list(positions)
    pos_counter = 0
    # Highlight
    highlight_coll = []
    testlog = "PID, Interaction Style, Mode, Eventtype, ID, Dead, Center"
    print(testlog)
    logging.info(testlog)
    # Pan
    old_offset = [0, 0]
    current_offset = [0, 0]
    offset_rate = 3
    offset_changed = False
    pan_circle = Circle()
    pan_tolerance = 50

    mode = None

    # Zoom
    zoomed_img = None

    # Event Source for Servers
    event_source = EventFire()

    # Bottle Server
    bottle = Bottle(event_source)
    threading.Thread(target=bottle.run).start()

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

    # create a surface on screen
    screen = pygame.display.set_mode((0, 0), pygame.NOFRAME)

    tangible_list = pygame.sprite.LayeredUpdates()
    create_tangibles(tangible_list)
    tang[DRAG].set_lockable(True)

    dragable_list = pygame.sprite.Group()

    image_list = ImageList()
    create_images(image_list, dragable_list)

    lockList = []

    """Flags und Timer um zu schnelles bewegen als Fehler etwas zu vermindern"""
    timer_drag = time.perf_counter()
    timer_highlight = time.perf_counter()

    deaths = {HIGHLIGHT: True, DRAG: True, GROUP: True, PAN: True, ZOOM: True}
    timer_delay = 0.5

    """Flags damit die endgültigen death events nur einmal pro death ausgelöst 
    werden"""
    once_drag = False
    once_highlight = False

    current_screen = screens[5]

    city_folder = ImageFolder('city')
    city_folder.set_center(850, 900)
    folders[0] = city_folder
    vacation_folder = ImageFolder('vacation')
    vacation_folder.set_center(1075, 900)
    folders[1] = vacation_folder
    pet_folder = ImageFolder('pet')
    pet_folder.set_center(1300, 900)
    folders[2] = pet_folder
    food_folder = ImageFolder('food')
    food_folder.set_center(1525, 900)
    folders[3] = food_folder
    screen_folder = ImageFolder('screen')
    screen_folder.set_center(1750, 900)
    folders[4] = screen_folder

    dragable_list.add(city_folder, vacation_folder, pet_folder, food_folder,
                      screen_folder)

    collisions_folders = [None, None, None, None, None]

    collisions_tangibles = [None, None, None, None, None]

    # define a variable to control the main loop
    running = True

    # main loop
    while running:
        # event handling, gets all event from the event queue
        if pos_counter+1 == len(pos_list):
            pos_counter = 0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # change the value to False, to exit the main loop
                running = False
                server.shutdown()
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                    server.shutdown()
                    pygame.quit()
                    sys.exit()
                if event.key == pygame.K_SPACE:
                    tang[DRAG].invert_lockable()
                    current_screen = screens[4]

            if event.type == TANGIBLESWITCH:
                log(tang[event.who.get_class_id()], event.type, mode)
                mode = event.mode
                log(tang[event.who.get_class_id()], event.type, mode)

            if event.type == TANGIBLEMOVE:
                # move tangibles into folders
                k = 0
                for i in range(len(collisions_folders)):
                    if collisions_folders[i]:
                        collisions_folders[i][k].change_screen(
                            screens[i], pos_list[pos_counter])
                        pos_counter += 1
                        k += 1


                # Drag
                if event.who.get_class_id() == DRAG:
                    if deaths[DRAG]:
                        collisions_tangibles[DRAG] = []
                        tang[DRAG].set_center(
                            event.who.get_bounds_component().get_position())
                        tang[DRAG].set_lockable(True)
                    deaths[DRAG] = False
                    tang[DRAG].set_alive(deaths[DRAG])
                    log(tang[DRAG], event.type, mode)
                    move_pos = tang[DRAG].get_center()
                    tang[DRAG].set_center(
                        event.who.get_bounds_component().get_position())
                    current_center = tang[DRAG].get_center()
                    delta = (move_pos[0] - current_center[0],
                             move_pos[1] - current_center[1])
                    if collisions_tangibles[DRAG] != [] and tang[
                        DRAG].get_lockable():
                        for x in collisions_tangibles[DRAG]:
                            if not x.get_locked():
                                x.lock()
                                lockList.append(x)
                                for y in lockList:
                                    if y not in collisions_tangibles[DRAG]:
                                        y.unlock()
                                        lockList.remove(y)
                    for x in lockList:
                        image_center = x.get_center()
                        try:
                            x.set_center(image_center[0] - delta[0],
                                        image_center[1] - delta[1])
                        except:
                            pass

                # Highlight
                if event.who.get_class_id() == HIGHLIGHT:  # HIGHLIGHTING GEHT
                    deaths[HIGHLIGHT] = False
                    once_highlight = False
                    tang[HIGHLIGHT].set_alive(deaths[HIGHLIGHT])
                    log(tang[HIGHLIGHT], event.type, mode)
                    tang[HIGHLIGHT].set_center(
                        event.who.get_bounds_component().get_position())
                    if highlight_coll:
                        for x in highlight_coll:
                            if x not in collisions_tangibles[HIGHLIGHT]:
                                x.set_light_changed(False)
                                highlight_coll.remove(x)
                    if collisions_tangibles[HIGHLIGHT]:
                        for x in collisions_tangibles[HIGHLIGHT]:
                            x.invert_highlight()
                            x.set_light_changed(True)
                            highlight_coll.append(x)

                # Group
                if event.who.get_class_id() == GROUP:  # Funktioniert, allerdings noch ohne offset und nicht animiert
                    deaths[GROUP] = False
                    tang[GROUP].set_alive(deaths[GROUP])
                    log(tang[GROUP], event.type, mode)
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
                    log(tang[ZOOM], event.type, mode)
                    tang[ZOOM].set_center(
                        event.who.get_bounds_component().get_position())
                    zoom_center = tang[ZOOM].get_center()
                    if deaths[ZOOM]:
                        deaths[ZOOM] = False
                        tang[ZOOM].set_alive(deaths[ZOOM])
                    if zoom_center[0] < 960:
                        align_right = True
                    else:
                        align_right = False
                    if collisions_tangibles[ZOOM]:
                        if len(collisions_tangibles[ZOOM]) > 1:
                            zoomed_img = collisions_tangibles[ZOOM][0]
                            pass
                        else:
                            zoomed_img = collisions_tangibles[ZOOM][0]
                            if align_right:
                                # zoomed_img.zoom(zoom_center, align_right)
                                pass
                            else:
                                pass
                    else:
                        zoomed_img = None

                # PAN mit Kreis
                if event.who.get_class_id() == PAN:
                    tang[PAN].set_center(
                        event.who.get_bounds_component().get_position())
                    log(tang[PAN], event.type, mode)
                    if deaths[PAN]:
                        deaths[PAN] = False
                        tang[PAN].set_alive(deaths[PAN])
                        tang[PAN].set_center(
                            event.who.get_bounds_component().get_position())
                        pan_center = tang[PAN].get_center()
                        pan_circle.set_center(pan_center)
                    tang_pan_center = tang[PAN].get_center()
                    pan_delta = (tang_pan_center[0] - pan_center[0],
                                 tang_pan_center[1] - pan_center[1])
                    if pan_delta[0] > pan_tolerance:  # rechts
                        current_offset[0] = current_offset[0] - offset_rate
                        offset_changed = True
                    if pan_delta[0] < -1 * pan_tolerance:  # links
                        current_offset[0] = current_offset[0] + offset_rate
                        offset_changed = True
                    if pan_delta[1] > pan_tolerance:  # hoch
                        current_offset[1] = current_offset[1] + offset_rate
                        offset_changed = True
                    if pan_delta[1] < -1 * pan_tolerance:  # runter
                        current_offset[1] = current_offset[1] - offset_rate
                        offset_changed = True

            if event.type == TANGIBLEDEATH:
                if event.who.get_class_id() == DRAG:
                    deaths[DRAG] = True
                    tang[DRAG].set_alive(deaths[DRAG])
                    log(tang[DRAG], event.type, mode)
                    timer_drag = time.perf_counter()

                if event.who.get_class_id() == HIGHLIGHT:
                    deaths[HIGHLIGHT] = True
                    tang[HIGHLIGHT].set_alive(deaths[HIGHLIGHT])
                    log(tang[HIGHLIGHT], event.type, mode)
                    timer_highlight = time.perf_counter()

                if event.who.get_class_id() == PAN:
                    deaths[PAN] = True
                    tang[PAN].set_alive(deaths[PAN])
                    log(tang[PAN], event.type, mode)
                    timer_pan = time.perf_counter()

                if event.who.get_class_id() == ZOOM:
                    deaths[ZOOM] = True
                    tang[ZOOM].set_alive(deaths[ZOOM])
                    log(tang[ZOOM], event.type, mode)
                    zoomed_img = None
                    timer_zoom = time.perf_counter()

                if event.who.get_class_id() == GROUP:
                    deaths[GROUP] = True
                    tang[GROUP].set_alive(deaths[GROUP])
                    log(tang[GROUP], event.type, mode)
                    timer_group = time.perf_counter()

        # Handle all death flags
        if deaths[DRAG] and time.perf_counter() - timer_drag > timer_delay:
            tang[DRAG].set_lockable(False)
            collisions_tangibles[DRAG] = []
            for x in lockList:
                x.unlock()
                lockList.remove(x)

        if deaths[HIGHLIGHT] and time.perf_counter() - \
                timer_highlight > timer_delay and not once_highlight:
            once_highlight = True
            collisions_tangibles[HIGHLIGHT] = []

        # Collision
        for x in tang.keys():
            if x != DRAG:
                if x != HIGHLIGHT:
                    collisions_tangibles[x] = pygame.sprite.spritecollide(
                        tang[x],
                        image_list, False)
                else:
                    collisions_tangibles[x] = pygame.sprite.spritecollide(
                        tang[x], dragable_list, False)
            else:
                collisions_tangibles[x] = pygame.sprite.spritecollide(tang[x],
                                                                      dragable_list,
                                                                      False)

        for x in folders.keys():
            print(x)
            print(folders[x])
            collisions_folders[x] = pygame.sprite.spritecollide(folders[x],
                                                                image_list,
                                                                False)
            print(len(collisions_folders))

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
        # if current_screen ==
        screen.fill(white)

        for key in folders:
            folders[key].draw(screen)

        # tangible_list.draw(screen)
        image_list.update(current_screen)
        image_list.draw(screen, current_screen)
        if zoomed_img is not None:
            zoomed_img.draw_unscaled(screen, align_right, current_screen)
        if not deaths[PAN]:
            pan_circle.draw(screen)
        pygame.display.flip()
        clock.tick(30)


# run the main function only if this module is executed as the main script
# (if you import this as a module then nothing is executed)
# if __name__ == "__main__":
# call the main function
main()
