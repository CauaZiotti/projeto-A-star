import pygame

pygame.init()

# Cores
COR_FUNDO_CELULA = (18, 18, 18)
COR_BORDA_CELULA = (27, 27, 27)
COR_MURO = (67, 67, 70)
COR_INICIO = (153, 254, 15)
COR_FINAL = (250, 50, 50)
COR_EXPANSAO_FECHADO = (19, 128, 252)
COR_EXPANSAO_ABERTO = (81, 163, 255)
COR_CAMINHO = (255, 255, 255)

# Cores para o ranking de finalização
CORES_RANKING = [
    (255, 215, 0),    # 1º Lugar: Dourado
    (192, 192, 192),  # 2º Lugar: Prata
    (205, 127, 50),   # 3º Lugar: Bronze
    (138, 138, 147)   # 4º Lugar: Cinza
]

# Configurações de Simulação
TAMANHO_NO = 12
STEPS_PER_FRAME = 3

# Fonte e Estilos
try:
    font_card_titulo = pygame.font.SysFont("Segoe UI", 20, bold=True)
    font_formula = pygame.font.SysFont("Consolas", 13, bold=True)
    font_titulo = pygame.font.SysFont("Segoe UI", 16, bold=True)
    font_sub = pygame.font.SysFont("Segoe UI", 12)
    font_header = pygame.font.SysFont("Segoe UI", 24, bold=True)
    font_instrucoes = pygame.font.SysFont("Segoe UI", 12)
except Exception:
    font_card_titulo = pygame.font.Font(None, 24)
    font_formula = pygame.font.Font(None, 16)
    font_titulo = pygame.font.Font(None, 20)
    font_sub = pygame.font.Font(None, 14)
    font_header = pygame.font.Font(None, 30)
    font_instrucoes = pygame.font.Font(None, 14)
