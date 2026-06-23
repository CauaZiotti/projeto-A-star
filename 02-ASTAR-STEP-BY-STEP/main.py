""" 
    ==========================================================
    Simulador de Algoritmo A* com Visualização Passo a Passo
    Gerado com IA para complementar a apresentação dos slides
    Para a explicação de como é feita a busca nesse algoritmo
    ==========================================================
"""

import pygame
import random
import sys
from queue import PriorityQueue
from config import *

# Inicialização do Pygame e Fontes
pygame.init()

# Paleta de Cores Premium (Alinhadas ao estilo dark/glassmorphism)
COR_CARD_BG = (22, 22, 26)
COR_CARD_BORDER = (37, 37, 42)
COR_TEXT_MUTED = (138, 138, 147)
COR_TEXT_BRIGHT = (255, 255, 255)
COR_ACCENT = (19, 128, 252)
COR_ACCENT_BG = (30, 60, 110)
COR_PANEL_BG = (16, 16, 20)
COR_PANEL_BORDER = (30, 30, 36)
COR_HIGHLIGHT = (29, 78, 137) # Destaque da linha de código ativa
COR_HIGHLIGHT_BORDER = (41, 121, 255)

# Configurações Adicionais de Fontes Locais
try:
    font_code = pygame.font.SysFont("Consolas", 14)
    font_code_bold = pygame.font.SysFont("Consolas", 14, bold=True)
    font_inspector = pygame.font.SysFont("Segoe UI", 13)
    font_inspector_bold = pygame.font.SysFont("Segoe UI", 13, bold=True)
    font_badge = pygame.font.SysFont("Segoe UI", 14, bold=True)
except Exception:
    font_code = pygame.font.Font(None, 18)
    font_code_bold = pygame.font.Font(None, 18)
    font_inspector = pygame.font.Font(None, 18)
    font_inspector_bold = pygame.font.Font(None, 18)
    font_badge = pygame.font.Font(None, 18)

# Linhas de Pseudo-código para exibição lateral
PSEUDO_CODIGO = [
    "01:  open_set = FilaDePrioridade()",
    "02:  open_set.inserir(inicio, f_score=h(inicio))",
    "03:  g_score[todos] = infinito; g_score[inicio] = 0",
    "04:  f_score[todos] = infinito; f_score[inicio] = h(inicio)",
    "05:  enquanto open_set não estiver vazio:",
    "06:      no_atual = open_set.remover_menor_f()",
    "07:      se no_atual == alvo:",
    "08:          reconstruir_caminho_final()",
    "09:          fim (sucesso)",
    "10:      para cada vizinho de no_atual:",
    "11:          temp_g = g_score[no_atual] + 1",
    "12:          se temp_g < g_score[vizinho]:",
    "13:              came_from[vizinho] = no_atual",
    "14:              g_score[vizinho] = temp_g",
    "15:              f_score[vizinho] = temp_g + h(vizinho)",
    "16:              se vizinho não em open_set:",
    "17:                  open_set.inserir(vizinho, f_score[vizinho])",
    "18:      no_atual.fechado = Verdadeiro"
]

class No:
    """Representa cada célula do grid."""
    def __init__(self, row, col, largura, total_linhas):
        self.row = row
        self.col = col
        self.largura = largura
        self.total_linhas = total_linhas
        self.cor = COR_FUNDO_CELULA
        self.vizinhos = []
        self.anim_scale = 1.0

    def get_pos(self): 
        return self.row, self.col
        
    def is_fechado(self): return self.cor == COR_EXPANSAO_FECHADO
    def is_aberto(self): return self.cor == COR_EXPANSAO_ABERTO
    def is_parede(self): return self.cor == COR_MURO
    def is_inicio(self): return self.cor == COR_INICIO
    def is_alvo(self): return self.cor == COR_FINAL

    def resetar(self):
        self.cor = COR_FUNDO_CELULA
        self.anim_scale = 1.0

    def tornar_inicio(self):
        self.cor = COR_INICIO
        self.anim_scale = 1.0

    def tornar_fechado(self):
        if self.cor not in (COR_EXPANSAO_FECHADO, COR_EXPANSAO_ABERTO):
            self.anim_scale = 0.0
        self.cor = COR_EXPANSAO_FECHADO

    def tornar_aberto(self):
        if self.cor not in (COR_EXPANSAO_FECHADO, COR_EXPANSAO_ABERTO):
            self.anim_scale = 0.0
        self.cor = COR_EXPANSAO_ABERTO

    def tornar_parede(self):
        self.cor = COR_MURO
        self.anim_scale = 1.0

    def tornar_alvo(self):
        self.cor = COR_FINAL
        self.anim_scale = 1.0

    def tornar_caminho(self):
        self.cor = COR_CAMINHO
        self.anim_scale = 1.0

    def desenhar(self, tela, ox, oy):
        x = ox + self.col * self.largura
        y = oy + self.row * self.largura
        
        # Fundo padrão da célula
        pygame.draw.rect(tela, COR_FUNDO_CELULA, (x, y, self.largura, self.largura))
        
        # Efeito de animação para abertura e fechamento
        if self.cor in (COR_EXPANSAO_FECHADO, COR_EXPANSAO_ABERTO):
            w = self.largura * self.anim_scale
            cx = x + self.largura / 2
            cy = y + self.largura / 2
            rx = cx - w / 2
            ry = cy - w / 2
            pygame.draw.rect(tela, self.cor, (rx, ry, w, w))
        else:
            pygame.draw.rect(tela, self.cor, (x, y, self.largura, self.largura))
            
        pygame.draw.rect(tela, COR_BORDA_CELULA, (x, y, self.largura, self.largura), 1)

    def atualizar_vizinhos(self, grid, total_linhas, total_colunas):
        self.vizinhos = []
        # Para baixo
        if self.row < total_linhas - 1 and not grid[self.row + 1][self.col].is_parede():
            self.vizinhos.append(grid[self.row + 1][self.col])
        # Para cima
        if self.row > 0 and not grid[self.row - 1][self.col].is_parede():
            self.vizinhos.append(grid[self.row - 1][self.col])
        # Para a direita
        if self.col < total_colunas - 1 and not grid[self.row][self.col + 1].is_parede():
            self.vizinhos.append(grid[self.row][self.col + 1])
        # Para a esquerda
        if self.col > 0 and not grid[self.row][self.col - 1].is_parede():
            self.vizinhos.append(grid[self.row][self.col - 1])


class Botao:
    """Botão interativo da interface."""
    def __init__(self, x, y, width, height, texto, cor_fundo, cor_texto, cor_borda=None, cor_hover=None, ativo=True, selecionado=False):
        self.rect = pygame.Rect(x, y, width, height)
        self.texto = texto
        self.cor_fundo = cor_fundo
        self.cor_texto = cor_texto
        self.cor_borda = cor_borda if cor_borda else cor_fundo
        self.cor_hover = cor_hover if cor_hover else (min(cor_fundo[0]+30, 255), min(cor_fundo[1]+30, 255), min(cor_fundo[2]+30, 255))
        self.ativo = ativo
        self.selecionado = selecionado

    def desenhar(self, tela, mouse_pos):
        if not self.ativo:
            cor_bg = (30, 30, 35)
            cor_txt = (80, 80, 85)
            cor_bd = (40, 40, 45)
        elif self.selecionado:
            cor_bg = COR_ACCENT
            cor_txt = (255, 255, 255)
            cor_bd = (255, 255, 255)
        elif self.rect.collidepoint(mouse_pos):
            cor_bg = self.cor_hover
            cor_txt = self.cor_texto
            cor_bd = (255, 255, 255)
        else:
            cor_bg = self.cor_fundo
            cor_txt = self.cor_texto
            cor_bd = self.cor_borda

        pygame.draw.rect(tela, cor_bg, self.rect, border_radius=6)
        pygame.draw.rect(tela, cor_bd, self.rect, 1, border_radius=6)

        text_surf = font_badge.render(self.texto, True, cor_txt)
        text_rect = text_surf.get_rect(center=self.rect.center)
        tela.blit(text_surf, text_rect)

    def clicado(self, mouse_pos):
        return self.ativo and self.rect.collidepoint(mouse_pos)


def criar_grid(linhas, colunas, tamanho_no):
    grid = []
    for r in range(linhas):
        grid.append([])
        for c in range(colunas):
            no = No(r, c, tamanho_no, linhas)
            grid[r].append(no)
    return grid


def limpar_caminhos_busca(grid):
    for r in range(len(grid)):
        for c in range(len(grid[r])):
            node = grid[r][c]
            if node.cor in (COR_EXPANSAO_FECHADO, COR_EXPANSAO_ABERTO, COR_CAMINHO):
                node.resetar()


def escolher_inicio_fim_distantes(linhas, colunas):
    passagens = []
    for r in range(1, linhas - 1):
        for c in range(1, colunas - 1):
            if r % 2 == 1 and c % 2 == 1:
                passagens.append((r, c))
                
    start = random.choice(passagens)
    min_dist = int((linhas + colunas) * 0.5)
    candidatos = [p for p in passagens if abs(p[0] - start[0]) + abs(p[1] - start[1]) >= min_dist]
    
    if candidatos:
        target = random.choice(candidatos)
    else:
        target = max(passagens, key=lambda p: abs(p[0] - start[0]) + abs(p[1] - start[1]))
        
    return start, target


def gerar_labirinto_dfs_single(grid, state, linhas, colunas):
    start_pos, target_pos = escolher_inicio_fim_distantes(linhas, colunas)
    state['inicio_pos'] = start_pos
    state['alvo_pos'] = target_pos
    
    for r in range(linhas):
        for c in range(colunas):
            grid[r][c].tornar_parede()
            
    visitados = set()
    pilha = []
    
    r_ini, c_ini = start_pos
    grid[r_ini][c_ini].resetar()
    visitados.add((r_ini, c_ini))
    pilha.append((r_ini, c_ini))
    
    while pilha:
        r, c = pilha[-1]
        vizinhos = []
        for dr, dc in [(-2, 0), (2, 0), (0, -2), (0, 2)]:
            nr, nc = r + dr, c + dc
            if 0 < nr < linhas - 1 and 0 < nc < colunas - 1:
                if (nr, nc) not in visitados:
                    vizinhos.append((nr, nc, dr, dc))
                    
        if vizinhos:
            nr, nc, dr, dc = random.choice(vizinhos)
            grid[r + dr // 2][c + dc // 2].resetar()
            grid[nr][nc].resetar()
            visitados.add((nr, nc))
            pilha.append((nr, nc))
        else:
            pilha.pop()
            
    grid[start_pos[0]][start_pos[1]].tornar_inicio()
    grid[target_pos[0]][target_pos[1]].tornar_alvo()


def gerar_labirinto_prim_single(grid, state, linhas, colunas):
    start_pos, target_pos = escolher_inicio_fim_distantes(linhas, colunas)
    state['inicio_pos'] = start_pos
    state['alvo_pos'] = target_pos
    
    for r in range(linhas):
        for c in range(colunas):
            grid[r][c].tornar_parede()
            
    opcoes = [(r, c) for r in range(1, linhas-1, 2) for c in range(1, colunas-1, 2)]
    r_ini, c_ini = random.choice(opcoes)
    grid[r_ini][c_ini].resetar()
    
    walls = []
    for dr, dc in [(-2, 0), (2, 0), (0, -2), (0, 2)]:
        nr, nc = r_ini + dr, c_ini + dc
        if 0 < nr < linhas - 1 and 0 < nc < colunas - 1:
            walls.append((r_ini + dr//2, c_ini + dc//2, nr, nc))
            
    while walls:
        idx = random.randint(0, len(walls) - 1)
        wr, wc, nr, nc = walls.pop(idx)
        
        if grid[nr][nc].is_parede():
            grid[wr][wc].resetar()
            grid[nr][nc].resetar()
            
            for dr, dc in [(-2, 0), (2, 0), (0, -2), (0, 2)]:
                nnr, nnc = nr + dr, nc + dc
                if 0 < nnr < linhas - 1 and 0 < nnc < colunas - 1:
                    if grid[nnr][nnc].is_parede():
                        walls.append((nr + dr//2, nc + dc//2, nnr, nnc))
                        
    grid[start_pos[0]][start_pos[1]].tornar_inicio()
    grid[target_pos[0]][target_pos[1]].tornar_alvo()


def gerar_obstaculos_organicos_single(grid, state, linhas, colunas):
    start_pos, target_pos = escolher_inicio_fim_distantes(linhas, colunas)
    state['inicio_pos'] = start_pos
    state['alvo_pos'] = target_pos
    
    for r in range(linhas):
        for c in range(colunas):
            grid[r][c].resetar()
            
    num_muros = int((linhas * colunas) // 100)
    for _ in range(num_muros):
        sr = random.randint(2, linhas - 3)
        sc = random.randint(2, colunas - 3)
        direcao = random.choice(['h', 'v', 'bloco'])
        tamanho = random.randint(4, 10)
        
        for i in range(tamanho):
            if direcao == 'h':
                nr, nc = sr, sc + i
            elif direcao == 'v':
                nr, nc = sr + i, sc
            else:
                nr, nc = sr + (i // 3), sc + (i % 3)
                
            if 0 < nr < linhas - 1 and 0 < nc < colunas - 1:
                grid[nr][nc].tornar_parede()
                
    for r in range(1, linhas - 1):
        for c in range(1, colunas - 1):
            if not grid[r][c].is_parede() and random.random() < 0.08:
                grid[r][c].tornar_parede()
                
    grid[start_pos[0]][start_pos[1]].tornar_inicio()
    grid[target_pos[0]][target_pos[1]].tornar_alvo()


def a_star_passo_a_passo(grid, inicio, alvo):
    """
    Gerador passo a passo do algoritmo A*. 
    Faz yields correspondendo a cada linha lógica do pseudo-código.
    """
    came_from = {}
    open_set = PriorityQueue()
    count = 0
    
    # Linha 1: open_set = FilaDePrioridade()
    yield {
        'line': 1, 'current': None, 'neighbor': None,
        'g': None, 'h': None, 'f': None,
        'msg': "Fila de Prioridades (open_set) inicializada vazia.",
        'open_set': [], 'came_from': came_from, 'status': 'executando'
    }
    
    # Linha 2: open_set.inserir(inicio, f_score=h(inicio))
    h_ini = abs(inicio.row - alvo.row) + abs(inicio.col - alvo.col)
    open_set.put((h_ini, count, inicio))
    open_set_hash = {inicio}
    
    yield {
        'line': 2, 'current': inicio, 'neighbor': None,
        'g': 0, 'h': h_ini, 'f': h_ini,
        'msg': f"Nó inicial ({inicio.row}, {inicio.col}) inserido na fila com f(n) = h(n) = {h_ini}.",
        'open_set': [(inicio, h_ini)], 'came_from': came_from, 'status': 'executando'
    }
    
    # Linha 3: g_score[todos] = inf; g_score[inicio] = 0
    g_score = {node: float('inf') for row in grid for node in row}
    g_score[inicio] = 0
    
    yield {
        'line': 3, 'current': inicio, 'neighbor': None,
        'g': 0, 'h': None, 'f': None,
        'msg': "Tabela g_score inicializada. Custo do início g(inicio) definido como 0.",
        'open_set': [(inicio, h_ini)], 'came_from': came_from, 'status': 'executando'
    }
    
    # Linha 4: f_score[todos] = inf; f_score[inicio] = h(inicio)
    f_score = {node: float('inf') for row in grid for node in row}
    f_score[inicio] = h_ini
    
    yield {
        'line': 4, 'current': inicio, 'neighbor': None,
        'g': 0, 'h': h_ini, 'f': h_ini,
        'msg': f"Tabela f_score inicializada. f_score[inicio] = g(0) + h({h_ini}) = {h_ini}.",
        'open_set': [(inicio, h_ini)], 'came_from': came_from, 'status': 'executando'
    }
    
    while not open_set.empty():
        # Obter estado ordenado da fila para visualização
        queue_items = sorted(open_set.queue, key=lambda x: x[0])
        display_queue = [(item[2], item[0]) for item in queue_items]
        
        # Linha 5: enquanto open_set não estiver vazio:
        yield {
            'line': 5, 'current': None, 'neighbor': None,
            'g': None, 'h': None, 'f': None,
            'msg': f"Fila possui {len(open_set_hash)} nó(s). Continuando loop...",
            'open_set': display_queue, 'came_from': came_from, 'status': 'executando'
        }
        
        # Linha 6: no_atual = open_set.remover_menor_f()
        item = open_set.get()
        current = item[2]
        if current in open_set_hash:
            open_set_hash.remove(current)
            
        queue_items = sorted(open_set.queue, key=lambda x: x[0])
        display_queue = [(it[2], it[0]) for it in queue_items]
        
        curr_g = g_score[current]
        curr_h = abs(current.row - alvo.row) + abs(current.col - alvo.col)
        curr_f = f_score[current]
        
        yield {
            'line': 6, 'current': current, 'neighbor': None,
            'g': curr_g, 'h': curr_h, 'f': curr_f,
            'msg': f"Extraído nó ({current.row}, {current.col}) com menor f(n) = {curr_f}.",
            'open_set': display_queue, 'came_from': came_from, 'status': 'executando'
        }
        
        # Linha 7: se no_atual == alvo:
        yield {
            'line': 7, 'current': current, 'neighbor': None,
            'g': curr_g, 'h': curr_h, 'f': curr_f,
            'msg': f"Verificando se o nó ({current.row}, {current.col}) é o alvo.",
            'open_set': display_queue, 'came_from': came_from, 'status': 'executando'
        }
        
        if current == alvo:
            # Linha 8: reconstruir_caminho_final()
            yield {
                'line': 8, 'current': current, 'neighbor': None,
                'g': curr_g, 'h': curr_h, 'f': curr_f,
                'msg': "Alvo alcançado! Iniciando reconstrução do caminho mais curto...",
                'open_set': display_queue, 'came_from': came_from, 'status': 'sucesso'
            }
            
            # Reconstrói visualmente passo a passo
            curr_node = current
            caminho_nodos = []
            while curr_node in came_from:
                caminho_nodos.append(curr_node)
                curr_node = came_from[curr_node]
                
            for node in reversed(caminho_nodos):
                if node != alvo and node != inicio:
                    node.tornar_caminho()
                yield {
                    'line': 8, 'current': node, 'neighbor': None,
                    'g': g_score[node], 'h': abs(node.row - alvo.row) + abs(node.col - alvo.col), 'f': f_score[node],
                    'msg': f"Traçando nó ({node.row}, {node.col}) na rota final.",
                    'open_set': display_queue, 'came_from': came_from, 'status': 'sucesso'
                }
                
            inicio.tornar_inicio()
            alvo.tornar_alvo()
            
            # Linha 9: fim (sucesso)
            yield {
                'line': 9, 'current': current, 'neighbor': None,
                'g': curr_g, 'h': curr_h, 'f': curr_f,
                'msg': "Caminho traçado com sucesso! Simulação finalizada.",
                'open_set': display_queue, 'came_from': came_from, 'status': 'sucesso'
            }
            return
            
        current.atualizar_vizinhos(grid, len(grid), len(grid[0]))
        
        # Linha 10: para cada vizinho de no_atual:
        yield {
            'line': 10, 'current': current, 'neighbor': None,
            'g': curr_g, 'h': curr_h, 'f': curr_f,
            'msg': f"Buscando vizinhos de ({current.row}, {current.col}). Encontrados {len(current.vizinhos)} vizinhos.",
            'open_set': display_queue, 'came_from': came_from, 'status': 'executando'
        }
        
        for neighbor in current.vizinhos:
            # Linha 11: temp_g = g_score[no_atual] + 1
            temp_g = curr_g + 1
            yield {
                'line': 11, 'current': current, 'neighbor': neighbor,
                'g': temp_g, 'h': None, 'f': None,
                'msg': f"Custo temporário g(n) para ({neighbor.row}, {neighbor.col}) calculado: {curr_g} + 1 = {temp_g}.",
                'open_set': display_queue, 'came_from': came_from, 'status': 'executando'
            }
            
            # Linha 12: se temp_g < g_score[vizinho]:
            prev_g = g_score[neighbor]
            yield {
                'line': 12, 'current': current, 'neighbor': neighbor,
                'g': temp_g, 'h': None, 'f': None,
                'msg': f"Testando se g(n) temporário={temp_g} < g_score anterior={prev_g} para ({neighbor.row}, {neighbor.col}).",
                'open_set': display_queue, 'came_from': came_from, 'status': 'executando'
            }
            
            if temp_g < g_score[neighbor]:
                # Linha 13: came_from[vizinho] = no_atual
                came_from[neighbor] = current
                yield {
                    'line': 13, 'current': current, 'neighbor': neighbor,
                    'g': temp_g, 'h': None, 'f': None,
                    'msg': f"Origem de ({neighbor.row}, {neighbor.col}) definida como ({current.row}, {current.col}).",
                    'open_set': display_queue, 'came_from': came_from, 'status': 'executando'
                }
                
                # Linha 14: g_score[vizinho] = temp_g
                g_score[neighbor] = temp_g
                yield {
                    'line': 14, 'current': current, 'neighbor': neighbor,
                    'g': temp_g, 'h': None, 'f': None,
                    'msg': f"Custo real g_score de ({neighbor.row}, {neighbor.col}) atualizado para {temp_g}.",
                    'open_set': display_queue, 'came_from': came_from, 'status': 'executando'
                }
                
                # Linha 15: f_score[vizinho] = temp_g + h(vizinho)
                neigh_h = abs(neighbor.row - alvo.row) + abs(neighbor.col - alvo.col)
                neigh_f = temp_g + neigh_h
                f_score[neighbor] = neigh_f
                yield {
                    'line': 15, 'current': current, 'neighbor': neighbor,
                    'g': temp_g, 'h': neigh_h, 'f': neigh_f,
                    'msg': f"f_score de ({neighbor.row}, {neighbor.col}) = g({temp_g}) + h({neigh_h}) = {neigh_f}.",
                    'open_set': display_queue, 'came_from': came_from, 'status': 'executando'
                }
                
                # Linha 16: se vizinho não em open_set:
                in_open = neighbor in open_set_hash
                yield {
                    'line': 16, 'current': current, 'neighbor': neighbor,
                    'g': temp_g, 'h': neigh_h, 'f': neigh_f,
                    'msg': f"Verificando se ({neighbor.row}, {neighbor.col}) já está no open_set: {'Sim' if in_open else 'Não'}.",
                    'open_set': display_queue, 'came_from': came_from, 'status': 'executando'
                }
                
                if not in_open:
                    # Linha 17: open_set.inserir(vizinho, f_score[vizinho])
                    count += 1
                    open_set.put((neigh_f, count, neighbor))
                    open_set_hash.add(neighbor)
                    if neighbor != alvo:
                        neighbor.tornar_aberto()
                        
                    queue_items = sorted(open_set.queue, key=lambda x: x[0])
                    display_queue = [(it[2], it[0]) for it in queue_items]
                    
                    yield {
                        'line': 17, 'current': current, 'neighbor': neighbor,
                        'g': temp_g, 'h': neigh_h, 'f': neigh_f,
                        'msg': f"Inserido ({neighbor.row}, {neighbor.col}) no open_set com prioridade {neigh_f} (Tornou-se ABERTO).",
                        'open_set': display_queue, 'came_from': came_from, 'status': 'executando'
                    }
                    
        # Linha 18: no_atual.fechado = Verdadeiro
        if current != inicio:
            current.tornar_fechado()
        yield {
            'line': 18, 'current': current, 'neighbor': None,
            'g': curr_g, 'h': curr_h, 'f': curr_f,
            'msg': f"Finalizada avaliação do nó ({current.row}, {current.col}). Marcado como FECHADO (azul escuro).",
            'open_set': display_queue, 'came_from': came_from, 'status': 'executando'
        }
        
    # Fila de prioridades esgotada sem achar o alvo
    yield {
        'line': 5, 'current': None, 'neighbor': None,
        'g': None, 'h': None, 'f': None,
        'msg': "Fila de prioridades vazia. Alvo inalcançável! Não há caminho válido.",
        'open_set': [], 'came_from': came_from, 'status': 'sem_caminho'
    }


def main():
    LARGURA_TELA = 1600
    ALTURA_TELA = 900
    
    TELA = pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA))
    pygame.display.set_caption("A*")
    
    # Dimensões da Grade
    LINHAS = 20
    COLUNAS = 20
    TAMANHO_NO = 30  # 35 * 20 = 700px (Quadrado perfeito na esquerda)
    
    # Posições e Dimensões dos Painéis
    CARD_L_X, CARD_L_Y, CARD_L_W, CARD_L_H = 40, 100, 740, 765
    CARD_R_X, CARD_R_Y, CARD_R_W, CARD_R_H = 800, 100, 760, 765
    
    GRID_X = CARD_L_X + (CARD_L_W - (COLUNAS * TAMANHO_NO)) // 2
    GRID_Y = CARD_L_Y + 50
    
    # Inicialização do Grid
    grid = criar_grid(LINHAS, COLUNAS, TAMANHO_NO)
    
    # Estado da simulação
    state = {
        'inicio_pos': None,
        'alvo_pos': None,
        'running': False,      # Executando automaticamente?
        'paused': False,       # Pausado ou em modo manual?
        'finished': False,     # Terminou a busca?
        'status_str': "Configurando...", # String de status
        'status_cor': COR_TEXT_MUTED,
        'ferramenta': 'parede', # 'parede', 'inicio', 'alvo'
        'velocidade_idx': 2,    # 'Médio'
    }
    
    # Geradores e passos
    generator = None
    step_info = None
    ultimo_passo_tempo = 0
    
    # Lista de Velocidades (Delay em milissegundos)
    VELOCIDADES = [
        ("Muito Lento", 1500),
        ("Lento", 750),
        ("Médio", 250),
        ("Rápido", 20)
    ]
    
    # Botões de Ferramentas (Esquerda)
    btn_ferramentas = {
        'parede': Botao(CARD_L_X + 150, CARD_L_Y + 12, 100, 26, "Parede", (35, 35, 40), COR_TEXT_BRIGHT, selecionado=True),
        'inicio': Botao(CARD_L_X + 260, CARD_L_Y + 12, 100, 26, "Início", (35, 35, 40), COR_INICIO),
        'alvo': Botao(CARD_L_X + 370, CARD_L_Y + 12, 100, 26, "Alvo", (35, 35, 40), COR_FINAL)
    }
    
    # Botões de Controlo (Direita - Linha de Cima)
    btn_controles = {
        'play': Botao(CARD_R_X + 20, CARD_R_Y + 12, 90, 26, "Play", (30, 80, 40), (255, 255, 255)),
        'passo': Botao(CARD_R_X + 120, CARD_R_Y + 12, 110, 26, "Passo a Passo", (35, 35, 40), COR_TEXT_BRIGHT),
        'modo': Botao(CARD_R_X + 240, CARD_R_Y + 12, 110, 26, "Modo: Auto", (35, 35, 40), COR_TEXT_BRIGHT),
        'limpar': Botao(CARD_R_X + 360, CARD_R_Y + 12, 80, 26, "Limpar", (35, 35, 40), COR_TEXT_BRIGHT),
        'limpar_tudo': Botao(CARD_R_X + 450, CARD_R_Y + 12, 100, 26, "Limpar Tudo", (60, 30, 30), COR_TEXT_BRIGHT),
        'velocidade': Botao(CARD_R_X + 560, CARD_R_Y + 12, 180, 26, f"Velocidade: {VELOCIDADES[state['velocidade_idx']][0]}", (35, 35, 40), COR_TEXT_BRIGHT)
    }
    
    # Botões de Labirinto (Direita - Linha de Baixo)
    btn_labirintos = {
        'dfs': Botao(CARD_R_X + 200, CARD_R_Y + 722, 130, 26, "Labirinto DFS", (40, 40, 45), COR_TEXT_BRIGHT),
        'prim': Botao(CARD_R_X + 340, CARD_R_Y + 722, 130, 26, "Labirinto Prim", (40, 40, 45), COR_TEXT_BRIGHT),
        'organico': Botao(CARD_R_X + 480, CARD_R_Y + 722, 130, 26, "Muros Orgânicos", (40, 40, 45), COR_TEXT_BRIGHT),
        'sair': Botao(CARD_R_X + 660, CARD_R_Y + 722, 80, 26, "Sair", (80, 20, 20), (255, 255, 255))
    }
    
    # Gera cenário inicial orgânico por padrão
    gerar_obstaculos_organicos_single(grid, state, LINHAS, COLUNAS)
    state['status_str'] = "Pronto para Simulação"
    state['status_cor'] = (138, 138, 147)
    
    clock = pygame.time.Clock()
    rodando = True
    
    # Função para redefinir o estado da simulação
    def acionar_limpeza(limpar_muros=False):
        nonlocal generator, step_info
        generator = None
        step_info = None
        state['running'] = False
        state['paused'] = False
        state['finished'] = False
        state['status_str'] = "Pronto para Simulação"
        state['status_cor'] = (138, 138, 147)
        btn_controles['play'].texto = "Play"
        btn_controles['play'].cor_fundo = (30, 80, 40)
        
        if limpar_muros:
            state['inicio_pos'] = None
            state['alvo_pos'] = None
            state['status_str'] = "Configure o Início e o Alvo"
            for r in range(LINHAS):
                for c in range(COLUNAS):
                    grid[r][c].resetar()
        else:
            limpar_caminhos_busca(grid)
            # Restaurar as posições de início e alvo visualmente
            if state['inicio_pos']:
                grid[state['inicio_pos'][0]][state['inicio_pos'][1]].tornar_inicio()
            if state['alvo_pos']:
                grid[state['alvo_pos'][0]][state['alvo_pos'][1]].tornar_alvo()
                
    # Função para rodar uma única linha/passo da busca A*
    def avancar_passo():
        nonlocal generator, step_info
        
        # Cria gerador caso não exista
        if generator is None:
            if not state['inicio_pos'] or not state['alvo_pos']:
                state['status_str'] = "Erro: Defina Início e Alvo"
                state['status_cor'] = (250, 50, 50)
                return
            
            limpar_caminhos_busca(grid)
            ip, ap = state['inicio_pos'], state['alvo_pos']
            inicio_node = grid[ip[0]][ip[1]]
            alvo_node = grid[ap[0]][ap[1]]
            
            # Atualiza vizinhos dos nós
            for r in range(LINHAS):
                for c in range(COLUNAS):
                    grid[r][c].atualizar_vizinhos(grid, LINHAS, COLUNAS)
            
            generator = a_star_passo_a_passo(grid, inicio_node, alvo_node)
            state['finished'] = False
            
        try:
            step_info = next(generator)
            # Atualiza o status baseando-se nas informações do gerador
            status = step_info['status']
            if status == 'sucesso':
                state['status_str'] = "Sucesso!"
                state['status_cor'] = (153, 254, 15)
                state['finished'] = True
                state['running'] = False
                btn_controles['play'].texto = "Play"
                btn_controles['play'].cor_fundo = (30, 80, 40)
            elif status == 'sem_caminho':
                state['status_str'] = "Sem Caminho para o Alvo"
                state['status_cor'] = (250, 50, 50)
                state['finished'] = True
                state['running'] = False
                btn_controles['play'].texto = "Play"
                btn_controles['play'].cor_fundo = (30, 80, 40)
            else:
                if state['running']:
                    state['status_str'] = "Executando A* (Auto)"
                    state['status_cor'] = COR_ACCENT
                else:
                    state['status_str'] = "Pausado / Passo a Passo"
                    state['status_cor'] = (255, 193, 7)
        except StopIteration:
            generator = None
            state['finished'] = True
            state['running'] = False
            btn_controles['play'].texto = "Play"
            btn_controles['play'].cor_fundo = (30, 80, 40)

    # LOOP PRINCIPAL
    while rodando:
        clock.tick(60)
        mouse_pos = pygame.mouse.get_pos()
        tempo_atual = pygame.time.get_ticks()
        
        # 1. TRATAMENTO DE EVENTOS DE ENTRADA
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                rodando = False
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    rodando = False
                # Teclas de atalho rápidas
                elif event.key == pygame.K_SPACE:
                    # Alterna execução
                    if not state['finished']:
                        state['running'] = not state['running']
                        if state['running']:
                            btn_controles['play'].texto = "Pause"
                            btn_controles['play'].cor_fundo = (180, 100, 30)
                        else:
                            btn_controles['play'].texto = "Play"
                            btn_controles['play'].cor_fundo = (30, 80, 40)
                elif event.key == pygame.K_RETURN and not state['running'] and not state['finished']:
                    avancar_passo()
                elif event.key == pygame.K_c:
                    acionar_limpeza(limpar_muros=False)
                elif event.key == pygame.K_v:
                    acionar_limpeza(limpar_muros=True)
                    
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Clique do mouse nos Botões de Ferramentas (Esquerda)
                for tool_name, btn in btn_ferramentas.items():
                    if btn.clicado(mouse_pos):
                        # Desmarca as outras
                        for k, b in btn_ferramentas.items():
                            b.selecionado = (k == tool_name)
                        state['ferramenta'] = tool_name
                
                # Clique do mouse nos Botões de Controles (Direita superior)
                if btn_controles['play'].clicado(mouse_pos):
                    if not state['finished']:
                        state['running'] = not state['running']
                        if state['running']:
                            btn_controles['play'].texto = "Pause"
                            btn_controles['play'].cor_fundo = (180, 100, 30)
                        else:
                            btn_controles['play'].texto = "Play"
                            btn_controles['play'].cor_fundo = (30, 80, 40)
                            
                elif btn_controles['passo'].clicado(mouse_pos):
                    if not state['running'] and not state['finished']:
                        avancar_passo()
                        
                elif btn_controles['modo'].clicado(mouse_pos):
                    # Alterna modo automático vs manual
                    if btn_controles['modo'].texto == "Modo: Auto":
                        btn_controles['modo'].texto = "Modo: Manual"
                        # Se estava rodando, pausa
                        state['running'] = False
                        btn_controles['play'].texto = "Play"
                        btn_controles['play'].cor_fundo = (30, 80, 40)
                    else:
                        btn_controles['modo'].texto = "Modo: Auto"
                        
                elif btn_controles['limpar'].clicado(mouse_pos):
                    acionar_limpeza(limpar_muros=False)
                    
                elif btn_controles['limpar_tudo'].clicado(mouse_pos):
                    acionar_limpeza(limpar_muros=True)
                    
                elif btn_controles['velocidade'].clicado(mouse_pos):
                    state['velocidade_idx'] = (state['velocidade_idx'] + 1) % len(VELOCIDADES)
                    btn_controles['velocidade'].texto = f"Velocidade: {VELOCIDADES[state['velocidade_idx']][0]}"
                
                # Clique do mouse nos Botões de Labirinto (Direita inferior)
                if not state['running'] and generator is None:
                    if btn_labirintos['dfs'].clicado(mouse_pos):
                        acionar_limpeza(limpar_muros=True)
                        gerar_labirinto_dfs_single(grid, state, LINHAS, COLUNAS)
                        state['status_str'] = "Labirinto DFS gerado"
                        
                    elif btn_labirintos['prim'].clicado(mouse_pos):
                        acionar_limpeza(limpar_muros=True)
                        gerar_labirinto_prim_single(grid, state, LINHAS, COLUNAS)
                        state['status_str'] = "Labirinto Prim gerado"
                        
                    elif btn_labirintos['organico'].clicado(mouse_pos):
                        acionar_limpeza(limpar_muros=True)
                        gerar_obstaculos_organicos_single(grid, state, LINHAS, COLUNAS)
                        state['status_str'] = "Obstáculos Orgânicos gerados"
                        
                if btn_labirintos['sair'].clicado(mouse_pos):
                    rodando = False
                    
                # Clique direto no Grid (Desenho Manual) - Apenas se NÃO estiver simulando
                if not state['running'] and generator is None:
                    if GRID_X <= mouse_pos[0] < GRID_X + (COLUNAS * TAMANHO_NO) and \
                       GRID_Y <= mouse_pos[1] < GRID_Y + (LINHAS * TAMANHO_NO):
                        
                        c = (mouse_pos[0] - GRID_X) // TAMANHO_NO
                        r = (mouse_pos[1] - GRID_Y) // TAMANHO_NO
                        clicked_node = grid[r][c]
                        
                        tool = state['ferramenta']
                        if tool == 'inicio':
                            # Remove anterior se houver
                            if state['inicio_pos']:
                                r_prev, c_prev = state['inicio_pos']
                                grid[r_prev][c_prev].resetar()
                            clicked_node.tornar_inicio()
                            state['inicio_pos'] = (r, c)
                            if state['status_str'] == "Configure o Início e o Alvo":
                                state['status_str'] = "Pronto para Simulação"
                        elif tool == 'alvo':
                            # Remove anterior se houver
                            if state['alvo_pos']:
                                r_prev, c_prev = state['alvo_pos']
                                grid[r_prev][c_prev].resetar()
                            clicked_node.tornar_alvo()
                            state['alvo_pos'] = (r, c)
                            if state['status_str'] == "Configure o Início e o Alvo":
                                state['status_str'] = "Pronto para Simulação"
                        elif tool == 'parede':
                            if not clicked_node.is_inicio() and not clicked_node.is_alvo():
                                if clicked_node.is_parede():
                                    clicked_node.resetar()
                                else:
                                    clicked_node.tornar_parede()

        # 2. SEGUIMENTO DO DESENHO CONTÍNUO DO MOUSE (Para Paredes)
        if not state['running'] and generator is None:
            if pygame.mouse.get_pressed()[0]: # Botão esquerdo pressionado
                if GRID_X <= mouse_pos[0] < GRID_X + (COLUNAS * TAMANHO_NO) and \
                   GRID_Y <= mouse_pos[1] < GRID_Y + (LINHAS * TAMANHO_NO):
                    c = (mouse_pos[0] - GRID_X) // TAMANHO_NO
                    r = (mouse_pos[1] - GRID_Y) // TAMANHO_NO
                    hovered_node = grid[r][c]
                    if state['ferramenta'] == 'parede':
                        # Apenas desenha parede por arrasto (não apaga) para fluidez
                        if not hovered_node.is_inicio() and not hovered_node.is_alvo():
                            hovered_node.tornar_parede()

        # 3. LÓGICA DE EXECUÇÃO AUTOMÁTICA
        if state['running'] and not state['finished']:
            delay_ms = VELOCIDADES[state['velocidade_idx']][1]
            if tempo_atual - ultimo_passo_tempo >= delay_ms:
                avancar_passo()
                ultimo_passo_tempo = tempo_atual

        # 4. ATUALIZAR ESCALA DE ANIMAÇÃO DAS CÉLULAS DO GRID
        for row in grid:
            for node in row:
                if node.anim_scale < 1.0:
                    node.anim_scale += 0.15
                    if node.anim_scale > 1.0:
                        node.anim_scale = 1.0

        # 5. RENDERIZAÇÃO DA TELA
        TELA.fill((12, 12, 14))
        
        # --- 5.1 HEADER (Cabeçalho Didático) ---
        pygame.draw.rect(TELA, COR_ACCENT, (0, 0, LARGURA_TELA, 4))
        
        text_head = font_header.render("A*", True, (255, 255, 255))
        TELA.blit(text_head, (40, 20))
        
        instrucoes_texto = "ESPAÇO: Play/Pause  |  ENTER: Próxima Linha (Manual)  |  C: Limpar Caminho  |  V: Limpar Tudo"
        text_inst = font_instrucoes.render(instrucoes_texto, True, COR_TEXT_MUTED)
        TELA.blit(text_inst, (40, 56))
        
        # Badge de status global no canto direito superior
        badge_rect = pygame.Rect(LARGURA_TELA - 260, 25, 220, 32)
        pygame.draw.rect(TELA, (22, 22, 26), badge_rect, border_radius=6)
        pygame.draw.rect(TELA, state['status_cor'], badge_rect, 1, border_radius=6)
        
        badge_text = font_badge.render(state['status_str'].upper(), True, state['status_cor'])
        text_rect = badge_text.get_rect(center=badge_rect.center)
        TELA.blit(badge_text, text_rect)
        
        pygame.draw.line(TELA, (37, 37, 42), (0, 92), (LARGURA_TELA, 92), 1)

        # --- 5.2 CARD ESQUERDA (Grade e Ferramentas) ---
        pygame.draw.rect(TELA, COR_CARD_BG, (CARD_L_X, CARD_L_Y, CARD_L_W, CARD_L_H), border_radius=12)
        pygame.draw.rect(TELA, COR_CARD_BORDER, (CARD_L_X, CARD_L_Y, CARD_L_W, CARD_L_H), 1, border_radius=12)
        
        lbl_ferr = font_titulo.render("Editor de Mapa:", True, COR_TEXT_BRIGHT)
        TELA.blit(lbl_ferr, (CARD_L_X + 25, CARD_L_Y + 16))
        
        # Desenhar botões de ferramenta
        for btn in btn_ferramentas.values():
            btn.desenhar(TELA, mouse_pos)
            
        # Desenhar Grade do Labirinto
        for row in grid:
            for node in row:
                node.desenhar(TELA, GRID_X, GRID_Y)

        # --- 5.3 CARD DIREITA (Controles, Pseudo-código e Inspetor) ---
        pygame.draw.rect(TELA, COR_CARD_BG, (CARD_R_X, CARD_R_Y, CARD_R_W, CARD_R_H), border_radius=12)
        pygame.draw.rect(TELA, COR_CARD_BORDER, (CARD_R_X, CARD_R_Y, CARD_R_W, CARD_R_H), 1, border_radius=12)
        
        # Desenhar botões de controle
        for btn in btn_controles.values():
            btn.desenhar(TELA, mouse_pos)
            
        # Divisor horizontal superior
        pygame.draw.line(TELA, COR_CARD_BORDER, (CARD_R_X, CARD_R_Y + 52), (CARD_R_X + CARD_R_W, CARD_R_Y + 52), 1)
        
        # --- 5.3.1 VISUALIZADOR DE PSEUDO-CÓDIGO ---
        lbl_code_title = font_titulo.render("Algoritmo em Execução (Pseudo-código A*):", True, COR_TEXT_BRIGHT)
        TELA.blit(lbl_code_title, (CARD_R_X + 25, CARD_R_Y + 65))
        
        y_offset = CARD_R_Y + 95
        linha_ativa = step_info['line'] if step_info else None
        
        for idx, linha in enumerate(PSEUDO_CODIGO):
            num_linha = idx + 1
            line_rect = pygame.Rect(CARD_R_X + 20, y_offset, CARD_R_W - 40, 20)
            
            # Se for a linha ativa no debugger, destaca com fundo iluminado
            if num_linha == linha_ativa:
                pygame.draw.rect(TELA, COR_HIGHLIGHT, line_rect, border_radius=4)
                pygame.draw.rect(TELA, COR_HIGHLIGHT_BORDER, line_rect, 1, border_radius=4)
                txt_color = COR_TEXT_BRIGHT
                rendered_text = font_code_bold.render(linha, True, txt_color)
            else:
                txt_color = COR_TEXT_MUTED
                rendered_text = font_code.render(linha, True, txt_color)
                
            TELA.blit(rendered_text, (CARD_R_X + 30, y_offset + 2))
            y_offset += 20

        # Divisor horizontal médio
        pygame.draw.line(TELA, COR_CARD_BORDER, (CARD_R_X, CARD_R_Y + 475), (CARD_R_X + CARD_R_W, CARD_R_Y + 475), 1)

        # --- 5.3.2 INSPECTOR DE VARIÁVEIS ---
        lbl_insp_title = font_titulo.render("Inspector de Variáveis (Tempo Real):", True, COR_TEXT_BRIGHT)
        TELA.blit(lbl_insp_title, (CARD_R_X + 25, CARD_R_Y + 488))
        
        insp_y = CARD_R_Y + 515
        
        # Determina dados das variáveis
        curr_str = "-"
        viz_str = "-"
        g_str = "-"
        h_str = "-"
        f_str = "-"
        expl_str = "Aguardando início da simulação..."
        fila_itens = []
        
        if step_info:
            c_node = step_info['current']
            n_node = step_info['neighbor']
            
            if c_node:
                curr_str = f"({c_node.row}, {c_node.col})"
            if n_node:
                viz_str = f"({n_node.row}, {n_node.col})"
                
            # Exibe custos
            if step_info['g'] is not None:
                g_str = str(step_info['g'])
            if step_info['h'] is not None:
                h_str = str(step_info['h'])
            if step_info['f'] is not None:
                f_str = f"{step_info['g']} + {step_info['h']} = {step_info['f']}"
                
            expl_str = step_info['msg']
            fila_itens = step_info['open_set']
            
        elif not state['inicio_pos'] or not state['alvo_pos']:
            expl_str = "Desenhe obstáculos, defina o início (verde) e o fim (vermelho) para começar."
        else:
            expl_str = "Simulação pronta! Clique em Play (Auto) ou Passo a Passo para iniciar."

        # Coluna 1: Informações de Nós
        TELA.blit(font_inspector.render("Localização dos Nós:", True, COR_TEXT_MUTED), (CARD_R_X + 25, insp_y))
        TELA.blit(font_inspector_bold.render(f"Nó Atual n:  {curr_str}", True, COR_TEXT_BRIGHT), (CARD_R_X + 25, insp_y + 22))
        TELA.blit(font_inspector_bold.render(f"Vizinho v:   {viz_str}", True, COR_TEXT_BRIGHT), (CARD_R_X + 25, insp_y + 44))
        
        # Coluna 2: Cálculos Matemáticos f(n) = g(n) + h(n)
        TELA.blit(font_inspector.render("Função de Custo A*:", True, COR_TEXT_MUTED), (CARD_R_X + 280, insp_y))
        TELA.blit(font_inspector_bold.render(f"g(n) (Custo Real):   {g_str}", True, COR_TEXT_BRIGHT), (CARD_R_X + 280, insp_y + 22))
        TELA.blit(font_inspector_bold.render(f"h(n) (Heurística):   {h_str}", True, COR_TEXT_BRIGHT), (CARD_R_X + 280, insp_y + 44))
        TELA.blit(font_inspector_bold.render(f"f(n) = g(n)+h(n):   {f_str}", True, COR_ACCENT), (CARD_R_X + 280, insp_y + 66))

        # Coluna 3: Fila de Prioridades (open_set)
        TELA.blit(font_inspector.render(f"Fila de Prioridades (Tamanho: {len(fila_itens)}):", True, COR_TEXT_MUTED), (CARD_R_X + 500, insp_y))
        
        for q_idx in range(5):
            line_y = insp_y + 22 + q_idx * 18
            if q_idx < len(fila_itens):
                q_node, q_f = fila_itens[q_idx]
                if q_node.is_inicio():
                    name = "Início"
                elif q_node.is_alvo():
                    name = "Alvo"
                else:
                    name = f"Nó({q_node.row},{q_node.col})"
                txt = f"{q_idx + 1}º: {name} (f={q_f})"
                TELA.blit(font_inspector.render(txt, True, COR_TEXT_BRIGHT), (CARD_R_X + 500, line_y))
            else:
                TELA.blit(font_inspector.render("-", True, COR_TEXT_MUTED), (CARD_R_X + 500, line_y))
                
        if len(fila_itens) > 5:
            TELA.blit(font_inspector.render(f"+ {len(fila_itens) - 5} mais nós...", True, COR_TEXT_MUTED), (CARD_R_X + 500, insp_y + 112))

        # Divisor horizontal inferior das variáveis
        pygame.draw.line(TELA, COR_CARD_BORDER, (CARD_R_X, CARD_R_Y + 662), (CARD_R_X + CARD_R_W, CARD_R_Y + 662), 1)

        # Rodapé de Explicação/Mensagem do Passo
        lbl_msg = font_inspector.render("Descrição do Passo:", True, COR_TEXT_MUTED)
        TELA.blit(lbl_msg, (CARD_R_X + 25, CARD_R_Y + 672))
        
        # Envelopa o texto para caber no limite
        if len(expl_str) > 90:
            part1 = expl_str[:85] + "..."
            TELA.blit(font_inspector_bold.render(part1, True, (255, 235, 59)), (CARD_R_X + 25, CARD_R_Y + 692))
        else:
            TELA.blit(font_inspector_bold.render(expl_str, True, (255, 235, 59)), (CARD_R_X + 25, CARD_R_Y + 692))

        # Divisor horizontal inferior final
        pygame.draw.line(TELA, COR_CARD_BORDER, (CARD_R_X, CARD_R_Y + 715), (CARD_R_X + CARD_R_W, CARD_R_Y + 715), 1)

        # --- 5.3.3 GERADORES DE LABIRINTO ---
        lbl_maze = font_badge.render("Gerar Novo Mapa:", True, COR_TEXT_BRIGHT)
        TELA.blit(lbl_maze, (CARD_R_X + 25, CARD_R_Y + 726))
        
        # Desenha botões de geração de labirinto e sair
        for btn in btn_labirintos.values():
            # Desativa os botões de labirinto se estiver simulando
            if btn.texto in ("Labirinto DFS", "Labirinto Prim", "Muros Orgânicos"):
                btn.ativo = (not state['running'] and generator is None)
            btn.desenhar(TELA, mouse_pos)

        pygame.display.update()
        
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
