import random

# --- CONFIGURACIÓN DE PUNTOS Y REGLAS ---
PUNTOS_INICIALES = 1000
COSTO_MOVIMIENTO = 1
COSTO_FLECHA = 10
RECOMPENSA_ORO = 1000
PENALIZACION_MUERTE = 1000

NOMBRES_DIRECCION = {
    "N": "Norte",
    "S": "Sur",
    "E": "Este",
    "O": "Oeste"
}

DIRECCIONES = ["N", "E", "S", "O"]
OFSETS_DIRECCION = {
    "N": (0, 1),
    "E": (1, 0),
    "S": (0, -1),
    "O": (-1, 0)
}


class Percepciones:
    def __init__(self, brisa=False, hedor=False, resplandor=False, grito=False, golpe=False):
        self.brisa = brisa
        self.hedor = hedor
        self.resplandor = resplandor
        self.grito = grito
        self.golpe = golpe


class MundoWumpus:
    def __init__(self, tamano=4, puntos_iniciales=PUNTOS_INICIALES, prob_pozo=0.2):
        self.tamano = tamano
        self.puntuacion = puntos_iniciales
        self.terminado = False
        self.victoria = False
        self.causa_fin = ""

        # Posición y estado del agente
        self.x = 1
        self.y = 1
        self.direccion = "E"
        self.tiene_flecha = True
        self.tiene_oro = False

        self.visitadas = {(1, 1)}

        # Generación del mundo (la casilla 1,1 siempre es segura)
        self.pozos = set()
        for x in range(1, self.tamano + 1):
            for y in range(1, self.tamano + 1):
                if (x, y) != (1, 1) and random.random() < prob_pozo:
                    self.pozos.add((x, y))

        # Posición del Wumpus
        todas_casillas = [(x, y) for x in range(1, self.tamano + 1) for y in range(1, self.tamano + 1) if (x, y) != (1, 1)]
        self.wumpus = random.choice(todas_casillas)
        self.wumpus_vivo = True

        # Posición del Oro
        self.pos_oro = random.choice(todas_casillas)

        # Eventos efímeros
        self.ultimo_grito = False
        self.ultimo_golpe = False

    def hay_oro(self, x, y):
        return self.pos_oro == (x, y) and not self.tiene_oro

    def hay_pozo(self, x, y):
        return (x, y) in self.pozos

    def _obtener_adyacentes(self, x, y):
        """Retorna únicamente las 4 casillas ortogonales adyacentes (Norte, Sur, Este, Oeste)."""
        adyacentes = []
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            if 1 <= nx <= self.tamano and 1 <= ny <= self.tamano:
                adyacentes.append((nx, ny))
        return adyacentes

    def percepciones(self):
        # Solamente se evalúan las 4 casillas ortogonales adyacentes
        ady = self._obtener_adyacentes(self.x, self.y)

        brisa = any(pos in self.pozos for pos in ady)
        hedor = any(pos == self.wumpus for pos in ady) or (self.x, self.y) == self.wumpus
        resplandor = self.hay_oro(self.x, self.y)

        p = Percepciones(
            brisa=brisa,
            hedor=hedor,
            resplandor=resplandor,
            grito=self.ultimo_grito,
            golpe=self.ultimo_golpe
        )

        self.ultimo_grito = False
        self.ultimo_golpe = False
        return p

    def _verificar_puntos_agotados(self):
        """Verifica si los puntos llegaron a 0 para finalizar el juego."""
        if self.puntuacion <= 0:
            self.puntuacion = 0
            if not self.terminado:
                self.terminado = True
                self.victoria = False
                self.causa_fin = "¡GAME OVER! Se te agotaron los puntos."

    def ejecutar_accion(self, accion, parametro=None):
        if self.terminado:
            return

        if accion == "avanzar":
            self.puntuacion -= COSTO_MOVIMIENTO
            dx, dy = OFSETS_DIRECCION[self.direccion]
            nx, ny = self.x + dx, self.y + dy

            if not (1 <= nx <= self.tamano and 1 <= ny <= self.tamano):
                self.ultimo_golpe = True
            else:
                self.x, self.y = nx, ny
                self.visitadas.add((self.x, self.y))

                if self.hay_pozo(self.x, self.y):
                    self.puntuacion -= PENALIZACION_MUERTE
                    self.terminado = True
                    self.victoria = False
                    self.causa_fin = "¡Caíste en un pozo sin fondo!"

                elif (self.x, self.y) == self.wumpus and self.wumpus_vivo:
                    self.puntuacion -= PENALIZACION_MUERTE
                    self.terminado = True
                    self.victoria = False
                    self.causa_fin = "¡El Wumpus te atrapó y te devoró!"

        elif accion == "orientar":
            if parametro in DIRECCIONES and self.direccion != parametro:
                self.direccion = parametro
                self.puntuacion -= COSTO_MOVIMIENTO

        elif accion == "girar_izquierda":
            self.puntuacion -= COSTO_MOVIMIENTO
            idx = DIRECCIONES.index(self.direccion)
            self.direccion = DIRECCIONES[(idx - 1) % 4]

        elif accion == "girar_derecha":
            self.puntuacion -= COSTO_MOVIMIENTO
            idx = DIRECCIONES.index(self.direccion)
            self.direccion = DIRECCIONES[(idx + 1) % 4]

        elif accion == "agarrar":
            self.puntuacion -= COSTO_MOVIMIENTO
            if self.hay_oro(self.x, self.y):
                self.tiene_oro = True
                self.puntuacion += RECOMPENSA_ORO

        elif accion == "disparar":
            if self.tiene_flecha:
                self.tiene_flecha = False
                self.puntuacion -= COSTO_FLECHA

                dx, dy = OFSETS_DIRECCION[self.direccion]
                fx, fy = self.x + dx, self.y + dy

                while 1 <= fx <= self.tamano and 1 <= fy <= self.tamano:
                    if (fx, fy) == self.wumpus and self.wumpus_vivo:
                        self.wumpus_vivo = False
                        self.ultimo_grito = True
                        break
                    fx += dx
                    fy += dy

        elif accion == "salir":
            self.puntuacion -= COSTO_MOVIMIENTO
            if self.x == 1 and self.y == 1:
                self.terminado = True
                if self.tiene_oro:
                    self.victoria = True
                    self.causa_fin = "¡VICTORIA! Escapaste de la cueva con el oro."
                else:
                    self.victoria = False
                    self.causa_fin = "Escapaste de la cueva sin el oro."

        self._verificar_puntos_agotados()