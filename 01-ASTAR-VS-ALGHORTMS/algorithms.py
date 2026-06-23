from queue import PriorityQueue
from collections import deque
from config import *

class SearchAlgorithm:
    def __init__(self, grid, inicio, alvo):
        self.grid = grid
        self.inicio = inicio
        self.alvo = alvo
        self.count = 0  # Desempate para nós com o mesmo peso (PriorityQueue)
        self.came_from = {}  # Dicionário para reconstruir o caminho percorrido
        self.generator = self._create_generator()

    def _create_generator(self):
        """Método a ser sobrescrito pelas subclasses."""
        raise NotImplementedError("Subclasses devem implementar o método _create_generator")

    def step(self):
        """Avança um passo na simulação pedindo o próximo estado do generator."""
        return next(self.generator)

    def _reconstruir_caminho(self, current):
        """
        Faz o caminho reverso do nó alvo até o início usando o dicionário came_from,
        pintando os nós de branco para mostrar a rota encontrada.
        """
        curr = current
        while curr in self.came_from:
            curr = self.came_from[curr]
            if curr != self.inicio:
                curr.tornar_caminho()
            yield True  # Pausa a cada nó pintado para o efeito visual da animação do caminho
        self.inicio.tornar_inicio()
        self.alvo.tornar_alvo()

class AStar(SearchAlgorithm):
    """
    ALGORITMO: A* (A-Estrela)
    
    RESUMO:
    O A* é um algoritmo de busca informada e heurística. Ele é considerado um dos 
    melhores para pathfinding porque busca a rota mais curta de forma inteligente.
    Ele evita expandir caminhos que claramente estão indo na direção oposta ao alvo.
    
    FÓRMULA: f(n) = g(n) + h(n)
    - g(n): Custo exato do nó inicial até o nó 'n' (Passos já dados).
    - h(n): Custo estimado (Heurística) do nó 'n' até o alvo. Aqui usamos a 
            Distância de Manhattan: |x1 - x2| + |y1 - y2|.
    - f(n): Custo total estimado. A Fila de Prioridade sempre escolhe o nó com menor f(n).
    """
    def _create_generator(self):
        # open_set é uma Fila de Prioridade (PriorityQueue) que ordena os nós pelo menor f_score
        open_set = PriorityQueue()
        # Adiciona o nó inicial na fila: tupla no formato (f_score, contador_desempate, no_atual)
        open_set.put((0, self.count, self.inicio))
        
        # g_score armazena o custo real (número de passos) desde o início até o nó
        # Inicializamos com infinito para todos os nós (ainda não visitados)
        g_score = {node: float('inf') for row in self.grid for node in row}
        g_score[self.inicio] = 0 # O custo do início para o início é zero passos
        
        # f_score armazena a soma g(n) + h(n)
        f_score = {node: float('inf') for row in self.grid for node in row}
        # A heurística inicial é apenas a distância de Manhattan do início ao fim, pois g(n)=0
        f_score[self.inicio] = abs(self.inicio.row - self.alvo.row) + abs(self.inicio.col - self.alvo.col)
        
        # Set de acesso rápido (hash map) para verificar O(1) se um nó já está aguardando na PriorityQueue
        open_set_hash = {self.inicio}
        
        while not open_set.empty():
            # Extrai o nó mais promissor da fila (o que tem o menor f_score, na posição 2 da tupla)
            current = open_set.get()[2]
            open_set_hash.remove(current)
            
            # CONDIÇÃO DE PARADA: Se o nó mais promissor for o alvo, encerramos a busca e reconstruímos a rota
            if current == self.alvo:
                yield from self._reconstruir_caminho(self.alvo)
                return
                
            # Verifica todos os nós vizinhos válidos (cima, baixo, esquerda, direita) - que não são paredes
            for neighbor in current.vizinhos:
                # O custo g(n) temporário do vizinho é o custo do nó atual + 1 passo
                temp_g_score = g_score[current] + 1
                
                # Se esse novo caminho é mais curto (menor g_score) do que qualquer caminho anterior para este vizinho
                if temp_g_score < g_score[neighbor]:
                    # Registramos de qual nó viemos para podermos desenhar a linha depois
                    self.came_from[neighbor] = current
                    # Atualizamos o custo real até ele
                    g_score[neighbor] = temp_g_score
                    
                    # Calcula o h(n) = Distância de Manhattan (heurística) do vizinho até o alvo final
                    h_score = abs(neighbor.row - self.alvo.row) + abs(neighbor.col - self.alvo.col)
                    # Calcula o f(n) final, que será usado para ranquear ele na fila de prioridade
                    f_score[neighbor] = temp_g_score + h_score
                    
                    # Se o vizinho ainda não estava na fila de espera, nós o adicionamos
                    if neighbor not in open_set_hash:
                        self.count += 1
                        open_set.put((f_score[neighbor], self.count, neighbor))
                        open_set_hash.add(neighbor)
                        
                        # Pinta o vizinho de azul claro, indicando que ele faz parte da "fronteira aberta" de exploração
                        if neighbor != self.alvo:
                            neighbor.tornar_aberto()
                            
            # O nó 'current' já teve todos os seus vizinhos checados. Pinta ele de azul escuro (fechado)
            if current != self.inicio:
                current.tornar_fechado()
                
            # Pausa a execução deste gerador, permitindo que a tela seja atualizada pela main e dando tempo para outros algoritmos executarem 1 frame
            yield False

class Dijkstra(SearchAlgorithm):
    """
    ALGORITMO: Algoritmo de Dijkstra
    
    RESUMO:
    O Dijkstra é um algoritmo de busca cega (não heurístico). Ele garante encontrar
    sempre o caminho mais curto, mas como não possui um "senso de direção" para saber
    onde está o alvo, ele expande uniformemente como uma poça d'água crescendo, o
    que custa muito mais processamento.
    
    FÓRMULA: f(n) = g(n)
    - Diferente do A*, Dijkstra só se importa com o custo exato do caminho percorrido, o g(n).
    - Ele descarta totalmente o h(n), não tentando adivinhar a distância até o fim.
    """
    def _create_generator(self):
        # Usa Fila de Prioridade, mas ordenando apenas pelo g_score (já que não há f_score)
        open_set = PriorityQueue()
        open_set.put((0, self.count, self.inicio))
        
        # Guarda o menor número de passos (custo) conhecido para chegar a cada nó (o g(n))
        g_score = {node: float('inf') for row in self.grid for node in row}
        g_score[self.inicio] = 0
        
        open_set_hash = {self.inicio}
        
        while not open_set.empty():
            # Tira o nó mais "barato" da fila
            current = open_set.get()[2]
            open_set_hash.remove(current)
            
            # Se bateu no alvo, inicia a reconstrução visual do caminho
            if current == self.alvo:
                yield from self._reconstruir_caminho(self.alvo)
                return
                
            # Olha os 4 lados
            for neighbor in current.vizinhos:
                # O novo custo é o custo de onde estou + 1
                temp_g_score = g_score[current] + 1
                
                # Encontrou uma rota mais vantajosa para o vizinho?
                if temp_g_score < g_score[neighbor]:
                    self.came_from[neighbor] = current
                    g_score[neighbor] = temp_g_score
                    
                    # Como ele é vantajoso, colocamos na fila de expansão
                    if neighbor not in open_set_hash:
                        self.count += 1
                        # ATENÇÃO AQUI: Em vez de f_score na fila (como o A* faz), colocamos o próprio g_score.
                        # É isso que diferencia o Dijkstra de um A-Estrela!
                        open_set.put((g_score[neighbor], self.count, neighbor))
                        open_set_hash.add(neighbor)
                        
                        if neighbor != self.alvo:
                            neighbor.tornar_aberto()
                            
            # Fecha (Azul Escuro) o nó exaurido
            if current != self.inicio:
                current.tornar_fechado()
                
            yield False

class BFS(SearchAlgorithm):
    """
    ALGORITMO: BFS (Busca em Largura - Breadth-First Search)
    
    RESUMO:
    Algoritmo sem pesos. Ele explora o labirinto expandindo os nós camada por camada.
    É garantido que encontre o caminho mais curto em grids onde o custo de ir de uma
    célula para outra é sempre igual a 1 (que é o caso do nosso mapa).
    
    ESTRUTURA DE DADOS: FILA (FIFO - First In, First Out)
    - O primeiro nó a entrar na fila de espera será o primeiro a ser explorado.
    - Isso obriga o algoritmo a processar todos os nós de "Distância 1" antes de 
      começar a olhar os de "Distância 2", formando o padrão em anel expansivo.
    """
    def _create_generator(self):
        # 'deque' do Python é uma fila duplamente terminada. Ideal porque fazer um .pop(0) em lista normal é lento
        queue = deque([self.inicio])
        # Precisamos de um Set para impedir de dar voltas em círculos infinitos e reavaliar o mesmo nó
        visited = {self.inicio}
        
        while queue:
            # Puxa o nó da EXTREMA ESQUERDA (o mais velho da fila). Essa é a mágica FIFO do BFS!
            current = queue.popleft()
            
            # Encerra se achou o que procurava
            if current == self.alvo:
                yield from self._reconstruir_caminho(self.alvo)
                return
                
            # Olha todos os vizinhos
            for neighbor in current.vizinhos:
                # O BFS não se importa com custo matemático. Se o vizinho não foi visitado, bora pra lá.
                if neighbor not in visited:
                    # Registra a rota
                    self.came_from[neighbor] = current
                    # Marca como visitado JÁ NA INSERÇÃO para evitar duplicações na fila
                    visited.add(neighbor)
                    
                    # Adiciona no final da fila (EXTREMA DIREITA)
                    queue.append(neighbor)
                    
                    if neighbor != self.alvo:
                        neighbor.tornar_aberto()
                        
            # Fecha a visualização do nó atual
            if current != self.inicio:
                current.tornar_fechado()
                
            yield False

class DFS(SearchAlgorithm):
    """
    ALGORITMO: DFS (Busca em Profundidade - Depth-First Search)
    
    RESUMO:
    Um algoritmo "teimoso" e linear. Ele ignora as camadas e segue um único corredor 
    ininterruptamente até não ter mais para onde ir (um beco sem saída). Só quando
    isso acontece ele dá ré e testa outra ramificação. É muito rápido, mas costuma
    encontrar caminhos extremamente ineficientes (em zigue-zague).
    
    ESTRUTURA DE DADOS: PILHA (LIFO - Last In, First Out)
    - O Último nó a entrar na pilha será o Primeiro a ser verificado.
    - É esse comportamento que faz ele ir o mais "fundo" possível antes de voltar.
    """
    def _create_generator(self):
        # Uma simples lista em Python já se comporta perfeitamente como uma Pilha (Stack)
        stack = [self.inicio]
        visited = {self.inicio}
        
        while stack:
            # Puxa o nó do TOPO DA PILHA (o último que foi inserido). Mágica LIFO!
            current = stack.pop()
            
            # Note que o DFS para na primeira vez que encostar no Alvo, mesmo que haja uma rota direta do lado dele.
            if current == self.alvo:
                yield from self._reconstruir_caminho(self.alvo)
                return
                
            # Verifica vizinhos
            for neighbor in current.vizinhos:
                if neighbor not in visited:
                    self.came_from[neighbor] = current
                    visited.add(neighbor)
                    
                    # Empilha o vizinho. O último a ser empilhado nesse loop 'for'
                    # será o primeiro a ser desempilhado no próximo 'pop()'
                    stack.append(neighbor)
                    
                    if neighbor != self.alvo:
                        neighbor.tornar_aberto()
                        
            # Marcar o nó atual como exaurido
            if current != self.inicio:
                current.tornar_fechado()
                
            yield False