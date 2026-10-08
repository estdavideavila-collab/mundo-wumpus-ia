import os
import sys
from collections import deque

# Añadimos la carpeta 'src' directamente a las rutas de ejecución
raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(raiz, "src"))

from mundo import MundoWumpus

def crear_escenario_victoria(tamano=4):
    while True:
        mundo = MundoWumpus(tamano=tamano)
        
        cola = deque([(1, 1)])
        visitados = {(1, 1)}
        camino_posible = False
        
        while cola:
            cx, cy = cola.popleft()
            if (cx, cy) == mundo.oro:
                camino_posible = True
                break
                
            for nx, ny in mundo.adyacentes(cx, cy):
                if (nx, ny) not in visitados:
                    if not mundo.hay_pozo(nx, ny) and (nx, ny) != mundo.wumpus:
                        visitados.add((nx, ny))
                        cola.append((nx, ny))
                        
        if camino_posible:
            return mundo