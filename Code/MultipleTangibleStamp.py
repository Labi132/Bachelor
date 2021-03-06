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
from views.tangible import Tangible

import nasatlx

white = [255, 255, 255]


CITY = 0
FOOD = 1
PET = 2
SCREENSHOT = 3
VACATION = 4
ENTER = 5

TANGIBLEMOVE = pygame.USEREVENT + 1  # custom events für tangible aktionen
TANGIBLEDEATH = pygame.USEREVENT + 2
TANGIBLESWITCH = pygame.USEREVENT + 3
FINISH = pygame.USEREVENT + 4

images = {('/home/lab/Desktop/Eder-Bachelor/Bachelor/Code/views/Bilder/city/1850-31663-22486.jpg', 'city'),
          ('/home/lab/Desktop/Eder-Bachelor/Bachelor/Code/views/Bilder/city/16698-19509-21439.jpg', 'city'),
          ('/home/lab/Desktop/Eder-Bachelor/Bachelor/Code/views/Bilder/city/2527-28344-8750.jpg', 'city'),
          ('/home/lab/Desktop/Eder-Bachelor/Bachelor/Code/views/Bilder/food/1784-13303-25651.jpg', 'food'),
          ('/home/lab/Desktop/Eder-Bachelor/Bachelor/Code/views/Bilder/food/26952-9826-8440.jpg', 'food'),
          ('/home/lab/Desktop/Eder-Bachelor/Bachelor/Code/views/Bilder/food/5814-21354-6198.jpg', 'food'),
          ('/home/lab/Desktop/Eder-Bachelor/Bachelor/Code/views/Bilder/food/6922-6421-23761.jpg', 'food'),
          ('/home/lab/Desktop/Eder-Bachelor/Bachelor/Code/views/Bilder/food/9136-30157-13435.jpg', 'food'),
          ('/home/lab/Desktop/Eder-Bachelor/Bachelor/Code/views/Bilder/food/7630-25710-28850.jpg', 'food'),
          ('/home/lab/Desktop/Eder-Bachelor/Bachelor/Code/views/Bilder/food/13227-23271-24173.jpg', 'food'),
          ('/home/lab/Desktop/Eder-Bachelor/Bachelor/Code/views/Bilder/pet/1663-8828-20036.jpg', 'pet'),
          ('/home/lab/Desktop/Eder-Bachelor/Bachelor/Code/views/Bilder/pet/21345-21403-26991.jpg', 'pet'),
          ('/home/lab/Desktop/Eder-Bachelor/Bachelor/Code/views/Bilder/pet/21725-31359-17861.jpg', 'pet'),
          ('/home/lab/Desktop/Eder-Bachelor/Bachelor/Code/views/Bilder/pet/5024-11894-22132.jpg', 'pet'),
          ('/home/lab/Desktop/Eder-Bachelor/Bachelor/Code/views/Bilder/pet/9197-7767-11525.jpg', 'pet'),
          ('/home/lab/Desktop/Eder-Bachelor/Bachelor/Code/views/Bilder/pet/21481-16485-2477.jpg', 'pet'),
          ('/home/lab/Desktop/Eder-Bachelor/Bachelor/Code/views/Bilder/pet/11026-4826-27783.jpg', 'pet'),
          ('/home/lab/Desktop/Eder-Bachelor/Bachelor/Code/views/Bilder/vacation/1520-27418-20445.jpg', 'vacation'),
          ('/home/lab/Desktop/Eder-Bachelor/Bachelor/Code/views/Bilder/vacation/11135-26313-18055.jpg', 'vacation'),
          ('/home/lab/Desktop/Eder-Bachelor/Bachelor/Code/views/Bilder/vacation/15850-29087-12247.jpg', 'vacation'),
          ('/home/lab/Desktop/Eder-Bachelor/Bachelor/Code/views/Bilder/vacation/13395-18402-20194.jpg', 'vacation'),
          ('/home/lab/Desktop/Eder-Bachelor/Bachelor/Code/views/Bilder/vacation/18127-625-18110.jpg', 'vacation'),
          ('/home/lab/Desktop/Eder-Bachelor/Bachelor/Code/views/Bilder/vacation/12269-16141-10967.jpg', 'vacation'),
          ('/home/lab/Desktop/Eder-Bachelor/Bachelor/Code/views/Bilder/vacation/28778-18317-17021.jpg', 'vacation'),
          ('/home/lab/Desktop/Eder-Bachelor/Bachelor/Code/views/Bilder/screenshot/1579-24281-14320.PNG', 'screen'),
          ('/home/lab/Desktop/Eder-Bachelor/Bachelor/Code/views/Bilder/screenshot/18291-15368-23200.PNG', 'screen'),
          ('/home/lab/Desktop/Eder-Bachelor/Bachelor/Code/views/Bilder/screenshot/6338-9164-14544.PNG', 'screen')}


positions = {
    (100, 100), (100, 350), (100, 600), (100, 850),
    (350, 100), (350, 350), (350, 600), (350, 850),
    (600, 100), (600, 350), (600, 600), (600, 850),
    (850, 100), (850, 350), (850, 600),  # (850, 850),
    (1100, 100), (1100, 350), (1100, 600),  # (1150, 850),
    (1350, 100), (1350, 350), (1350, 600),  # (1400, 850),
    (1600, 100), (1600, 350), (1600, 600),
    (1850, 100), (1850, 350), (1850, 600)}

tangibles = {CITY: 0, FOOD: 1, PET: 2, SCREENSHOT: 3, VACATION: 4, ENTER: 5 }

tang = {}

folders = {}

# TANGIBLES, FOLDERS_INVERS UND SCREENS SIND IN DER REIHENFOLGE IDENTISCH
# AUFGRUND FOLGENDER AUFRUFE.
# TODO: UMGEHEN

folders_invers = {'city': 0, 'food': 1, 'pet': 2, 'screen': 3, 'vacation': 4,
                  'main': 5}

screens = {0: 'city', 1: 'food', 2: 'pet', 3: 'screen',
           4: 'vacation', 5: 'main'}

events = {12: "Quit", 25: "Movement", 26: "Death", 27: "Switch", 28: "Finish"}

image_counts = {'screen': 3, 'city': 3, 'vacation': 7, 'pet': 7, 'food': 7}

PID = None
INTERACTION = None

image_counter = 0


logging.basicConfig(filename='tangibles_log.txt', format='%(asctime)s %(message)s',
                    level=logging.INFO)


def create_tangibles(tangl):
    for key in tangibles:
        new_tang = Tangible(key)
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

    food_folder = ImageFolder('food', position_list)
    folders[1] = food_folder

    pet_folder = ImageFolder('pet', position_list)
    folders[2] = pet_folder

    screen_folder = ImageFolder('screen', position_list)
    folders[3] = screen_folder

    vacation_folder = ImageFolder('vacation', position_list)
    folders[4] = vacation_folder


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


def reset_folder_position():
    folders[0].set_center(850, 850)
    folders[1].set_center(1075, 850)
    folders[2].set_center(1300, 850)
    folders[3].set_center(1525, 850)
    folders[4].set_center(1750, 850)


def log(tangible, eventtype, mode):
    message = ", " + str(PID) + ", "
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


def start_servers(event_source):
    """
        Copyright Jürgen Hahn
        Jürgen Hahn, M.Sc.
        Nachwuchsgruppe / Junior Research Group
        "Physical-Digital Affordances"
        Lehrstuhl für Medieninformatik / Media Informatics Group
        Universität Regensburg
        Universitätsstr. 31
        93053 Regensburg
        Germany

        Tel.: +49941 46297 - 537
        E-Mail: juergen.hahn@ur.de
        Web: http://mi.ur.de/sekretariat-team/juergen-hahn/index.html
        PDA: https://hci.ur.de/people/juergen_hahn
        Twitter: https://twitter.com/JuergenHahn1
    """
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
    # ENDE Copyright


def move_image(collisions_img_folders, current_screen, new_screen):
    for i in range(len(collisions_img_folders)):
        if collisions_img_folders[i]:
            x = collisions_img_folders[i]
            global image_counter
            if isinstance(x, Images):
                if x.get_active():
                    current = x.get_screen()
                    if current == new_screen:
                        if current != screens[5]:
                            y = folders_invers[current]
                            folders[y].remove_item()
                        x.change_screen(screens[5])
                        image_counter += 1
                    else:
                        if current != screens[5]:
                            y = folders_invers[current]
                            folders[y].remove_item()
                        else:
                            image_counter -= 1
                        x.change_screen(new_screen)
                        folders[i].add_item()
                    x.update(current_screen)


def tangible_alive(tangible, event, mode):
    tangible.set_alive(True)
    log(tangible, event.type, mode)
    tangible.set_center(event.who.get_bounds_component().get_position())


# define a main function
def main():
    # TODO: WIEDER EINBAUEN

    global PID
    global INTERACTION

    PID = sys.argv[1]
    INTERACTION = sys.argv[2]

    pos_list = list(positions)
    pos_list.sort()

    testlog = "Time, PID, Interaction Style, Mode, Event-type, ID, Alive?, Center"
    logging.info(testlog)

    mode = None

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
    global image_counter
    image_counter = len(image_list.sprites())

    """Flags und Timer um zu schnelles bewegen als Fehler etwas zu vermindern"""
    timer_enter = time.perf_counter()
    timer_delay = 0.5

    """Flags damit die endgültigen death events nur einmal pro death ausgelöst 
    werden"""
    once_enter = False

    folder_once = False

    current_screen = screens[5]

    create_folders(folder_list, dragable_list, pos_list)
    reset_folder_position()

    collisions_tangibles = [None, None, None, None, None, None]

    # define a variable to control the main loop
    running = True

    # main loop
    while running:
        # event handling, gets all event from the event queue
        # Collision
        # TODO: Zoom ordner?, bug beim groupen im gleichen ordner reproduzeiren
        #  und fixen, list-Error beim ordnerwechsel fixen
        for x in tang.keys():
            collisions_tangibles[x] = pygame.sprite.spritecollide(tang[x],
                                                                  image_list,
                                                                  False)

        collisions_open_folders = pygame.sprite.spritecollide(tang[ENTER],
                                                              folder_list,
                                                              False)

        check_ending(image_list)

        for event in pygame.event.get():
            if event.type == FINISH:
                log(tang[CITY], event.type, mode)
                running = False
                server.shutdown()
                pygame.quit()
                nasatlx.main()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    log(tang[CITY], pygame.QUIT, mode)
                    running = False
                    server.shutdown()
                    pygame.quit()
                    nasatlx.main()

            if event.type == TANGIBLEMOVE:
                # Enter
                if event.who.get_class_id() == ENTER:
                    once_enter = False
                    tangible_alive(tang[ENTER], event, mode)
                    if collisions_open_folders and not folder_once:
                        if current_screen == collisions_open_folders[0].get_tag():
                            current_screen = screens[5]
                            image_list.update(current_screen)
                            reset_image_positions(image_list, pos_list)
                            reset_folder_position()
                        else:
                            current_screen = collisions_open_folders[0].get_tag()
                            collisions_open_folders[0].reset_positions(image_list)
                            reset_folder_position()
                        folder_once = True

                # City
                if event.who.get_class_id() == CITY:
                    tangible_alive(tang[CITY], event, mode)
                    move_image(collisions_tangibles[CITY],
                               current_screen, screens[CITY])

                # Screenshot
                if event.who.get_class_id() == SCREENSHOT:
                    tangible_alive(tang[SCREENSHOT], event, mode)
                    move_image(collisions_tangibles[SCREENSHOT],
                               current_screen, screens[SCREENSHOT])

                # Food
                if event.who.get_class_id() == FOOD:
                    tangible_alive(tang[FOOD], event, mode)
                    move_image(collisions_tangibles[FOOD],
                               current_screen, screens[FOOD])

                # Pet
                if event.who.get_class_id() == PET:
                    tangible_alive(tang[PET], event, mode)
                    move_image(collisions_tangibles[PET],
                               current_screen, screens[PET])

                # Vacation
                if event.who.get_class_id() == VACATION:
                    tangible_alive(tang[VACATION], event, mode)
                    move_image(collisions_tangibles[VACATION],
                               current_screen, screens[VACATION])

            if event.type == TANGIBLEDEATH:
                tangible_id = event.who.get_class_id()
                tang[tangible_id].set_alive(False)
                log(tang[tangible_id], event.type, mode)


        if not tang[ENTER].get_alive() and time.perf_counter() - \
                timer_enter > timer_delay:
            collisions_tangibles[ENTER] = []
            if not once_enter:
                tang[ENTER].set_center((-500, -500))
                once_enter = True
                folder_once = False

        # DRAW
        screen.fill(white)
        for key in folders:
            folders[key].draw(screen)
        dragable_list.update(current_screen)
        image_list.draw(screen, current_screen)
        pygame.display.flip()
        clock.tick(30)


# run the main function only if this module is executed as the main script
# (if you import this as a module then nothing is executed)
# if __name__ == "__main__":
# call the main function
main()
