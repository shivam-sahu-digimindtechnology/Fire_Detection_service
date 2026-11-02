import pygame
import time

pygame.mixer.init()

pygame.mixer.music.load(r'F:\Fire_Detection_service\fire_service\demo\vdo\alert.mp3')

pygame.mixer.music.play()

print('ALARM PLAYING...')

time.sleep(5)

pygame.mixer.music.stop()

print('ALARM STOPPED')