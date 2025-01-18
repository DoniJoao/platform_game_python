import random
import pgzrun
from pygame import Rect
import math

# Dimensões da tela
WIDTH = 800
HEIGHT = 600
TILE_SIZE = 32

# Variáveis globais
game_time = 0
is_game_running = False
is_music_on = True
game_scene = None

class Platform:
    def __init__(self, x, y, width, height, platform_type='grass'):
        self.rect = Rect(x, y, width, height)
        self.type = platform_type

class AnimatedSprite:
    def __init__(self, base_name, idle_frames=2, walk_frames=3, attack_frames=3, jump_frames=2):
        self.animations = {
            'idle': [f"{base_name}_idle_{i}" for i in range(idle_frames)],
            'walk': [f"{base_name}_walk_{i}" for i in range(walk_frames)],
            'attack': [f"{base_name}_attack_{i}" for i in range(attack_frames)],
            'jump': [f"{base_name}_jump_{i}" for i in range(jump_frames)]
        }
        self.current_animation = 'idle'
        self.frame = 0
        self.animation_time = 0
        self.animation_speed = 0.1

    def update(self, dt):
        self.animation_time += dt
        if self.animation_time >= self.animation_speed:
            self.animation_time = 0
            self.frame = (self.frame + 1) % len(self.animations[self.current_animation])

    def get_current_sprite(self):
        return self.animations[self.current_animation][self.frame]

class Player:
    def __init__(self, pos):
        self.pos = list(pos)
        self.velocity = [0, 0]
        self.rect = Rect(pos[0], pos[1], 32, 48)
        self.sprite = AnimatedSprite('player')
        self.is_attacking = False
        self.is_jumping = False
        self.facing_right = True
        self.health = 100
        self.attack_cooldown = 0
        self.attack_duration = 0.3
        self.attack_timer = 0
        self.jump_power = -400
        self.can_jump = False

    def update(self, dt, platforms):
        if self.attack_cooldown > 0:
            self.attack_cooldown -= dt

        if self.is_attacking:
            self.attack_timer += dt
            if self.attack_timer >= self.attack_duration:
                self.is_attacking = False
                self.attack_timer = 0

        # Atualiza animação
        if self.is_attacking:
            self.sprite.current_animation = 'attack'
        elif self.is_jumping:
            self.sprite.current_animation = 'jump'
        elif abs(self.velocity[0]) > 0:
            self.sprite.current_animation = 'walk'
        else:
            self.sprite.current_animation = 'idle'

        # Aplica gravidade
        self.velocity[1] += 800 * dt
        
        # Atualiza posição
        new_pos = [
            self.pos[0] + self.velocity[0] * dt,
            self.pos[1] + self.velocity[1] * dt
        ]

        # Verifica colisões horizontais
        self.rect.x = new_pos[0]
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.velocity[0] > 0:
                    self.rect.right = platform.rect.left
                    new_pos[0] = self.rect.x
                elif self.velocity[0] < 0:
                    self.rect.left = platform.rect.right
                    new_pos[0] = self.rect.x

        # Verifica colisões verticais
        self.rect.y = new_pos[1]
        self.can_jump = False
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.velocity[1] > 0:  # Caindo
                    self.rect.bottom = platform.rect.top
                    new_pos[1] = self.rect.y
                    self.velocity[1] = 0
                    self.can_jump = True
                    self.is_jumping = False
                elif self.velocity[1] < 0:  # Subindo
                    self.rect.top = platform.rect.bottom
                    new_pos[1] = self.rect.y
                    self.velocity[1] = 0

        self.pos = new_pos
        self.sprite.update(dt)

    def attack(self):
        if self.attack_cooldown <= 0:
            self.is_attacking = True
            self.attack_timer = 0
            self.attack_cooldown = 0.5
            try:
                sounds.attack.play()
            except:
                pass

    def jump(self):
        if self.can_jump:
            self.velocity[1] = self.jump_power
            self.is_jumping = True
            self.can_jump = False

    def draw(self):
        try:
            sprite = self.sprite.get_current_sprite()
            if not self.facing_right:
                screen.blit(sprite, (self.pos[0], self.pos[1]), flip_x=True)
            else:
                screen.blit(sprite, (self.pos[0], self.pos[1]))
        except:
            screen.draw.filled_rect(self.rect, (255, 0, 0))

class Enemy:
    def __init__(self, pos, enemy_type='normal'):
        self.pos = list(pos)
        self.velocity = [0, 0]
        self.rect = Rect(pos[0], pos[1], 32, 48)
        self.sprite = AnimatedSprite('enemy')
        self.health = 50
        self.enemy_type = enemy_type
        self.facing_right = True
        self.is_jumping = False
        self.can_jump = False
        self.is_attacking = False
        self.attack_cooldown = 0
        self.attack_duration = 0.3
        self.attack_timer = 0
        self.jump_power = -400
        self.movement_speed = 100

    def update(self, dt, platforms, player_pos):
        if self.attack_cooldown > 0:
            self.attack_cooldown -= dt

        if self.is_attacking:
            self.attack_timer += dt
            if self.attack_timer >= self.attack_duration:
                self.is_attacking = False
                self.attack_timer = 0

        # IA básica
        distance_to_player = abs(player_pos[0] - self.pos[0])
        if distance_to_player < 50 and self.attack_cooldown <= 0:  # Ataca se perto
            self.attack()
        elif distance_to_player < 200:  # Persegue se médio
            self.velocity[0] = self.movement_speed if player_pos[0] > self.pos[0] else -self.movement_speed
            self.facing_right = player_pos[0] > self.pos[0]
        
        # Pula se encontrar plataforma
        if self.can_jump and random.random() < 0.02:
            self.jump()

        # Atualiza animação
        if self.is_attacking:
            self.sprite.current_animation = 'attack'
        elif self.is_jumping:
            self.sprite.current_animation = 'jump'
        elif abs(self.velocity[0]) > 0:
            self.sprite.current_animation = 'walk'
        else:
            self.sprite.current_animation = 'idle'

        # Aplica gravidade
        self.velocity[1] += 800 * dt
        
        # Atualiza posição com colisões
        new_pos = [
            self.pos[0] + self.velocity[0] * dt,
            self.pos[1] + self.velocity[1] * dt
        ]

        # Colisões com plataformas
        self.rect.x = new_pos[0]
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.velocity[0] > 0:
                    self.rect.right = platform.rect.left
                    new_pos[0] = self.rect.x
                    self.velocity[0] *= -1
                elif self.velocity[0] < 0:
                    self.rect.left = platform.rect.right
                    new_pos[0] = self.rect.x
                    self.velocity[0] *= -1

        self.rect.y = new_pos[1]
        self.can_jump = False
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.velocity[1] > 0:
                    self.rect.bottom = platform.rect.top
                    new_pos[1] = self.rect.y
                    self.velocity[1] = 0
                    self.can_jump = True
                    self.is_jumping = False
                elif self.velocity[1] < 0:
                    self.rect.top = platform.rect.bottom
                    new_pos[1] = self.rect.y
                    self.velocity[1] = 0

        self.pos = new_pos
        self.sprite.update(dt)

    def attack(self):
        if self.attack_cooldown <= 0:
            self.is_attacking = True
            self.attack_timer = 0
            self.attack_cooldown = 1.0
            try:
                sounds.attack.play()
            except:
                pass

    def jump(self):
        if self.can_jump:
            self.velocity[1] = self.jump_power
            self.is_jumping = True
            self.can_jump = False

    def draw(self):
        try:
            sprite = self.sprite.get_current_sprite()
            if not self.facing_right:
                screen.blit(sprite, (self.pos[0], self.pos[1]), flip_x=True)
            else:
                screen.blit(sprite, (self.pos[0], self.pos[1]))
        except:
            screen.draw.filled_rect(self.rect, (0, 0, 255))

class GameScene:
    def __init__(self):
        self.reset_game()

    def reset_game(self):
        self.player = Player([WIDTH // 2, HEIGHT - 100])
        self.enemies = []
        self.score = 0
        self.platforms = []
        self.generate_level()
        
        try:
            music.play('background')
        except:
            pass

    def generate_level(self):
        # Cria o chão base
        ground_height = HEIGHT - TILE_SIZE
        for x in range(0, WIDTH, TILE_SIZE):
            self.platforms.append(Platform(x, ground_height, TILE_SIZE, TILE_SIZE, 'grass'))

        # Cria plataformas flutuantes
        for _ in range(10):
            plat_width = random.randint(2, 6) * TILE_SIZE
            plat_x = random.randint(0, WIDTH - plat_width)
            plat_y = random.randint(HEIGHT // 2, HEIGHT - 100)
            
            # Cria plataforma principal
            self.platforms.append(Platform(plat_x, plat_y, plat_width, TILE_SIZE, 'grass'))
            
            # Adiciona algumas rochas como obstáculos
            if random.random() < 0.3:
                rock_x = plat_x + random.randint(0, plat_width - TILE_SIZE)
                self.platforms.append(Platform(rock_x, plat_y - TILE_SIZE, TILE_SIZE, TILE_SIZE, 'rock'))

        # Adiciona inimigos
        for _ in range(5):
            enemy_x = random.randint(0, WIDTH - 32)
            enemy_y = random.randint(0, HEIGHT - 100)
            enemy_type = random.choice(['normal', 'chaser'])
            self.enemies.append(Enemy([enemy_x, enemy_y], enemy_type))

    def check_combat(self):
        # Verifica ataques do jogador
        if self.player.is_attacking:
            attack_rect = self.player.rect.copy()
            if self.player.facing_right:
                attack_rect.x += self.player.rect.width
            else:
                attack_rect.x -= self.player.rect.width

            for enemy in self.enemies[:]:
                if attack_rect.colliderect(enemy.rect):
                    enemy.health -= 25
                    if enemy.health <= 0:
                        self.enemies.remove(enemy)
                        self.score += 10

        # Verifica ataques dos inimigos
        for enemy in self.enemies:
            if enemy.is_attacking:
                attack_rect = enemy.rect.copy()
                if enemy.facing_right:
                    attack_rect.x += enemy.rect.width
                else:
                    attack_rect.x -= enemy.rect.width

                if attack_rect.colliderect(self.player.rect):
                    self.player.health -= 10
                    if self.player.health <= 0:
                        try:
                            sounds.game_over.play()
                        except:
                            pass
                        self.reset_game()

    def update(self, dt):
        self.player.update(dt, self.platforms)
        for enemy in self.enemies:
            enemy.update(dt, self.platforms, self.player.pos)
        self.check_combat()

    def draw(self):
        # Desenha o fundo
        screen.blit('sky', (0, 0))

        # Desenha as plataformas
        for platform in self.platforms:
            if platform.type == 'grass':
                screen.blit('grass', (platform.rect.x, platform.rect.y))
            elif platform.type == 'rock':
                screen.blit('rock', (platform.rect.x, platform.rect.y))

        # Desenha os inimigos
        for enemy in self.enemies:
            enemy.draw()

        # Desenha o jogador
        self.player.draw()

        # Desenha a UI
        screen.draw.text(f"Score: {self.score}", topleft=(10, 10), color="white")
        screen.draw.text(f"Health: {self.player.health}", topleft=(10, 40), color="white")

def draw_menu():
    screen.fill((0, 0, 0))
    screen.draw.text("Platform Game", center=(WIDTH // 2, HEIGHT // 4), fontsize=60, color="white")
    screen.draw.text("Press ENTER to Start", center=(WIDTH // 2, HEIGHT // 2), fontsize=40, color="white")
    screen.draw.text("Controls:", center=(WIDTH // 2, HEIGHT * 3 // 4 - 60), fontsize=30, color="white")
    screen.draw.text("Arrow Keys - Move", center=(WIDTH // 2, HEIGHT * 3 // 4 - 20), fontsize=30, color="white")
    screen.draw.text("Space - Jump", center=(WIDTH // 2, HEIGHT * 3 // 4 + 10), fontsize=30, color="white")
    screen.draw.text("Z - Attack", center=(WIDTH // 2, HEIGHT * 3 // 4 + 10), fontsize=30,  color="white")

def on_key_down(key):
    global is_game_running, game_scene  # Declaração global corrigida
    if key == keys.SPACE and is_game_running:
        game_scene.player.jump()
    elif key == keys.RETURN and not is_game_running:
        is_game_running = True
        game_scene = GameScene()

def update(dt):
    if is_game_running:
        if keyboard.left:
            game_scene.player.velocity[0] = -200
            game_scene.player.facing_right = False
        elif keyboard.right:
            game_scene.player.velocity[0] = 200
            game_scene.player.facing_right = True
        else:
            game_scene.player.velocity[0] = 0

        game_scene.update(dt)

def draw():
    if is_game_running:
        game_scene.draw()
    else:
        draw_menu()

pgzrun.go()