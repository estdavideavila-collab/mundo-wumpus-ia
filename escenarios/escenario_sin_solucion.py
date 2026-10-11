import os
import sys

# Añadimos la carpeta 'src' directamente a las rutas de ejecución
raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(raiz, "src"))

from mundo import MundoWumpus

# Mapa fijo para el video. Hay brisa en (2,1) y en (1,2), entonces (2,2) puede
# ser pozo y no hay como demostrar que alguna casilla nueva es segura.
# Camino físico sí hay (por 2,2), pero el agente no puede saberlo sin arriesgarse.
#
#   y=4  .  .  .  .
#   y=3  P  O  W  .
#   y=2  .  .  .  .
#   y=1  A  .  P  .
#       x=1 2  3  4
POZOS = {(3, 1), (1, 3)}
WUMPUS = (3, 3)
ORO = (2, 3)


def crear_escenario_sin_solucion():
    return MundoWumpus(tamano=4, pozos=POZOS, wumpus=WUMPUS, oro=ORO)
