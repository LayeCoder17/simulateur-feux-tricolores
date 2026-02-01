# traffic_light_manager.py

from traffic_light import FeuTricolore, EtatFeu
from scenarios import Scenario


class TrafficLightManager:
    """Gère les 4 feux du carrefour avec une logique de phases coordonnées."""

    # Définition des phases
    PHASE_VERTICAL = "VERTICAL"  # NORD-SUD au VERT
    PHASE_HORIZONTAL = "HORIZONTAL"  # EST-OUEST au VERT

    def __init__(self, scenario: Scenario):
        """
        Initialise le gestionnaire de feux.

        Args:
            scenario: Scénario à utiliser pour tous les feux
        """
        self.scenario = scenario
        self.phase_actuelle = self.PHASE_VERTICAL

        # Créer 4 feux indépendants (un par coin)
        self.feu_ne = FeuTricolore(scenario)  # NORD-EST
        self.feu_nw = FeuTricolore(scenario)  # NORD-OUEST
        self.feu_se = FeuTricolore(scenario)  # SUD-EST
        self.feu_sw = FeuTricolore(scenario)  # SUD-OUEST

        # Dictionnaire pour accès facile
        self.feux = {
            "NE": self.feu_ne,
            "NW": self.feu_nw,
            "SE": self.feu_se,
            "SW": self.feu_sw,
        }

        # En mode nuit, tous les feux en ORANGE (pas de phase)
        if self.scenario.est_mode_nuit():
            self._appliquer_mode_nuit()
        else:
            # Initialiser en phase VERTICAL (NORD-SUD au VERT)
            self._appliquer_phase_vertical()

        self.temps_phase = 0.0
        self.duree_phase_actuelle = self.scenario.duree_vert

    def _appliquer_mode_nuit(self) -> None:
        """ NOUVEAU: Applique le mode nuit (tous les feux en ORANGE clignotant)."""
        for feu in self.feux.values():
            feu.forcer_etat(EtatFeu.ORANGE)
        self.temps_phase = 0.0
        self.phase_actuelle = "ORANGE_CLIGNOTANT"  #  Pas de phase

    def _appliquer_phase_vertical(self) -> None:
        """
        Applique la phase VERTICAL.
        NORD-SUD: VERT
        EST-OUEST: ROUGE
        """
        self.phase_actuelle = self.PHASE_VERTICAL

        # Routes VERTICALES (NORD-SUD) au VERT ← NW et SE
        self.feu_nw.forcer_etat(EtatFeu.VERT)
        self.feu_se.forcer_etat(EtatFeu.VERT)

        # Routes HORIZONTALES (EST-OUEST) au ROUGE ← NE et SW
        self.feu_ne.forcer_etat(EtatFeu.ROUGE)
        self.feu_sw.forcer_etat(EtatFeu.ROUGE)

        self.temps_phase = 0.0
        self.duree_phase_actuelle = self.scenario.duree_vert

    def _appliquer_phase_horizontal(self) -> None:
        """
        Applique la phase HORIZONTAL.
        EST-OUEST: VERT
        NORD-SUD: ROUGE
        """
        self.phase_actuelle = self.PHASE_HORIZONTAL

        # Routes HORIZONTALES (EST-OUEST) au VERT ← NE et SW
        # CORRECTION: Utiliser forcer_etat() au lieu de while/changer_etat()
        self.feu_ne.forcer_etat(EtatFeu.VERT)
        self.feu_sw.forcer_etat(EtatFeu.VERT)

        # Routes VERTICALES (NORD-SUD) au ROUGE ← NW et SE
        self.feu_nw.forcer_etat(EtatFeu.ROUGE)
        self.feu_se.forcer_etat(EtatFeu.ROUGE)

        self.temps_phase = 0.0
        self.duree_phase_actuelle = self.scenario.duree_vert

    def changer_phase(self) -> None:
        """Bascule à la phase suivante."""
        #  SÉCURITÉ: Ne JAMAIS changer de phase en mode nuit
        if self.scenario.est_mode_nuit():
            return

        if self.phase_actuelle == self.PHASE_VERTICAL:
            # VERTICAL → HORIZONTAL
            # D'abord passer tous les feux à ORANGE
            self._passer_tous_orange()
            self.duree_phase_actuelle = self.scenario.duree_orange + self.scenario.duree_rouge

            # Puis appliquer la nouvelle phase
            self._appliquer_phase_horizontal()
        else:
            # HORIZONTAL → VERTICAL
            # D'abord passer tous les feux à ORANGE
            self._passer_tous_orange()
            self.duree_phase_actuelle = self.scenario.duree_orange + self.scenario.duree_rouge

            # Puis appliquer la nouvelle phase
            self._appliquer_phase_vertical()

    def _passer_tous_orange(self) -> None:
        """Passe tous les feux au ORANGE avant le changement de phase."""
        # CORRECTION: Utiliser forcer_etat() au lieu de while/changer_etat()
        for feu in self.feux.values():
            feu.forcer_etat(EtatFeu.ORANGE)

    def mettre_a_jour(self, delta_t: float) -> None:
        """
        Met à jour tous les feux et gère le changement de phase.

        Args:
            delta_t: Intervalle de temps en secondes
        """
        if delta_t <= 0:
            raise ValueError("delta_t doit être > 0")

        # Mettre à jour chaque feu
        for feu in self.feux.values():
            feu.mettre_a_jour(delta_t)

        # CORRECTION: En mode nuit, NE PAS changer de phase (juste clignoter)
        if self.scenario.est_mode_nuit():
            return  # Sortir immédiatement, pas de changement de phase

        # Tracker le temps de phase
        self.temps_phase += delta_t

        # Déterminer la durée de la phase actuelle
        if self.phase_actuelle == self.PHASE_VERTICAL:
            duree_phase = self.scenario.duree_vert + self.scenario.duree_orange
        else:
            duree_phase = self.scenario.duree_vert + self.scenario.duree_orange

        # Changer de phase si nécessaire
        if self.temps_phase >= duree_phase:
            self.changer_phase()

    def appliquer_scenario(self, scenario: Scenario) -> None:
        """Applique un nouveau scénario à tous les feux."""
        self.scenario = scenario

        for feu in self.feux.values():
            feu.appliquer_scenario(scenario)

        # Si mode nuit, appliquer mode nuit au lieu de phase
        if self.scenario.est_mode_nuit():
            self._appliquer_mode_nuit()
        else:
            # Réinitialiser la phase actuelle
            self._appliquer_phase_vertical()

    def obtenir_etat_feu(self, position: str) -> str:
        """
        Retourne l'état d'un feu spécifique.

        Args:
            position: "NE", "NW", "SE" ou "SW"

        Returns:
            État du feu (ROUGE, ORANGE, VERT)
        """
        if position not in self.feux:
            raise ValueError(f"Position invalide: {position}. Doit être NE, NW, SE ou SW")
        return self.feux[position].etat_actuel.value

    def obtenir_etat_affichage_feu(self, position: str) -> str:
        """
        Retourne l'état d'affichage d'un feu (gère clignotement).

        Args:
            position: "NE", "NW", "SE" ou "SW"
        """
        if position not in self.feux:
            raise ValueError(f"Position invalide: {position}")
        return self.feux[position].obtenir_etat_affichage()

    def obtenir_tous_les_etats(self) -> dict:
        """Retourne l'état de tous les 4 feux."""
        return {
            "NE": self.obtenir_etat_feu("NE"),
            "NW": self.obtenir_etat_feu("NW"),
            "SE": self.obtenir_etat_feu("SE"),
            "SW": self.obtenir_etat_feu("SW"),
        }

    def obtenir_tous_les_etats_affichage(self) -> dict:
        """Retourne l'état d'affichage de tous les 4 feux."""
        return {
            "NE": self.obtenir_etat_affichage_feu("NE"),
            "NW": self.obtenir_etat_affichage_feu("NW"),
            "SE": self.obtenir_etat_affichage_feu("SE"),
            "SW": self.obtenir_etat_affichage_feu("SW"),
        }

    def obtenir_phase_actuelle(self) -> str:
        """Retourne la phase actuelle (VERTICAL ou HORIZONTAL)."""
        return self.phase_actuelle

    def obtenir_info_manager(self) -> dict:
        """Retourne un dictionnaire avec l'état complet du gestionnaire."""
        return {
            'phase': self.phase_actuelle,
            'temps_phase': self.temps_phase,
            'etats_feux': self.obtenir_tous_les_etats(),
            'scenario': self.scenario.nom,
        }

    def reinitialiser(self) -> None:
        """Réinitialise tous les feux à l'état initial."""
        for feu in self.feux.values():
            feu.__init__(self.scenario)

        # CORRECTION: Appliquer le bon mode
        if self.scenario.est_mode_nuit():
            self._appliquer_mode_nuit()
        else:
            self._appliquer_phase_vertical()

    def forcer_phase(self, phase: str) -> None:
        """
        Force une phase spécifique.

        Args:
            phase: "VERTICAL" ou "HORIZONTAL"
        """
        if phase == self.PHASE_VERTICAL:
            self._appliquer_phase_vertical()
        elif phase == self.PHASE_HORIZONTAL:
            self._appliquer_phase_horizontal()
        else:
            raise ValueError(f"Phase invalide: {phase}")

    def __repr__(self) -> str:
        etats = self.obtenir_tous_les_etats()
        return (f"<TrafficLightManager Phase={self.phase_actuelle} "
                f"NE={etats['NE']} NW={etats['NW']} "
                f"SE={etats['SE']} SW={etats['SW']}>")

    def __str__(self) -> str:
        etats = self.obtenir_tous_les_etats()
        return (f"Feux Carrefour | Phase: {self.phase_actuelle} | "
                f"NE:{etats['NE']} NW:{etats['NW']} "
                f"SE:{etats['SE']} SW:{etats['SW']}")