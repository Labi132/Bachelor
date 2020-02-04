import argparse
import threading

from lib.pythonosc import dispatcher
from lib.pythonosc import osc_server

from parsers.MessageParser import MessageParser
from parsers.MessageTypes import MessageTypes

from EventFire import EventFire


import pygame
import sys
from views.images import Images
from views.tangible import Tangible

white = [255, 255, 255]
red = [255, 0, 0]
images = {('views/img0.png', (200, 100)), ('views/img1.jpg', (550, 100)),
          ('views/img2.jpg', (900, 100)), ('views/img3.jpg', (1250, 100))}
          #,('img4.jpg', (1600, 100)), ('img5.jpg', (200, 300)),
          #('img6.png', (550, 300)), ('img7.png', (900, 300)),
          #('img8.png', (1250, 300)), ('img9.jpg', (1600, 300))}

# , , , , , ,
# 'img10.jpg', 'img11.jpg', 'img12.jpg'}



# define a main function
def main():
    event_source = EventFire()
    tangible_list = None
    tangible_pos = None
    tangible_delta = None

    #Aus Jürgens Code
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

    # initialize the pygame module
    pygame.init()
    TANGIBLEMOVE = pygame.USEREVENT + 1
    TANGIBLEDEATH = pygame.USEREVENT + 2
    clock = pygame.time.Clock()
    lockable = True
    # create a surface on screen that has the size of 240 x 180
    screen = pygame.display.set_mode((0, 0), pygame.NOFRAME)
    tangible_list = pygame.sprite.Group()
    control_rect = Tangible()
    tangible_list.add(control_rect)
    control_rect.set_center(pygame.mouse.get_pos())
    image_list = pygame.sprite.Group()
    for x in images:
        newImage = Images(x[0])
        newImage.set_center(x[1][0], x[1][1])
        image_list.add(newImage)

    lockList = []
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
                if event.key == pygame.K_SPACE:
                    print(mp.get_tracked_objects())
                    lockable = not lockable
            if not lockable and lockList != []:
                for x in lockList:
                    x.unlock()
                    lockList.remove(x)
            if event.type == pygame.MOUSEMOTION:
                collisions = pygame.sprite.spritecollide(control_rect,
                                                         image_list,
                                                         False)
                delta = pygame.mouse.get_rel()
                control_rect.move(delta[0], delta[1])
                for x in lockList:
                    x.move(delta[0], delta[1])
                if collisions != [] and lockable:
                    for x in collisions:
                        if x.get_locked() == False:
                            x.lock()
                            lockList.append(x)
                            for y in lockList:
                                if y not in collisions:
                                    y.unlock()
                                    lockList.remove(y)
            if event.type == pygame.MOUSEBUTTONDOWN:
                collisions = pygame.sprite.spritecollide(control_rect,
                                                         image_list, False)
                if collisions:
                    for i in range(len(collisions)):
                        collisions[i].invert_highlight()
            if event.type == TANGIBLEMOVE:
                print(event.who)
            if event.type == TANGIBLEDEATH:
                print(event.who)
        screen.fill(white)
        # tangible_list.update()
        # image_list.update()
        tangible_list.draw(screen)
        image_list.draw(screen)
        for x in image_list:
            x.draw_highlight(screen)
        pygame.display.flip()
        clock.tick(30)


# run the main function only if this module is executed as the main script
# (if you import this as a module then nothing is executed)
# if __name__ == "__main__":
# call the main function
main()
