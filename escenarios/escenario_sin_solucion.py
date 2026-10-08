import os
import sys
import random

# Añadimos la carpeta 'src' directamente a las rutas de ejecución
raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(raiz, "src"))

from mundo import MundoWumpus

def crear_escenario_sin_solucion(tamano=4):
    casillas_validas = [(x, y) for x in range(1, tamano + 1) for y in range(1, tamano + 1) if (x, y) not in [(1, 1), (1, 2), (2, 1)]]
    
    pozos_forzados = {(1, 2), (2, 1)}
    pozos_extra = {c for c in casillas_validas if random.random() < 0.15}
    pozos_totales = pozos_forzados.union(pozos_extra)
    
    wumpus_pos = random.choice(casillas_validas)
    oro_pos = random.choice(casillas_validas)
    pozos_totales.discard(oro_pos)
    
    return MundoWumpus(
        tamano=tamano,
        wumpus=wumpus_pos,
        pozos=pozos_totales,
        oro=oro_pos
    )