import random
import pgzrun
from pygame import Rect
import math

try:
    import noise
except ImportError:
    print("O módulo 'noise' não está instalado. O terreno será gerado de forma mais simples.")
    USE_NOISE = False
else:
    USE_NOISE = True

# Dimensões da tela
WIDTH = 800
HEIGHT = 600
TILE_SIZE = 32

# Variáveis globais
game_time = 0
is_game_running = False
is_music_on = True
game_scene = None

# Configurações de geração procedural
OCTAVES = 6
PERSISTENCE = 0.5
LACUNARITY = 2.0

# Primeiro definimos a classe base de animação
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
        # Criar um Actor para cada frame de animação
        self.actors = {}
        for anim_name, frames in self.animations.items():
            self.actors[anim_name] = [Actor(frame_name) for frame_name in frames]

    def update(self, dt):
        self.animation_time += dt
        if self.animation_time >= self.animation_speed:
            self.animation_time = 0
            self.frame = (self.frame + 1) % len(self.animations[self.current_animation])

    def get_current_actor(self):
        return self.actors[self.current_animation][self.frame]

class Enemy:
    def __init__(self, pos, enemy_type='normal'):
        self.pos = pos
        self.velocity = [0, 0]
        self.rect = Rect(pos[0], pos[1], 40, 60)
        self.sprite = AnimatedSprite('enemy')
        self.health = 50
        self.behavior_timer = 0
        self.behavior_duration = random.uniform(1, 3)
        self.movement_speed = random.uniform(50, 150)
        self.enemy_type = enemy_type
        self.facing_right = True
        self.is_jumping = False

    def update(self, dt, player_pos):  # Este método precisa estar presente
        self.behavior_timer += dt
        if self.behavior_timer >= self.behavior_duration:
            self.behavior_timer = 0
            self.behavior_duration = random.uniform(1, 3)
            self.choose_behavior(player_pos)

        if self.enemy_type == 'normal':
            self.normal_movement(dt)
        elif self.enemy_type == 'chaser':
            self.chase_movement(dt, player_pos)
        elif self.enemy_type == 'flying':
            self.flying_movement(dt)

        if self.is_jumping:
            self.sprite.current_animation = 'jump'
        elif abs(self.velocity[0]) > 0:
            self.sprite.current_animation = 'walk'
        else:
            self.sprite.current_animation = 'idle'

        self.rect.x = self.pos[0]
        self.rect.y = self.pos[1]
        self.sprite.update(dt)

        if self.pos[1] >= HEIGHT - self.rect.height:
            self.is_jumping = False

    def choose_behavior(self, player_pos):
        if self.enemy_type == 'normal':
            self.velocity[0] = random.choice([-1, 1]) * self.movement_speed
            if random.random() < 0.2:
                self.jump()
        elif self.enemy_type == 'chaser':
            self.velocity[0] = self.movement_speed if player_pos[0] > self.pos[0] else -self.movement_speed
            if random.random() < 0.3:
                self.jump()
        elif self.enemy_type == 'flying':
            self.velocity = [
                random.uniform(-100, 100),
                random.uniform(-100, 100)
            ]

    def jump(self):
        if not self.is_jumping and self.pos[1] >= HEIGHT - self.rect.height:
            self.velocity[1] = -300
            self.is_jumping = True

    def normal_movement(self, dt):
        self.velocity[1] += 500 * dt
        if self.pos[1] >= HEIGHT - self.rect.height:
            self.pos[1] = HEIGHT - self.rect.height
            self.velocity[1] = 0
        
        # Atualiza a posição com base na velocidade
        self.pos[0] += self.velocity[0] * dt
        self.pos[1] += self.velocity[1] * dt

    def chase_movement(self, dt, player_pos):
        self.normal_movement(dt)
        self.facing_right = player_pos[0] > self.pos[0]

    def flying_movement(self, dt):
        self.pos[0] += math.sin(game_time) * 2
        self.pos[1] += math.cos(game_time) * 2

    def draw(self):
        current_actor = self.sprite.get_current_actor()
        current_actor.pos = (self.pos[0], self.pos[1])
        
        if not self.facing_right:
            current_actor.angle = 180
            current_actor.flip_x = True
        else:
            current_actor.angle = 0
            current_actor.flip_x = False
            
        current_actor.draw()

# Depois definimos a classe Player que usa AnimatedSprite
class Player:
    def __init__(self, pos):
        self.pos = pos
        self.velocity = [0, 0]
        self.rect = Rect(pos[0], pos[1], 40, 60)
        self.sprite = AnimatedSprite('player')
        self.is_attacking = False
        self.is_jumping = False
        self.facing_right = True
        self.health = 100
        self.attack_cooldown = 0
        self.jump_power = -300
        self.can_jump = True

    def update(self, dt):
        if self.attack_cooldown > 0:
            self.attack_cooldown -= dt

        if self.is_attacking and self.attack_cooldown <= 0:
            self.sprite.current_animation = 'attack'
            try:
                sounds.attack.play()
            except:
                pass
            self.attack_cooldown = 0.5
        elif self.is_jumping:
            self.sprite.current_animation = 'jump'
        elif abs(self.velocity[0]) > 0:
            self.sprite.current_animation = 'walk'
        else:
            self.sprite.current_animation = 'idle'

        self.velocity[1] += 500 * dt  # Gravidade
        self.pos[0] += self.velocity[0] * dt
        self.pos[1] += self.velocity[1] * dt

        self.pos[0] = max(0, min(self.pos[0], WIDTH - self.rect.width))
        if self.pos[1] > HEIGHT - self.rect.height:
            self.pos[1] = HEIGHT - self.rect.height
            self.velocity[1] = 0
            self.can_jump = True
            self.is_jumping = False

        self.rect.x = self.pos[0]
        self.rect.y = self.pos[1]
        self.sprite.update(dt)

    def jump(self):
        if self.can_jump:
            self.velocity[1] = self.jump_power
            self.can_jump = False
            self.is_jumping = True

    def draw(self):
        current_actor = self.sprite.get_current_actor()
        current_actor.pos = (self.pos[0], self.pos[1])
        
        if not self.facing_right:
            current_actor.angle = 180
            current_actor.flip_x = True
        else:
            current_actor.angle = 0
            current_actor.flip_x = False
            
        current_actor.draw()


class GameScene:
    def __init__(self):
        self.reset_game()

    def reset_game(self):
        self.player = Player([WIDTH // 2, HEIGHT - 100])
        self.enemies = []
        self.score = 0
        self.spawn_timer = 0
        self.generate_enemies()

    def generate_enemies(self):
        num_enemies = random.randint(3, 7)
        enemy_types = ['normal', 'chaser', 'flying']
        for _ in range(num_enemies):
            enemy_type = random.choice(enemy_types)
            x = random.randint(0, WIDTH - 40)
            y = random.randint(HEIGHT // 2, HEIGHT - 100)
            self.enemies.append(Enemy([x, y], enemy_type))

    def update(self, dt):
        global game_time
        game_time += dt

        self.player.update(dt)
        self.spawn_timer += dt

        if self.spawn_timer >= 5:
            self.spawn_timer = 0
            if len(self.enemies) < 10:
                enemy_type = random.choice(['normal', 'chaser', 'flying'])
                x = random.randint(0, WIDTH - 40)
                self.enemies.append(Enemy([x, 0], enemy_type))

        for enemy in self.enemies[:]:
            enemy.update(dt, self.player.pos)

            if self.player.rect.colliderect(enemy.rect):
                if self.player.is_attacking:
                    self.enemies.remove(enemy)
                    self.score += 10
                else:
                    self.player.health -= 10
                    if self.player.health <= 0:
                        self.reset_game()

    def draw(self):
        # Desenha o céu
        screen.blit('sky', (0, 0))
        
        # Desenha o chão (uma linha simples)
        screen.draw.filled_rect(Rect(0, HEIGHT - 20, WIDTH, 20), (100, 100, 100))

        self.player.draw()
        for enemy in self.enemies:
            enemy.draw()

        screen.draw.text(f"Score: {self.score}", topleft=(10, 10), color="white")
        screen.draw.text(f"Health: {self.player.health}", topleft=(10, 40), color="white")

# Funções de controle
def draw_menu():
    screen.fill((0, 0, 0))
    screen.draw.text("Platformer Game", center=(WIDTH // 2, HEIGHT // 4), fontsize=60, color="white")
    screen.draw.text("Press ENTER to Start", center=(WIDTH // 2, HEIGHT // 2), fontsize=40, color="white")
    screen.draw.text("Controls:", center=(WIDTH // 2, HEIGHT * 3 // 4 - 40), fontsize=30, color="white")
    screen.draw.text("Arrow Keys - Move", center=(WIDTH // 2, HEIGHT * 3 // 4), fontsize=30, color="white")
    screen.draw.text("Z - Attack", center=(WIDTH // 2, HEIGHT * 3 // 4 + 30), fontsize=30, color="white")
    screen.draw.text("Space - Jump", center=(WIDTH // 2, HEIGHT * 3 // 4 + 60), fontsize=30, color="white")

def on_key_down(key):
    global is_game_running
    if key == keys.SPACE and is_game_running and game_scene.player.can_jump:
        game_scene.player.jump()
    elif key == keys.RETURN and not is_game_running:
        is_game_running = True
        try:
            music.play("background")
        except:
            pass

def on_key_up(key):
    if key == keys.LEFT or key == keys.RIGHT and game_scene:
        game_scene.player.velocity[0] = 0

def update(dt):
    if is_game_running:
        if keyboard.left:
            game_scene.player.velocity[0] = -200
            game_scene.player.facing_right = False
        elif keyboard.right:
            game_scene.player.velocity[0] = 200
            game_scene.player.facing_right = True
        
        if keyboard.z:
            game_scene.player.is_attacking = True
        else:
            game_scene.player.is_attacking = False

        game_scene.update(dt)

def draw():
    if is_game_running:
        game_scene.draw()
    else:
        draw_menu()

# Inicialização
game_scene = GameScene()
pgzrun.go()