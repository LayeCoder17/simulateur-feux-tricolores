# vehicules.py

from dataclasses import dataclass


@dataclass
class Voiture:
    """Représente une voiture dans la simulation du carrefour."""
    id_voiture: int
    type_voiture: str
    couleur: str
    position_x: float
    position_y: float
    vitesse_max: float
    direction: str  # "NORD_SUD" ou "EST_OUEST"
    vitesse: float = None

    # Constantes pour les limites d'écran
    LIMITE_NORD = 500
    LIMITE_SUD = -500
    LIMITE_EST = 500
    LIMITE_OUEST = -500

    def __post_init__(self):
        """Initialise la voiture après la création."""
        if self.vitesse is None:
            self.vitesse = self.vitesse_max

        if self.vitesse_max == 0:
            raise ValueError("vitesse_max ne doit pas être 0 (peut être + ou -)")

        if self.direction not in ["NORD_SUD", "EST_OUEST"]:
            raise ValueError(f"Direction invalide: {self.direction}. Doit être 'NORD_SUD' ou 'EST_OUEST'")

    def avancer(self, delta_t: float) -> None:
        """Déplace la voiture selon sa direction et sa vitesse."""
        if delta_t <= 0:
            raise ValueError("delta_t doit être > 0")

        if self.direction == "NORD_SUD":
            self.position_y += self.vitesse * delta_t
        elif self.direction == "EST_OUEST":
            self.position_x += self.vitesse * delta_t
        else:
            raise ValueError(f"Direction inconnue: {self.direction}")

    def arreter(self) -> None:
        """Arrête complètement la voiture (vitesse = 0)."""
        self.vitesse = 0.0

    def ralentir(self, facteur: float = 0.5) -> None:
        """Réduit la vitesse selon un facteur (0 < facteur <= 1)."""
        if not (0 < facteur <= 1):
            raise ValueError("facteur de ralentissement doit être dans ]0,1]")

        self.vitesse = self.vitesse_max * facteur

    def accelerer(self, facteur: float = 1.0) -> None:
        """Augmente la vitesse jusqu'à la vitesse max."""
        if not (0 < facteur <= 1):
            raise ValueError("facteur d'accélération doit être dans ]0,1]")

        if self.vitesse_max > 0:
            self.vitesse = min(self.vitesse_max * facteur, self.vitesse_max)
        else:
            self.vitesse = max(self.vitesse_max * facteur, self.vitesse_max)

    def remettre_vitesse_normale(self) -> None:
        """Remet la voiture à sa vitesse maximale."""
        self.vitesse = self.vitesse_max

    def est_hors_limites(self) -> bool:
        """Vérifie si la voiture a dépassé les limites de l'écran."""
        if self.direction == "NORD_SUD":
            return self.position_y > self.LIMITE_NORD or self.position_y < self.LIMITE_SUD
        else:
            return self.position_x > self.LIMITE_EST or self.position_x < self.LIMITE_OUEST

    def est_dans_zone_carrefour(self) -> bool:
        """ Vérifie si la voiture est DANS la zone du carrefour (-80 à +80)"""
        CARREFOUR_MIN = -80
        CARREFOUR_MAX = 80
        return (CARREFOUR_MIN <= self.position_x <= CARREFOUR_MAX and
                CARREFOUR_MIN <= self.position_y <= CARREFOUR_MAX)

    def est_proche_du_carrefour(self) -> bool:
        """ Vérifie si la voiture s'approche du carrefour (zone de freinage)"""
        ZONE_APPROCHE_MIN = -150
        ZONE_APPROCHE_MAX = 150

        if self.direction == "NORD_SUD":
            return ((ZONE_APPROCHE_MIN <= self.position_y < -80) or
                    (80 < self.position_y <= ZONE_APPROCHE_MAX))
        else:
            return ((ZONE_APPROCHE_MIN <= self.position_x < -80) or
                    (80 < self.position_x <= ZONE_APPROCHE_MAX))

    def mettre_a_jour(self, feu, delta_t: float, deplacer: bool = True) -> None:
        """
        Met à jour l'état de la voiture selon le feu tricolore.
        """
        if self.est_proche_du_carrefour():
            #  AVANT le carrefour: respecter le feu STRICTEMENT
            if feu.est_rouge():
                self.vitesse = 0.0  # ARRÊT COMPLET
            elif feu.est_orange():
                self.ralentir(0.2)  # Ralentir à 20%
            else:  # VERT
                self.remettre_vitesse_normale()

        elif self.est_dans_zone_carrefour():
            #  DANS le carrefour: traverser à vitesse normale
            self.remettre_vitesse_normale()

        else:
            # LOIN du carrefour: vitesse normale
            self.remettre_vitesse_normale()

        # Déplacer seulement si deplacer=True
        if deplacer:
            self.avancer(delta_t)

    def reinitialiser(self) -> None:
        """Réinitialise la voiture à sa vitesse maximale."""
        self.vitesse = self.vitesse_max

    def obtenir_position_tuple(self) -> tuple:
        """Retourne la position sous forme de tuple (x, y)."""
        return (self.position_x, self.position_y)

    def obtenir_info_affichage(self) -> dict:
        """Retourne les informations pour l'affichage graphique."""
        return {
            'id': self.id_voiture,
            'type': self.type_voiture,
            'couleur': self.couleur,
            'position': self.obtenir_position_tuple(),
            'vitesse': self.vitesse,
            'direction': self.direction
        }

    def __repr__(self) -> str:
        return (f"<Voiture id={self.id_voiture} type={self.type_voiture} "
                f"pos=({self.position_x:.1f}, {self.position_y:.1f}) "
                f"v={self.vitesse:.1f}/{self.vitesse_max:.1f} dir={self.direction}>")

    def __str__(self) -> str:
        return f"Voiture {self.id_voiture} ({self.type_voiture}) - {self.couleur}"