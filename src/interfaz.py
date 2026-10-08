import os
import sys
import pygame

# Aseguramos la importación de módulos
raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(raiz)
sys.path.append(os.path.join(raiz, "src"))

from mundo import NOMBRES_DIRECCION, MundoWumpus

# --- PALETA DE COLORES ---
COLOR_FONDO = (10, 11, 30)            # Azul/violeta oscuro de fondo
COLOR_MARCO = (0, 194, 255)            # Cian brillante neón
COLOR_CASILLA_NIGLA = (28, 12, 58)     # Violeta oscuro
COLOR_CASILLA_VISITADA = (50, 25, 95)  # Violeta claro
COLOR_BANNER = (0, 200, 150)           # Verde esmeralda
COLOR_PANEL_BOX = (15, 22, 48)         # Fondo de cajas de estado
COLOR_TEXTO_BLANCO = (255, 255, 255)
COLOR_TEXTO_MUTED = (160, 180, 210)
COLOR_ORO = (255, 215, 0)
COLOR_PELIGRO = (255, 60, 90)

# Botones
COLOR_BOTON = (0, 168, 143)            # Verde/turquesa
COLOR_BOTON_HOVER = (0, 215, 180)
COLOR_BOTON_DESHABILITADO = (35, 45, 60) # Gris oscuro para botones inactivos
COLOR_TEXTO_DESHABILITADO = (100, 110, 125)

ANCHO, ALTO = 1050, 720
TABLERO_X, TABLERO_Y, TABLERO_LADO = 35, 100, 560
PANEL_X = 630


class Interfaz:
    def __init__(self):
        pygame.init()
        self.pantalla = pygame.display.set_mode((ANCHO, ALTO))
        pygame.display.set_caption("La Caverna del Wumpus")
        self.reloj = pygame.time.Clock()
        
        # Fuentes
        self.f_puntos = pygame.font.SysFont("impact", 28)
        self.f_banner = pygame.font.SysFont("arial", 15, bold=True)
        self.f_texto = pygame.font.SysFont("arial", 13, bold=True)
        self.f_btn = pygame.font.SysFont("arial", 12, bold=True)
        self.f_popup_num = pygame.font.SysFont("impact", 24)
        
        self.tamano_actual = 4
        self.mensaje_bot = "Juego iniciado."
        
        # Estados de Pop-ups e Ingreso de Texto
        self.mostrar_popup_tamano = False
        self.tamano_input_str = "4"
        self.input_editado = False
        
        self.botones_rects = {}
        self.reiniciar_mundo()

    def reiniciar_mundo(self):
        try:
            val = int(self.tamano_input_str)
            self.tamano_actual = max(3, min(20, val))
        except ValueError:
            pass
            
        self.tamano_input_str = str(self.tamano_actual)
        self.input_editado = False

        self.mundo = MundoWumpus(tamano=self.tamano_actual)
        self.mensaje_bot = f"Juego iniciado ({self.tamano_actual}x{self.tamano_actual})."

    def abrir_popup_tamano(self):
        self.tamano_input_str = str(self.tamano_actual)
        self.input_editado = False
        self.mostrar_popup_tamano = True

    def ejecutar(self):
        while True:
            pos_mouse = pygame.mouse.get_pos()
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                    self._manejar_click(pos_mouse)
                elif ev.type == pygame.KEYDOWN and self.mostrar_popup_tamano:
                    self._manejar_tecla_popup(ev)
            
            self._dibujar(pos_mouse)
            pygame.display.flip()
            self.reloj.tick(60)

    def _manejar_tecla_popup(self, ev):
        if ev.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
            self.reiniciar_mundo()
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

    def _manejar_click(self, pos):
        mx, my = pos

        # Clics dentro del Pop-up de Fin de Juego (Victoria / Derrota)
        if self.mundo.terminado:
            if "btn_popup_reiniciar" in self.botones_rects and self.botones_rects["btn_popup_reiniciar"].collidepoint(pos):
                self.abrir_popup_tamano()
            elif "btn_popup_salir" in self.botones_rects and self.botones_rects["btn_popup_salir"].collidepoint(pos):
                pygame.quit()
                sys.exit()
            return

        # Clics dentro del Pop-up de Configuración de Tamaño
        if self.mostrar_popup_tamano:
            if "btn_popup_jugar" in self.botones_rects and self.botones_rects["btn_popup_jugar"].collidepoint(pos):
                self.reiniciar_mundo()
                self.mostrar_popup_tamano = False
                return
            if ("caja_input_1" in self.botones_rects and self.botones_rects["caja_input_1"].collidepoint(pos)) or \
               ("caja_input_2" in self.botones_rects and self.botones_rects["caja_input_2"].collidepoint(pos)):
                self.input_editado = False
                return
            return

        m = self.mundo

        # Clics en la Botonera Lateral
        for nombre, rect in self.botones_rects.items():
            if rect.collidepoint(pos):
                if nombre == "btn_tomar_oro":
                    if m.hay_oro(m.x, m.y) and not m.terminado:
                        m.ejecutar_accion("agarrar")
                    return
                elif nombre == "btn_disparar":
                    if not m.terminado and m.tiene_flecha:
                        m.ejecutar_accion("disparar")
                    return
                elif nombre == "btn_salir":
                    if m.x == 1 and m.y == 1 and not m.terminado:
                        m.ejecutar_accion("salir")
                    return
                elif nombre == "btn_reiniciar":
                    self.abrir_popup_tamano()
                    return
                elif nombre == "btn_bot":
                    self.mensaje_bot = "🤖 [BOT]: Solución lista para conectar."
                    return

        # Clics en el Tablero (Girar o Avanzar)
        tam_celda = TABLERO_LADO // m.tamano
        if TABLERO_X <= mx < TABLERO_X + TABLERO_LADO and TABLERO_Y <= my < TABLERO_Y + TABLERO_LADO:
            col = (mx - TABLERO_X) // tam_celda
            fila = (my - TABLERO_Y) // tam_celda
            
            target_x = col + 1
            target_y = m.tamano - fila
            
            dx = target_x - m.x
            dy = target_y - m.y
            
            if abs(dx) + abs(dy) == 1:
                if dx == 1:
                    dir_clic = "E"
                elif dx == -1:
                    dir_clic = "O"
                elif dy == 1:
                    dir_clic = "N"
                elif dy == -1:
                    dir_clic = "S"
                
                if m.direccion != dir_clic:
                    m.ejecutar_accion("orientar", dir_clic)
                else:
                    m.ejecutar_accion("avanzar")

    def _pos_celda(self, x, y, tam_celda):
        col = x - 1
        fila = self.mundo.tamano - y
        return TABLERO_X + col * tam_celda, TABLERO_Y + fila * tam_celda

    def _dibujar_wumpus(self, cx, cy, radio, vivo=True):
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
        pygame.draw.polygon(self.pantalla, col_cuerno, pts_c_izq)
        pygame.draw.polygon(self.pantalla, col_linea, pts_c_izq, 2)

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
        pygame.draw.polygon(self.pantalla, col_cuerno, pts_c_der)
        pygame.draw.polygon(self.pantalla, col_linea, pts_c_der, 2)

        pygame.draw.line(self.pantalla, col_linea, (cx - s * 0.40, cy - s * 0.78), (cx - s * 0.56, cy - s * 0.58), 2)
        pygame.draw.line(self.pantalla, col_linea, (cx - s * 0.62, cy - s * 0.72), (cx - s * 0.75, cy - s * 0.50), 2)
        pygame.draw.line(self.pantalla, col_linea, (cx + s * 0.40, cy - s * 0.78), (cx + s * 0.56, cy - s * 0.58), 2)
        pygame.draw.line(self.pantalla, col_linea, (cx + s * 0.62, cy - s * 0.72), (cx + s * 0.75, cy - s * 0.50), 2)

        # 2. Cuerpo y patas
        rect_cuerpo = pygame.Rect(int(cx - s * 0.48), int(cy - s * 0.05), int(s * 0.96), int(s * 0.85))
        pygame.draw.ellipse(self.pantalla, col_rojo, rect_cuerpo)
        pygame.draw.ellipse(self.pantalla, col_linea, rect_cuerpo, 2)

        pygame.draw.ellipse(self.pantalla, col_rojo, (cx - s * 0.45, cy + s * 0.40, s * 0.38, s * 0.40))
        pygame.draw.ellipse(self.pantalla, col_linea, (cx - s * 0.45, cy + s * 0.40, s * 0.38, s * 0.40), 2)
        pygame.draw.ellipse(self.pantalla, col_rojo, (cx + s * 0.07, cy + s * 0.40, s * 0.38, s * 0.40))
        pygame.draw.ellipse(self.pantalla, col_linea, (cx + s * 0.07, cy + s * 0.40, s * 0.38, s * 0.40), 2)

        # 3. Sombra de cara y cuernos secundarios
        rect_cara = pygame.Rect(int(cx - s * 0.45), int(cy - s * 0.50), int(s * 0.90), int(s * 0.55))
        pygame.draw.ellipse(self.pantalla, col_rojo_osc, rect_cara)

        pts_m_izq = [(cx - s * 0.30, cy - s * 0.12), (cx - s * 0.68, cy - s * 0.28), (cx - s * 0.50, cy + s * 0.15)]
        pts_m_der = [(cx + s * 0.30, cy - s * 0.12), (cx + s * 0.68, cy - s * 0.28), (cx + s * 0.50, cy + s * 0.15)]
        pygame.draw.polygon(self.pantalla, col_cuerno, pts_m_izq)
        pygame.draw.polygon(self.pantalla, col_linea, pts_m_izq, 2)
        pygame.draw.polygon(self.pantalla, col_cuerno, pts_m_der)
        pygame.draw.polygon(self.pantalla, col_linea, pts_m_der, 2)

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
        pygame.draw.polygon(self.pantalla, col_rojo, pts_barba)
        pygame.draw.polygon(self.pantalla, col_linea, pts_barba, 2)

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
        pygame.draw.polygon(self.pantalla, col_rojo, pts_flequillo)
        pygame.draw.polygon(self.pantalla, col_linea, pts_flequillo, 2)

    def _dibujar_agente(self, cx, cy, radio, direccion):
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
        pygame.draw.ellipse(self.pantalla, col_ropa, (cx + s * 0.15, cy - s * 0.50, s * 0.25, s * 0.45))
        pygame.draw.ellipse(self.pantalla, col_linea, (cx + s * 0.15, cy - s * 0.50, s * 0.25, s * 0.45), 2)
        for offset_x in [-0.05, 0.05, 0.12]:
            pygame.draw.line(self.pantalla, (160, 185, 195), (cx + s * 0.25, cy - s * 0.48), (cx + s * 0.25 + s * offset_x, cy - s * 0.70), 3)

        # 2. Piernas
        pata_izq = pygame.Rect(int(cx - s * 0.35), int(cy + s * 0.25), int(s * 0.28), int(s * 0.45))
        pata_der = pygame.Rect(int(cx + s * 0.07), int(cy + s * 0.25), int(s * 0.28), int(s * 0.45))
        pygame.draw.rect(self.pantalla, col_pantalones, pata_izq, border_radius=4)
        pygame.draw.rect(self.pantalla, col_linea, pata_izq, width=2, border_radius=4)
        pygame.draw.rect(self.pantalla, col_pantalones, pata_der, border_radius=4)
        pygame.draw.rect(self.pantalla, col_linea, pata_der, width=2, border_radius=4)

        # 3. Túnica
        tunica = pygame.Rect(int(cx - s * 0.40), int(cy - s * 0.10), int(s * 0.80), int(s * 0.48))
        pygame.draw.ellipse(self.pantalla, col_ropa, tunica)
        pygame.draw.ellipse(self.pantalla, col_linea, tunica, 2)

        # 4. Capucha y rostro
        rect_capucha = pygame.Rect(int(cx - s * 0.45), int(cy - s * 0.65), int(s * 0.88), int(s * 0.60))
        pygame.draw.ellipse(self.pantalla, col_capucha, rect_capucha)
        pygame.draw.ellipse(self.pantalla, col_linea, rect_capucha, 2)

        rect_cara = pygame.Rect(int(cx - s * 0.25), int(cy - s * 0.50), int(s * 0.50), int(s * 0.35))
        pygame.draw.ellipse(self.pantalla, col_piel, rect_cara)

        pts_oreja_i = [(cx - s * 0.22, cy - s * 0.38), (cx - s * 0.52, cy - s * 0.48), (cx - s * 0.22, cy - s * 0.28)]
        pts_oreja_d = [(cx + s * 0.22, cy - s * 0.38), (cx + s * 0.52, cy - s * 0.48), (cx + s * 0.22, cy - s * 0.28)]
        pygame.draw.polygon(self.pantalla, col_piel, pts_oreja_i)
        pygame.draw.polygon(self.pantalla, col_linea, pts_oreja_i, 2)
        pygame.draw.polygon(self.pantalla, col_piel, pts_oreja_d)
        pygame.draw.polygon(self.pantalla, col_linea, pts_oreja_d, 2)

        pygame.draw.circle(self.pantalla, col_linea, (int(cx - s * 0.10), int(cy - s * 0.38)), int(s * 0.04))
        pygame.draw.circle(self.pantalla, col_linea, (int(cx + s * 0.10), int(cy - s * 0.38)), int(s * 0.04))
        pygame.draw.ellipse(self.pantalla, col_borde_cap, rect_capucha, width=int(s * 0.08))

        # 5. Arco y Flecha
        dx_f, dy_f = {"E": (1, 0), "N": (0, -1), "O": (-1, 0), "S": (0, 1)}[direccion]
        arc_x = cx + dx_f * s * 0.35
        arc_y = cy + dy_f * s * 0.35
        pygame.draw.arc(self.pantalla, col_arco, (arc_x - s * 0.4, arc_y - s * 0.4, s * 0.8, s * 0.8), 0.5, 5.5, 3)
        
        p1 = (cx, cy)
        p2 = (cx + dx_f * s * 0.65, cy + dy_f * s * 0.65)
        pygame.draw.line(self.pantalla, col_linea, p1, p2, 2)
        pygame.draw.circle(self.pantalla, (200, 200, 210), (int(p2[0]), int(p2[1])), int(s * 0.06))

    def _dibujar(self, pos_mouse):
        self.pantalla.fill(COLOR_FONDO)
        m = self.mundo
        self.botones_rects.clear()

        # --- TABLERO NEÓN ---
        marco_tablero = pygame.Rect(TABLERO_X - 6, TABLERO_Y - 6, TABLERO_LADO + 12, TABLERO_LADO + 12)
        pygame.draw.rect(self.pantalla, COLOR_MARCO, marco_tablero, width=3, border_radius=4)

        tam_celda = TABLERO_LADO // m.tamano
        for y in range(1, m.tamano + 1):
            for x in range(1, m.tamano + 1):
                px, py = self._pos_celda(x, y, tam_celda)
                rect = pygame.Rect(px + 2, py + 2, tam_celda - 4, tam_celda - 4)
                
                visible = (x, y) in m.visitadas or m.terminado
                col_c = COLOR_CASILLA_VISITADA if visible else COLOR_CASILLA_NIGLA
                pygame.draw.rect(self.pantalla, col_c, rect)
                pygame.draw.rect(self.pantalla, COLOR_MARCO, rect, width=1)

                dx = abs(x - m.x)
                dy = abs(y - m.y)
                if (dx + dy == 1) and not m.terminado and not self.mostrar_popup_tamano and rect.collidepoint(pos_mouse):
                    pygame.draw.rect(self.pantalla, COLOR_BOTON_HOVER, rect, width=2)

                if visible:
                    cx, cy = rect.center
                    r_elem = max(3, tam_celda // 5)
                    if m.hay_oro(x, y):
                        pygame.draw.circle(self.pantalla, COLOR_ORO, (cx, cy), r_elem)
                    if m.hay_pozo(x, y) and m.terminado:
                        pygame.draw.circle(self.pantalla, (0, 0, 0), (cx, cy), r_elem)
                    if (x, y) == m.wumpus and m.terminado:
                        self._dibujar_wumpus(cx, cy, r_elem, m.wumpus_vivo)

        # Agente
        px, py = self._pos_celda(m.x, m.y, tam_celda)
        cx, cy = px + tam_celda // 2, py + tam_celda // 2
        r_agente = max(4, tam_celda // 3.5)
        self._dibujar_agente(cx, cy, r_agente, m.direccion)

        # --- PANEL DERECHO ---
        txt_pts = self.f_puntos.render(f"PUNTOS  {m.puntuacion:06d}", True, COLOR_TEXTO_BLANCO)
        self.pantalla.blit(txt_pts, (PANEL_X, 20))

        p = m.percepciones()
        py_panel = TABLERO_Y - 6

        # ESTADO DEL JUGADOR
        self._dibujar_banner("ESTADO DEL JUGADOR", PANEL_X, py_panel, 380, 28)
        py_panel += 32
        
        box_estado = pygame.Rect(PANEL_X, py_panel, 380, 95)
        pygame.draw.rect(self.pantalla, COLOR_PANEL_BOX, box_estado)
        pygame.draw.rect(self.pantalla, COLOR_MARCO, box_estado, width=2)
        
        txt_pos = self.f_texto.render(f"Posicion Actual:  ({m.x}, {m.y})", True, COLOR_TEXTO_BLANCO)
        txt_dir = self.f_texto.render(f"Mirando Hacia:   {NOMBRES_DIRECCION[m.direccion]}", True, COLOR_TEXTO_BLANCO)
        txt_flc = self.f_texto.render(f"Flechas:          {'1' if m.tiene_flecha else '0'}", True, COLOR_TEXTO_BLANCO)
        
        self.pantalla.blit(txt_pos, (PANEL_X + 20, py_panel + 12))
        self.pantalla.blit(txt_dir, (PANEL_X + 20, py_panel + 38))
        self.pantalla.blit(txt_flc, (PANEL_X + 20, py_panel + 64))

        # PERCEPCION
        py_panel += 115
        self._dibujar_banner("PERCEPCION", PANEL_X, py_panel, 380, 28)
        py_panel += 32

        box_percepcion = pygame.Rect(PANEL_X, py_panel, 380, 95)
        pygame.draw.rect(self.pantalla, COLOR_PANEL_BOX, box_percepcion)
        pygame.draw.rect(self.pantalla, COLOR_MARCO, box_percepcion, width=2)

        txt_bri = self.f_texto.render(f"Brisa:               {'SI' if p.brisa else 'NO'}", True, COLOR_TEXTO_BLANCO)
        txt_hed = self.f_texto.render(f"Hedor:              {'SI' if p.hedor else 'NO'}", True, COLOR_TEXTO_BLANCO)
        txt_res = self.f_texto.render(f"Resplandor:      {'SI' if p.resplandor else 'NO'}", True, COLOR_TEXTO_BLANCO)

        self.pantalla.blit(txt_bri, (PANEL_X + 20, py_panel + 12))
        self.pantalla.blit(txt_hed, (PANEL_X + 20, py_panel + 38))
        self.pantalla.blit(txt_res, (PANEL_X + 20, py_panel + 64))

        # ACCIONES
        py_panel += 115
        self._dibujar_banner("ACCIONES", PANEL_X, py_panel, 380, 28)
        py_panel += 32

        box_acciones = pygame.Rect(PANEL_X, py_panel, 380, 185)
        pygame.draw.rect(self.pantalla, COLOR_PANEL_BOX, box_acciones)
        pygame.draw.rect(self.pantalla, COLOR_MARCO, box_acciones, width=2)

        puedes_tomar = m.hay_oro(m.x, m.y) and not m.terminado
        puedes_disparar = m.tiene_flecha and not m.terminado
        puedes_salir = (m.x == 1 and m.y == 1) and not m.terminado

        self._crear_boton("btn_tomar_oro", "TOMAR ORO", PANEL_X + 15, py_panel + 15, 170, 42, pos_mouse, habilitado=puedes_tomar)
        self._crear_boton("btn_disparar", "DISPARAR\nFLECHA", PANEL_X + 15, py_panel + 67, 170, 45, pos_mouse, habilitado=puedes_disparar)
        self._crear_boton("btn_salir", "SALIR DE LA\nCUEVA", PANEL_X + 15, py_panel + 122, 170, 45, pos_mouse, habilitado=puedes_salir)

        self._crear_boton("btn_reiniciar", "REINICIAR", PANEL_X + 195, py_panel + 15, 170, 42, pos_mouse)
        self._crear_boton("btn_bot", "SOLUCION\nDEL BOT", PANEL_X + 195, py_panel + 67, 170, 100, pos_mouse)

        py_panel += 195
        s_bot = self.f_btn.render(f"Estado: {self.mensaje_bot}", True, COLOR_TEXTO_MUTED)
        self.pantalla.blit(s_bot, (PANEL_X, py_panel))

        # --- POP-UPS ---
        if self.mostrar_popup_tamano:
            self._dibujar_popup_tamano(pos_mouse)
        elif m.terminado:
            self._dibujar_popup_fin(pos_mouse)

    def _dibujar_banner(self, texto, x, y, ancho, alto):
        rect = pygame.Rect(x, y, ancho, alto)
        pygame.draw.rect(self.pantalla, COLOR_BANNER, rect, border_radius=3)
        pygame.draw.rect(self.pantalla, COLOR_MARCO, rect, width=1, border_radius=3)
        txt = self.f_banner.render(texto, True, COLOR_FONDO)
        self.pantalla.blit(txt, txt.get_rect(center=rect.center))

    def _crear_boton(self, clave, texto, x, y, ancho, alto, pos_mouse, habilitado=True):
        rect = pygame.Rect(x, y, ancho, alto)
        self.botones_rects[clave] = rect
        
        hover = rect.collidepoint(pos_mouse) and not self.mostrar_popup_tamano and not self.mundo.terminado and habilitado
        
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

    def _dibujar_popup_tamano(self, pos_mouse):
        overlay = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        self.pantalla.blit(overlay, (0, 0))

        pop_w, pop_h = 360, 240
        pop_x = (ANCHO - pop_w) // 2
        pop_y = (ALTO - pop_h) // 2
        rect_popup = pygame.Rect(pop_x, pop_y, pop_w, pop_h)

        pygame.draw.rect(self.pantalla, COLOR_PANEL_BOX, rect_popup, border_radius=4)
        pygame.draw.rect(self.pantalla, COLOR_MARCO, rect_popup, width=3, border_radius=4)

        self._dibujar_banner("TAMAÑO DE TABLERO", pop_x + 4, pop_y + 4, pop_w - 8, 38)

        if self.tamano_input_str.isdigit():
            val_display = f"{int(self.tamano_input_str):02d}"
        elif self.tamano_input_str == "":
            val_display = ""
        else:
            val_display = "--"
        
        col_borde_input = COLOR_ORO if not self.input_editado else COLOR_MARCO

        caja1 = pygame.Rect(pop_x + 65, pop_y + 85, 80, 50)
        self.botones_rects["caja_input_1"] = caja1
        pygame.draw.rect(self.pantalla, (0, 0, 0), caja1)
        pygame.draw.rect(self.pantalla, col_borde_input, caja1, width=2)
        txt1 = self.f_popup_num.render(val_display, True, COLOR_TEXTO_BLANCO)
        self.pantalla.blit(txt1, txt1.get_rect(center=caja1.center))

        txt_x = self.f_popup_num.render("X", True, COLOR_TEXTO_BLANCO)
        self.pantalla.blit(txt_x, txt_x.get_rect(center=(pop_x + pop_w // 2, pop_y + 110)))

        caja2 = pygame.Rect(pop_x + pop_w - 145, pop_y + 85, 80, 50)
        self.botones_rects["caja_input_2"] = caja2
        pygame.draw.rect(self.pantalla, (0, 0, 0), caja2)
        pygame.draw.rect(self.pantalla, col_borde_input, caja2, width=2)
        txt2 = self.f_popup_num.render(val_display, True, COLOR_TEXTO_BLANCO)
        self.pantalla.blit(txt2, txt2.get_rect(center=caja2.center))

        btn_jugar = pygame.Rect(pop_x + 35, pop_y + 165, pop_w - 70, 48)
        self.botones_rects["btn_popup_jugar"] = btn_jugar
        
        hover = btn_jugar.collidepoint(pos_mouse)
        col_btn = COLOR_BOTON_HOVER if hover else COLOR_BANNER
        pygame.draw.rect(self.pantalla, col_btn, btn_jugar, border_radius=4)
        pygame.draw.rect(self.pantalla, COLOR_MARCO, btn_jugar, width=2, border_radius=4)
        
        txt_jugar = self.f_popup_num.render("JUGAR", True, COLOR_TEXTO_BLANCO)
        self.pantalla.blit(txt_jugar, txt_jugar.get_rect(center=btn_jugar.center))

    def _dibujar_popup_fin(self, pos_mouse):
        m = self.mundo
        overlay = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.pantalla.blit(overlay, (0, 0))

        pop_w, pop_h = 440, 270
        pop_x = (ANCHO - pop_w) // 2
        pop_y = (ALTO - pop_h) // 2
        rect_popup = pygame.Rect(pop_x, pop_y, pop_w, pop_h)

        pygame.draw.rect(self.pantalla, COLOR_PANEL_BOX, rect_popup, border_radius=8)
        pygame.draw.rect(self.pantalla, COLOR_MARCO, rect_popup, width=3, border_radius=8)

        titulo = "¡ VICTORIA !" if m.victoria else "¡ DERROTA !"
        col_titulo = COLOR_ORO if m.victoria else COLOR_PELIGRO

        banner_rect = pygame.Rect(pop_x + 6, pop_y + 6, pop_w - 12, 42)
        pygame.draw.rect(self.pantalla, col_titulo, banner_rect, border_radius=5)
        txt_banner = self.f_popup_num.render(titulo, True, COLOR_FONDO)
        self.pantalla.blit(txt_banner, txt_banner.get_rect(center=banner_rect.center))

        txt_causa = self.f_banner.render(m.causa_fin, True, COLOR_TEXTO_BLANCO)
        r_causa = txt_causa.get_rect(center=(pop_x + pop_w // 2, pop_y + 88))
        self.pantalla.blit(txt_causa, r_causa)

        txt_pts = self.f_puntos.render(f"PUNTOS FINALES: {m.puntuacion:06d}", True, col_titulo)
        r_pts = txt_pts.get_rect(center=(pop_x + pop_w // 2, pop_y + 135))
        self.pantalla.blit(txt_pts, r_pts)

        # Botón Volver a Jugar
        btn_reiniciar = pygame.Rect(pop_x + 25, pop_y + 185, 185, 52)
        self.botones_rects["btn_popup_reiniciar"] = btn_reiniciar
        hover_r = btn_reiniciar.collidepoint(pos_mouse)
        col_btn_r = COLOR_BOTON_HOVER if hover_r else COLOR_BOTON
        pygame.draw.rect(self.pantalla, col_btn_r, btn_reiniciar, border_radius=6)
        pygame.draw.rect(self.pantalla, COLOR_MARCO, btn_reiniciar, width=2, border_radius=6)

        txt_btn_r = self.f_popup_num.render("VOLVER A JUGAR", True, COLOR_TEXTO_BLANCO)
        self.pantalla.blit(txt_btn_r, txt_btn_r.get_rect(center=btn_reiniciar.center))

        # Botón Salir
        btn_salir = pygame.Rect(pop_x + 230, pop_y + 185, 185, 52)
        self.botones_rects["btn_popup_salir"] = btn_salir
        hover_s = btn_salir.collidepoint(pos_mouse)
        col_btn_s = COLOR_BOTON_HOVER if hover_s else COLOR_PELIGRO
        pygame.draw.rect(self.pantalla, col_btn_s, btn_salir, border_radius=6)
        pygame.draw.rect(self.pantalla, COLOR_MARCO, btn_salir, width=2, border_radius=6)

        txt_btn_s = self.f_popup_num.render("SALIR", True, COLOR_TEXTO_BLANCO)
        self.pantalla.blit(txt_btn_s, txt_btn_s.get_rect(center=btn_salir.center))