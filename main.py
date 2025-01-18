import pgzrun
from pygame import Rect
import random
import math

# Constants
TITLE = "Tiny Town Survivor"
WIDTH = 800
HEIGHT = 600

# Game states
MENU = 'menu'
PLAYING = 'playing'
GAME_OVER = 'game_over'

# Simplified animations for testing
PLAYER_ANIMATIONS = {
    'idle': ['character_idle1'],  # Simplificado para um frame
    'walk': ['character_walk1'],  # Simplificado para um frame
    'attack': ['character_attack1']  # Simplificado para um frame
}

ENEMY_ANIMATIONS = {
    'idle': ['enemy_idle1'],  # Simplificado para um frame
    'walk': ['enemy_walk1']  # Simplificado para um frame
}

class GameObject:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.rect = Rect(x, y, width, height)
        self.animation_frame = 0
        self.animation_delay = 0.1
        self.animation_timer = 0
        self.current_animation = 'idle'
        self.direction = 1
        
    def update_animation(self, dt):
        self.animation_timer += dt
        if self.animation_timer >= self.animation_delay:
            self.animation_timer = 0
            self.animation_frame = (self.animation_frame + 1) % len(self.get_animation_frames())
            
    def get_animation_frames(self):
        return []
        
    def update_rect(self):
        self.rect.x = self.x
        self.rect.y = self.y

class Player(GameObject):
    def __init__(self, x, y):
        super().__init__(x, y, 32, 32)
        self.speed = 200
        self.health = 100
        self.is_attacking = False
        self.attack_timer = 0
        self.attack_duration = 0.3
        self.attack_cooldown = 0.5
        self.attack_range = 50
        
    def get_animation_frames(self):
        return PLAYER_ANIMATIONS[self.current_animation]
        
    def move(self, dx, dy, dt):
        if not self.is_attacking:
            self.x += dx * self.speed * dt
            self.y += dy * self.speed * dt
            self.update_rect()
            
            if dx != 0 or dy != 0:
                self.current_animation = 'walk'
                self.direction = 1 if dx > 0 else (-1 if dx < 0 else self.direction)
            else:
                self.current_animation = 'idle'
    
    def attack(self):
        if not self.is_attacking and self.attack_timer <= 0:
            self.is_attacking = True
            self.attack_timer = self.attack_duration
            self.current_animation = 'attack'
            try:
                if game.sound_enabled:
                    sounds.attack.play()
            except AttributeError:
                pass  # Ignora se o som não existir
    
    def update(self, dt):
        if self.is_attacking:
            self.attack_timer -= dt
            if self.attack_timer <= 0:
                self.is_attacking = False
                self.current_animation = 'idle'
                self.attack_timer = self.attack_cooldown
        elif self.attack_timer > 0:
            self.attack_timer -= dt

class Enemy(GameObject):
    def __init__(self, x, y):
        super().__init__(x, y, 32, 32)
        self.speed = 100
        self.patrol_radius = 100
        self.start_x = x
        self.start_y = y
        self.patrol_angle = random.random() * math.pi * 2
        self.health = 50
        
    def get_animation_frames(self):
        return ENEMY_ANIMATIONS[self.current_animation]
        
    def update(self, dt, player):
        self.patrol_angle += dt
        self.x = self.start_x + math.cos(self.patrol_angle) * self.patrol_radius
        self.y = self.start_y + math.sin(self.patrol_angle) * self.patrol_radius
        
        self.current_animation = 'walk'
        self.direction = 1 if math.cos(self.patrol_angle) > 0 else -1
        
        self.update_rect()
        self.update_animation(dt)

class Game:
    def __init__(self):
        self.state = MENU
        self.sound_enabled = True
        self.player = Player(WIDTH // 2, HEIGHT // 2)
        self.enemies = [
            Enemy(random.randint(100, WIDTH-100), random.randint(100, HEIGHT-100))
            for _ in range(5)
        ]
        self.buttons = {
            'start': Rect(WIDTH//2 - 100, HEIGHT//2 - 50, 200, 40),
            'sound': Rect(WIDTH//2 - 100, HEIGHT//2 + 10, 200, 40),
            'exit': Rect(WIDTH//2 - 100, HEIGHT//2 + 70, 200, 40)
        }
        
    def update(self, dt):
        if self.state == PLAYING:
            dx = dy = 0
            if keyboard.left:
                dx = -1
            elif keyboard.right:
                dx = 1
            if keyboard.up:
                dy = -1
            elif keyboard.down:
                dy = 1
            
            if keyboard.space:
                self.player.attack()
                
            self.player.move(dx, dy, dt)
            self.player.update(dt)
            self.player.update_animation(dt)
            
            enemies_to_remove = []
            for enemy in self.enemies:
                enemy.update(dt, self.player)
                
                if (self.player.is_attacking and 
                    enemy.rect.colliderect(Rect(
                        self.player.x - self.player.attack_range * (1 - self.player.direction) // 2,
                        self.player.y - self.player.attack_range // 2,
                        self.player.attack_range,
                        self.player.attack_range
                    ))):
                    enemy.health -= 25
                    if enemy.health <= 0:
                        enemies_to_remove.append(enemy)
                
                elif enemy.rect.colliderect(self.player.rect):
                    self.player.health -= 10
                    if self.player.health <= 0:
                        self.state = GAME_OVER
                        try:
                            if self.sound_enabled:
                                sounds.game_over.play()
                        except AttributeError:
                            pass
            
            for enemy in enemies_to_remove:
                self.enemies.remove(enemy)

    def draw(self):
        screen.fill((50, 50, 50))  # Cor de fundo cinza escuro
        
        if self.state == MENU:
            screen.draw.filled_rect(self.buttons['start'], (100, 100, 200))
            screen.draw.filled_rect(self.buttons['sound'], (100, 100, 200))
            screen.draw.filled_rect(self.buttons['exit'], (100, 100, 200))
            
            screen.draw.text("Start Game", center=(WIDTH//2, HEIGHT//2 - 30), color="white")
            sound_text = "Sound: ON" if self.sound_enabled else "Sound: OFF"
            screen.draw.text(sound_text, center=(WIDTH//2, HEIGHT//2 + 30), color="white")
            screen.draw.text("Exit", center=(WIDTH//2, HEIGHT//2 + 90), color="white")
            
        elif self.state == PLAYING:
            # Draw player (with direction handling)
            try:
                player_image = self.player.get_animation_frames()[self.player.animation_frame]
                # Flip the sprite if facing left
                if self.player.direction == -1:
                    screen.blit(player_image, (self.player.x, self.player.y), flipx=True)
                else:
                    screen.blit(player_image, (self.player.x, self.player.y))
            except:
                screen.draw.filled_rect(Rect(self.player.x, self.player.y, 32, 32), (0, 255, 0))
            
            # Draw enemies (with direction handling)
            for enemy in self.enemies:
                try:
                    enemy_image = enemy.get_animation_frames()[enemy.animation_frame]
                    # Flip the sprite if facing left
                    if enemy.direction == -1:
                        screen.blit(enemy_image, (enemy.x, enemy.y), flipx=True)
                    else:
                        screen.blit(enemy_image, (enemy.x, enemy.y))
                except:
                    screen.draw.filled_rect(Rect(enemy.x, enemy.y, 32, 32), (255, 0, 0))
                
            # Draw health bar
            health_rect = Rect(10, 10, self.player.health * 2, 20)
            screen.draw.filled_rect(health_rect, (200, 0, 0))
            
        elif self.state == GAME_OVER:
            screen.draw.text("GAME OVER", center=(WIDTH//2, HEIGHT//2), color="white")
            screen.draw.text("Click to return to menu", center=(WIDTH//2, HEIGHT//2 + 40), color="white")
            
game = Game()

def update(dt):
    game.update(dt)

def draw():
    game.draw()

def on_mouse_down(pos):
    if game.state == MENU:
        if game.buttons['start'].collidepoint(pos):
            game.state = PLAYING
            try:
                if game.sound_enabled:
                    music.play('background_music')
            except:
                pass
        elif game.buttons['sound'].collidepoint(pos):
            game.sound_enabled = not game.sound_enabled
            try:
                if game.sound_enabled:
                    music.play('background_music')
                else:
                    music.stop()
            except:
                pass
        elif game.buttons['exit'].collidepoint(pos):
            quit()
    elif game.state == GAME_OVER:
        game.state = MENU
        game.player.health = 100

pgzrun.go()