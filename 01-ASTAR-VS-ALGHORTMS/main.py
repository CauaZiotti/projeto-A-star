import pygame
from config import *
from gui import *
from algorithms import AStar, Dijkstra, BFS, DFS

def acionar_simulacao(grids, state, stats, linhas, colunas):
    limpar_caminhos_busca(grids)
    state['finish_order'] = []
    for i in range(4):
        stats[i] = {'visitados': 0, 'caminho': 0, 'passos': 0, 'status': 'Simulando...'}
    for g in grids:
        for row in g:
            for node in row:
                node.atualizar_vizinhos(g, linhas, colunas)
                
    ip, ap = state['inicio_pos'], state['alvo_pos']
    for g in grids:
        g[ip[0]][ip[1]].tornar_inicio()
        g[ap[0]][ap[1]].tornar_alvo()
        
    state['generators'] = [
        AStar(grids[0], grids[0][ip[0]][ip[1]], grids[0][ap[0]][ap[1]]),
        Dijkstra(grids[1], grids[1][ip[0]][ip[1]], grids[1][ap[0]][ap[1]]),
        BFS(grids[2], grids[2][ip[0]][ip[1]], grids[2][ap[0]][ap[1]]),
        DFS(grids[3], grids[3][ip[0]][ip[1]], grids[3][ap[0]][ap[1]])
    ]
    state['gen_finished'] = [False] * 4
    state['running'] = True
    state['search_finished'] = False

def gerenciar_eventos(grids, state, stats, linhas, colunas):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False
            
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return False
                
            if not state['running']:
                if event.key == pygame.K_SPACE and state['inicio_pos'] and state['alvo_pos']:
                    acionar_simulacao(grids, state, stats, linhas, colunas)
                elif event.key == pygame.K_c:
                    limpar_tudo(grids, state, stats, linhas, colunas)
                elif event.key == pygame.K_g:
                    gerar_labirinto_dfs(grids, state, linhas, colunas)
                    reiniciar_status(stats)
                elif event.key == pygame.K_p:
                    gerar_labirinto_prim(grids, state, linhas, colunas)
                    reiniciar_status(stats)
                elif event.key == pygame.K_r:
                    gerar_obstaculos_organicos(grids, state, linhas, colunas)
                    reiniciar_status(stats)

    return True

def atualizar_passos_simulacao(state, stats, steps_per_frame):
    if state['running']:
        for _ in range(steps_per_frame):
            all_done = True
            for i in range(4):
                if not state['gen_finished'][i]:
                    all_done = False
                    try:
                        state['generators'][i].step()
                        stats[i]['passos'] += 1
                    except StopIteration:
                        state['gen_finished'][i] = True
                        if i not in state['finish_order']:
                            state['finish_order'].append(i)
            if all_done:
                state['running'] = False
                state['search_finished'] = True
                break

def atualizar_estatisticas(grids, stats, state):
    for i in range(4):
        visitados = sum(1 for row in grids[i] for node in row if node.is_fechado() or node.is_aberto())
        caminho = sum(1 for row in grids[i] for node in row if node.cor == COR_CAMINHO)
        stats[i]['visitados'] = visitados
        stats[i]['caminho'] = caminho
        
        if not state['inicio_pos'] or not state['alvo_pos']:
            stats[i]['status'] = "Configurando..."
        elif state['running']:
            if state['gen_finished'][i]:
                stats[i]['status'] = "Concluído" if caminho > 0 else "Sem Caminho"
            else:
                stats[i]['status'] = "Simulando..."
        elif state['search_finished']:
            stats[i]['status'] = "Concluído" if caminho > 0 else "Sem Caminho"
        else:
            stats[i]['status'] = "Pronto"

def main():
    infoObject = pygame.display.Info()
    LARGURA_TELA = infoObject.current_w
    ALTURA_TELA = infoObject.current_h
    
    TELA = pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA), pygame.NOFRAME)
    pygame.display.set_caption("Comparador de Algoritmos de Busca: A*, Dijkstra, BFS, DFS")
    
    W_CARD = (LARGURA_TELA - 170) // 4
    H_CARD = ALTURA_TELA - 150
    
    COLUNAS = (W_CARD - 40) // TAMANHO_NO
    if COLUNAS % 2 == 0: COLUNAS -= 1
    
    LINHAS = (H_CARD - 325) // TAMANHO_NO
    if LINHAS % 2 == 0: LINHAS -= 1
    
    GRID_W = COLUNAS * TAMANHO_NO
    GRID_H = LINHAS * TAMANHO_NO
    
    OX_GRID = (W_CARD - GRID_W) // 2
    OY_GRID = 85
    
    grids = [criar_grid(LINHAS, COLUNAS, TAMANHO_NO) for _ in range(4)]
    
    cards = [
        {
            'x': 40 + i * (W_CARD + 30), 'y': 110, 'width': W_CARD, 'height': H_CARD,
            'titulo': titulo, 'formula': formula, 'subtitulo': sub, 'grid_idx': i
        } for i, (titulo, formula, sub) in enumerate([
            ("A* (A-Estrela)", "f(n) = g(n) + h(n)", "Heurística h(n) = Manhattan"),
            ("Dijkstra", "f(n) = g(n)", "Busca cega por custo real g(n)"),
            ("BFS (Busca em Largura)", "Fila (FIFO)", "Uniforme por níveis/camadas"),
            ("DFS (Busca em Profundidade)", "Pilha (LIFO)", "Exploração linear profunda")
        ])
    ]
    
    state = {
        'inicio_pos': None,
        'alvo_pos': None,
        'running': False,
        'search_finished': False,
        'finish_order': [],
        'generators': [],
        'gen_finished': [False] * 4
    }
    
    stats = [
        {'visitados': 0, 'caminho': 0, 'passos': 0, 'status': 'Aguardando'} for _ in range(4)
    ]
    
    clock = pygame.time.Clock()
    rodando = True
    
    TELA = pygame.display.get_surface()
    
    # Gera cenário com obstáculos orgânicos por padrão ao iniciar
    gerar_obstaculos_organicos(grids, state, LINHAS, COLUNAS)
    
    while rodando:
        clock.tick(60)
        
        rodando = gerenciar_eventos(grids, state, stats, LINHAS, COLUNAS)
        if not rodando:
            break
            
        atualizar_passos_simulacao(state, stats, STEPS_PER_FRAME)
        
        for g in grids:
            for row in g:
                for node in row:
                    if node.anim_scale < 1.0:
                        node.anim_scale += 0.15
                        if node.anim_scale > 1.0:
                            node.anim_scale = 1.0

        atualizar_estatisticas(grids, stats, state)

        TELA.fill((12, 12, 14))
        desenhar_cabecalho(TELA, LARGURA_TELA, state)
        
        all_visited = [stats[idx]['visitados'] for idx in range(4)]
        max_vis = max(all_visited) if all_visited else 1
        if max_vis == 0:
            max_vis = 1
            
        desenhar_cartoes(TELA, cards, grids, stats, state, OX_GRID, OY_GRID, GRID_W, GRID_H, H_CARD, max_vis)
        pygame.display.update()
        
    pygame.quit()

if __name__ == "__main__":
    main()