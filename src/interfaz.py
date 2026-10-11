import os
import sys
import pygame

# Aseguramos la importación de módulos
raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(raiz)
sys.path.append(os.path.join(raiz, "src"))

from mundo import NOMBRES_DIRECCION, MundoWumpus
from bot import ControladorBot, direccion_hacia, giros_hacia
from escenarios.escenario_victoria import crear_escenario_victoria
from escenarios.escenario_sin_solucion import crear_escenario_sin_solucion

# --- PALETA DE COLORES ---
COLOR_FONDO = (10, 11, 30)            # Azul/violeta oscuro de fondo
COLOR_MARCO = (0, 194, 255)            # Cian brillante neón
COLOR_CASILLA_NIGLA = (28, 12, 58)     # Violeta oscuro
COLOR_CASILLA_VISITADA = (50, 25, 95)  # Violeta claro
COLOR_BANNER = (0, 200, 150)           # Verde esmeralda
COLOR_PANEL_BOX = (15, 22, 48)         # Fondo de cajas de estado
COLOR_TEXTO_BLANCO = (255, 255, 255)
COLOR_TEXTO_MUTED = (160, 180, 210)
COLOR_TEXTO_TENUE = (95, 105, 150)
COLOR_ORO = (255, 215, 0)
COLOR_PELIGRO = (255, 60, 90)
COLOR_AVISO = (255, 160, 60)           # Naranja para "sin solución"
COLOR_SEGURA = (90, 230, 140)

# Botones
COLOR_BOTON = (0, 168, 143)            # Verde/turquesa
COLOR_BOTON_HOVER = (0, 215, 180)
COLOR_BOTON_DESHABILITADO = (35, 45, 60) # Gris oscuro para botones inactivos
COLOR_TEXTO_DESHABILITADO = (100, 110, 125)

ANCHO, ALTO = 1050, 720
TABLERO_X, TABLERO_Y, TABLERO_LADO = 35, 100, 560
PANEL_X, PANEL_ANCHO = 630, 380

VELOCIDAD_BOT_MS = 400   # Pausa entre acciones del bot, para que se alcance a ver en el video
MAX_MENSAJES = 4

NOMBRES_MODO = {
    "aleatorio": "Mapa aleatorio",
    "victoria": "Escenario: victoria",
    "sin_solucion": "Escenario: sin solución segura",
}


# --- SPRITES (dibujados con pygame, así el ejecutable no depende de imágenes) ---

def dibujar_wumpus(sup, cx, cy, radio, vivo=True):
    """Dibuja al Wumpus basado en la ilustración del monstruo rojo peludo."""
    s = radio * 1.25

    if vivo:
        col_rojo = (225, 25, 30)
        col_rojo_osc = (145, 15, 20)
        col_cuerno = (245, 235, 110)
        col_linea = (15, 10, 15)
    else:
        col_rojo = (90, 85, 90)
        col_rojo_osc = (55, 50, 55)
        col_cuerno = (150, 150, 140)
        col_linea = (20, 20, 20)

    # 1. Cuernos superiores
    pts_c_izq = [
        (cx - s * 0.15, cy - s * 0.35),
        (cx - s * 0.45, cy - s * 0.90),
        (cx - s * 0.85, cy - s * 0.75),
        (cx - s * 0.88, cy - s * 0.38),
        (cx - s * 0.65, cy - s * 0.15),
        (cx - s * 0.55, cy - s * 0.40),
        (cx - s * 0.68, cy - s * 0.60),
        (cx - s * 0.35, cy - s * 0.68)
    ]
    pygame.draw.polygon(sup, col_cuerno, pts_c_izq)
    pygame.draw.polygon(sup, col_linea, pts_c_izq, 2)

    pts_c_der = [
        (cx + s * 0.15, cy - s * 0.35),
        (cx + s * 0.45, cy - s * 0.90),
        (cx + s * 0.85, cy - s * 0.75),
        (cx + s * 0.88, cy - s * 0.38),
        (cx + s * 0.65, cy - s * 0.15),
        (cx + s * 0.55, cy - s * 0.40),
        (cx + s * 0.68, cy - s * 0.60),
        (cx + s * 0.35, cy - s * 0.68)
    ]
    pygame.draw.polygon(sup, col_cuerno, pts_c_der)
    pygame.draw.polygon(sup, col_linea, pts_c_der, 2)

    pygame.draw.line(sup, col_linea, (cx - s * 0.40, cy - s * 0.78), (cx - s * 0.56, cy - s * 0.58), 2)
    pygame.draw.line(sup, col_linea, (cx - s * 0.62, cy - s * 0.72), (cx - s * 0.75, cy - s * 0.50), 2)
    pygame.draw.line(sup, col_linea, (cx + s * 0.40, cy - s * 0.78), (cx + s * 0.56, cy - s * 0.58), 2)
    pygame.draw.line(sup, col_linea, (cx + s * 0.62, cy - s * 0.72), (cx + s * 0.75, cy - s * 0.50), 2)

    # 2. Cuerpo y patas
    rect_cuerpo = pygame.Rect(int(cx - s * 0.48), int(cy - s * 0.05), int(s * 0.96), int(s * 0.85))
    pygame.draw.ellipse(sup, col_rojo, rect_cuerpo)
    pygame.draw.ellipse(sup, col_linea, rect_cuerpo, 2)

    pygame.draw.ellipse(sup, col_rojo, (cx - s * 0.45, cy + s * 0.40, s * 0.38, s * 0.40))
    pygame.draw.ellipse(sup, col_linea, (cx - s * 0.45, cy + s * 0.40, s * 0.38, s * 0.40), 2)
    pygame.draw.ellipse(sup, col_rojo, (cx + s * 0.07, cy + s * 0.40, s * 0.38, s * 0.40))
    pygame.draw.ellipse(sup, col_linea, (cx + s * 0.07, cy + s * 0.40, s * 0.38, s * 0.40), 2)

    # 3. Sombra de cara y cuernos secundarios
    rect_cara = pygame.Rect(int(cx - s * 0.45), int(cy - s * 0.50), int(s * 0.90), int(s * 0.55))
    pygame.draw.ellipse(sup, col_rojo_osc, rect_cara)

    pts_m_izq = [(cx - s * 0.30, cy - s * 0.12), (cx - s * 0.68, cy - s * 0.28), (cx - s * 0.50, cy + s * 0.15)]
    pts_m_der = [(cx + s * 0.30, cy - s * 0.12), (cx + s * 0.68, cy - s * 0.28), (cx + s * 0.50, cy + s * 0.15)]
    pygame.draw.polygon(sup, col_cuerno, pts_m_izq)
    pygame.draw.polygon(sup, col_linea, pts_m_izq, 2)
    pygame.draw.polygon(sup, col_cuerno, pts_m_der)
    pygame.draw.polygon(sup, col_linea, pts_m_der, 2)

    # 4. Barba y flequillo
    pts_barba = [
        (cx - s * 0.38, cy - s * 0.08),
        (cx - s * 0.28, cy + s * 0.40),
        (cx - s * 0.12, cy + s * 0.25),
        (cx - s * 0.02, cy + s * 0.55),
        (cx + s * 0.10, cy + s * 0.25),
        (cx + s * 0.25, cy + s * 0.42),
        (cx + s * 0.38, cy - s * 0.08)
    ]
    pygame.draw.polygon(sup, col_rojo, pts_barba)
    pygame.draw.polygon(sup, col_linea, pts_barba, 2)

    pts_flequillo = [
        (cx - s * 0.45, cy - s * 0.48),
        (cx - s * 0.25, cy - s * 0.20),
        (cx - s * 0.08, cy - s * 0.40),
        (cx, cy - s * 0.05),
        (cx + s * 0.08, cy - s * 0.40),
        (cx + s * 0.25, cy - s * 0.20),
        (cx + s * 0.45, cy - s * 0.48),
        (cx + s * 0.10, cy - s * 0.60),
        (cx, cy - s * 0.52),
        (cx - s * 0.10, cy - s * 0.60)
    ]
    pygame.draw.polygon(sup, col_rojo, pts_flequillo)
    pygame.draw.polygon(sup, col_linea, pts_flequillo, 2)


def dibujar_agente(sup, cx, cy, radio, direccion):
    """Dibuja al Aventurero basado en la ilustración del arquero de piel azul."""
    s = radio * 1.2

    col_piel = (85, 115, 135)
    col_capucha = (175, 160, 125)
    col_borde_cap = (225, 215, 180)
    col_ropa = (125, 100, 80)
    col_pantalones = (70, 80, 90)
    col_arco = (155, 115, 80)
    col_linea = (20, 25, 30)

    # 1. Carcaj
    pygame.draw.ellipse(sup, col_ropa, (cx + s * 0.15, cy - s * 0.50, s * 0.25, s * 0.45))
    pygame.draw.ellipse(sup, col_linea, (cx + s * 0.15, cy - s * 0.50, s * 0.25, s * 0.45), 2)
    for offset_x in [-0.05, 0.05, 0.12]:
        pygame.draw.line(sup, (160, 185, 195), (cx + s * 0.25, cy - s * 0.48), (cx + s * 0.25 + s * offset_x, cy - s * 0.70), 3)

    # 2. Piernas
    pata_izq = pygame.Rect(int(cx - s * 0.35), int(cy + s * 0.25), int(s * 0.28), int(s * 0.45))
    pata_der = pygame.Rect(int(cx + s * 0.07), int(cy + s * 0.25), int(s * 0.28), int(s * 0.45))
    pygame.draw.rect(sup, col_pantalones, pata_izq, border_radius=4)
    pygame.draw.rect(sup, col_linea, pata_izq, width=2, border_radius=4)
    pygame.draw.rect(sup, col_pantalones, pata_der, border_radius=4)
    pygame.draw.rect(sup, col_linea, pata_der, width=2, border_radius=4)

    # 3. Túnica
    tunica = pygame.Rect(int(cx - s * 0.40), int(cy - s * 0.10), int(s * 0.80), int(s * 0.48))
    pygame.draw.ellipse(sup, col_ropa, tunica)
    pygame.draw.ellipse(sup, col_linea, tunica, 2)

    # 4. Capucha y rostro
    rect_capucha = pygame.Rect(int(cx - s * 0.45), int(cy - s * 0.65), int(s * 0.88), int(s * 0.60))
    pygame.draw.ellipse(sup, col_capucha, rect_capucha)
    pygame.draw.ellipse(sup, col_linea, rect_capucha, 2)

    rect_cara = pygame.Rect(int(cx - s * 0.25), int(cy - s * 0.50), int(s * 0.50), int(s * 0.35))
    pygame.draw.ellipse(sup, col_piel, rect_cara)

    pts_oreja_i = [(cx - s * 0.22, cy - s * 0.38), (cx - s * 0.52, cy - s * 0.48), (cx - s * 0.22, cy - s * 0.28)]
    pts_oreja_d = [(cx + s * 0.22, cy - s * 0.38), (cx + s * 0.52, cy - s * 0.48), (cx + s * 0.22, cy - s * 0.28)]
    pygame.draw.polygon(sup, col_piel, pts_oreja_i)
    pygame.draw.polygon(sup, col_linea, pts_oreja_i, 2)
    pygame.draw.polygon(sup, col_piel, pts_oreja_d)
    pygame.draw.polygon(sup, col_linea, pts_oreja_d, 2)

    pygame.draw.circle(sup, col_linea, (int(cx - s * 0.10), int(cy - s * 0.38)), int(s * 0.04))
    pygame.draw.circle(sup, col_linea, (int(cx + s * 0.10), int(cy - s * 0.38)), int(s * 0.04))
    pygame.draw.ellipse(sup, col_borde_cap, rect_capucha, width=int(s * 0.08))

    # 5. Arco y Flecha
    dx_f, dy_f = {"E": (1, 0), "N": (0, -1), "O": (-1, 0), "S": (0, 1)}[direccion]
    arc_x = cx + dx_f * s * 0.35
    arc_y = cy + dy_f * s * 0.35
    pygame.draw.arc(sup, col_arco, (arc_x - s * 0.4, arc_y - s * 0.4, s * 0.8, s * 0.8), 0.5, 5.5, 3)

    p1 = (cx, cy)
    p2 = (cx + dx_f * s * 0.65, cy + dy_f * s * 0.65)
    pygame.draw.line(sup, col_linea, p1, p2, 2)
    pygame.draw.circle(sup, (200, 200, 210), (int(p2[0]), int(p2[1])), int(s * 0.06))


def dibujar_oro(sup, cx, cy, r):
    pygame.draw.circle(sup, (200, 150, 0), (cx, cy), r)
    pygame.draw.circle(sup, COLOR_ORO, (cx, cy), int(r * 0.8))
    pygame.draw.circle(sup, (255, 245, 170), (int(cx - r * 0.3), int(cy - r * 0.3)), max(1, int(r * 0.25)))


def dibujar_pozo(sup, cx, cy, r):
    pygame.draw.circle(sup, (70, 45, 105), (cx, cy), int(r * 1.3))
    pygame.draw.circle(sup, (0, 0, 0), (cx, cy), r)


def crear_icono(lado=64):
    icono = pygame.Surface((lado, lado), pygame.SRCALPHA)
    dibujar_wumpus(icono, lado * 0.5, lado * 0.53, lado * 0.42)
    return icono


class Interfaz:
    def __init__(self):
        pygame.init()
        pygame.display.set_icon(crear_icono())
        self.pantalla = pygame.display.set_mode((ANCHO, ALTO))
        pygame.display.set_caption("La Caverna del Wumpus")
        self.reloj = pygame.time.Clock()

        # Fuentes
        self.f_titulo = pygame.font.SysFont("impact", 30)
        self.f_puntos = pygame.font.SysFont("impact", 28)
        self.f_banner = pygame.font.SysFont("arial", 15, bold=True)
        self.f_texto = pygame.font.SysFont("arial", 13, bold=True)
        self.f_btn = pygame.font.SysFont("arial", 12, bold=True)
        self.f_marca = pygame.font.SysFont("arial", 11, bold=True)
        self.f_popup_num = pygame.font.SysFont("impact", 24)
        self.f_popup_btn = pygame.font.SysFont("impact", 20)

        self.tamano_actual = 4

        # Estados de Pop-ups e Ingreso de Texto
        self.mostrar_popup_tamano = False
        self.tamano_input_str = "4"
        self.input_editado = False

        self.botones_rects = {}
        self.reiniciar_mundo()
        # Al abrir se escoge el mapa: aleatorio o uno de los dos escenarios del video
        self.abrir_popup_tamano()

    # --- PARTIDAS ---

    def _nueva_partida(self, mundo, modo):
        self.mundo = mundo
        self.modo = modo
        self.percepcion = mundo.percepciones()
        self.bot = None
        self.bot_sin_solucion = False
        self.ultimo_paso_bot = 0
        self.mensajes = []
        self._registrar(f"Partida nueva: {NOMBRES_MODO[modo]} ({mundo.tamano}x{mundo.tamano}).")

    def reiniciar_mundo(self):
        try:
            val = int(self.tamano_input_str)
            self.tamano_actual = max(3, min(20, val))
        except ValueError:
            pass

        self.tamano_input_str = str(self.tamano_actual)
        self.input_editado = False
        self._nueva_partida(MundoWumpus(tamano=self.tamano_actual), "aleatorio")

    def cargar_escenario(self, modo):
        crear = crear_escenario_victoria if modo == "victoria" else crear_escenario_sin_solucion
        self._nueva_partida(crear(), modo)

    def abrir_popup_tamano(self):
        self.tamano_input_str = str(self.tamano_actual)
        self.input_editado = False
        self.mostrar_popup_tamano = True

    def _fin_de_partida(self):
        return self.mundo.terminado or self.bot_sin_solucion

    def _bot_jugando(self):
        return self.bot is not None and not self._fin_de_partida()

    def _puede_jugar(self):
        return not self.mostrar_popup_tamano and not self._fin_de_partida() and self.bot is None

    # --- ACCIONES SOBRE EL MUNDO ---

    def _accion(self, accion, por_bot=False):
        m = self.mundo
        if m.terminado:
            return
        m.ejecutar_accion(accion)
        # Golpe y grito solo duran una lectura, por eso se guarda aquí y no en cada frame
        self.percepcion = m.percepciones()
        self._registrar(self._describir(accion), por_bot)

    def _describir(self, accion):
        m, p = self.mundo, self.percepcion
        if m.terminado:
            return m.causa_fin
        if accion == "avanzar":
            return "¡Golpe! Chocaste contra una pared." if p.golpe else f"Avanzaste a ({m.x}, {m.y})."
        if accion in ("girar_izquierda", "girar_derecha"):
            lado = "izquierda" if accion == "girar_izquierda" else "derecha"
            return f"Giraste a la {lado}, ahora miras al {NOMBRES_DIRECCION[m.direccion]}."
        if accion == "agarrar":
            return "Tomaste el oro. Vuelve a (1,1) y sal de la cueva."
        if accion == "disparar":
            return "¡Grito! La flecha mató al Wumpus." if p.grito else "La flecha no le dio a nada."
        return ""

    def _registrar(self, texto, por_bot=False):
        if texto:
            self.mensajes.append(("BOT: " if por_bot else "") + texto)
            self.mensajes = self.mensajes[-MAX_MENSAJES:]

    def _tomar_oro(self):
        if self.mundo.hay_oro(self.mundo.x, self.mundo.y):
            self._accion("agarrar")

    def _disparar(self):
        if self.mundo.tiene_flecha:
            self._accion("disparar")

    def _salir(self):
        if (self.mundo.x, self.mundo.y) == (1, 1):
            self._accion("salir")

    # --- BOT ---

    def _iniciar_bot(self):
        # El bot arranca desde (1,1) en el mismo mapa, así se compara con lo que hizo el jugador
        m = self.mundo
        self._nueva_partida(MundoWumpus(tamano=m.tamano, pozos=m.pozos, wumpus=m.wumpus, oro=m.pos_oro), self.modo)
        self.bot = ControladorBot(self.mundo.tamano)
        self._registrar("Arranco desde (1,1) en este mismo mapa.", por_bot=True)
        self.ultimo_paso_bot = pygame.time.get_ticks()

    def _paso_bot(self):
        if not self._bot_jugando() or self.mostrar_popup_tamano:
            return
        ahora = pygame.time.get_ticks()
        if ahora - self.ultimo_paso_bot < VELOCIDAD_BOT_MS:
            return
        self.ultimo_paso_bot = ahora

        accion = self.bot.siguiente_accion(self.mundo, self.percepcion)
        if accion is None:
            self.bot_sin_solucion = True
            self._registrar("No hay casilla segura para seguir. Me detengo.", por_bot=True)
        else:
            self._accion(accion, por_bot=True)

    # --- EVENTOS ---

    def ejecutar(self):
        while True:
            pos_mouse = pygame.mouse.get_pos()
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                    self._manejar_click(ev.pos)
                elif ev.type == pygame.KEYDOWN:
                    if self.mostrar_popup_tamano:
                        self._manejar_tecla_popup(ev)
                    else:
                        self._manejar_tecla_juego(ev)

            self._paso_bot()
            self._dibujar(pos_mouse)
            pygame.display.flip()
            self.reloj.tick(60)

    def _manejar_tecla_popup(self, ev):
        if ev.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
            self.reiniciar_mundo()
            self.mostrar_popup_tamano = False
        elif ev.key == pygame.K_ESCAPE:
            self.mostrar_popup_tamano = False
        elif ev.key in (pygame.K_BACKSPACE, pygame.K_DELETE):
            self.input_editado = True
            self.tamano_input_str = self.tamano_input_str[:-1]
        elif ev.unicode and ev.unicode.isdigit():
            if not self.input_editado:
                self.tamano_input_str = ev.unicode
                self.input_editado = True
            elif len(self.tamano_input_str) < 2:
                self.tamano_input_str += ev.unicode

    def _manejar_tecla_juego(self, ev):
        if not self._puede_jugar():
            return
        if ev.key == pygame.K_LEFT:
            self._accion("girar_izquierda")
        elif ev.key == pygame.K_RIGHT:
            self._accion("girar_derecha")
        elif ev.key == pygame.K_UP:
            self._accion("avanzar")
        elif ev.key == pygame.K_SPACE:
            self._disparar()
        elif ev.key == pygame.K_g:
            self._tomar_oro()
        elif ev.key == pygame.K_s:
            self._salir()

    def _clic_en(self, clave, pos):
        rect = self.botones_rects.get(clave)
        return rect is not None and rect.collidepoint(pos)

    def _manejar_click(self, pos):
        # El pop-up de nueva partida va primero pq se puede abrir encima del de fin de juego
        if self.mostrar_popup_tamano:
            if self._clic_en("btn_popup_jugar", pos):
                self.reiniciar_mundo()
                self.mostrar_popup_tamano = False
            elif self._clic_en("btn_popup_victoria", pos):
                self.cargar_escenario("victoria")
                self.mostrar_popup_tamano = False
            elif self._clic_en("btn_popup_sin_solucion", pos):
                self.cargar_escenario("sin_solucion")
                self.mostrar_popup_tamano = False
            elif self._clic_en("caja_input_1", pos) or self._clic_en("caja_input_2", pos):
                self.input_editado = False
            return

        # Clics dentro del Pop-up de Fin de Juego (Victoria / Derrota / Sin solución)
        if self._fin_de_partida():
            if self._clic_en("btn_popup_reiniciar", pos):
                self.abrir_popup_tamano()
            elif self._clic_en("btn_popup_salir", pos):
                pygame.quit()
                sys.exit()
            return

        if self._clic_en("btn_reiniciar", pos):
            self.abrir_popup_tamano()
            return

        # Mientras juega el bot no se aceptan acciones del jugador
        if self.bot is not None:
            return

        acciones_botones = {
            "btn_bot": self._iniciar_bot,
            "btn_girar_izq": lambda: self._accion("girar_izquierda"),
            "btn_avanzar": lambda: self._accion("avanzar"),
            "btn_girar_der": lambda: self._accion("girar_derecha"),
            "btn_tomar_oro": self._tomar_oro,
            "btn_disparar": self._disparar,
            "btn_salir": self._salir,
        }
        for clave, hacer in acciones_botones.items():
            if self._clic_en(clave, pos):
                hacer()
                return

        self._clic_tablero(pos)

    def _clic_tablero(self, pos):
        # Clic en casilla vecina: si no la está mirando gira, si ya la mira avanza
        m = self.mundo
        tam_celda = TABLERO_LADO // m.tamano
        col = (pos[0] - TABLERO_X) // tam_celda
        fila = (pos[1] - TABLERO_Y) // tam_celda
        if not (0 <= col < m.tamano and 0 <= fila < m.tamano):
            return

        direccion = direccion_hacia((m.x, m.y), (col + 1, m.tamano - fila))
        if direccion is None:
            return

        if m.direccion != direccion:
            for giro in giros_hacia(m.direccion, direccion):
                self._accion(giro)
        else:
            self._accion("avanzar")

    # --- DIBUJO ---

    def _pos_celda(self, x, y, tam_celda):
        col = x - 1
        fila = self.mundo.tamano - y
        return TABLERO_X + col * tam_celda, TABLERO_Y + fila * tam_celda

    def _dibujar(self, pos_mouse):
        self.pantalla.fill(COLOR_FONDO)
        self.botones_rects.clear()

        self._dibujar_encabezado()
        self._dibujar_tablero(pos_mouse)
        self._dibujar_panel(pos_mouse)

        # --- POP-UPS ---
        if self.mostrar_popup_tamano:
            self._dibujar_popup_tamano(pos_mouse)
        elif self._fin_de_partida():
            self._dibujar_popup_fin(pos_mouse)

    def _dibujar_encabezado(self):
        titulo = self.f_titulo.render("LA CAVERNA DEL WUMPUS", True, COLOR_MARCO)
        self.pantalla.blit(titulo, (TABLERO_X - 6, 16))

        modo = f"{NOMBRES_MODO[self.modo]}  ·  {self.mundo.tamano}x{self.mundo.tamano}"
        if self.bot is not None:
            modo += "  ·  Juega el bot"
        txt = self.f_texto.render(modo, True, COLOR_TEXTO_MUTED)
        self.pantalla.blit(txt, (TABLERO_X - 6, 62))

    def _dibujar_tablero(self, pos_mouse):
        m = self.mundo
        fin = self._fin_de_partida()

        # --- TABLERO NEÓN ---
        marco_tablero = pygame.Rect(TABLERO_X - 6, TABLERO_Y - 6, TABLERO_LADO + 12, TABLERO_LADO + 12)
        pygame.draw.rect(self.pantalla, COLOR_MARCO, marco_tablero, width=3, border_radius=4)

        tam_celda = TABLERO_LADO // m.tamano
        marcas_visibles = tam_celda >= 40
        for y in range(1, m.tamano + 1):
            for x in range(1, m.tamano + 1):
                px, py = self._pos_celda(x, y, tam_celda)
                rect = pygame.Rect(px + 2, py + 2, tam_celda - 4, tam_celda - 4)

                visitada = (x, y) in m.visitadas
                visible = visitada or fin
                col_c = COLOR_CASILLA_VISITADA if visible else COLOR_CASILLA_NIGLA
                pygame.draw.rect(self.pantalla, col_c, rect)
                pygame.draw.rect(self.pantalla, COLOR_MARCO, rect, width=1)

                if abs(x - m.x) + abs(y - m.y) == 1 and self._puede_jugar() and rect.collidepoint(pos_mouse):
                    pygame.draw.rect(self.pantalla, COLOR_BOTON_HOVER, rect, width=2)

                if marcas_visibles:
                    coord = self.f_marca.render(f"{x},{y}", True, COLOR_TEXTO_TENUE)
                    self.pantalla.blit(coord, coord.get_rect(bottomright=(rect.right - 4, rect.bottom - 2)))
                    if visitada:
                        self._dibujar_pistas(x, y, rect)
                    elif self.bot is not None:
                        self._dibujar_conocimiento_bot((x, y), rect)

                if visible:
                    cx, cy = rect.center
                    r_elem = max(3, tam_celda // 5)
                    if m.hay_oro(x, y):
                        dibujar_oro(self.pantalla, cx, cy, r_elem)
                    if m.hay_pozo(x, y) and fin:
                        dibujar_pozo(self.pantalla, cx, cy, r_elem)
                    if (x, y) == m.wumpus and fin:
                        dibujar_wumpus(self.pantalla, cx, cy, r_elem, m.wumpus_vivo)

        # Agente
        px, py = self._pos_celda(m.x, m.y, tam_celda)
        cx, cy = px + tam_celda // 2, py + tam_celda // 2
        r_agente = max(4, tam_celda // 3.5)
        dibujar_agente(self.pantalla, cx, cy, r_agente, m.direccion)

        # Ayudas debajo del tablero
        y_ayuda = TABLERO_Y + TABLERO_LADO + 14
        ayudas = [
            "Clic en casilla vecina o teclado: Izq/Der girar · Arriba avanzar · Espacio disparar · G oro · S salir",
            "B brisa · H hedor  |  Bot: OK casilla segura · P? posible pozo · W? posible Wumpus",
        ]
        for i, texto in enumerate(ayudas):
            txt = self.f_btn.render(texto, True, COLOR_TEXTO_TENUE)
            self.pantalla.blit(txt, (TABLERO_X - 6, y_ayuda + i * 18))

    def _dibujar_pistas(self, x, y, rect):
        # Lo que el jugador ya sintió en esa casilla (B = brisa, H = hedor)
        m = self.mundo
        ady = m._obtener_adyacentes(x, y)
        marcas = []
        if any(c in m.pozos for c in ady):
            marcas.append(("B", COLOR_MARCO))
        if m.wumpus in ady:
            marcas.append(("H", COLOR_PELIGRO))
        for i, (letra, color) in enumerate(marcas):
            txt = self.f_marca.render(letra, True, color)
            self.pantalla.blit(txt, (rect.x + 5 + i * 13, rect.y + 3))

    def _dibujar_conocimiento_bot(self, celda, rect):
        # Lo que el agente dedujo de las casillas que todavía no visita
        a = self.bot.agente
        if celda in a.casillas_seguras:
            texto, color = "OK", COLOR_SEGURA
        elif celda in a.posibles_pozos and celda in a.posible_wumpus:
            texto, color = "P? W?", COLOR_AVISO
        elif celda in a.posibles_pozos:
            texto, color = "P?", COLOR_AVISO
        elif celda in a.posible_wumpus:
            texto, color = "W?", COLOR_PELIGRO
        else:
            return
        txt = self.f_marca.render(texto, True, color)
        self.pantalla.blit(txt, txt.get_rect(topright=(rect.right - 5, rect.y + 3)))

    def _dibujar_panel(self, pos_mouse):
        m, p = self.mundo, self.percepcion

        # --- PANEL DERECHO ---
        txt_pts = self.f_puntos.render(f"PUNTOS  {m.puntuacion}", True, COLOR_TEXTO_BLANCO)
        self.pantalla.blit(txt_pts, (PANEL_X, 20))

        # ESTADO DEL JUGADOR
        caja = self._seccion("ESTADO DEL JUGADOR", TABLERO_Y - 6, 80)
        self._fila(f"Posición:  ({m.x}, {m.y})", caja, 0, 0)
        self._fila(f"Mirando hacia:  {NOMBRES_DIRECCION[m.direccion]}", caja, 0, 1)
        self._fila(f"Flechas:  {1 if m.tiene_flecha else 0}", caja, 0, 2)
        self._fila(f"Oro:  {'SÍ' if m.tiene_oro else 'NO'}", caja, 1, 0, COLOR_ORO if m.tiene_oro else None)

        # PERCEPCIÓN
        caja = self._seccion("PERCEPCIÓN", caja.bottom + 10, 80)
        percepciones = [("Brisa", p.brisa), ("Hedor", p.hedor), ("Resplandor", p.resplandor), ("Golpe", p.golpe), ("Grito", p.grito)]
        for i, (nombre, activa) in enumerate(percepciones):
            self._fila(f"{nombre}:  {'SÍ' if activa else 'NO'}", caja, i // 3, i % 3, COLOR_ORO if activa else None)

        # ACCIONES
        caja = self._seccion("ACCIONES", caja.bottom + 10, 160)
        jugar = self._puede_jugar()
        ancho, alto, sep = 112, 40, 10
        x0, y0 = caja.x + 12, caja.y + 12
        cols = [x0 + i * (ancho + sep) for i in range(3)]

        self._crear_boton("btn_girar_izq", "GIRAR IZQ", cols[0], y0, ancho, alto, pos_mouse, habilitado=jugar)
        self._crear_boton("btn_avanzar", "AVANZAR", cols[1], y0, ancho, alto, pos_mouse, habilitado=jugar)
        self._crear_boton("btn_girar_der", "GIRAR DER", cols[2], y0, ancho, alto, pos_mouse, habilitado=jugar)

        y1 = y0 + alto + 8
        self._crear_boton("btn_tomar_oro", "TOMAR ORO", cols[0], y1, ancho, alto, pos_mouse, habilitado=jugar and m.hay_oro(m.x, m.y))
        self._crear_boton("btn_disparar", "DISPARAR\nFLECHA", cols[1], y1, ancho, alto, pos_mouse, habilitado=jugar and m.tiene_flecha)
        self._crear_boton("btn_salir", "SALIR DE LA\nCUEVA", cols[2], y1, ancho, alto, pos_mouse, habilitado=jugar and (m.x, m.y) == (1, 1))

        y2 = y1 + alto + 8
        self._crear_boton("btn_reiniciar", "NUEVA PARTIDA", cols[0], y2, ancho, alto, pos_mouse)
        self._crear_boton("btn_bot", "SOLUCIÓN DEL BOT", cols[1], y2, ancho * 2 + sep, alto, pos_mouse, habilitado=self.bot is None)

        # MENSAJES
        caja = self._seccion("MENSAJES", caja.bottom + 10, TABLERO_Y + TABLERO_LADO + 6 - (caja.bottom + 42))
        for i, texto in enumerate(self.mensajes):
            color = COLOR_TEXTO_BLANCO if i == len(self.mensajes) - 1 else COLOR_TEXTO_MUTED
            txt = self.f_btn.render(texto, True, color)
            self.pantalla.blit(txt, (caja.x + 12, caja.y + 8 + i * 19), area=pygame.Rect(0, 0, caja.w - 24, txt.get_height()))

    def _seccion(self, titulo, y, alto):
        """Banner + caja del panel derecho. Devuelve el rect de la caja."""
        self._dibujar_banner(titulo, PANEL_X, y, PANEL_ANCHO, 28)
        caja = pygame.Rect(PANEL_X, y + 32, PANEL_ANCHO, alto)
        pygame.draw.rect(self.pantalla, COLOR_PANEL_BOX, caja)
        pygame.draw.rect(self.pantalla, COLOR_MARCO, caja, width=2)
        return caja

    def _fila(self, texto, caja, col, fila, color=None):
        txt = self.f_texto.render(texto, True, color or COLOR_TEXTO_BLANCO)
        self.pantalla.blit(txt, (caja.x + 20 + col * 190, caja.y + 10 + fila * 22))

    def _dibujar_banner(self, texto, x, y, ancho, alto):
        rect = pygame.Rect(x, y, ancho, alto)
        pygame.draw.rect(self.pantalla, COLOR_BANNER, rect, border_radius=3)
        pygame.draw.rect(self.pantalla, COLOR_MARCO, rect, width=1, border_radius=3)
        txt = self.f_banner.render(texto, True, COLOR_FONDO)
        self.pantalla.blit(txt, txt.get_rect(center=rect.center))

    def _crear_boton(self, clave, texto, x, y, ancho, alto, pos_mouse, habilitado=True):
        rect = pygame.Rect(x, y, ancho, alto)
        self.botones_rects[clave] = rect

        hover = rect.collidepoint(pos_mouse) and not self.mostrar_popup_tamano and not self._fin_de_partida() and habilitado

        if not habilitado:
            color = COLOR_BOTON_DESHABILITADO
            col_texto = COLOR_TEXTO_DESHABILITADO
        else:
            color = COLOR_BOTON_HOVER if hover else COLOR_BOTON
            col_texto = COLOR_TEXTO_BLANCO

        pygame.draw.rect(self.pantalla, color, rect, border_radius=6)
        pygame.draw.rect(self.pantalla, col_texto if not habilitado else COLOR_TEXTO_BLANCO, rect, width=1, border_radius=6)

        lineas = texto.split("\n")
        if len(lineas) == 1:
            txt = self.f_btn.render(texto, True, col_texto)
            self.pantalla.blit(txt, txt.get_rect(center=rect.center))
        else:
            total_h = len(lineas) * 14
            start_y = rect.centery - (total_h // 2) + 6
            for idx, l in enumerate(lineas):
                txt = self.f_btn.render(l, True, col_texto)
                r_txt = txt.get_rect(centerx=rect.centerx, centery=start_y + (idx * 14))
                self.pantalla.blit(txt, r_txt)

    def _boton_popup(self, clave, texto, rect, pos_mouse, color_base, fuente):
        self.botones_rects[clave] = rect
        col_btn = COLOR_BOTON_HOVER if rect.collidepoint(pos_mouse) else color_base
        pygame.draw.rect(self.pantalla, col_btn, rect, border_radius=6)
        pygame.draw.rect(self.pantalla, COLOR_MARCO, rect, width=2, border_radius=6)
        txt = fuente.render(texto, True, COLOR_TEXTO_BLANCO)
        self.pantalla.blit(txt, txt.get_rect(center=rect.center))

    def _dibujar_popup_tamano(self, pos_mouse):
        overlay = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        self.pantalla.blit(overlay, (0, 0))

        pop_w, pop_h = 400, 330
        pop_x = (ANCHO - pop_w) // 2
        pop_y = (ALTO - pop_h) // 2
        rect_popup = pygame.Rect(pop_x, pop_y, pop_w, pop_h)
        centro_x = pop_x + pop_w // 2

        pygame.draw.rect(self.pantalla, COLOR_PANEL_BOX, rect_popup, border_radius=4)
        pygame.draw.rect(self.pantalla, COLOR_MARCO, rect_popup, width=3, border_radius=4)

        self._dibujar_banner("NUEVA PARTIDA", pop_x + 4, pop_y + 4, pop_w - 8, 38)

        # Mapa aleatorio con tamaño
        lbl = self.f_texto.render("Mapa aleatorio (tamaño de 3 a 20)", True, COLOR_TEXTO_MUTED)
        self.pantalla.blit(lbl, lbl.get_rect(center=(centro_x, pop_y + 60)))

        if self.tamano_input_str.isdigit():
            val_display = f"{int(self.tamano_input_str):02d}"
        elif self.tamano_input_str == "":
            val_display = ""
        else:
            val_display = "--"

        col_borde_input = COLOR_ORO if not self.input_editado else COLOR_MARCO

        for clave, caja_x in (("caja_input_1", pop_x + 85), ("caja_input_2", pop_x + pop_w - 165)):
            caja = pygame.Rect(caja_x, pop_y + 76, 80, 50)
            self.botones_rects[clave] = caja
            pygame.draw.rect(self.pantalla, (0, 0, 0), caja)
            pygame.draw.rect(self.pantalla, col_borde_input, caja, width=2)
            txt = self.f_popup_num.render(val_display, True, COLOR_TEXTO_BLANCO)
            self.pantalla.blit(txt, txt.get_rect(center=caja.center))

        txt_x = self.f_popup_num.render("X", True, COLOR_TEXTO_BLANCO)
        self.pantalla.blit(txt_x, txt_x.get_rect(center=(centro_x, pop_y + 101)))

        btn_jugar = pygame.Rect(pop_x + 35, pop_y + 140, pop_w - 70, 44)
        self._boton_popup("btn_popup_jugar", "JUGAR ALEATORIO", btn_jugar, pos_mouse, COLOR_BANNER, self.f_popup_num)

        # Los dos mapas fijos que pide el profe para el video
        lbl = self.f_texto.render("Escenarios del video (4x4)", True, COLOR_TEXTO_MUTED)
        self.pantalla.blit(lbl, lbl.get_rect(center=(centro_x, pop_y + 208)))

        ancho_btn = (pop_w - 80) // 2
        btn_v = pygame.Rect(pop_x + 35, pop_y + 226, ancho_btn, 50)
        btn_s = pygame.Rect(pop_x + 45 + ancho_btn, pop_y + 226, ancho_btn, 50)
        self._boton_popup("btn_popup_victoria", "GANABLE", btn_v, pos_mouse, COLOR_BOTON, self.f_popup_btn)
        self._boton_popup("btn_popup_sin_solucion", "SIN SOLUCIÓN", btn_s, pos_mouse, COLOR_BOTON, self.f_popup_btn)

        ayuda = self.f_btn.render("Enter: jugar aleatorio  ·  Esc: cerrar", True, COLOR_TEXTO_TENUE)
        self.pantalla.blit(ayuda, ayuda.get_rect(center=(centro_x, pop_y + 304)))

    def _dibujar_popup_fin(self, pos_mouse):
        m = self.mundo

        # Solo se oscurece el panel, así el tablero queda a la vista con el mapa destapado
        overlay = pygame.Surface((ANCHO - PANEL_X + 15, ALTO), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 190))
        self.pantalla.blit(overlay, (PANEL_X - 15, 0))

        pop_w, pop_h = PANEL_ANCHO, 270
        pop_x = PANEL_X
        pop_y = (ALTO - pop_h) // 2
        rect_popup = pygame.Rect(pop_x, pop_y, pop_w, pop_h)
        centro_x = pop_x + pop_w // 2

        pygame.draw.rect(self.pantalla, COLOR_PANEL_BOX, rect_popup, border_radius=8)
        pygame.draw.rect(self.pantalla, COLOR_MARCO, rect_popup, width=3, border_radius=8)

        murio = m.hay_pozo(m.x, m.y) or ((m.x, m.y) == m.wumpus and m.wumpus_vivo)
        if not m.terminado:
            titulo, col_titulo, causa = "SIN SOLUCIÓN SEGURA", COLOR_AVISO, "El agente no encontró una casilla segura."
        elif m.victoria:
            titulo, col_titulo, causa = "¡ VICTORIA !", COLOR_ORO, m.causa_fin
        elif murio:
            titulo, col_titulo, causa = "¡ DERROTA !", COLOR_PELIGRO, m.causa_fin
        else:
            titulo, col_titulo, causa = "FIN DE LA PARTIDA", COLOR_TEXTO_MUTED, m.causa_fin

        banner_rect = pygame.Rect(pop_x + 6, pop_y + 6, pop_w - 12, 42)
        pygame.draw.rect(self.pantalla, col_titulo, banner_rect, border_radius=5)
        txt_banner = self.f_popup_num.render(titulo, True, COLOR_FONDO)
        self.pantalla.blit(txt_banner, txt_banner.get_rect(center=banner_rect.center))

        txt_causa = self.f_banner.render(causa, True, COLOR_TEXTO_BLANCO)
        self.pantalla.blit(txt_causa, txt_causa.get_rect(center=(centro_x, pop_y + 88)))

        txt_pts = self.f_puntos.render(f"PUNTOS FINALES: {m.puntuacion}", True, col_titulo)
        self.pantalla.blit(txt_pts, txt_pts.get_rect(center=(centro_x, pop_y + 135)))

        ancho_btn = (pop_w - 50) // 2
        btn_reiniciar = pygame.Rect(pop_x + 18, pop_y + 190, ancho_btn, 52)
        btn_salir = pygame.Rect(pop_x + 32 + ancho_btn, pop_y + 190, ancho_btn, 52)
        self._boton_popup("btn_popup_reiniciar", "VOLVER A JUGAR", btn_reiniciar, pos_mouse, COLOR_BOTON, self.f_popup_btn)
        self._boton_popup("btn_popup_salir", "SALIR", btn_salir, pos_mouse, COLOR_PELIGRO, self.f_popup_btn)
