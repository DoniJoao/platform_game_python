import pgzrun
from pygame import Rect
import random

WIDTH = 800
HEIGHT = 600

# Variáveis globais
is_game_running = False
game_scene = None

class Player:
    def __init__(self, pos):
        self.pos = list(pos)  # Convertemos para lista para poder modificar
        self.velocity = [0, 0]
        self.rect = Rect(pos[0], pos[1], 40, 60)
        self.is_jumping = False
        self.facing_right = True
        self.health = 100
        self.is_attacking = False
        self.on_ground = True

    def update(self, dt):
        # Aplicar gravidade
        if not self.on_ground:
            self.velocity[1] += 800 * dt  # Gravidade mais forte

        # Atualizar posição
        self.pos[0] += self.velocity[0] * dt
        self.pos[1] += self.velocity[1] * dt

        # Manter dentro da tela
        self.pos[0] = max(0, min(self.pos[0], WIDTH - self.rect.width))
        
        # Verificar colisão com o chão
        if self.pos[1] > HEIGHT - self.rect.height:
            self.pos[1] = HEIGHT - self.rect.height
            self.velocity[1] = 0
            self.on_ground = True
            self.is_jumping = False
        else:
            self.on_ground = False

        # Atualizar retângulo de colisão
        self.rect.x = self.pos[0]
        self.rect.y = self.pos[1]

    def jump(self):
        if self.on_ground:
            self.velocity[1] = -500  # Força do pulo
            self.is_jumping = True
            self.on_ground = False

    def draw(self):
        screen.draw.filled_rect(self.rect, (255, 0, 0))

class Enemy:
    def __init__(self, pos):
        self.pos = list(pos)
        self.velocity = [100, 0]  # Movimento horizontal constante
        self.rect = Rect(pos[0], pos[1], 40, 40)
        self.direction = 1  # 1 para direita, -1 para esquerda

    def update(self, dt):
        # Movimento de patrulha simples
        self.pos[0] += self.velocity[0] * dt * self.direction
        
        # Mudar direção nas bordas da tela
        if self.pos[0] <= 0:
            self.direction = 1
        elif self.pos[0] >= WIDTH - self.rect.width:
            self.direction = -1

        # Atualizar retângulo de colisão
        self.rect.x = self.pos[0]
        self.rect.y = self.pos[1]

    def draw(self):
        screen.draw.filled_rect(self.rect, (0, 0, 255))

class GameScene:
    def __init__(self):
        self.reset_game()

    def reset_game(self):
        self.player = Player([WIDTH // 2, HEIGHT - 100])
        self.enemies = [
            Enemy([100, HEIGHT - 60]),
            Enemy([600, HEIGHT - 60])
        ]
        self.score = 0
        self.platforms = [
            Rect(300, HEIGHT - 150, 200, 20),
            Rect(100, HEIGHT - 250, 200, 20),
            Rect(500, HEIGHT - 350, 200, 20)
        ]

    def update(self, dt):
        self.player.update(dt)
        
        # Atualizar inimigos
        for enemy in self.enemies[:]:
            enemy.update(dt)
            
            # Verificar colisão com jogador
            if self.player.rect.colliderect(enemy.rect):
                if self.player.is_attacking:
                    self.enemies.remove(enemy)
                    self.score += 10
                else:
                    self.player.health -= 10
                    if self.player.health <= 0:
                        self.reset_game()

        # Verificar colisão com plataformas
        for platform in self.platforms:
            if self.player.rect.colliderect(platform):
                # Colisão por cima da plataforma
                if self.player.velocity[1] > 0:  # Caindo
                    self.player.pos[1] = platform.top - self.player.rect.height
                    self.player.velocity[1] = 0
                    self.player.on_ground = True
                    self.player.is_jumping = False

    def draw(self):
        screen.fill((135, 206, 235))  # Céu azul
        
        # Desenhar plataformas
        for platform in self.platforms:
            screen.draw.filled_rect(platform, (0, 255, 0))
        
        # Desenhar jogador e inimigos
        self.player.draw()
        for enemy in self.enemies:
            enemy.draw()
            
        # Interface
        screen.draw.text(f"Score: {self.score}", topleft=(10, 10), color="white")
        screen.draw.text(f"Health: {self.player.health}", topleft=(10, 40), color="white")

def draw_menu():
    screen.fill((0, 0, 0))
    screen.draw.text("Platform Game", center=(WIDTH // 2, HEIGHT // 4), fontsize=60, color="white")
    screen.draw.text("Press ENTER to Start", center=(WIDTH // 2, HEIGHT // 2), fontsize=40, color="white")
    screen.draw.text("Controls:", center=(WIDTH // 2, HEIGHT * 3 // 4 - 40), fontsize=30, color="white")
    screen.draw.text("Arrow Keys - Move", center=(WIDTH // 2, HEIGHT * 3 // 4), fontsize=30, color="white")
    screen.draw.text("Z - Attack", center=(WIDTH // 2, HEIGHT * 3 // 4 + 30), fontsize=30, color="white")
    screen.draw.text("Space - Jump", center=(WIDTH // 2, HEIGHT * 3 // 4 + 60), fontsize=30, color="white")

def on_key_down(key):
    global is_game_running
    if key == keys.SPACE and is_game_running:
        game_scene.player.jump()
    elif key == keys.RETURN and not is_game_running:
        is_game_running = True

def update(dt):
    if is_game_running:
        if keyboard.left:
            game_scene.player.velocity[0] = -300
            game_scene.player.facing_right = False
        elif keyboard.right:
            game_scene.player.velocity[0] = 300
            game_scene.player.facing_right = True
        else:
            game_scene.player.velocity[0] = 0
        
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