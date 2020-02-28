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

from views.images import Images, ImageList, ImageFolder
from views.tangible import Tangible, Circle

import nasatlx

white = [255, 255, 255]

HIGHLIGHT = 0
DRAG = 1
GROUP = 2
PAN = 3
ZOOM = 4

TANGIBLEMOVE = pygame.USEREVENT + 1  # custom events für tangible aktionen
TANGIBLEDEATH = pygame.USEREVENT + 2
TANGIBLESWITCH = pygame.USEREVENT + 3
FINISH = pygame.USEREVENT + 4

images = {('/home/lab/Desktop/Eder-Bachelor/Bachelor/bt/views/Bilder/city/1850-31663-22486.jpg', 'city'),
          ('/home/lab/Desktop/Eder-Bachelor/Bachelor/bt/views/Bilder/city/16698-19509-21439.jpg', 'city'),
          ('/home/lab/Desktop/Eder-Bachelor/Bachelor/bt/views/Bilder/city/2527-28344-8750.jpg', 'city'),
          ('/home/lab/Desktop/Eder-Bachelor/Bachelor/bt/views/Bilder/food/1784-13303-25651.jpg', 'food'),
          ('/home/lab/Desktop/Eder-Bachelor/Bachelor/bt/views/Bilder/food/26952-9826-8440.jpg', 'food'),
          ('/home/lab/Desktop/Eder-Bachelor/Bachelor/bt/views/Bilder/food/5814-21354-6198.jpg', 'food'),
          ('/home/lab/Desktop/Eder-Bachelor/Bachelor/bt/views/Bilder/food/6922-6421-23761.jpg', 'food'),
          ('/home/lab/Desktop/Eder-Bachelor/Bachelor/bt/views/Bilder/food/9136-30157-13435.jpg', 'food'),
          ('/home/lab/Desktop/Eder-Bachelor/Bachelor/bt/views/Bilder/food/7630-25710-28850.jpg', 'food'),
          ('/home/lab/Desktop/Eder-Bachelor/Bachelor/bt/views/Bilder/food/13227-23271-24173.jpg', 'food'),
          ('/home/lab/Desktop/Eder-Bachelor/Bachelor/bt/views/Bilder/pet/1663-8828-20036.jpg', 'pet'),
          ('/home/lab/Desktop/Eder-Bachelor/Bachelor/bt/views/Bilder/pet/21345-21403-26991.jpg', 'pet'),
          ('/home/lab/Desktop/Eder-Bachelor/Bachelor/bt/views/Bilder/pet/21725-31359-17861.jpg', 'pet'),
          ('/home/lab/Desktop/Eder-Bachelor/Bachelor/bt/views/Bilder/pet/5024-11894-22132.jpg', 'pet'),
          ('/home/lab/Desktop/Eder-Bachelor/Bachelor/bt/views/Bilder/pet/9197-7767-11525.jpg', 'pet'),
          ('/home/lab/Desktop/Eder-Bachelor/Bachelor/bt/views/Bilder/pet/21481-16485-2477.jpg', 'pet'),
          ('/home/lab/Desktop/Eder-Bachelor/Bachelor/bt/views/Bilder/pet/11026-4826-27783.jpg', 'pet'),
          ('/home/lab/Desktop/Eder-Bachelor/Bachelor/bt/views/Bilder/vacation/1520-27418-20445.jpg', 'vacation'),
          ('/home/lab/Desktop/Eder-Bachelor/Bachelor/bt/views/Bilder/vacation/11135-26313-18055.jpg', 'vacation'),
          ('/home/lab/Desktop/Eder-Bachelor/Bachelor/bt/views/Bilder/vacation/15850-29087-12247.jpg', 'vacation'),
          ('/home/lab/Desktop/Eder-Bachelor/Bachelor/bt/views/Bilder/vacation/13395-18402-20194.jpg', 'vacation'),
          ('/home/lab/Desktop/Eder-Bachelor/Bachelor/bt/views/Bilder/vacation/18127-625-18110.jpg', 'vacation'),
          ('/home/lab/Desktop/Eder-Bachelor/Bachelor/bt/views/Bilder/vacation/12269-16141-10967.jpg', 'vacation'),
          ('/home/lab/Desktop/Eder-Bachelor/Bachelor/bt/views/Bilder/vacation/28778-18317-17021.jpg', 'vacation'),
          ('/home/lab/Desktop/Eder-Bachelor/Bachelor/bt/views/Bilder/screenshot/1579-24281-14320.PNG', 'screen'),
          ('/home/lab/Desktop/Eder-Bachelor/Bachelor/bt/views/Bilder/screenshot/18291-15368-23200.PNG', 'screen'),
          ('/home/lab/Desktop/Eder-Bachelor/Bachelor/bt/views/Bilder/screenshot/6338-9164-14544.PNG', 'screen')}


positions = {
    (100, 100), (100, 350), (100, 600), (100, 850),
    (350, 100), (350, 350), (350, 600), (350, 850),
    (600, 100), (600, 350), (600, 600), (600, 850),
    (850, 100), (850, 350), (850, 600),  # (850, 850),
    (1100, 100), (1100, 350), (1100, 600),  # (1150, 850),
    (1350, 100), (1350, 350), (1350, 600),  # (1400, 850),
    (1600, 100), (1600, 350), (1600, 600),
    (1850, 100), (1850, 350), (1850, 600)}

tangibles = {HIGHLIGHT: 0, DRAG: 1, ZOOM: 2, PAN: 3, GROUP: 4}

tang = {}

folders = {}

folders_invers = {'city': 0, 'vacation': 1, 'pet': 2, 'food': 3, 'screen': 4,
                  'main': 5}

screens = {0: 'city', 1: 'vacation', 2: 'pet', 3: 'food',
           4: 'screen', 5: 'main'}

events = {12: "Quit", 25: "Movement", 26: "Death", 27: "Switch", 28: "Finish"}

image_counts = {'screen': 3, 'city': 3, 'vacation': 7, 'pet': 7, 'food': 7}

PID = None
INTERACTION = None


logging.basicConfig(filename='log.txt', format='%(asctime)s %(message)s',
                    level=logging.INFO)


def create_tangibles(tangl):
    for key in tangibles:
        new_tang = Tangible([], key)
        tang[key] = new_tang
        tangl.add(new_tang)


def create_images(imgl, dragl):
    image_list = list(images)
    position_list = list(positions)
    random.shuffle(image_list)
    k = 0
    for x in image_list:
        new_image = Images(x, screens[5])
        new_image.set_center(position_list[k][0], position_list[k][1])
        k += 1
        imgl.add(new_image)
        dragl.add(new_image)


def create_folders(folder_list, dragable_list, position_list):
    city_folder = ImageFolder('city', position_list)
    folders[0] = city_folder

    vacation_folder = ImageFolder('vacation', position_list)
    folders[1] = vacation_folder

    pet_folder = ImageFolder('pet', position_list)
    folders[2] = pet_folder

    food_folder = ImageFolder('food', position_list)
    folders[3] = food_folder

    screen_folder = ImageFolder('screen', position_list)
    folders[4] = screen_folder

    folder_list.add(city_folder, vacation_folder, pet_folder, food_folder,
                    screen_folder)
    dragable_list.add(city_folder, vacation_folder, pet_folder, food_folder,
                      screen_folder)


def reset_image_positions(imagl, pos_list):
    k = 0
    for x in imagl:
        if x.get_screen() == screens[5]:
            x.set_center_reset(pos_list[k][0], pos_list[k][1])
            k += 1


def check_ending(imgl):
    for x in imgl:
        if not x.get_correct():
            return False
    my_event = pygame.event.Event(FINISH)
    pygame.event.post(my_event)


def reset_folder_position(folderl):
    folder = folderl.sprites()
    folder[0].set_center(850, 850)
    folder[1].set_center(1075, 850)
    folder[2].set_center(1300, 850)
    folder[3].set_center(1525, 850)
    folder[4].set_center(1750, 850)


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
    # "Alive: " + str(tangible.get_alive()) + ", "
    message += str(tangible.get_center())
    # "Center: " + str(tangible.get_center())
    logging.info(message)


def death_drag(lock_list):
    tang[DRAG].set_lockable(False)
    for x in lock_list:
        x.unlock()
        lock_list.remove(x)


def start_servers(event_source):
    # threading.Thread(target=bottle.run).start()

    # Aus Jürgens Code
    mp = MessageParser(event_source)

    dispatch = dispatcher.Dispatcher()
    dispatch.map(MessageTypes.POINTER.value, mp.parse)
    dispatch.map(MessageTypes.TOKEN.value, mp.parse)
    dispatch.map(MessageTypes.BOUNDS.value, mp.parse)
    dispatch.map(MessageTypes.FRAME.value, mp.parse)
    dispatch.map(MessageTypes.ALIVE.value, mp.parse)
    dispatch.map(MessageTypes.SYMBOL.value, mp.parse)

    server = osc_server.ThreadingOSCUDPServer(("127.0.0.1", 3333), dispatch)

    print("Serving on {}".format(server.server_address))

    server_ = threading.Thread(target=server.serve_forever)

    server_.start()

    return server
    # ENDE KOPIERTER CODE HIER


def img_folder_collision(collisions_img_folders, image_counter, current_screen):
    for i in range(len(collisions_img_folders)):
        if collisions_img_folders[i]:
            for x in collisions_img_folders[i]:
                if x.get_active():
                    prev = x.get_screen()
                    if x.get_screen() == folders[i].get_tag():
                        if prev != screens[5]:
                            y = folders_invers[prev]
                            folders[y].remove_item()
                        x.change_screen(screens[5])
                        image_counter += 1
                    else:
                        if prev != screens[5]:
                            y = folders_invers[prev]
                            folders[y].remove_item()
                        else:
                            image_counter -= 1
                        x.change_screen(screens[i])
                        folders[i].add_item()
                x.update(current_screen)


def tangible_alive(tang, event, mode):
    tang.set_alive(True)
    log(tang, event.type, mode)
    tang.set_center(event.who.get_bounds_component().get_position())


# define a main function
def main():
    global PID
    global INTERACTION

    PID = sys.argv[1]
    INTERACTION = sys.argv[2]

    pos_list = list(positions)
    pos_list.sort()

    # Highlight
    highlight_coll = []
    testlog = "PID, Interaction Style, Mode, Event-type, ID, Alive?, Center"
    logging.info(testlog)

    # Pan
    old_offset = [0, 0]
    current_offset = [0, 0]
    offset_rate = 3
    pan_tolerance = 40
    offset_changed = False
    pan_circle = Circle()

    mode = None

    # Zoom
    zoomed_img = None

    # Event Source for Servers
    event_source = EventFire()

    # Start Servers
    server = start_servers(event_source)

    # initialize the pygame module
    pygame.init()
    clock = pygame.time.Clock()

    # create a surface on screen
    screen = pygame.display.set_mode((0, 0), pygame.NOFRAME)

    tangible_list = pygame.sprite.Group()
    create_tangibles(tangible_list)

    dragable_list = pygame.sprite.Group()
    folder_list = pygame.sprite.Group()

    image_list = ImageList()
    create_images(image_list, dragable_list)
    image_counter = len(image_list.sprites())

    lockList = []

    """Flags und Timer um zu schnelles bewegen als Fehler etwas zu vermindern"""
    timer_drag = time.perf_counter()
    timer_highlight = time.perf_counter()
    timer_delay = 0.5

    """Flags damit die endgültigen death events nur einmal pro death ausgelöst 
    werden"""
    once_highlight = False

    folder_once = False

    current_screen = screens[5]

    create_folders(folder_list, dragable_list, pos_list)
    reset_folder_position(folder_list)

    collisions_img_folders = [None, None, None, None,
                              None]  # one none per folder

    collisions_tangibles = [None, None, None, None,
                            None]  # one none per tangible where collision
    # is relevant

    # define a variable to control the main loop
    running = True

    # main loop
    while running:
        # event handling, gets all event from the event queue
        # Collision
        # TODO: Zoom ordner?, bug beim groupen im gleichen ordner reproduzeiren und fixen, list-Error beim ordnerwechsel fixen
        for x in tang.keys():
            if x == PAN or x == GROUP:
                pass
            else:
                collisions_tangibles[x] = pygame.sprite.spritecollide(tang[x],
                                                                      dragable_list,
                                                                      False)

        for x in folders.keys():
            collisions_img_folders[x] = pygame.sprite.spritecollide(folders[x],
                                                                    image_list,
                                                                    False)

        collisions_open_folders = pygame.sprite.spritecollide(tang[HIGHLIGHT],
                                                              folder_list,
                                                              False)

        check_ending(image_list)

        for event in pygame.event.get():
            if event.type == FINISH:
                log(tang[DRAG], event.type, mode)
                running = False
                server.shutdown()
                pygame.quit()
                nasatlx.main()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    log(tang[DRAG], pygame.QUIT, mode)
                    running = False
                    server.shutdown()
                    pygame.quit()
                    nasatlx.main()

            if event.type == TANGIBLEMOVE:
                # move tangibles into folders
                if not tang[PAN].get_alive():
                    img_folder_collision(collisions_img_folders, image_counter,
                                         current_screen)

                # Drag
                if event.who.get_class_id() == DRAG:
                    if not tang[DRAG].get_alive():
                        collisions_tangibles[DRAG] = []
                        tang[DRAG].set_center(
                            event.who.get_bounds_component().get_position())
                        tang[DRAG].set_lockable(True)

                    move_pos = tang[DRAG].get_center()
                    tangible_alive(tang[DRAG], event, mode)
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
                        except TypeError:
                            pass

                # Highlight TODO: TESTEN OB RESETTEN DER FOLDER BESSER ANKOMMT ALS NICHT RESETTEN
                if event.who.get_class_id() == HIGHLIGHT:
                    once_highlight = False
                    tangible_alive(tang[HIGHLIGHT], event, mode)
                    if collisions_open_folders and not folder_once:
                        if current_screen == collisions_open_folders[0].get_tag():
                            current_screen = screens[5]
                            image_list.update(current_screen)
                            reset_image_positions(image_list, pos_list)
                            reset_folder_position(folder_list)
                        else:
                            current_screen = collisions_open_folders[0].get_tag()
                            collisions_open_folders[0].reset_positions(image_list)
                            reset_folder_position(folder_list)
                        folder_once = True
                    if highlight_coll:
                        for x in highlight_coll:
                            if x not in collisions_tangibles[HIGHLIGHT]:
                                x.set_light_changed(False)
                                highlight_coll.remove(x)
                    if collisions_tangibles[HIGHLIGHT]:
                        for x in collisions_tangibles[HIGHLIGHT]:
                            if isinstance(x, Images):
                                x.invert_highlight()
                                x.set_light_changed(True)
                                highlight_coll.append(x)

                # Group
                if event.who.get_class_id() == GROUP:  # Funktioniert, allerdings nicht animiert
                    tangible_alive(tang[GROUP], event, mode)
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
                    tangible_alive(tang[ZOOM], event, mode)
                    zoom_center = tang[ZOOM].get_center()
                    if zoom_center[0] < 960:
                        align_right = True
                    else:
                        align_right = False
                    if collisions_tangibles[ZOOM]:
                        if isinstance(collisions_tangibles[ZOOM][0], Images):
                            zoomed_img = collisions_tangibles[ZOOM][0]
                    else:
                        zoomed_img = None

                # PAN mit Kreis
                if event.who.get_class_id() == PAN:
                    tang[PAN].set_center(
                        event.who.get_bounds_component().get_position())
                    log(tang[PAN], event.type, mode)
                    if not tang[PAN].get_alive():
                        tang[PAN].set_alive(True)
                        tang[PAN].set_center(
                            event.who.get_bounds_component().get_position())
                        pan_center = tang[PAN].get_center()
                        pan_circle.set_center(pan_center)
                    tang_pan_center = tang[PAN].get_center()
                    pan_delta = (tang_pan_center[0] - pan_center[0],
                                 tang_pan_center[1] - pan_center[1])
                    if pan_delta[0] > pan_tolerance:  # rechts
                        current_offset[0] = current_offset[0] + offset_rate
                        offset_changed = True
                    if pan_delta[0] < -1 * pan_tolerance:  # links
                        current_offset[0] = current_offset[0] - offset_rate
                        offset_changed = True
                    if pan_delta[1] > pan_tolerance:  # hoch
                        current_offset[1] = current_offset[1] + offset_rate
                        offset_changed = True
                    if pan_delta[1] < -1 * pan_tolerance:  # runter
                        current_offset[1] = current_offset[1] - offset_rate
                        offset_changed = True

            if event.type == TANGIBLEDEATH:
                tangible_id = event.who.get_class_id()
                tang[tangible_id].set_alive(False)
                log(tang[tangible_id], event.type, mode)

                if tangible_id == ZOOM:
                    zoomed_img = None

                if tangible_id == DRAG:
                    timer_drag = time.perf_counter()

                if tangible_id == HIGHLIGHT:
                    timer_highlight = time.perf_counter()

        # Handle all death flags
        if not tang[DRAG].get_alive() and time.perf_counter() - \
                timer_drag > timer_delay:
            death_drag(lockList)
            collisions_tangibles[DRAG] = []

        if not tang[HIGHLIGHT].get_alive() and time.perf_counter() - \
                timer_highlight > timer_delay:
            collisions_tangibles[HIGHLIGHT] = []
            if not once_highlight:
                tang[HIGHLIGHT].set_center((-500, -500))
                once_highlight = True
                folder_once = False

        # PAN offset application
        if offset_changed:
            offset_delta = [current_offset[0] - old_offset[0],
                            current_offset[1] - old_offset[1]]
            for x in dragable_list:
                x.move(offset_delta[0], offset_delta[1])
            offset_changed = False
            old_offset[0] += offset_delta[0]
            old_offset[1] += offset_delta[1]

        # DRAW
        screen.fill(white)
        for key in folders:
            folders[key].draw(screen)
        dragable_list.update(current_screen)
        image_list.draw(screen, current_screen)
        if zoomed_img is not None:
            zoomed_img.draw_unscaled(screen, align_right, current_screen)
        if tang[PAN].get_alive():
            pan_circle.draw(screen)
        pygame.display.flip()
        clock.tick(30)


# run the main function only if this module is executed as the main script
# (if you import this as a module then nothing is executed)
# if __name__ == "__main__":
# call the main function
main()
