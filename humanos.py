"""
Personajes humanos de cuerpo completo con sombreado (estilo de dinos.py).

    h = Humano(ropa=(40, 40, 50), sombrero="casco_minero", barba=True)
    h.dibujar(img, x, y_pies, escala, t, pose="caminar", expr="feliz")

Poses: quieto, caminar, saludar, celebrar, sostener, sentado
Expresiones: normal, feliz, sorpresa, triste, serio, miedo, cansado
"""
from __future__ import annotations

import math

from dinos import TINTA, Lienzo, Sprite, capsula, catmull, claro, elipse, oscuro


class Humano:
    def __init__(self, ropa=(70, 90, 140), pantalon=(50, 55, 70), piel=(236, 192, 156), pelo=(60, 42, 30),
                 peinado="corto", sombrero=None, barba=False, lentes=False, corbata=None, chaleco=None,
                 cinturon=False, vestido=False, bufanda=None, zapatos=(40, 34, 32), descalzo_der=False,
                 color_sombrero=None, realista=False, cabeza=1.0):
        self.ropa, self.pantalon, self.piel, self.pelo = ropa, pantalon, piel, pelo
        self.peinado, self.sombrero, self.barba, self.lentes = peinado, sombrero, barba, lentes
        self.corbata, self.chaleco, self.cinturon, self.vestido = corbata, chaleco, cinturon, vestido
        self.bufanda, self.zapatos, self.descalzo_der = bufanda, zapatos, descalzo_der
        self.color_sombrero = color_sombrero
        self.cabeza = cabeza
        lienzo_cls = None
        if realista:
            from realista import LienzoReal
            lienzo_cls = LienzoReal
        self.sprite = Sprite(self._dib, 600, 1000, 300, 960, fases=12, lienzo_cls=lienzo_cls)

    # ------------------------------------------------------------------ #
    def _dib(self, L: Lienzo, f, boca, parp, extra):
        pose, expr = extra
        piel, ropa = self.piel, self.ropa
        andar = math.sin(f) if pose == "caminar" else 0.0
        # piernas
        for lado in (-1, 1):
            sw = andar * 34 * lado
            cad = (lado * 46, -330)
            pie = (lado * 50 + sw, -30)
            if pose == "sentado":
                pie = (lado * 60 + 70, -150)
                L.forma(capsula(cad, (lado * 55 + 120, -300), 84, 76), self.pantalon, intensidad=0.08)
                L.forma(capsula((lado * 55 + 120, -300), pie, 70, 62), self.pantalon, intensidad=0.08)
            else:
                L.forma(capsula(cad, pie, 86, 72), self.pantalon if not self.vestido else piel, intensidad=0.08)
            descalzo = self.descalzo_der and lado == 1
            L.forma(elipse(pie[0] + 18, pie[1] + 8, 54, 26), piel if descalzo else self.zapatos, intensidad=0.12)
        # brazo trasero
        self._brazo(L, -1, pose, andar, atras=True)
        # torso
        torso = [(-100, -600), (100, -600), (112, -360), (88, -300), (-88, -300), (-112, -360)]
        if self.vestido:
            torso = [(-96, -600), (96, -600), (108, -440), (150, -250), (-150, -250), (-108, -440)]
        cuerpo = L.forma(torso, ropa, intensidad=0.1)
        if self.chaleco:
            L.forma([(-100, -590), (-30, -590), (-20, -310), (-90, -310), (-108, -360)], self.chaleco,
                    clip=cuerpo, borde=False)
            L.forma([(100, -590), (30, -590), (20, -310), (90, -310), (108, -360)], self.chaleco, clip=cuerpo,
                    borde=False)
            for y in (-470, -400):
                L.linea([(-104, y), (-24, y)], (225, 228, 232), 12)
                L.linea([(24, y), (104, y)], (225, 228, 232), 12)
        if self.corbata:
            L.forma([(-34, -600), (0, -560), (34, -600)], (245, 245, 245), suave=False, ancho=3)
            L.forma([(-12, -562), (12, -562), (18, -420), (0, -396), (-18, -420)], self.corbata, suave=False,
                    ancho=3)
        if self.cinturon:
            L.forma([(-110, -350), (110, -350), (108, -322), (-108, -322)], (80, 58, 36), suave=False, ancho=3)
            L.forma([(-16, -352), (16, -352), (16, -320), (-16, -320)], (210, 180, 90), suave=False, ancho=3)
        if self.bufanda:
            L.forma(catmull([(-80, -610), (80, -610), (70, -560), (-70, -560)], 3), self.bufanda, ancho=4)
            L.forma([(40, -580), (70, -580), (80, -470), (50, -470)], self.bufanda, ancho=4)
        # cuello y cabeza
        L.forma(capsula((0, -600), (0, -650), 62, 62), oscuro(piel, 0.92), sombra=False, brillo=False)
        hc = -740
        if self.cabeza != 1.0:
            L.tf = (0, -625, self.cabeza)
        if self.peinado == "largo":
            L.forma(catmull([(-108, -790), (-118, -660), (-96, -600), (96, -600), (118, -660), (108, -790)], 3),
                    self.pelo, intensidad=0.08)
        for sx in (-1, 1):
            L.forma(elipse(sx * 96, hc + 6, 20, 28), piel, intensidad=0.1)
        L.forma(elipse(0, hc, 98, 112), piel, intensidad=0.1)
        if self.barba:
            L.forma(catmull([(-92, -730), (-80, -660), (-40, -630), (0, -625), (40, -630), (80, -660), (92, -730),
                             (60, -690), (0, -680), (-60, -690)], 3), claro(self.pelo, 0.15), intensidad=0.06,
                    ancho=4)
        self._pelo(L, hc)
        self._cara(L, hc, expr, parp, boca)
        self._sombrero(L, hc)
        L.tf = None
        # brazo delantero
        self._brazo(L, 1, pose, andar, atras=False)

    def _brazo(self, L, lado, pose, andar, atras):
        hombro = (lado * 100, -570)
        manga = oscuro(self.ropa, 0.85) if atras else self.ropa
        if self.vestido and not atras:
            manga = self.piel
        if pose in ("celebrar",) or (pose == "saludar" and lado == 1):
            codo = (lado * 150, -680)
            mano = (lado * 170 + (10 * math.sin(andar) if pose == "saludar" else 0), -800)
        elif pose == "sostener":
            codo = (lado * 120, -440)
            mano = (lado * 50, -420)
        elif pose == "sentado":
            codo = (lado * 120, -440)
            mano = (lado * 80 + 60, -350)
        else:
            sw = andar * 40 * -lado
            codo = (lado * 125 + sw * 0.4, -450)
            mano = (lado * 120 + sw, -330)
        L.forma(capsula(hombro, codo, 58, 50), manga, intensidad=0.08)
        L.forma(capsula(codo, mano, 50, 42), manga, intensidad=0.08)
        L.forma(elipse(mano[0], mano[1], 26, 26), self.piel, intensidad=0.12, ancho=4)

    def _pelo(self, L, hc):
        p = self.pelo
        if self.sombrero in ("casco_minero", "pickelhaube", "casco_aviador"):
            return
        if self.peinado == "calvo":
            return
        if self.peinado in ("corto", "barba"):
            L.forma(catmull([(-100, -760), (-92, -820), (-40, -858), (20, -860), (80, -830), (102, -770),
                             (80, -790), (30, -810), (-30, -808), (-82, -786)], 3), p, intensidad=0.08)
        elif self.peinado == "largo":
            L.forma(catmull([(-104, -740), (-96, -830), (-40, -866), (30, -866), (92, -830), (104, -740),
                             (60, -800), (0, -812), (-60, -800)], 3), p, intensidad=0.08)
        elif self.peinado == "rizado":
            for i in range(9):
                a = math.pi + i / 8 * math.pi
                L.forma(elipse(90 * math.cos(a), hc - 30 + 95 * math.sin(a), 34, 34), p, intensidad=0.1, ancho=4)
        elif self.peinado == "trenza":
            L.forma(catmull([(-104, -750), (-96, -830), (-40, -866), (30, -866), (92, -830), (104, -750),
                             (60, -805), (0, -815), (-60, -805)], 3), p, intensidad=0.08)
            for i in range(4):
                L.forma(elipse(100, -680 + i * 50, 26, 30), p, intensidad=0.1, ancho=4)

    def _cara(self, L, hc, expr, parp, boca):
        ojo_y = hc - 10
        for sx in (-1, 1):
            if expr == "cansado" or parp:
                L.linea([(sx * 22, ojo_y), (sx * 52, ojo_y + 2)], TINTA, 5)
            else:
                r = 17 if expr in ("sorpresa", "miedo") else 14
                L.ojo(sx * 37, ojo_y, r, iris=(90, 70, 50), mirar=(0.1, 0))
            cy = ojo_y - 34
            if expr in ("triste", "miedo"):
                L.linea([(sx * 18, cy - 10), (sx * 54, cy + 4)], oscuro(self.pelo, 0.8), 6)
            elif expr == "serio":
                L.linea([(sx * 18, cy + 4), (sx * 54, cy - 4)], oscuro(self.pelo, 0.8), 6)
            elif expr == "sorpresa":
                L.linea([(sx * 20, cy - 8), (sx * 54, cy - 12)], oscuro(self.pelo, 0.8), 6)
            else:
                L.linea([(sx * 18, cy), (sx * 54, cy - 4)], oscuro(self.pelo, 0.8), 6)
        if self.lentes:
            for sx in (-1, 1):
                L.forma(elipse(sx * 38, ojo_y, 32, 22), (25, 25, 30), ancho=4, sombra=False)
            L.linea([(-8, ojo_y - 4), (8, ojo_y - 4)], TINTA, 4)
        L.linea(catmull([(-4, hc + 6), (-12, hc + 34), (6, hc + 38)], 4, cerrado=False), oscuro(self.piel, 0.7), 4)
        my = hc + 66
        if expr in ("sorpresa", "miedo") or boca > 0.2:
            L.forma(elipse(0, my, 16, 20), (120, 40, 50), ancho=4, sombra=False, brillo=False)
        elif expr == "feliz":
            L.forma(catmull([(-34, my - 8), (34, my - 8), (20, my + 16), (-20, my + 16)], 3), (120, 40, 50),
                    ancho=4, sombra=False, brillo=False)
            L.forma([(-24, my - 6), (24, my - 6), (20, my + 2), (-20, my + 2)], (250, 250, 245), suave=False,
                    borde=False, sombra=False, brillo=False)
        elif expr in ("triste", "cansado"):
            L.linea(catmull([(-24, my + 8), (0, my - 4), (24, my + 8)], 4, cerrado=False), TINTA, 5)
        else:
            L.linea([(-22, my), (22, my)], TINTA, 5)

    def _sombrero(self, L, hc):
        s = self.sombrero
        top = hc - 112
        if s == "casco_minero":
            c = self.color_sombrero or (245, 200, 40)
            L.forma(catmull([(-112, -785), (-104, -875), (-50, -925), (50, -925), (104, -875), (112, -785)], 3) +
                    [(130, -775), (-130, -775)], c, intensidad=0.1)
            L.forma(elipse(0, -830, 34, 28), (230, 230, 220), ancho=4)
            L.circulo(0, -830, 18, (255, 250, 200), borde=False)
        elif s == "pickelhaube":
            L.forma(catmull([(-108, -785), (-100, -875), (-50, -921), (50, -921), (100, -875), (108, -785)], 3) +
                    [(120, -771), (-120, -771)], (120, 124, 110), intensidad=0.1)
            L.forma([(-12, -921), (12, -921), (0, -995)], (130, 130, 120), suave=False, ancho=4)
        elif s == "gorra_tommy":
            c = self.color_sombrero or (150, 130, 90)
            L.forma(catmull([(-112, -815), (-100, -895), (0, -925), (100, -895), (112, -815)], 3), c,
                    intensidad=0.1)
            L.forma(elipse(30, -815, 110, 20), oscuro(c, 0.7), intensidad=0.1)
        elif s == "fedora":
            c = self.color_sombrero or (60, 56, 52)
            L.forma(elipse(0, -790, 160, 30), c, intensidad=0.1)
            L.forma(catmull([(-90, -790), (-80, -890), (0, -870), (80, -890), (90, -790)], 3), c, intensidad=0.1)
            L.forma([(-90, -810), (90, -810), (90, -790), (-90, -790)], (30, 28, 26), suave=False, borde=False)
        elif s == "gorro_lana":
            c = self.color_sombrero or (180, 60, 60)
            L.forma(catmull([(-110, -795), (-100, -885), (0, -925), (100, -885), (110, -795)], 3), c,
                    intensidad=0.1)
            L.forma([(-114, -815), (114, -815), (114, -777), (-114, -777)], oscuro(c, 0.8), suave=False, ancho=4)
            L.circulo(0, -905, 26, claro(c, 0.3))
        elif s == "chupalla":
            c = self.color_sombrero or (200, 170, 110)
            L.forma(elipse(0, -790, 190, 34), c, intensidad=0.1)
            L.forma(catmull([(-86, -790), (-80, -880), (80, -880), (86, -790)], 3), c, intensidad=0.1)
            L.forma([(-86, -812), (86, -812), (86, -792), (-86, -792)], (150, 40, 40), suave=False, borde=False)
        elif s == "azafata":
            c = self.color_sombrero or (40, 120, 130)
            L.forma(catmull([(-70, -840), (-60, -880), (60, -880), (70, -840)], 3) + [(80, -830), (-80, -830)], c,
                    intensidad=0.1)
        elif s == "casco_aviador":
            L.forma(catmull([(-110, -740), (-104, -840), (-50, -880), (50, -880), (104, -840), (110, -740)], 3),
                    (120, 80, 50), intensidad=0.1)

    def dibujar(self, img, x, y, s, t, pose="quieto", expr="normal", vel=1.0, espejo=False, tinte=None, alfa=1.0,
                sombra=True, boca=0.0):
        self.sprite.dibujar(img, x, y, s, t, vel=vel, boca=boca, espejo=espejo, extra=(pose, expr), sombra=sombra,
                            tinte=tinte, alfa=alfa)
