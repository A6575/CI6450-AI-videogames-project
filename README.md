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
├── src/                  # Código fuente del juego
│   ├── main.py           # Archivo principal de ejecución
│   └── imports/          # Módulos y clases del juego
│       ├── map/          # Clases relacionadas con el mapa y caminos
│       │   └── path.py   # Clase para la generación y manejo de caminos
│       ├── player/       # Clases relacionadas con el jugador
│       │   └── player.py # Clase para el personaje principal
│       ├── npc/          # Clases relacionadas con los NPCs
│       │   └── npc.py    # Clase para los NPCs
│       ├── moves/        # Clases de algoritmos de movimiento
│       └── gui.py        # Clase para la interfaz gráfica
│
├── assets/               # Recursos del juego (imágenes, sonidos, etc.)
│
├── requirements.txt      # Lista de dependencias de Python
│
└── README.md             # Este archivo
```
