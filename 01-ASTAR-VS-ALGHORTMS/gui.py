import pygame
import random
from config import *

class No:
    def __init__(self, row, col, largura, total_linhas):
        self.row = row
        self.col = col
        self.largura = largura
        self.total_linhas = total_linhas
        self.cor = COR_FUNDO_CELULA
        self.vizinhos = []
        self.anim_scale = 1.0

    def get_pos(self): return self.row, self.col
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
        
        pygame.draw.rect(tela, COR_FUNDO_CELULA, (x, y, self.largura, self.largura))
        
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
        if self.row < total_linhas - 1 and not grid[self.row + 1][self.col].is_parede():
            self.vizinhos.append(grid[self.row + 1][self.col])
        if self.row > 0 and not grid[self.row - 1][self.col].is_parede():
            self.vizinhos.append(grid[self.row - 1][self.col])
        if self.col < total_colunas - 1 and not grid[self.row][self.col + 1].is_parede():
            self.vizinhos.append(grid[self.row][self.col + 1])
        if self.col > 0 and not grid[self.row][self.col - 1].is_parede():
            self.vizinhos.append(grid[self.row][self.col - 1])

def desenhar_cabecalho(tela, w_tela, state):
    pygame.draw.rect(tela, (19, 128, 252), (0, 0, w_tela, 4))
    
    text_head = font_header.render("COMPARAÇÃO DE ALGORITMOS DE BUSCA", True, (255, 255, 255))
    tela.blit(text_head, (40, 20))
    
    instrucoes_texto = "ESPAÇO: Simular  |  R: Orgânico  |  G: Lab. DFS  |  P: Lab. Prim  |  C: Limpar  |  ESC: Sair"
    text_inst = font_instrucoes.render(instrucoes_texto, True, (138, 138, 147))
    tela.blit(text_inst, (40, 56))
    
    badge_rect = pygame.Rect(w_tela - 220, 25, 180, 32)
    if state['running']:
        color = (19, 128, 252)
        text_str = "SIMULANDO"
    elif state['search_finished']:
        color = (153, 254, 15)
        text_str = "CONCLUÍDO"
    else:
        color = (138, 138, 147)
        text_str = "AGUARDANDO"
        
    pygame.draw.rect(tela, (22, 22, 26), badge_rect, border_radius=6)
    pygame.draw.rect(tela, color, badge_rect, 1, border_radius=6)
    badge_text = font_titulo.render(text_str, True, color)
    text_rect = badge_text.get_rect(center=badge_rect.center)
    tela.blit(badge_text, text_rect)
    
    pygame.draw.line(tela, (37, 37, 42), (0, 95), (w_tela, 95), 1)

def desenhar_ranking_badge(tela, card, g_idx, finish_order):
    if g_idx in finish_order:
        posicao = finish_order.index(g_idx)
        texto_ranking = f"{posicao + 1}º"
        cor_ranking = CORES_RANKING[posicao] if posicao < len(CORES_RANKING) else (138, 138, 147)
        
        badge_w, badge_h = 36, 22
        bx = card['x'] + card['width'] - badge_w - 20
        by = card['y'] + 15
        
        pygame.draw.rect(tela, (30, 30, 36), (bx, by, badge_w, badge_h), border_radius=4)
        pygame.draw.rect(tela, cor_ranking, (bx, by, badge_w, badge_h), 1, border_radius=4)
        
        rank_surf = font_titulo.render(texto_ranking, True, cor_ranking)
        rank_rect = rank_surf.get_rect(center=(bx + badge_w // 2, by + badge_h // 2))
        tela.blit(rank_surf, rank_rect)

def desenhar_painel_metricas(tela, card, g_idx, stats, max_vis, ox_grid, oy_grid, grid_w, grid_h, h_card):
    sp_x = card['x'] + ox_grid
    sp_y = card['y'] + oy_grid + grid_h + 15
    sp_w = grid_w
    sp_h = h_card - (oy_grid + grid_h + 15) - 20
    
    pygame.draw.rect(tela, (16, 16, 20), (sp_x, sp_y, sp_w, sp_h), border_radius=8)
    pygame.draw.rect(tela, (30, 30, 36), (sp_x, sp_y, sp_w, sp_h), 1, border_radius=8)
    
    status_curr = stats[g_idx]['status']
    status_color = (19, 128, 252) if status_curr == "Simulando..." else (153, 254, 15) if status_curr == "Concluído" else (250, 50, 50) if status_curr == "Sem Caminho" else (138, 138, 147)
    
    status_lbl = font_titulo.render("Status:", True, (255, 255, 255))
    status_val = font_titulo.render(status_curr, True, status_color)
    tela.blit(status_lbl, (sp_x + 15, sp_y + 15))
    tela.blit(status_val, (sp_x + sp_w - status_val.get_width() - 15, sp_y + 15))
    
    exp_lbl = font_sub.render("Células Exploradas (Busca):", True, (138, 138, 147))
    exp_val = font_titulo.render(str(stats[g_idx]['visitados']), True, (255, 255, 255))
    tela.blit(exp_lbl, (sp_x + 15, sp_y + 45))
    tela.blit(exp_val, (sp_x + sp_w - exp_val.get_width() - 15, sp_y + 43))
    
    cam_lbl = font_sub.render("Comprimento do Caminho:", True, (138, 138, 147))
    cam_val = font_titulo.render(str(stats[g_idx]['caminho']) if stats[g_idx]['caminho'] > 0 else "-", True, (255, 255, 255))
    tela.blit(cam_lbl, (sp_x + 15, sp_y + 75))
    tela.blit(cam_val, (sp_x + sp_w - cam_val.get_width() - 15, sp_y + 73))
    
    pas_lbl = font_sub.render("Passos / Loops de Simulação:", True, (138, 138, 147))
    pas_val = font_titulo.render(str(stats[g_idx]['passos']), True, (255, 255, 255))
    tela.blit(pas_lbl, (sp_x + 15, sp_y + 105))
    tela.blit(pas_val, (sp_x + sp_w - pas_val.get_width() - 15, sp_y + 103))
    
    bar_lbl = font_sub.render("Eficiência de Exploração (Menor é Melhor):", True, (138, 138, 147))
    tela.blit(bar_lbl, (sp_x + 15, sp_y + 140))
    
    bar_x = sp_x + 15
    bar_y = sp_y + 165
    bar_w = sp_w - 30
    bar_h = 14
    
    pygame.draw.rect(tela, (27, 27, 33), (bar_x, bar_y, bar_w, bar_h), border_radius=4)
    fill_pct = stats[g_idx]['visitados'] / max_vis
    fill_w = int(bar_w * fill_pct)
    if fill_w > 0:
        pygame.draw.rect(tela, (19, 128, 252), (bar_x, bar_y, fill_w, bar_h), border_radius=4)

def desenhar_cartoes(tela, cards, grids, stats, state, ox_grid, oy_grid, grid_w, grid_h, h_card, max_vis):
    for card in cards:
        pygame.draw.rect(tela, (22, 22, 26), (card['x'], card['y'], card['width'], card['height']), border_radius=12)
        pygame.draw.rect(tela, (37, 37, 42), (card['x'], card['y'], card['width'], card['height']), 1, border_radius=12)
        
        title_surf = font_card_titulo.render(card['titulo'], True, (255, 255, 255))
        tela.blit(title_surf, (card['x'] + 25, card['y'] + 15))
        
        formula_surf = font_formula.render(card['formula'], True, (19, 128, 252))
        tela.blit(formula_surf, (card['x'] + 25, card['y'] + 42))
        
        desc_surf = font_sub.render(card['subtitulo'], True, (138, 138, 147))
        tela.blit(desc_surf, (card['x'] + 25, card['y'] + 63))
        
        g_idx = card['grid_idx']
        desenhar_ranking_badge(tela, card, g_idx, state['finish_order'])
        
        for row in grids[g_idx]:
            for node in row:
                node.desenhar(tela, card['x'] + ox_grid, card['y'] + oy_grid)
                
        desenhar_painel_metricas(tela, card, g_idx, stats, max_vis, ox_grid, oy_grid, grid_w, grid_h, h_card)

def criar_grid(linhas, colunas, tamanho_no):
    grid = []
    for r in range(linhas):
        grid.append([])
        for c in range(colunas):
            no = No(r, c, tamanho_no, linhas)
            grid[r].append(no)
    return grid

def limpar_caminhos_busca(grids):
    for g in grids:
        for r in range(len(g)):
            for c in range(len(g[r])):
                node = g[r][c]
                if node.cor in (COR_EXPANSAO_FECHADO, COR_EXPANSAO_ABERTO, COR_CAMINHO):
                    node.resetar()

def reiniciar_status(stats):
    for i in range(4):
        stats[i]['visitados'] = 0
        stats[i]['caminho'] = 0
        stats[i]['passos'] = 0
        stats[i]['status'] = 'Aguardando'

def limpar_tudo(grids, state, stats, linhas, colunas):
    state['inicio_pos'] = None
    state['alvo_pos'] = None
    state['running'] = False
    state['search_finished'] = False
    state['finish_order'] = []
    reiniciar_status(stats)
    for i in range(4):
        for r in range(linhas):
            for c in range(colunas):
                grids[i][r][c].resetar()

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

def gerar_labirinto_dfs(grids, state, linhas, colunas):
    start_pos, target_pos = escolher_inicio_fim_distantes(linhas, colunas)
    state['inicio_pos'] = start_pos
    state['alvo_pos'] = target_pos
    state['search_finished'] = False
    state['finish_order'] = []
    
    master = grids[0]
    for r in range(linhas):
        for c in range(colunas):
            master[r][c].tornar_parede()
            
    visitados = set()
    pilha = []
    
    r_ini, c_ini = start_pos
    master[r_ini][c_ini].resetar()
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
            master[r + dr // 2][c + dc // 2].resetar()
            master[nr][nc].resetar()
            visitados.add((nr, nc))
            pilha.append((nr, nc))
        else:
            pilha.pop()
            
    master[start_pos[0]][start_pos[1]].tornar_inicio()
    master[target_pos[0]][target_pos[1]].tornar_alvo()
    sincronizar_grids(grids, 0)

def gerar_labirinto_prim(grids, state, linhas, colunas):
    start_pos, target_pos = escolher_inicio_fim_distantes(linhas, colunas)
    state['inicio_pos'] = start_pos
    state['alvo_pos'] = target_pos
    state['search_finished'] = False
    state['finish_order'] = []
    
    master = grids[0]
    for r in range(linhas):
        for c in range(colunas):
            master[r][c].tornar_parede()
            
    opcoes = [(r, c) for r in range(1, linhas-1, 2) for c in range(1, colunas-1, 2)]
    r_ini, c_ini = random.choice(opcoes)
    master[r_ini][c_ini].resetar()
    
    walls = []
    for dr, dc in [(-2, 0), (2, 0), (0, -2), (0, 2)]:
        nr, nc = r_ini + dr, c_ini + dc
        if 0 < nr < linhas - 1 and 0 < nc < colunas - 1:
            walls.append((r_ini + dr//2, c_ini + dc//2, nr, nc))
            
    while walls:
        idx = random.randint(0, len(walls) - 1)
        wr, wc, nr, nc = walls.pop(idx)
        
        if master[nr][nc].is_parede():
            master[wr][wc].resetar()
            master[nr][nc].resetar()
            
            for dr, dc in [(-2, 0), (2, 0), (0, -2), (0, 2)]:
                nnr, nnc = nr + dr, nc + dc
                if 0 < nnr < linhas - 1 and 0 < nnc < colunas - 1:
                    if master[nnr][nnc].is_parede():
                        walls.append((nr + dr//2, nc + dc//2, nnr, nnc))
                        
    master[start_pos[0]][start_pos[1]].tornar_inicio()
    master[target_pos[0]][target_pos[1]].tornar_alvo()
    sincronizar_grids(grids, 0)

def gerar_obstaculos_organicos(grids, state, linhas, colunas):
    start_pos, target_pos = escolher_inicio_fim_distantes(linhas, colunas)
    state['inicio_pos'] = start_pos
    state['alvo_pos'] = target_pos
    state['search_finished'] = False
    state['finish_order'] = []
    
    master = grids[0]
    for r in range(linhas):
        for c in range(colunas):
            master[r][c].resetar()
            
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
                master[nr][nc].tornar_parede()
                
    for r in range(1, linhas - 1):
        for c in range(1, colunas - 1):
            if not master[r][c].is_parede() and random.random() < 0.08:
                master[r][c].tornar_parede()
                
    master[start_pos[0]][start_pos[1]].tornar_inicio()
    master[target_pos[0]][target_pos[1]].tornar_alvo()
    sincronizar_grids(grids, 0)

def sincronizar_grids(grids, master_idx=0):
    master = grids[master_idx]
    for i, g in enumerate(grids):
        if i == master_idx:
            continue
        for r in range(len(master)):
            for c in range(len(master[r])):
                g[r][c].cor = master[r][c].cor