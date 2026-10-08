class Agente:
    def __init__(self):
        self.posicion = (1, 1)
        self.orientacion = "NORTE"

        self.tiene_flecha = True
        self.tiene_oro = False
        self.vivo = True

        # Memoria del agente
        self.casillas_visitadas = {(1, 1)}

        self.historial_posiciones = [(1, 1)]

        # Conocimiento de seguridad
        self.sin_pozo = {(1, 1)}
        self.sin_wumpus = {(1, 1)}
        self.casillas_seguras = {(1, 1)}

        # Posibles peligros
        self.posibles_pozos = set()
        self.posible_wumpus = set()

        self.puntuacion = 0


    def registrar_visita(self, posicion):
        self.posicion = posicion
        self.casillas_visitadas.add(posicion)

        if not self.historial_posiciones or self.historial_posiciones[-1] != posicion:
            self.historial_posiciones.append(posicion)

        self.sin_pozo.add(posicion)
        self.sin_wumpus.add(posicion)

        self.actualizar_seguridad(posicion)


    def marcar_sin_pozo(self, posicion):
        self.sin_pozo.add(posicion)
        self.posibles_pozos.discard(posicion)

        self.actualizar_seguridad(posicion)


    def marcar_sin_wumpus(self, posicion):
        self.sin_wumpus.add(posicion)
        self.posible_wumpus.discard(posicion)

        self.actualizar_seguridad(posicion)


    def actualizar_seguridad(self, posicion):
        if (
            posicion in self.sin_pozo
            and posicion in self.sin_wumpus
        ):
            self.casillas_seguras.add(posicion)


    def marcar_posible_pozo(self, posicion):
        if posicion not in self.sin_pozo:
            self.posibles_pozos.add(posicion)


    def marcar_posible_wumpus(self, posicion):
        if posicion not in self.sin_wumpus:
            self.posible_wumpus.add(posicion)


    def recoger_oro(self):
        self.tiene_oro = True


    def usar_flecha(self):
        if self.tiene_flecha:
            self.tiene_flecha = False
            self.puntuacion -= 10
            return True

        return False


    def aplicar_costo_accion(self):
        self.puntuacion -= 1


    def morir(self):
        self.vivo = False
        self.puntuacion -= 1000


    def ganar(self):
        self.puntuacion += 1000

    def regresar_por_historial(self):
        if len(self.historial_posiciones) > 1:
            self.historial_posiciones.pop()
            self.posicion = self.historial_posiciones[-1]
            return self.posicion

        return self.posicion