import pygame
import sys
import math
from typing import List, Tuple, Optional, Dict

# Inicializar pygame
pygame.init()

# Nueva configuración de colores con tema oscuro
BACKGROUND = (30, 30, 30)        # Fondo oscuro
BOARD_BG = (50, 50, 50)          # Gris oscuro para el tablero
GRID_COLOR = (200, 200, 200)     # Gris claro para las líneas
HUMAN_COLOR = (255, 60, 60)      # Rojo brillante para el jugador humano
AI_COLOR = (50, 150, 255)        # Azul brillante para la IA
TREE_BG = (30, 30, 50)           # Azul oscuro para fondo del árbol
NODE_BORDER = (255, 255, 255)    # Blanco para bordes de nodos
TERMINAL_WIN = (60, 255, 60)     # Verde brillante para victorias
TERMINAL_LOSS = (255, 80, 80)    # Rojo brillante para derrotas
TERMINAL_DRAW = (255, 255, 100)  # Amarillo brillante para empates
MAX_NODE = (0, 200, 255)         # Azul para nodos maximizadores
MIN_NODE = (255, 100, 100)       # Rojo suave para nodos minimizadores
TEXT_COLOR = (230, 230, 230)     # Gris claro para texto
INFO_PANEL_COLOR = (30, 30, 50)  # Azul oscuro para panel informativo

# Colores de los bordes y detalles adicionales
LINE_HIGHLIGHT = (100, 100, 255) # Azul claro para resaltar las líneas
NODE_SHADOW_COLOR = (0, 0, 0)    # Sombra para los nodos en el árbol
NODE_BORDER_HIGHLIGHT = (255, 215, 0)  # Resaltado de bordes en nodos al pasar el ratón

# Configuración de pantalla (ajustada para mayor tamaño visual)
BOARD_WIDTH = 300
TREE_WIDTH = 800
HEIGHT = 750
LINE_WIDTH = 3
BOARD_ROWS = 3
BOARD_COLS = 3
SQUARE_SIZE = BOARD_WIDTH // BOARD_COLS
CIRCLE_RADIUS = SQUARE_SIZE // 3
NODE_RADIUS = 15

# Mejorar la apariencia de la ventana
screen = pygame.display.set_mode((BOARD_WIDTH + TREE_WIDTH, HEIGHT))
pygame.display.set_caption("3 en Raya con Árbol Minimax")
font = pygame.font.SysFont('Arial', 18, bold=True)
small_font = pygame.font.SysFont('Arial', 14)
tiny_font = pygame.font.SysFont('Arial', 12)

# Tablero
board = [[None for _ in range(BOARD_COLS)] for _ in range(BOARD_ROWS)]

# Jugadores
HUMAN = "X"  # Minimizador
AI = "O"     # Maximizador

# Valores para Minimax estándar
WIN_VALUE = 1     # Victoria para el maximizador (IA)
LOSE_VALUE = -1   # Victoria para el minimizador (Humano)
DRAW_VALUE = 0    # Empate

# Variables para visualización del árbol
tree_nodes = []
tree_edges = []
current_evaluation = ""

# Diccionario para evitar estados duplicados
state_cache = {}

def board_to_tuple(board_state):
    """Convierte el estado del tablero a un formato hasheable (tupla de tuplas)"""
    return tuple(tuple(row) for row in board_state)

class TreeNode:
    def __init__(self, board_state, value, depth, is_maximizing, move=None):
        self.board_state = [row[:] for row in board_state]  # Copia profunda del tablero
        self.value = value
        self.depth = depth
        self.is_maximizing = is_maximizing
        self.move = move  # Último movimiento que llevó a este estado (fila, columna)
        self.children = []
        self.pos = (0, 0)  # Posición en pantalla
        self.id = len(tree_nodes)
        # Contador de victorias/derrotas/empates para este nodo
        self.wins = 0      # Victorias para IA
        self.losses = 0    # Victorias para Humano
        self.draws = 0     # Empates
        # Estado terminal
        self.is_terminal = False
        self.terminal_type = None  # "win", "loss", "draw"
        tree_nodes.append(self)

    def add_child(self, child):
        self.children.append(child)
        tree_edges.append((self.id, child.id))
        
    def analyze_terminal_states(self):
        """Analiza estados terminales en subárboles"""
        if not self.children:
            winner = check_winner(self.board_state)
            if winner == AI:
                self.is_terminal = True
                self.terminal_type = "win"
                return 1, 0, 0  # win, loss, draw
            elif winner == HUMAN:
                self.is_terminal = True
                self.terminal_type = "loss"
                return 0, 1, 0
            elif is_full(self.board_state):
                self.is_terminal = True
                self.terminal_type = "draw"
                return 0, 0, 1
            return 0, 0, 0
        
        total_wins, total_losses, total_draws = 0, 0, 0
        for child in self.children:
            w, l, d = child.analyze_terminal_states()
            total_wins += w
            total_losses += l
            total_draws += d
            
        self.wins = total_wins
        self.losses = total_losses
        self.draws = total_draws
        return total_wins, total_losses, total_draws

# Mejoras en las funciones de dibujo
def draw_board():
    """Dibuja el tablero y las fichas con mejor estética"""
    # Fondo del tablero
    pygame.draw.rect(screen, BOARD_BG, (0, 0, BOARD_WIDTH, HEIGHT))
    
    # Borde del tablero
    pygame.draw.rect(screen, GRID_COLOR, (0, 0, BOARD_WIDTH, BOARD_WIDTH), 6)
    
    # Dibujar líneas del tablero con un suave resalte
    for row in range(1, BOARD_ROWS):
        pygame.draw.line(screen, LINE_HIGHLIGHT, (0, row * SQUARE_SIZE), (BOARD_WIDTH, row * SQUARE_SIZE), LINE_WIDTH)
    for col in range(1, BOARD_COLS):
        pygame.draw.line(screen, LINE_HIGHLIGHT, (col * SQUARE_SIZE, 0), (col * SQUARE_SIZE, BOARD_WIDTH), LINE_WIDTH)
    
    # Dibujar fichas con efectos mejorados
    for row in range(BOARD_ROWS):
        for col in range(BOARD_COLS):
            if board[row][col] == HUMAN:
                # Dibujar X con mejor aspecto
                center_x = col * SQUARE_SIZE + SQUARE_SIZE // 2
                center_y = row * SQUARE_SIZE + SQUARE_SIZE // 2
                offset = SQUARE_SIZE // 3
                
                # Línea principal
                pygame.draw.line(screen, HUMAN_COLOR,
                               (center_x - offset, center_y - offset),
                               (center_x + offset, center_y + offset), 
                               LINE_WIDTH + 2)
                # Línea secundaria
                pygame.draw.line(screen, HUMAN_COLOR,
                               (center_x + offset, center_y - offset),
                               (center_x - offset, center_y + offset), 
                               LINE_WIDTH + 2)
                
            elif board[row][col] == AI:
                # Dibujar O con mejor aspecto
                center_x = col * SQUARE_SIZE + SQUARE_SIZE // 2
                center_y = row * SQUARE_SIZE + SQUARE_SIZE // 2
                
                # Círculo exterior con sombra sutil
                pygame.draw.circle(screen, AI_COLOR,
                                  (center_x, center_y),
                                  CIRCLE_RADIUS + 2, 0)
                
                # Círculo interior (para efecto de anillo)
                pygame.draw.circle(screen, BOARD_BG,
                                  (center_x, center_y),
                                  CIRCLE_RADIUS - LINE_WIDTH + 1, 0)
    
    # Panel de información mejorado con colores suaves
    info_panel = pygame.Rect(10, BOARD_WIDTH + 10, BOARD_WIDTH - 20, HEIGHT - BOARD_WIDTH - 20)
    pygame.draw.rect(screen, INFO_PANEL_COLOR, info_panel, border_radius=10)
    pygame.draw.rect(screen, (200, 210, 220), info_panel, 2, border_radius=10)
    
    # Mostrar estado del juego con texto mejorado
    status = check_winner(board)
    if status == HUMAN:
        text = font.render("¡Ganaste!", True, HUMAN_COLOR)
    elif status == AI:
        text = font.render("Gana la IA", True, AI_COLOR)
    elif is_full(board):
        text = font.render("¡Empate!", True, TEXT_COLOR)
    else:
        if is_human_turn:
            text = font.render("Tu turno (X)", True, HUMAN_COLOR)
        else:
            text = font.render("Turno de la IA (O)", True, AI_COLOR)
    
    screen.blit(text, (info_panel.centerx - text.get_width() // 2, info_panel.y + 15))
    
    # Instrucciones en el panel
    instructions = [
        "R: Reiniciar juego",
        "A: Analizar árbol",
        "M: Mostrar árbol completo"
    ]
    
    for i, instruction in enumerate(instructions):
        text = small_font.render(instruction, True, TEXT_COLOR)
        screen.blit(text, (info_panel.x + 20, info_panel.y + 50 + i * 25))
    
    # Explicación de valores
    explanation = [
        "Valores de nodos:",
        " 1: Victoria para la IA (O)",
        " 0: Empate",
        "-1: Victoria para Humano (X)"
    ]
    
    for i, line in enumerate(explanation):
        text = small_font.render(line, True, TEXT_COLOR)
        screen.blit(text, (info_panel.x + 20, info_panel.y + 150 + i * 25))

def draw_tree():
    """Dibuja el árbol de decisión Minimax con más estética y claridad"""
    # Fondo del área del árbol
    pygame.draw.rect(screen, TREE_BG, (BOARD_WIDTH, 0, TREE_WIDTH, HEIGHT))
    
    # Borde vertical para separar tablero y árbol
    pygame.draw.line(screen, (180, 190, 200), (BOARD_WIDTH, 0), (BOARD_WIDTH, HEIGHT), 3)
    
    # Zona de visualización
    tree_rect = pygame.Rect(BOARD_WIDTH, 0, TREE_WIDTH, HEIGHT)
    
    # Dibujar conexiones primero (para que queden detrás de los nodos)
    for edge in tree_edges:
        if edge[0] < len(tree_nodes) and edge[1] < len(tree_nodes):
            start_node = tree_nodes[edge[0]]
            end_node = tree_nodes[edge[1]]
            
            # Dibujar línea de conexión con un color suave
            pygame.draw.line(screen, NODE_SHADOW_COLOR, 
                           start_node.pos, end_node.pos, 2)
    
    # Dibujar nodos con sombras y bordes resaltados
    for node in tree_nodes:
        # Color del nodo según si es maximizador/minimizador o terminal
        if node.is_terminal:
            if node.terminal_type == "win":
                color = TERMINAL_WIN
            elif node.terminal_type == "loss":
                color = TERMINAL_LOSS
            else:  # draw
                color = TERMINAL_DRAW
        else:
            color = MAX_NODE if node.is_maximizing else MIN_NODE
        
        # Sombra sutil del nodo
        pygame.draw.circle(screen, NODE_SHADOW_COLOR, (node.pos[0] + 2, node.pos[1] + 2), NODE_RADIUS)
        
        # Dibujar el nodo con borde resaltado
        pygame.draw.circle(screen, color, node.pos, NODE_RADIUS)
        pygame.draw.circle(screen, NODE_BORDER, node.pos, NODE_RADIUS, 1)
        
        # Mostrar valor del nodo
        value_text = small_font.render(str(node.value), True, TEXT_COLOR)
        screen.blit(value_text, (node.pos[0] - value_text.get_width() // 2, 
                                node.pos[1] - value_text.get_height() // 2))
        
        # Mostrar estadísticas del subárbol
        stats_text = tiny_font.render(f"W:{node.wins} L:{node.losses} D:{node.draws}", True, TEXT_COLOR)
        screen.blit(stats_text, (node.pos[0] - stats_text.get_width() // 2, 
                                node.pos[1] - 25))

        # Dibujar un mini tablero en cada nodo
        mini_board_size = 30
        mini_square = mini_board_size / 3
        mini_board_pos = (node.pos[0] - mini_board_size / 2, node.pos[1] + 30)
        
        # Fondo del mini tablero
        pygame.draw.rect(screen, BOARD_BG, 
                        (mini_board_pos[0], mini_board_pos[1], mini_board_size, mini_board_size))
        pygame.draw.rect(screen, NODE_BORDER, 
                        (mini_board_pos[0], mini_board_pos[1], mini_board_size, mini_board_size), 1)
        
        # Líneas del mini tablero
        for i in range(1, 3):
            pygame.draw.line(screen, NODE_BORDER, 
                            (mini_board_pos[0], mini_board_pos[1] + i * mini_square),
                            (mini_board_pos[0] + mini_board_size, mini_board_pos[1] + i * mini_square), 1)
            pygame.draw.line(screen, NODE_BORDER, 
                            (mini_board_pos[0] + i * mini_square, mini_board_pos[1]),
                            (mini_board_pos[0] + i * mini_square, mini_board_pos[1] + mini_board_size), 1)
        
        # Dibujar fichas en el mini tablero
        for r in range(3):
            for c in range(3):
                center_x = mini_board_pos[0] + c * mini_square + mini_square/2
                center_y = mini_board_pos[1] + r * mini_square + mini_square/2
                
                if node.board_state[r][c] == HUMAN:
                    # X en mini tablero
                    offset = mini_square * 0.3
                    pygame.draw.line(screen, HUMAN_COLOR,
                                  (center_x - offset, center_y - offset),
                                  (center_x + offset, center_y + offset), 1)
                    pygame.draw.line(screen, HUMAN_COLOR,
                                  (center_x + offset, center_y - offset),
                                  (center_x - offset, center_y + offset), 1)
                elif node.board_state[r][c] == AI:
                    # O en mini tablero
                    pygame.draw.circle(screen, AI_COLOR,
                                     (center_x, center_y),
                                     mini_square/2 - 2, 1)

# Continuar con las demás funciones y lógica de juego...

def check_winner(b: List[List[Optional[str]]]) -> Optional[str]:
    """Comprueba si hay un ganador"""
    # Filas
    for row in b:
        if row[0] == row[1] == row[2] and row[0] is not None:
            return row[0]
    
    # Columnas
    for col in range(3):
        if b[0][col] == b[1][col] == b[2][col] and b[0][col] is not None:
            return b[0][col]
    
    # Diagonales
    if b[0][0] == b[1][1] == b[2][2] and b[0][0] is not None:
        return b[0][0]
    if b[0][2] == b[1][1] == b[2][0] and b[0][2] is not None:
        return b[0][2]
    
    return None

def is_full(b: List[List[Optional[str]]]) -> bool:
    """Comprueba si el tablero está lleno"""
    return all(cell is not None for row in b for cell in row)

def get_available_moves(b: List[List[Optional[str]]]) -> List[Tuple[int, int]]:
    """Devuelve una lista de casillas vacías en el tablero"""
    moves = []
    for row in range(BOARD_ROWS):
        for col in range(BOARD_COLS):
            if b[row][col] is None:
                moves.append((row, col))
    return moves

def minimax(b: List[List[Optional[str]]], depth: int, is_maximizing: bool) -> float:
    """
    Implementación del algoritmo Minimax sin poda alfa-beta
    """
    # Comprobar estado terminal
    winner = check_winner(b)
    if winner == AI:  # Victoria para IA (Maximizador)
        return WIN_VALUE
    elif winner == HUMAN:  # Victoria para Humano (Minimizador)
        return LOSE_VALUE
    elif is_full(b):  # Empate
        return DRAW_VALUE
    
    # Ordenar los movimientos
    available_moves = get_available_moves(b)
    
    if is_maximizing:  # Turno de la IA (Maximizador)
        max_eval = -math.inf
        for row, col in available_moves:
            b[row][col] = AI
            eval_value = minimax(b, depth + 1, False)
            b[row][col] = None
            max_eval = max(max_eval, eval_value)
        return max_eval
    
    else:  # Turno del Humano (Minimizador)
        min_eval = math.inf
        for row, col in available_moves:
            b[row][col] = HUMAN
            eval_value = minimax(b, depth + 1, True)
            b[row][col] = None
            min_eval = min(min_eval, eval_value)
        return min_eval

def best_move() -> Tuple[int, int]:
    """Encuentra el mejor movimiento para la IA usando Minimax y construye el árbol"""
    global tree_nodes, tree_edges, current_evaluation, state_cache
    
    # Limpiar el árbol anterior y caché de estados
    tree_nodes = []
    tree_edges = []
    state_cache = {}
    
    best_score = -math.inf
    move = (-1, -1)
    
    # Nodo raíz (turno de la IA - Maximizador)
    root_node = TreeNode(board, 0, 0, True)
    
    # Evaluar cada movimiento posible para la IA
    available_moves = get_available_moves(board)
    
    for row, col in available_moves:
        # Simular movimiento
        board[row][col] = AI
        
        # Crear nodo para este movimiento
        move_node = TreeNode(board, 0, 1, False, (row, col))
        root_node.add_child(move_node)
        
        # Evaluar movimiento desde perspectiva del minimizador (Humano)
        score = minimax(board, 1, False)
        
        # Deshacer movimiento
        board[row][col] = None
        
        # Actualizar mejor movimiento
        if score > best_score:
            best_score = score
            move = (row, col)
        
        # Actualizar valor del nodo
        move_node.value = score
        
        # Mensaje de evaluación para visualización
        current_evaluation = f"Evaluando ({row},{col}): {score}"
        position_tree()
        draw_all()
        pygame.display.flip()
        pygame.time.delay(300)  # Pausa para visualización
    
    # Analizar estadísticas de estados terminales
    root_node.analyze_terminal_states()
    
    # Actualizar evaluación con interpretación
    interpretation = ""
    if best_score == WIN_VALUE:
        interpretation = "Victoria garantizada"
    elif best_score == LOSE_VALUE:
        interpretation = "Pérdida inevitable"
    elif best_score == DRAW_VALUE:
        interpretation = "Mejor resultado: empate"
    
    current_evaluation = f"Mejor movimiento: {move} con valor {best_score} ({interpretation})"
    return move

def position_tree():
    """Calcula las posiciones de los nodos para visualización"""
    if not tree_nodes:
        return
    
    # Organizar nodos por niveles
    levels = {}
    for node in tree_nodes:
        if node.depth not in levels:
            levels[node.depth] = []
        levels[node.depth].append(node)
    
    max_depth = max(levels.keys()) if levels else 0
    
    # Posicionar nodos
    for depth, nodes in levels.items():
        # Calcular posición vertical según profundidad
        y_pos = 50 + depth * 100
        
        # Calcular espaciado horizontal
        x_spacing = TREE_WIDTH // (len(nodes) + 1)
        
        # Asignar posición a cada nodo
        for i, node in enumerate(nodes):
            x_pos = BOARD_WIDTH + x_spacing * (i + 1)
            node.pos = (x_pos, y_pos)

def draw_all():
    """Dibuja todos los elementos"""
    # Limpiar pantalla con color de fondo
    screen.fill(BACKGROUND)
    
    # Dibujar componentes
    draw_board()
    draw_tree()

def reset_game():
    """Reinicia el juego"""
    global board, is_human_turn, game_over, tree_nodes, tree_edges, current_evaluation, state_cache
    board = [[None for _ in range(BOARD_COLS)] for _ in range(BOARD_ROWS)]
    is_human_turn = True
    game_over = False
    tree_nodes = []
    tree_edges = []
    current_evaluation = ""
    state_cache = {}

def analyze_tree():
    """Analiza el árbol para actualizar estadísticas"""
    if tree_nodes:
        # Encontrar nodo raíz (profundidad 0)
        for node in tree_nodes:
            if node.depth == 0:
                node.analyze_terminal_states()
                break

def handle_keyboard():
    """Maneja la entrada del teclado"""
    keys = pygame.key.get_pressed()
    
    # Analizar árbol (para actualizar estadísticas)
    if keys[pygame.K_a]:
        analyze_tree()
    
    # Mostrar árbol completo con la tecla M
    if keys[pygame.K_m]:
        draw_tree()

# Variables de estado del juego
is_human_turn = True  # Comienza el humano
game_over = False

# Juego principal
def main():
    global is_human_turn, game_over
    
    clock = pygame.time.Clock()
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            # Reiniciar juego al presionar 'R'
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                reset_game()
            
            # Manejar clic del mouse para el turno del humano
            if not game_over and is_human_turn and event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                # Verificar que el clic fue en el tablero
                if x < BOARD_WIDTH and y < BOARD_WIDTH:
                    row = y // SQUARE_SIZE
                    col = x // SQUARE_SIZE
                    
                    # Verificar casilla vacía
                    if board[row][col] is None:
                        # Realizar movimiento humano
                        board[row][col] = HUMAN
                        is_human_turn = False
                        
                        # Verificar fin del juego
                        if check_game_over():
                            game_over = True
        
        # Manejar teclado
        handle_keyboard()
        
        # Turno de la IA
        if not game_over and not is_human_turn:
            pygame.time.delay(500)  # Pequeña pausa
            
            # Obtener mejor movimiento
            row, col = best_move()
            board[row][col] = AI
            
            is_human_turn = True
            
            # Verificar fin del juego
            if check_game_over():
                game_over = True
        
        # Actualizar pantalla
        draw_all()
        pygame.display.update()
        clock.tick(30)  # Limitar a 30 FPS

def check_game_over() -> bool:
    """Comprueba si el juego ha terminado"""
    winner = check_winner(board)
    if winner or is_full(board):
        return True
    return False

if __name__ == "__main__":
    main()
