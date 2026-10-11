from collections import deque

from agente import Agente
from logica import LogicaAgente
from mundo import DIRECCIONES, OFSETS_DIRECCION


def giros_hacia(actual, objetivo):
    """Giros de 90° que hay que hacer para pasar de una dirección a otra."""
    pasos = (DIRECCIONES.index(objetivo) - DIRECCIONES.index(actual)) % 4
    if pasos == 3:
        return ["girar_izquierda"]
    return ["girar_derecha"] * pasos


def direccion_hacia(origen, destino):
    delta = (destino[0] - origen[0], destino[1] - origen[1])
    for direccion, ofs in OFSETS_DIRECCION.items():
        if ofs == delta:
            return direccion
    return None


class ControladorBot:
    """Puente entre el agente lógico (agente.py + logica.py) y el mundo.

    Cada llamado devuelve UNA acción del mundo ("girar_derecha", "avanzar",
    "agarrar", "salir"...) para que la interfaz la ejecute y se vea paso a paso.
    """

    def __init__(self, tamano):
        self.agente = Agente()
        self.logica = LogicaAgente(self.agente, tamano)
        self.cola = deque()
        self.por_percibir = True
        self.sin_solucion = False

    def siguiente_accion(self, mundo, percepcion):
        if self.cola:
            return self.cola.popleft()

        # Recién llegó a una casilla nueva: la lógica actualiza lo que sabe
        if self.por_percibir:
            self.por_percibir = False
            self.agente.registrar_visita((mundo.x, mundo.y))
            resultado = self.logica.procesar_percepcion({
                "brisa": percepcion.brisa,
                "hedor": percepcion.hedor,
                "resplandor": percepcion.resplandor,
            })
            if resultado == "AGARRAR_ORO":
                return "agarrar"

        decision = self.logica.decidir_accion()

        if decision == "SALIR":
            return "salir"

        if decision == "REGRESAR":
            destino = self.agente.regresar_por_historial()
        elif isinstance(decision, tuple) and decision[0] == "MOVER":
            destino = decision[1]
            self.por_percibir = True
        else:
            destino = None

        direccion = direccion_hacia((mundo.x, mundo.y), destino) if destino else None
        if direccion is None:
            self.sin_solucion = True
            return None

        self.cola.extend(giros_hacia(mundo.direccion, direccion))
        self.cola.append("avanzar")
        return self.cola.popleft()
