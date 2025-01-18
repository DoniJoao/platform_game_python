import pgzrun

TITLE = "Test Game"
WIDTH = 800
HEIGHT = 600

def draw():
    screen.fill((100, 100, 200))  # Preenche a tela com uma cor azulada
    screen.draw.text("Menu de Teste", center=(WIDTH//2, HEIGHT//2), color="white", fontsize=60)

def update():
    pass

pgzrun.go()