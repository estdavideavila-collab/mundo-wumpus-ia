import os
import sys

# Aseguramos las rutas de importación
raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(raiz)
sys.path.append(os.path.join(raiz, "src"))

from interfaz import Interfaz

def main():
    print("Iniciando La Caverna del Wumpus...")
    app = Interfaz()
    app.ejecutar()

# IMPORTANTE: Esta línea es la que arranca el juego
if __name__ == "__main__":
    main()