from collections import deque


class LogicaAgente:
    def __init__(self, agente, tamano=4):
        self.agente = agente
        self.tamano = tamano

    def obtener_vecinos(self, posicion):
        x, y = posicion

        posibles = [
            (x + 1, y),
            (x - 1, y),
            (x, y + 1),
            (x, y - 1)
        ]

        vecinos_validos = []

        for px, py in posibles:
            if 1 <= px <= self.tamano and 1 <= py <= self.tamano:
                vecinos_validos.append((px, py))

        return vecinos_validos

    def procesar_percepcion(self, percepcion):
        posicion_actual = self.agente.posicion
        vecinos = self.obtener_vecinos(posicion_actual)

        hay_brisa = percepcion.get("brisa", False)
        hay_hedor = percepcion.get("hedor", False)
        hay_resplandor = percepcion.get("resplandor", False)

        # Si no hay brisa, los vecinos no tienen pozo
        if not hay_brisa:
            for vecino in vecinos:
                self.agente.marcar_sin_pozo(vecino)

        # Si hay brisa, pueden existir pozos alrededor
        else:
            for vecino in vecinos:
                self.agente.marcar_posible_pozo(vecino)

        # Si no hay hedor, los vecinos no tienen Wumpus
        if not hay_hedor:
            for vecino in vecinos:
                self.agente.marcar_sin_wumpus(vecino)

        # Si hay hedor, el Wumpus puede estar alrededor
        else:
            for vecino in vecinos:
                self.agente.marcar_posible_wumpus(vecino)

        # Si hay resplandor, el oro está en esta casilla
        if hay_resplandor and not self.agente.tiene_oro:
            self.agente.recoger_oro()
            return "AGARRAR_ORO"

        return "CONTINUAR"

    def elegir_siguiente_casilla(self):
        # Busca la casilla segura sin visitar más cercana, caminando solo por lo seguro,
        # y devuelve el primer paso. Si los vecinos no sirven, se devuelve en vez de rendirse.
        inicio = self.agente.posicion
        primer_paso = {inicio: None}
        cola = deque([inicio])

        while cola:
            actual = cola.popleft()

            for vecino in self.obtener_vecinos(actual):
                if vecino in primer_paso or vecino not in self.agente.casillas_seguras:
                    continue

                primer_paso[vecino] = vecino if actual == inicio else primer_paso[actual]

                if vecino not in self.agente.casillas_visitadas:
                    return primer_paso[vecino]

                cola.append(vecino)

        return None

    def decidir_accion(self):
        # Si tiene el oro y ya regresó al inicio, debe salir
        if self.agente.tiene_oro and self.agente.posicion == (1, 1):
            return "SALIR"

        # Si tiene el oro, debe regresar por el camino recorrido
        if self.agente.tiene_oro:
            return "REGRESAR"

        # Si no tiene oro, busca una casilla segura no visitada
        siguiente = self.elegir_siguiente_casilla()

        if siguiente is not None:
            return ("MOVER", siguiente)

        # Si no hay movimiento seguro disponible
        return "SIN_SOLUCION"