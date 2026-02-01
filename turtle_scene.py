# turtle_scene.py

import turtle
import tkinter as tk
from vehicules import Voiture


class SceneTurtle:
    """Carrefour  intégré dans une fenêtre Tkinter."""

    SCREEN_WIDTH = 900
    SCREEN_HEIGHT = 900

    CORNER_NE = (110, 80)
    CORNER_NW = (-80, 110)
    CORNER_SW = (-110, -80)
    CORNER_SE = (80, -110)

    COLOR_BG = "#0d1117"
    COLOR_ASPHALT = "#2d333b"
    COLOR_LANE = "#ffd60a"
    COLOR_SIDEWALK = "#7d8590"
    COLOR_ROAD_EDGE = "#ffffff"

    VOITURE_LARGEUR = 30
    VOITURE_HAUTEUR = 15

    def __init__(self, parent_frame: tk.Frame):
        """ Intègrer Turtle dans le frame Tkinter """
        self.parent_frame = parent_frame

        # Canvas Tkinter pour Turtle
        self.canvas = tk.Canvas(
            parent_frame,
            width=self.SCREEN_WIDTH,
            height=self.SCREEN_HEIGHT,
            bg=self.COLOR_BG,
            highlightthickness=0
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # TurtleScreen sur le canvas
        self.screen = turtle.TurtleScreen(self.canvas)
        self.screen.bgcolor(self.COLOR_BG)
        self.screen.tracer(0, 0)  # Animation manuelle uniquement

        # Drawer principal
        self.drawer = turtle.RawTurtle(self.screen)
        self.drawer.hideturtle()
        self.drawer.speed(0)
        self.drawer.penup()

        # Feux
        self.feux_turtles = {}
        for nom in ["NE", "NW", "SW", "SE"]:
            t = turtle.RawTurtle(self.screen)
            t.hideturtle()
            t.speed(0)
            t.penup()
            self.feux_turtles[nom] = t

        # Voitures
        self.voitures_turtles = {}

        # Dessin du décor
        self._dessiner_routes()
        self._dessiner_intersection_centrale()
        self._dessiner_bordures()
        self._dessiner_trottoirs()
        self._dessiner_passages_pietons()
        self._dessiner_marquages()
        self._dessiner_feux()

    def _dessiner_routes(self):
        d = self.drawer
        d.color(self.COLOR_ASPHALT)

        # NORD
        d.goto(-60, 60)
        d.begin_fill()
        d.pendown()
        d.goto(60, 60)
        d.goto(60, 450)
        d.goto(-60, 450)
        d.goto(-60, 60)
        d.end_fill()
        d.penup()

        # SUD
        d.goto(-60, -450)
        d.begin_fill()
        d.pendown()
        d.goto(60, -450)
        d.goto(60, -60)
        d.goto(-60, -60)
        d.goto(-60, -450)
        d.end_fill()
        d.penup()

        # EST
        d.goto(60, -60)
        d.begin_fill()
        d.pendown()
        d.goto(450, -60)
        d.goto(450, 60)
        d.goto(60, 60)
        d.goto(60, -60)
        d.end_fill()
        d.penup()

        # OUEST
        d.goto(-450, -60)
        d.begin_fill()
        d.pendown()
        d.goto(-60, -60)
        d.goto(-60, 60)
        d.goto(-450, 60)
        d.goto(-450, -60)
        d.end_fill()
        d.penup()

    def _dessiner_intersection_centrale(self):
        d = self.drawer
        d.color(self.COLOR_ASPHALT)
        d.goto(-60, -60)
        d.begin_fill()
        d.pendown()
        d.goto(60, -60)
        d.goto(60, 60)
        d.goto(-60, 60)
        d.goto(-60, -60)
        d.end_fill()
        d.penup()

    def _dessiner_bordures(self):
        d = self.drawer
        d.color(self.COLOR_ROAD_EDGE)
        d.width(2)

        lines = [
            [(-450, 60), (-60, 60)],
            [(60, 60), (450, 60)],
            [(-450, -60), (-60, -60)],
            [(60, -60), (450, -60)],
            [(-60, -450), (-60, -60)],
            [(-60, 60), (-60, 450)],
            [(60, -450), (60, -60)],
            [(60, 60), (60, 450)],
        ]
        for start, end in lines:
            d.goto(start)
            d.pendown()
            d.goto(end)
            d.penup()
        d.width(1)

    def _dessiner_trottoirs(self):
        d = self.drawer
        d.color(self.COLOR_SIDEWALK)

        trottoirs = [
            [(60, 60), (450, 60), (450, 450), (60, 450)],
            [(-60, 60), (-450, 60), (-450, 450), (-60, 450)],
            [(-60, -60), (-450, -60), (-450, -450), (-60, -450)],
            [(60, -60), (450, -60), (450, -450), (60, -450)],
        ]

        for points in trottoirs:
            d.goto(points[0])
            d.begin_fill()
            d.pendown()
            for p in points[1:]:
                d.goto(p)
            d.end_fill()
            d.penup()

    def _dessiner_passages_pietons(self):
        d = self.drawer
        d.color("#ffffff")
        d.width(2)

        for x in range(-45, 55, 6):
            d.goto(x, 75); d.pendown(); d.goto(x, 115); d.penup()
            d.goto(x, -75); d.pendown(); d.goto(x, -115); d.penup()

        for y in range(-45, 55, 6):
            d.goto(75, y); d.pendown(); d.goto(115, y); d.penup()
            d.goto(-75, y); d.pendown(); d.goto(-115, y); d.penup()

        d.width(1)

    def _dessiner_marquages(self):
        d = self.drawer
        d.color(self.COLOR_LANE)
        d.width(3)

        positions = [(-450, 0), (60, 0), (0, 60), (0, -450)]
        headings = [0, 0, 90, 90]

        for pos, heading in zip(positions, headings):
            d.goto(pos)
            d.setheading(heading)
            for _ in range(20):
                d.pendown()
                d.forward(10)
                d.penup()
                d.forward(10)

        d.width(1)

    def _dessiner_feu(self, nom, position, etat="ROUGE"):
        t = self.feux_turtles[nom]
        t.clear()

        x, y = position
        rayon = 10

        orientation = "VERTICAL" if nom in ["NW", "SE"] else "HORIZONTAL"

        if etat == "ROUGE":
            col_rouge, col_orange, col_vert = "#ff3b30", "#1f1f1f", "#0a3b1a"
        elif etat == "ORANGE":
            col_rouge, col_orange, col_vert = "#1f1f1f", "#ff9500", "#0a3b1a"
        elif etat == "NOIR":
            col_rouge, col_orange, col_vert = "#1f1f1f", "#1f1f1f", "#0a3b1a"
        else:  # VERT
            col_rouge, col_orange, col_vert = "#1f1f1f", "#1f1f1f", "#34c759"

        boitier_largeur = 28 if orientation == "VERTICAL" else 80
        boitier_hauteur = 80 if orientation == "VERTICAL" else 28
        espacements = [12, 0, -12] if orientation == "VERTICAL" else [-12, 0, 12]

        # Boîtier noir
        t.goto(x - boitier_largeur // 2, y - boitier_hauteur // 2)
        t.color("#000000")
        t.begin_fill()
        t.pendown()
        t.forward(boitier_largeur)
        t.left(90)
        t.forward(boitier_hauteur)
        t.left(90)
        t.forward(boitier_largeur)
        t.left(90)
        t.forward(boitier_hauteur)
        t.left(90)
        t.end_fill()
        t.penup()

        # Contour gris
        t.goto(x - boitier_largeur // 2, y - boitier_hauteur // 2)
        t.color("#333333")
        t.width(1)
        t.pendown()
        t.forward(boitier_largeur)
        t.left(90)
        t.forward(boitier_hauteur)
        t.left(90)
        t.forward(boitier_largeur)
        t.left(90)
        t.forward(boitier_hauteur)
        t.left(90)
        t.penup()

        couleurs_list = [col_rouge, col_orange, col_vert]
        for i, offset in enumerate(espacements):
            couleur = couleurs_list[i]
            cx = x if orientation == "VERTICAL" else x + offset
            cy = y + offset if orientation == "VERTICAL" else y

            # Ombre cercle
            t.goto(cx, cy - rayon - 1)
            t.color("#0a0a0a")
            t.begin_fill()
            t.pendown()
            t.circle(rayon + 1)
            t.end_fill()
            t.penup()

            # Cercle couleur
            t.goto(cx, cy - rayon)
            t.color("#000000", couleur)
            t.begin_fill()
            t.pendown()
            t.circle(rayon)
            t.end_fill()
            t.penup()

            # Reflet blanc
            t.goto(cx - 3, cy + 3)
            t.color("#ffffff")
            t.begin_fill()
            t.pendown()
            t.circle(2)
            t.end_fill()
            t.penup()

    def _dessiner_feux(self):
        self._dessiner_feu("NE", self.CORNER_NE, "ROUGE")
        self._dessiner_feu("NW", self.CORNER_NW, "ROUGE")
        self._dessiner_feu("SW", self.CORNER_SW, "ROUGE")
        self._dessiner_feu("SE", self.CORNER_SE, "ROUGE")

    def _creer_voiture_turtle(self, voiture: Voiture):
        t = turtle.RawTurtle(self.screen)
        t.hideturtle()
        t.speed(0)
        t.penup()
        self._redessiner_voiture(t, voiture)
        return t

    def _redessiner_voiture(self, t: turtle.RawTurtle, voiture: Voiture):
        t.clear()

        x, y = voiture.position_x, voiture.position_y
        couleur = voiture.couleur

        w, h = (self.VOITURE_LARGEUR, self.VOITURE_HAUTEUR) if voiture.direction == "EST_OUEST" else (self.VOITURE_HAUTEUR, self.VOITURE_LARGEUR)

        # Carrosserie
        t.goto(x - w // 2, y - h // 2)
        t.color(couleur)
        t.pendown()
        t.begin_fill()
        for _ in range(2):
            t.forward(w)
            t.left(90)
            t.forward(h)
            t.left(90)
        t.end_fill()
        t.penup()

        # Pare-brise
        t.goto(x - 8, y + 4)
        t.color("#cccccc")
        t.pendown()
        t.begin_fill()
        t.goto(x + 8, y + 4)
        t.goto(x, y + 7)
        t.goto(x - 8, y + 4)
        t.end_fill()
        t.penup()

        # Vitres arrière
        t.goto(x - 5, y - 4)
        t.color("#1a1a1a")
        t.pendown()
        t.begin_fill()
        t.forward(10)
        t.left(90)
        t.forward(3)
        t.left(90)
        t.forward(10)
        t.left(90)
        t.forward(3)
        t.left(90)
        t.end_fill()
        t.penup()

        # Phares
        t.goto(x - 10, y + 3); t.color("#ffff99"); t.pendown(); t.circle(2); t.penup()
        t.goto(x + 10, y + 3); t.pendown(); t.circle(2); t.penup()

        # Roues
        t.goto(x - 10, y - 9); t.color("#000000"); t.pendown(); t.circle(3); t.penup()
        t.goto(x + 10, y - 9); t.pendown(); t.circle(3); t.penup()

    def mettre_a_jour_voitures(self, liste_voitures: list):
        ids_actuels = {v.id_voiture for v in liste_voitures}
        ids_affiches = set(self.voitures_turtles.keys())

        for id_v in ids_affiches - ids_actuels:
            t = self.voitures_turtles[id_v]
            t.clear()
            t.hideturtle()
            del self.voitures_turtles[id_v]

        for voiture in liste_voitures:
            if voiture.id_voiture not in self.voitures_turtles:
                self.voitures_turtles[voiture.id_voiture] = self._creer_voiture_turtle(voiture)
            else:
                self._redessiner_voiture(self.voitures_turtles[voiture.id_voiture], voiture)

    def mettre_a_jour_tous_les_feux(self, etats_feux: dict):
        for position, etat in etats_feux.items():
            self._dessiner_feu(position, getattr(self, f"CORNER_{position}"), etat)

    def rafraichir(self):
        self.screen.update()

    def effacer_toutes_les_voitures(self):
        for t in self.voitures_turtles.values():
            t.clear()
            t.hideturtle()
        self.voitures_turtles.clear()


if __name__ == "__main__":
    scene = SceneTurtle()
    scene.afficher()