import argparse
import sys
from typing import List

import pygame

from game import audio, settings
from game.entities import GameWorld


def draw_menu(screen: pygame.Surface, weapon_names: List[str], highlighted: int) -> None:
    screen.fill(settings.BACKGROUND_COLOR)
    title_font = settings.get_font(56)
    subtitle_font = settings.get_font(24)
    option_font = settings.get_font(32)
    tip_font = settings.get_font(20)

    title = title_font.render("Chibi Garden Guardians", True, settings.UI_COLOR)
    screen.blit(title, (settings.SCREEN_WIDTH // 2 - title.get_width() // 2, 70))

    subtitle = subtitle_font.render("Wybierz broń (1-3), aby rozpocząć obronę ogródka", True, settings.UI_COLOR)
    screen.blit(subtitle, (settings.SCREEN_WIDTH // 2 - subtitle.get_width() // 2, 150))

    for idx, name in enumerate(weapon_names):
        data = settings.WEAPON_DEFS[name]
        text = option_font.render(f"{idx + 1}. {name}", True, settings.UI_COLOR)
        y = 220 + idx * 80
        x = settings.SCREEN_WIDTH // 2 - text.get_width() // 2
        screen.blit(text, (x, y))
        desc = tip_font.render(data["description"], True, settings.UI_COLOR)
        screen.blit(desc, (settings.SCREEN_WIDTH // 2 - desc.get_width() // 2, y + 42))
        if idx == highlighted:
            pygame.draw.rect(screen, data["color"], pygame.Rect(x - 18, y - 10, text.get_width() + 36, 66), 3)

    help_text = tip_font.render("Sterowanie: WSAD lub strzałki, mysz – celowanie i strzał, ESC – menu", True, settings.UI_COLOR)
    screen.blit(help_text, (settings.SCREEN_WIDTH // 2 - help_text.get_width() // 2, settings.SCREEN_HEIGHT - 70))

    pygame.display.flip()


def draw_pause_message(screen: pygame.Surface) -> None:
    font = settings.get_font(24)
    text = font.render("ESC – powrót do menu | R – restart", True, settings.UI_COLOR)
    screen.blit(text, (settings.SCREEN_WIDTH - text.get_width() - 20, settings.SCREEN_HEIGHT - 40))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Chibi Garden Guardians prototype")
    parser.add_argument("--mute", action="store_true", help="Wyłącz dźwięk oraz muzykę")
    parser.add_argument("--fullscreen", action="store_true", help="Uruchom grę w trybie pełnoekranowym")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    pygame.init()

    audio_enabled = True
    if args.mute:
        audio_enabled = False
    else:
        try:
            pygame.mixer.init()
        except pygame.error:
            audio_enabled = False
            print("Nie udało się zainicjalizować miksowania audio – gra zostanie uruchomiona w trybie bez dźwięku.")

    audio.set_audio_enabled(audio_enabled)

    display_flags = 0
    if args.fullscreen:
        display_flags |= pygame.FULLSCREEN

    screen = pygame.display.set_mode((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT), display_flags)
    clock = pygame.time.Clock()
    pygame.display.set_caption("Chibi Garden Guardians")

    if audio_enabled:
        audio.start_music()

    weapon_names = list(settings.WEAPON_DEFS.keys())
    highlighted = 0
    state = "menu"
    world = GameWorld()

    while True:
        dt = clock.tick(settings.FPS) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if state == "menu":
                if event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_ESCAPE, pygame.K_q):
                        pygame.quit()
                        sys.exit()
                    if event.key in (pygame.K_UP, pygame.K_w):
                        highlighted = (highlighted - 1) % len(weapon_names)
                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        highlighted = (highlighted + 1) % len(weapon_names)
                    elif event.key in (pygame.K_1, pygame.K_KP1):
                        highlighted = 0
                    elif event.key in (pygame.K_2, pygame.K_KP2):
                        highlighted = min(1, len(weapon_names) - 1)
                    elif event.key in (pygame.K_3, pygame.K_KP3):
                        highlighted = min(2, len(weapon_names) - 1)
                    if event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_1, pygame.K_KP1, pygame.K_2, pygame.K_KP2, pygame.K_3, pygame.K_KP3):
                        weapon_name = weapon_names[highlighted]
                        world = GameWorld(weapon_name=weapon_name)
                        audio.play("power")
                        state = "running"
            elif state == "running":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        state = "menu"
                        world = GameWorld()
                        audio.play("power")
                    if event.key == pygame.K_r and world.player.health <= 0:
                        world.reset()

        if state == "menu":
            draw_menu(screen, weapon_names, highlighted)
            continue

        world.update(dt)
        world.draw(screen)
        world.draw_ui(screen)
        draw_pause_message(screen)
        pygame.display.flip()


if __name__ == "__main__":
    main()

