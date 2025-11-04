from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import List, Optional

import pygame

from . import audio, settings


def create_weapon(name: str) -> "Weapon":
    info = settings.WEAPON_DEFS[name]
    return Weapon(
        name=name,
        color=pygame.Color(*info["color"]),
        cooldown=info["cooldown"],
        bullet_speed=info["bullet_speed"],
        bullet_damage=info["bullet_damage"],
        spread=info["spread"],
        projectiles=info["projectiles"],
        pierce=info.get("piercing", 0),
    )


@dataclass
class Particle:
    position: pygame.math.Vector2
    velocity: pygame.math.Vector2
    color: pygame.Color
    lifetime: float
    radius: float

    def update(self, dt: float) -> None:
        self.position += self.velocity * dt
        self.lifetime -= dt
        self.radius = max(0, self.radius - 40 * dt)

    def draw(self, surface: pygame.Surface) -> None:
        if self.lifetime <= 0 or self.radius <= 0:
            return
        pygame.draw.circle(surface, self.color, self.position, int(self.radius))


@dataclass
class Bullet:
    position: pygame.math.Vector2
    velocity: pygame.math.Vector2
    color: pygame.Color
    damage: float
    radius: float = 6
    pierce: int = 0
    alive: bool = True

    def update(self, dt: float, bounds: pygame.Rect) -> None:
        if not self.alive:
            return
        self.position += self.velocity * dt
        if not bounds.collidepoint(self.position.x, self.position.y):
            self.alive = False

    def draw(self, surface: pygame.Surface) -> None:
        if self.alive:
            pygame.draw.circle(surface, self.color, self.position, int(self.radius))


@dataclass
class Enemy:
    position: pygame.math.Vector2
    velocity: pygame.math.Vector2
    speed: float
    health: float
    max_health: float
    color: pygame.Color
    size: int
    name: str

    def update(self, dt: float, player_pos: pygame.math.Vector2) -> None:
        direction = (player_pos - self.position)
        if direction.length_squared() > 0:
            direction = direction.normalize()
        self.velocity = direction * self.speed
        self.position += self.velocity * dt

    @property
    def rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.position.x - self.size / 2), int(self.position.y - self.size / 2), self.size, self.size)

    def take_damage(self, amount: float) -> None:
        self.health -= amount

    def is_dead(self) -> bool:
        return self.health <= 0

    def draw(self, surface: pygame.Surface) -> None:
        rect = self.rect
        pygame.draw.ellipse(surface, self.color, rect)
        eye_color = (20, 20, 20)
        pygame.draw.circle(surface, eye_color, (rect.centerx - rect.width // 6, rect.centery - rect.height // 6), max(2, rect.width // 10))
        pygame.draw.circle(surface, eye_color, (rect.centerx + rect.width // 6, rect.centery - rect.height // 6), max(2, rect.width // 10))
        pygame.draw.arc(surface, eye_color, rect.inflate(-rect.width // 3, -rect.height // 2), 3.4, 5.0, 2)


@dataclass
class Weapon:
    name: str
    color: pygame.Color
    cooldown: float
    bullet_speed: float
    bullet_damage: float
    spread: float
    projectiles: int
    pierce: int = 0
    timer: float = 0.0

    def try_fire(self, position: pygame.math.Vector2, target: pygame.math.Vector2) -> List[Bullet]:
        if self.timer > 0:
            return []
        direction = (target - position)
        if direction.length_squared() == 0:
            direction = pygame.math.Vector2(1, 0)
        base_angle = direction.angle_to(pygame.math.Vector2(1, 0))
        bullets = []
        spread_step = self.spread / max(1, self.projectiles - 1) if self.projectiles > 1 else 0
        start_angle = base_angle - self.spread / 2
        for i in range(self.projectiles):
            angle = start_angle + i * spread_step
            vector = pygame.math.Vector2(1, 0).rotate(-angle)
            bullet = Bullet(
                position=pygame.math.Vector2(position),
                velocity=vector * self.bullet_speed,
                color=self.color,
                damage=self.bullet_damage,
                pierce=self.pierce,
            )
            bullets.append(bullet)
        self.timer = self.cooldown
        return bullets

    def update(self, dt: float) -> None:
        self.timer = max(0.0, self.timer - dt)


@dataclass
class Player:
    position: pygame.math.Vector2
    speed: float
    radius: int = 24
    color: pygame.Color = field(default_factory=lambda: pygame.Color(120, 200, 120))
    weapon: Optional[Weapon] = None
    health: int = 100

    def handle_input(self, dt: float) -> None:
        keys = pygame.key.get_pressed()
        velocity = pygame.math.Vector2(0, 0)
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            velocity.y -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            velocity.y += 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            velocity.x -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            velocity.x += 1
        if velocity.length_squared() > 0:
            velocity = velocity.normalize()
        self.position += velocity * self.speed * dt

    def keep_in_bounds(self, bounds: pygame.Rect) -> None:
        self.position.x = max(bounds.left + self.radius, min(bounds.right - self.radius, self.position.x))
        self.position.y = max(bounds.top + self.radius, min(bounds.bottom - self.radius, self.position.y))

    def draw(self, surface: pygame.Surface) -> None:
        pygame.draw.circle(surface, self.color, self.position, self.radius)
        eye_color = pygame.Color(30, 50, 30)
        pygame.draw.circle(surface, eye_color, (int(self.position.x - self.radius / 3), int(self.position.y - self.radius / 3)), 4)
        pygame.draw.circle(surface, eye_color, (int(self.position.x + self.radius / 3), int(self.position.y - self.radius / 3)), 4)
        pygame.draw.arc(surface, eye_color, pygame.Rect(self.position.x - self.radius / 2, self.position.y - self.radius / 4, self.radius, self.radius / 2), 3.4, 5.0, 2)


class GameWorld:
    def __init__(self, weapon_name: Optional[str] = None) -> None:
        self.bounds = pygame.Rect(0, 0, settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT)
        self.player = Player(
            position=pygame.math.Vector2(settings.SCREEN_WIDTH // 2, settings.SCREEN_HEIGHT // 2),
            speed=settings.PLAYER_SPEED,
        )
        self.enemies: List[Enemy] = []
        self.bullets: List[Bullet] = []
        self.particles: List[Particle] = []
        self.elapsed = 0.0
        self.spawn_timer = 0.0
        self.spawn_interval = 1.4
        self.score = 0
        self.weapon_name: Optional[str] = None
        if weapon_name:
            self.set_weapon_by_name(weapon_name)

    def set_weapon(self, weapon: Weapon) -> None:
        self.weapon_name = weapon.name
        self.player.weapon = weapon

    def set_weapon_by_name(self, name: str) -> None:
        self.set_weapon(create_weapon(name))

    def update(self, dt: float) -> None:
        self.elapsed += dt
        self.player.handle_input(dt)
        self.player.keep_in_bounds(self.bounds)

        if self.player.weapon:
            self.player.weapon.update(dt)

        mouse_pos = pygame.math.Vector2(pygame.mouse.get_pos())
        mouse_pressed = pygame.mouse.get_pressed()[0]
        if mouse_pressed and self.player.weapon and self.player.health > 0:
            new_bullets = self.player.weapon.try_fire(self.player.position, mouse_pos)
            if new_bullets:
                self.bullets.extend(new_bullets)
                audio.play("shoot")

        for bullet in self.bullets:
            bullet.update(dt, self.bounds)

        self.bullets = [b for b in self.bullets if b.alive]

        for enemy in self.enemies:
            enemy.update(dt, self.player.position)

        self.handle_collisions()

        for particle in self.particles:
            particle.update(dt)
        self.particles = [p for p in self.particles if p.lifetime > 0 and p.radius > 0]

        player_alive = self.player.health > 0

        if not player_alive:
            return

        self.spawn_timer -= dt
        if self.spawn_timer <= 0:
            self.spawn_enemy_wave()
            self.spawn_timer = max(0.4, self.spawn_interval - self.elapsed * 0.01)

    def handle_collisions(self) -> None:
        player_rect = pygame.Rect(0, 0, self.player.radius * 2, self.player.radius * 2)
        player_rect.center = self.player.position
        for enemy in list(self.enemies):
            if enemy.rect.colliderect(player_rect):
                self.player.health -= 10
                self.spawn_particles(enemy.position, enemy.color)
                audio.play("hit")
                enemy.take_damage(enemy.health)
                if enemy.is_dead() and enemy in self.enemies:
                    self.enemies.remove(enemy)
            for bullet in list(self.bullets):
                if bullet.alive and enemy.rect.collidepoint(bullet.position):
                    enemy.take_damage(bullet.damage)
                    self.spawn_particles(bullet.position, bullet.color)
                    audio.play("hit")
                    if enemy.is_dead():
                        self.score += 5
                        self.spawn_particles(enemy.position, enemy.color)
                        self.enemies.remove(enemy)
                    if bullet.pierce > 0:
                        bullet.pierce -= 1
                    else:
                        bullet.alive = False
                    break

        if self.player.health <= 0:
            self.player.health = 0

    def spawn_enemy_wave(self) -> None:
        spawn_count = 1 + int(self.elapsed // 12)
        for _ in range(spawn_count):
            type_name = random.choices(list(settings.ENEMY_TYPES.keys()), weights=[0.5, 0.3, 0.2])[0]
            info = settings.ENEMY_TYPES[type_name]
            spawn_edge = random.choice(['top', 'bottom', 'left', 'right'])
            if spawn_edge == 'top':
                pos = pygame.math.Vector2(random.randint(0, settings.SCREEN_WIDTH), -info['size'])
            elif spawn_edge == 'bottom':
                pos = pygame.math.Vector2(random.randint(0, settings.SCREEN_WIDTH), settings.SCREEN_HEIGHT + info['size'])
            elif spawn_edge == 'left':
                pos = pygame.math.Vector2(-info['size'], random.randint(0, settings.SCREEN_HEIGHT))
            else:
                pos = pygame.math.Vector2(settings.SCREEN_WIDTH + info['size'], random.randint(0, settings.SCREEN_HEIGHT))
            enemy = Enemy(
                position=pos,
                velocity=pygame.math.Vector2(0, 0),
                speed=info['speed'],
                health=info['health'],
                max_health=info['health'],
                color=pygame.Color(*info['color']),
                size=info['size'],
                name=type_name,
            )
            self.enemies.append(enemy)

    def spawn_particles(self, position: pygame.math.Vector2, color: pygame.Color) -> None:
        palette = list(settings.PARTICLE_COLORS) + [(color.r, color.g, color.b)]
        for _ in range(12):
            velocity = pygame.math.Vector2(random.uniform(-120, 120), random.uniform(-120, 120))
            particle_color = random.choice(palette)
            particle = Particle(
                position=pygame.math.Vector2(position),
                velocity=velocity,
                color=pygame.Color(*particle_color),
                lifetime=random.uniform(0.2, 0.6),
                radius=random.uniform(2, 6),
            )
            self.particles.append(particle)

    def draw(self, surface: pygame.Surface) -> None:
        self.draw_grid(surface)
        for particle in self.particles:
            particle.draw(surface)
        for enemy in self.enemies:
            enemy.draw(surface)
        for bullet in self.bullets:
            bullet.draw(surface)
        self.player.draw(surface)

    def draw_grid(self, surface: pygame.Surface) -> None:
        surface.fill(settings.BACKGROUND_COLOR)
        spacing = 48
        for x in range(0, settings.SCREEN_WIDTH, spacing):
            pygame.draw.line(surface, settings.GRID_COLOR, (x, 0), (x, settings.SCREEN_HEIGHT))
        for y in range(0, settings.SCREEN_HEIGHT, spacing):
            pygame.draw.line(surface, settings.GRID_COLOR, (0, y), (settings.SCREEN_WIDTH, y))

    def draw_ui(self, surface: pygame.Surface) -> None:
        font_small = settings.get_font(20)
        font_large = settings.get_font(32)
        health_text = font_large.render(f"Zdrowie: {self.player.health}", True, settings.UI_COLOR)
        surface.blit(health_text, (20, 20))
        score_text = font_small.render(f"Wynik: {self.score}", True, settings.UI_COLOR)
        surface.blit(score_text, (20, 60))
        timer_text = font_small.render(f"Czas: {int(self.elapsed)} s", True, settings.UI_COLOR)
        surface.blit(timer_text, (20, 84))
        if self.player.weapon:
            weapon_text = font_small.render(f"Broń: {self.player.weapon.name}", True, settings.UI_COLOR)
            surface.blit(weapon_text, (20, 108))
        if self.player.health <= 0:
            go_font = settings.get_font(48)
            go_text = go_font.render("Przegrałeś! Naciśnij R aby spróbować ponownie", True, settings.UI_COLOR)
            surface.blit(go_text, (settings.SCREEN_WIDTH / 2 - go_text.get_width() / 2, settings.SCREEN_HEIGHT / 2 - 24))

    def reset(self) -> None:
        weapon_name = self.weapon_name
        self.__init__(weapon_name=weapon_name)
        if weapon_name:
            audio.play("power")
