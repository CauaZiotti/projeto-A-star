import pygame
import math
from queue import PriorityQueue

# Configurações da Janela
LARGURA = 800
ALTURA = 600
TELA = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Visualizador do Algoritmo A*")

# Cores
VERMELHO = (255, 0, 0)      # Lista Fechada (Já visitado)
VERDE = (0, 255, 0)         # Lista Aberta (Na fila para visitar)
AZUL = (0, 0, 255)          # Ponto Alvo (Final)
AMARELO = (255, 255, 0)     # Caminho Encontrado
BRANCO = (255, 255, 255)    # Caminho Livre
PRETO = (0, 0, 0)           # Obstáculo / Parede
ROXO = (128, 0, 128)        # Caminho sendo construído (Visual)
LARANJA = (255, 165 ,0)     # Ponto de Início
CINZA = (128, 128, 128)     # Linhas do Grid

class No:
    def __init__(self, linha, col, largura, total_linhas):
        self.linha = linha
        self.col = col
        self.x = linha * largura
        self.y = col * largura
        self.cor = BRANCO
        self.largura = largura
        self.total_linhas = total_linhas
        self.vizinhos = []

    def get_pos(self): return self.linha, self.col
    
    # Checagens de estado
    def is_fechado(self): return self.cor == VERMELHO
    def is_aberto(self): return self.cor == VERDE
    def is_parede(self): return self.cor == PRETO
    def is_inicio(self): return self.cor == LARANJA
    def is_alvo(self): return self.cor == AZUL

    # Mudanças de estado
    def resetar(self): self.cor = BRANCO
    def tornar_inicio(self): self.cor = LARANJA
    def tornar_fechado(self): self.cor = VERMELHO
    def tornar_aberto(self): self.cor = VERDE
    def tornar_parede(self): self.cor = PRETO
    def tornar_alvo(self): self.cor = AZUL
    def tornar_caminho(self): self.cor = AMARELO

    def desenhar(self, tela):
        pygame.draw.rect(tela, self.cor, (self.x, self.y, self.largura, self.largura))

    def atualizar_vizinhos(self, grid):
        self.vizinhos = []
        # Baixo
        if self.linha < self.total_linhas - 1 and not grid[self.linha + 1][self.col].is_parede():
            self.vizinhos.append(grid[self.linha + 1][self.col])
        # Cima
        if self.linha > 0 and not grid[self.linha - 1][self.col].is_parede():
            self.vizinhos.append(grid[self.linha - 1][self.col])
        # Direita
        if self.col < self.total_linhas - 1 and not grid[self.linha][self.col + 1].is_parede():
            self.vizinhos.append(grid[self.linha][self.col + 1])
        # Esquerda
        if self.col > 0 and not grid[self.linha][self.col - 1].is_parede():
            self.vizinhos.append(grid[self.linha][self.col - 1])

# Função Heurística (Distância de Manhattan)
def heuristica(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    return abs(x1 - x2) + abs(y1 - y2)

# Função para reconstruir e pintar o caminho final
def reconstruir_caminho(veio_de, atual, desenhar):
    while atual in veio_de:
        atual = veio_de[atual]
        atual.tornar_caminho()
        desenhar()

# ALGORITMO A* PRINCIPAL
def algoritmo_a_estrela(desenhar, grid, inicio, alvo):
    count = 0
    lista_aberta = PriorityQueue()
    # Coloca o nó inicial na fila de prioridade com f(n) = 0
    lista_aberta.put((0, count, inicio))
    
    veio_de = {} # Guarda o "Nó Pai" para traçar o caminho de volta
    
    # g(n): Custo real do caminho do início até o nó atual
    g_score = {no: float("inf") for linha in grid for no in linha}
    g_score[inicio] = 0
    
    # f(n) = g(n) + h(n)
    f_score = {no: float("inf") for linha in grid for no in linha}
    f_score[inicio] = heuristica(inicio.get_pos(), alvo.get_pos())

    # Estrutura auxiliar para saber facilmente o que está na Lista Aberta
    lista_aberta_hash = {inicio}

    while not lista_aberta.empty():
        # Permite fechar a janela enquanto o algoritmo roda
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        # Pega o nó com o menor f(n)
        atual = lista_aberta.get()[2]
        lista_aberta_hash.remove(atual)

        # Se chegamos no alvo, termina e desenha o caminho
        if atual == alvo:
            reconstruir_caminho(veio_de, alvo, desenhar)
            alvo.tornar_alvo()
            inicio.tornar_inicio()
            return True

        # Analisa os vizinhos do nó atual
        for vizinho in atual.vizinhos:
            custo_temp_g = g_score[atual] + 1

            # Se achamos um caminho mais rápido para este vizinho
            if custo_temp_g < g_score[vizinho]:
                veio_de[vizinho] = atual
                g_score[vizinho] = custo_temp_g
                f_score[vizinho] = custo_temp_g + heuristica(vizinho.get_pos(), alvo.get_pos())
                
                # Adiciona na Lista Aberta se já não estiver lá
                if vizinho not in lista_aberta_hash:
                    count += 1
                    lista_aberta.put((f_score[vizinho], count, vizinho))
                    lista_aberta_hash.add(vizinho)
                    vizinho.tornar_aberto() # Fica VERDE

        desenhar()

        if atual != inicio:
            atual.tornar_fechado() # Passa para a Lista Fechada (Fica VERMELHO)

    return False # Retorna Falso se não achar caminho nenhum

# Funções de Construção Visual (Grid e Tela)
def criar_grid(linhas, largura):
    grid = []
    tamanho_no = largura // linhas
    for i in range(linhas):
        grid.append([])
        for j in range(linhas):
            no = No(i, j, tamanho_no, linhas)
            grid[i].append(no)
    return grid

def desenhar_linhas_grid(tela, linhas, largura):
    tamanho_no = largura // linhas
    for i in range(linhas):
        pygame.draw.line(tela, CINZA, (0, i * tamanho_no), (largura, i * tamanho_no))
        for j in range(linhas):
            pygame.draw.line(tela, CINZA, (j * tamanho_no, 0), (j * tamanho_no, largura))

def desenhar_tudo(tela, grid, linhas, largura):
    tela.fill(BRANCO)
    for linha in grid:
        for no in linha:
            no.desenhar(tela)
    desenhar_linhas_grid(tela, linhas, largura)
    pygame.display.update()

def pegar_pos_mouse(pos, linhas, largura):
    tamanho_no = largura // linhas
    y, x = pos
    linha = y // tamanho_no
    col = x // tamanho_no
    return linha, col

# LOOP PRINCIPAL DA APLICAÇÃO
def main(tela, largura):
    LINHAS = 50 # Quantidade de quadrados no grid
    grid = criar_grid(LINHAS, largura)

    inicio = None
    alvo = None
    rodando = True

    while rodando:
        desenhar_tudo(tela, grid, LINHAS, largura)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                rodando = False

            # Controles do Mouse
            if pygame.mouse.get_pressed()[0]: # Botão Esquerdo (Desenhar)
                pos = pygame.mouse.get_pos()
                linha, col = pegar_pos_mouse(pos, LINHAS, largura)
                no = grid[linha][col]
                if not inicio and no != alvo:
                    inicio = no
                    inicio.tornar_inicio()
                elif not alvo and no != inicio:
                    alvo = no
                    alvo.tornar_alvo()
                elif no != inicio and no != alvo:
                    no.tornar_parede()

            elif pygame.mouse.get_pressed()[2]: # Botão Direito (Apagar)
                pos = pygame.mouse.get_pos()
                linha, col = pegar_pos_mouse(pos, LINHAS, largura)
                no = grid[linha][col]
                no.resetar()
                if no == inicio:
                    inicio = None
                elif no == alvo:
                    alvo = None

            # Controles do Teclado
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and inicio and alvo:
                    for linha in grid:
                        for no in linha:
                            no.atualizar_vizinhos(grid)
                    # Passa uma função lambda para o algoritmo conseguir atualizar a tela passo a passo
                    algoritmo_a_estrela(lambda: desenhar_tudo(tela, grid, LINHAS, largura), grid, inicio, alvo)

                if event.key == pygame.K_c: # Limpar a tela
                    inicio = None
                    alvo = None
                    grid = criar_grid(LINHAS, largura)

    pygame.quit()

if __name__ == "__main__":
    main(TELA, LARGURA)

"""
Clique Esquerdo: Pinta o Ponto de Início (Laranja), depois o Alvo (Azul) e, em seguida, desenha as Paredes (Preto).

Clique Direito: Apaga o que você clicou.

Barra de Espaço: Inicia o algoritmo A*.

Tecla 'C': Limpa todo o mapa.
"""