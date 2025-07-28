Tres en Raya con Visualización del Árbol Minimax

Este proyecto implementa un juego de Tres en Raya (Tic-Tac-Toe) con una inteligencia artificial basada en el algoritmo Minimax. Además, incluye una visualización en tiempo real del árbol de decisiones que la IA explora para determinar su movimiento, lo que lo convierte en una herramienta educativa ideal para comprender cómo funciona la toma de decisiones en juegos simples.


Características principales

- Juego funcional de Tres en Raya en un tablero 3x3.
- IA que utiliza el algoritmo Minimax para tomar decisiones.
- Visualización dinámica del árbol de búsqueda Minimax.
- Interfaz gráfica desarrollada con Pygame, con diseño moderno y tema oscuro.
- Panel informativo que muestra el estado del juego y las instrucciones.
- Estadísticas de victorias, derrotas y empates en los subárboles del árbol de decisiones.
- Opciones para reiniciar el juego (tecla R), analizar el árbol (tecla A) y visualizarlo completamente (tecla M).

Controles

- R: Reiniciar el juego.
- A: Analizar y actualizar las estadísticas del árbol.
- M: Mostrar el árbol completo (si está implementado).
- Clic izquierdo: Colocar una ficha (turno del jugador humano).



Descripción: A la izquierda se encuentra el tablero de juego; a la derecha, el árbol de decisiones con nodos coloreados según su tipo (IA, humano o estado terminal).

Tecnologías utilizadas

- Python 3.8 o superior
- Pygame (para la interfaz gráfica)
- Algoritmo Minimax (sin poda alfa-beta)

Instalación

1. Clonar el repositorio:
   git clone https://github.com/tu-usuario/tres-en-raya-minimax-visual.git
   cd tres-en-raya-minimax-visual

2. Instalar las dependencias:
   pip install -r requirements.txt

3. Ejecutar el programa:
   python src/main.py

Estructura del proyecto

tres-en-raya-minimax-visual/
├── src/
│   └── main.py             


Documentación técnica

El archivo docs/algoritmo_minimax.md contiene una explicación detallada del funcionamiento del algoritmo Minimax, su aplicación en este juego, y cómo se construye y visualiza el árbol de decisiones.

Aprendizaje y uso educativo

Este proyecto es útil para estudiantes y desarrolladores que deseen comprender:
- El funcionamiento del algoritmo Minimax.
- La representación de árboles de decisión en juegos.
- Estrategias de búsqueda en espacios de estado.
- Programación orientada a objetos en Python.
- Visualización de estructuras de datos complejas.

