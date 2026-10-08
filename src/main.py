from agente import Agente
from logica import LogicaAgente


# Caso 1: aún no tiene oro y hay una casilla segura
agente = Agente()
logica = LogicaAgente(agente)

agente.casillas_seguras.add((2, 1))

accion = logica.decidir_accion()

print("Caso 1:", accion)


# Caso 2: tiene oro y está lejos del inicio
agente.tiene_oro = True
agente.posicion = (2, 1)

accion = logica.decidir_accion()

print("Caso 2:", accion)


# Caso 3: tiene oro y ya volvió al inicio
agente.posicion = (1, 1)

accion = logica.decidir_accion()

print("Caso 3:", accion)


# Caso 4: no existe una casilla segura para continuar
agente = Agente()
logica = LogicaAgente(agente)

accion = logica.decidir_accion()

print("Caso 4:", accion)