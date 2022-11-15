
import pygame

yellow = pygame.image.load("Images/Unused/soldier_yellow.png")
blue = pygame.image.load("Images/Unused/soldier_blue.png")
green = pygame.image.load("Images/Unused/soldier_green.png")
red = pygame.image.load("Images/Unused/soldier_red.png")
gray = pygame.image.load("Images/Unused/soldier_gray.png")
pink = pygame.image.load("Images/Unused/soldier_pink.png")

w, h = yellow.get_size()

soldiers = pygame.Surface((w * 3, h * 2), pygame.SRCALPHA)
soldiers.blit(yellow, (w * 0, h * 0))
soldiers.blit(blue, (w * 1, h * 0))
soldiers.blit(green, (w * 2, h * 0))
soldiers.blit(red, (w * 0, h * 1))
soldiers.blit(gray, (w * 1, h * 1))
soldiers.blit(pink, (w * 2, h * 1))

pygame.image.save(soldiers, "Images/soldiers2.png")
