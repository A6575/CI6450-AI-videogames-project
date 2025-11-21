# CI6450-AI-videogames-project

## Descripción del Proyecto
Este proyecto tiene como objetivo desarrollar un videojuego utilizando técnicas de inteligencia artificial, como parte del trabajo práctico de la materia CI6450 - "IA para videojuegos".

## Descripción del Juego
Por definir.

## Cómo Jugar
Actualmente, el juego permite el movimiento del personaje principal utilizando las teclas de dirección del teclado.

## Requisitos

- **Python**: 3.10 o superior
- **Librerías necesarias**:
	- Pygame 2.6.1
	- PyTMX 3.32
	- Shapely 2.1.2

## Entorno virtual

Usar un entorno virtual aisla las dependencias del proyecto. A continuación pasos comunes (suponiendo Python 3.10+).

1. Crear el entorno (desde la raíz del proyecto):
- En macOS / Linux:
```bash
python3 -m venv env
```
- En Windows (PowerShell o CMD):
```powershell
py -m venv env
```

2. Activar el entorno:
- macOS / Linux:
```bash
source env/bin/activate
```
- Windows (PowerShell):
```powershell
env\Scripts\Activate.ps1
```
- Windows (CMD):
```cmd
env\Scripts\activate.bat
```

3. Actualizar pip (opcional):
```bash
py/python3 -m pip install --upgrade pip
```

4. Instalar dependencias del proyecto:
```bash
pip install -r requirements.txt
```

5. Desactivar el entorno cuando termines:
```bash
deactivate
```

6. Eliminar el entorno (si es necesario):
- macOS / Linux:
```bash
rm -rf env
```
- Windows (PowerShell/CMD):
```powershell
rmdir /s env
```

## Estructura del Proyecto

```
CI6450-AI-videogames-project/
│
├── src/                  		  # Código fuente del juego
│   ├── main.py           		  # Archivo principal de ejecución
│   └── imports/          		  # Módulos y clases del juego
│       ├── map/          		  # Clases relacionadas con el mapa y caminos
│       │   ├── path.py   		  # Clase para la generación y manejo de caminos
│		│	└── mapa.py	  		  # Clase para la representación y manejo del mapa
│       ├── player/       		  # Clases relacionadas con el jugador
│       │   └── player.py 		  # Clase para el personaje principal
│		├── objects/      		  # Clases relacionadas con los objetos del juego
│		├── pathfinding/  		  # Función A* para el calculo del camino
│       ├── npc/          		  # Clases relacionadas con los NPCs (Incluye HSM)
│       ├── moves/        		  # Clases de algoritmos de movimiento
│       ├── game.py       		  # Clase para el manejo del juego.
│       ├── nav_mesh.py   		  # Clases relacionadas con la malla de navegación
│       ├── renderer.py   		  # Clases relacionada con el renderizado del juego
│       └── scenario_factory.py   # Clase para seteo de NPC con un único algoritmo de movimiento
│
├── assets/               		  # Recursos del juego (imágenes, sonidos, etc.)
│
├── requirements.txt      		  # Lista de dependencias de Python
│
├── world-representation.png      # Imagen de la representación visual del mundo del juego
│
└── README.md            		  # Este archivo
```
