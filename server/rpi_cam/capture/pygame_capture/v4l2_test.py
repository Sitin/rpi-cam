import time

from PIL import Image
import pygame.image
import pygame.camera


FPS = 24


pygame.camera.init()
pygame.camera.list_cameras()

camera = pygame.camera.Camera(pygame.camera.list_cameras()[0], (320, 240))

camera.start()

for i in range(100):
    filename = '/tmp/pygame_captured{:04d}.jpg'.format(i)

    start = time.time()

    surface = camera.get_image()
    pygame.image.save(surface, filename)

    end = time.time()

    print('Saved as {filename} for {milis:08.6f} ms'.format(filename=filename, milis=(end - start) * 1000))

    if 1/FPS > (end - start):
        sleeping_time = 1/FPS - (end-start)
        print('Sleeping for {} miliseconds...'.format(sleeping_time * 1000))
        time.sleep(sleeping_time)

camera.stop()
