# Simulador e Comparador de Algoritmos de Busca (A*)

Este projeto contém ferramentas interativas para a visualização, comparação e estudo passo a passo de algoritmos de busca e de determinação de caminhos (pathfinding). Ele foi desenvolvido para complementar apresentações conceituais e fornecer uma compreensão visual intuitiva do funcionamento interno de cada método.

O repositório é composto por dois módulos principais em Python que utilizam a biblioteca **Pygame** para interfaces em tempo real.

---

## 📂 Estrutura do Projeto

*   **[01-ASTAR-VS-ALGHORTMS](./01-ASTAR-VS-ALGHORTMS)**: Comparador simultâneo lado a lado de quatro algoritmos clássicos de busca em grids com obstáculos.
*   **[02-ASTAR-STEP-BY-STEP](./02-ASTAR-STEP-BY-STEP)**: Simulador detalhado passo a passo da lógica do A*, exibindo a execução linha por linha do pseudo-código e os valores de variáveis em tempo real (como uma ferramenta de depuração visual).
*   **[SLIDES.pdf](./SLIDES.pdf)**: Material de suporte teórico para apresentações sobre os algoritmos.

---

## 🚀 Como Executar

### Pré-requisitos
Certifique-se de ter o Python 3 instalado no seu computador. Além disso, a biblioteca `pygame` é necessária.

### Instalação das dependências
Abra o terminal na pasta raiz do projeto e instale o Pygame:
```bash
pip install pygame
```

### Executando os Aplicativos

1.  **Comparador de Algoritmos (Lado a Lado):**
    ```bash
    python 01-ASTAR-VS-ALGHORTMS/main.py
    ```

2.  **Visualizador Passo a Passo (A* Detalhado):**
    ```bash
    python 02-ASTAR-STEP-BY-STEP/main.py
    ```

---

## 🔍 Detalhes dos Módulos

### 1. Comparador Simultâneo (`01-ASTAR-VS-ALGHORTMS`)
Permite desenhar barreiras personalizadas e observar simultaneamente em 4 grids como cada algoritmo se comporta para encontrar a saída.

**Vídeo de Demonstração:**
<video src=".github/a-star-vs-others-algorithms.mp4" width="100%" controls></video>


*   **Algoritmos Comparados:**
    *   **A* (A-Estrela):** Busca heurística inteligente utilizando `f(n) = g(n) + h(n)` (com distância de Manhattan).
    *   **Dijkstra:** Busca pelo menor caminho baseada apenas no custo acumulado real `g(n)`.
    *   **BFS (Busca em Largura):** Exploração radial e uniforme camada por camada (FIFO).
    *   **DFS (Busca em Profundidade):** Exploração rápida e linear de caminhos profundos (LIFO).
*   **Controles:**
    *   `ESPAÇO`: Inicia/Pausa a simulação simultânea.
    *   `R`: Gera cenário com obstáculos orgânicos aleatórios.
    *   `G`: Gera um labirinto perfeito usando o algoritmo DFS.
    *   `P`: Gera um labirinto perfeito usando o algoritmo de Prim.
    *   `C`: Limpa a grade e as posições de início e destino para desenhar do zero.
    *   `ESC`: Fecha o aplicativo.
*   **Métricas Exibidas:** Número de células visitadas (eficiência), comprimento do caminho final, contagem de passos e classificação de finalização (ranking).

### 2. A* Passo a Passo (`02-ASTAR-STEP-BY-STEP`)
Uma ferramenta educacional avançada que divide o funcionamento do algoritmo A* em instruções de baixo nível.

**Vídeo de Demonstração:**
<video src=".github/a-star-step-by-step.mp4" width="100%" controls></video>


*   **Recursos do Depurador:**
    *   **Pseudo-código Lateral:** A linha atual do pseudo-código sendo executada fica em destaque (amarelo/azul).
    *   **Painel Inspetor de Variáveis:** Mostra o nó atual, o vizinho sob avaliação e os cálculos de custo em tempo real (`g`, `h`, `f`).
    *   **Estrutura de Dados:** Exibe os elementos ativos na fila de prioridades (`open_set`) e as conexões do dicionário de caminhos (`came_from`).
*   **Controles na Interface:**
    *   **Modo Auto / Manual:** Altera a velocidade de avanço das etapas ou permite executar o loop de instrução a instrução de forma manual.
    *   **Controle de Velocidade:** Altera a taxa de atualização (`Muito Lento`, `Lento`, `Médio`, `Rápido`).
    *   **Botão Passo a Passo (ou `ENTER`):** Executa exatamente uma linha lógica do pseudo-código.
    *   **Ferramentas de Grade:** Permite alternar e pintar na grade novos obstáculos (Paredes), pontos de Início ou Alvos.
    *   **Geradores de Cenário:** Criação rápida de labirintos complexos para testar o algoritmo sob estresse.
