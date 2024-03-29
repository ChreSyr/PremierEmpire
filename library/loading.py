
import pygame
from library.memory import Memory, resource_path


def set_progression(prc):

    if loading_screen:

        logo_top, logo_left = screen_size[0] / 2 - logo.get_width() / 2,\
                              screen_size[1] / 2 - logo.get_height() / 2
        screen.fill(fuchsia)  # Transparent background
        pygame.draw.rect(screen, (255, 255, 255), pygame.Rect(int(logo_top), int(logo_left),
                                                   int(logo.get_width() * prc), logo.get_height()))
        screen.blit(logo, (logo_top, logo_left))
        pygame.display.update()


pygame.init()
memory = Memory()
screen_size = memory.screen_size.get()
loading_screen = True


def load(name):

    return pygame.image.load(resource_path(f"images/{name}.png"))

pygame.display.set_icon(load("icon"))

if loading_screen:
    # LOADING SCREEN

    logo = load("logo")
    screen = pygame.display.set_mode(screen_size, pygame.NOFRAME | pygame.HIDDEN)
    pygame.display.set_mode(screen_size, pygame.NOFRAME | pygame.SHOWN)
    done = False
    fuchsia = (1, 0, 0)  # Transparency color

    # Transparency
    try:
        import win32api
        import win32con
        import win32gui
        # Create layered window
        hwnd = pygame.display.get_wm_info()["window"]
        win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE,
                               win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) | win32con.WS_EX_LAYERED)
        # Set window transparency color
        win32gui.SetLayeredWindowAttributes(hwnd, win32api.RGB(*fuchsia), 0, win32con.LWA_COLORKEY)
    except ModuleNotFoundError:
        pass

    set_progression(0)
