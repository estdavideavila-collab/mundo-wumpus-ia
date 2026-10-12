import os
import sys

# Añadimos la carpeta 'src' directamente a las rutas de ejecución
raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(raiz, "src"))

from mundo import MundoWumpus

# Mapa fijo para el video. El agente siente brisa en (4,2) y hedor en (3,2),
# igual encuentra camino seguro, toma el oro en (2,2) y vuelve a (1,1).
#
#   y=4  .  .  .  .
#   y=3  P  .  W  P
#   y=2  .  O  .  .
#   y=1  A  .  .  .
#       x=1 2  3  4
POZOS = {(1, 3), (4, 3)}
WUMPUS = (3, 3)
ORO = (2, 2)


def crear_escenario_victoria():
    return MundoWumpus(tamano=4, pozos=POZOS, wumpus=WUMPUS, oro=ORO)
