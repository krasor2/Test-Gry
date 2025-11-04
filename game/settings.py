import pygame

SCREEN_WIDTH = 960
SCREEN_HEIGHT = 540
FPS = 60

BACKGROUND_COLOR = (20, 28, 22)
GRID_COLOR = (35, 55, 38)
UI_COLOR = (238, 255, 220)

FONT_NAME = "freesansbold.ttf"

PLAYER_SPEED = 240

# Enemy definitions: (speed, health, color)
ENEMY_TYPES = {
    "Sproutling": {
        "speed": 100,
        "health": 30,
        "color": (120, 255, 120),
        "size": 26,
        "description": "Powolny kiełek, ale bardzo liczny.",
    },
    "Root Beast": {
        "speed": 70,
        "health": 60,
        "color": (205, 120, 60),
        "size": 36,
        "description": "Gruby korzeń z solidną ilością zdrowia.",
    },
    "Sporeshroom": {
        "speed": 140,
        "health": 25,
        "color": (180, 160, 255),
        "size": 22,
        "description": "Szybki grzybek, który próbuje okrążyć bohatera.",
    },
}

WEAPON_DEFS = {
    "Seed Blaster": {
        "color": (255, 235, 120),
        "cooldown": 0.25,
        "bullet_speed": 520,
        "bullet_damage": 15,
        "spread": 0,
        "projectiles": 1,
        "description": "Szybko strzela nasionami o umiarkowanych obrażeniach.",
    },
    "Thorn Fork": {
        "color": (120, 255, 120),
        "cooldown": 0.6,
        "bullet_speed": 420,
        "bullet_damage": 12,
        "spread": 12,
        "projectiles": 3,
        "description": "Trójstrzał z cierni – idealny na grupy.",
    },
    "Solar Beam": {
        "color": (255, 180, 80),
        "cooldown": 0.9,
        "bullet_speed": 620,
        "bullet_damage": 28,
        "spread": 4,
        "projectiles": 2,
        "piercing": 1,
        "description": "Wolniejszy, ale przebija dodatkowego wroga.",
    },
}

PARTICLE_COLORS = [
    (255, 180, 80),
    (255, 255, 160),
    (120, 255, 120),
    (180, 160, 255),
]


pygame.init()
FONT_CACHE = {}

def get_font(size: int) -> pygame.font.Font:
    key = (FONT_NAME, size)
    if key not in FONT_CACHE:
        FONT_CACHE[key] = pygame.font.Font(FONT_NAME, size)
    return FONT_CACHE[key]
