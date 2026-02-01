# traffic_light.py

from enum import Enum


class EtatFeu(Enum):
    """Énumération des états possibles d'un feu tricolore."""
    ROUGE = "ROUGE"
    ORANGE = "ORANGE"
    VERT = "VERT"


class FeuTricolore:
    """Représente un feu tricolore individuel."""

    def __init__(self, scenario):
        """
        Initialise un feu tricolore.

        Args:
            scenario: Scénario contenant les durées des feux
        """
        self._valider_scenario(scenario)
        self.scenario = scenario

        # En mode nuit, démarrer en ORANGE
        if self.scenario.est_mode_nuit():
            self.etat_actuel = EtatFeu.ORANGE
            self.duree_etat = float('inf')  # Durée infinie en mode nuit!
        else:
            self.etat_actuel = EtatFeu.ROUGE
            self.duree_etat = self.scenario.duree_rouge

        self.temps_clignotement = 0.0
        self.orange_visible = True

    @staticmethod
    def _valider_scenario(scenario):
        """Valide que les durées du scénario sont correctes."""
        for duree in (scenario.duree_vert,
                      scenario.duree_orange,
                      scenario.duree_rouge):
            if duree <= 0:
                raise ValueError("Les durées de feu doivent être > 0")

    def changer_etat(self):
        """Change l'état du feu selon le cycle: ROUGE -> VERT -> ORANGE -> ROUGE"""
        #  SÉCURITÉ: Ne JAMAIS changer en mode nuit
        if self.scenario.est_mode_nuit():
            return

        if self.etat_actuel is EtatFeu.ROUGE:
            self.etat_actuel = EtatFeu.VERT
            self.duree_etat = self.scenario.duree_vert
        elif self.etat_actuel is EtatFeu.VERT:
            self.etat_actuel = EtatFeu.ORANGE
            self.duree_etat = self.scenario.duree_orange
        else:  # ORANGE
            self.etat_actuel = EtatFeu.ROUGE
            self.duree_etat = self.scenario.duree_rouge

        self.temps_clignotement = 0.0
        self.orange_visible = True

    def mettre_a_jour(self, delta_t: float) -> None:
        """
        Met à jour l'état du feu tricolore.

        Args:
            delta_t: Intervalle de temps en secondes
        """
        if delta_t <= 0:
            raise ValueError("delta_t doit être > 0")

        #  MODE NUIT: Seulement gérer le clignotement
        if self.scenario.est_mode_nuit():
            # Forcer ORANGE
            if self.etat_actuel is not EtatFeu.ORANGE:
                self.etat_actuel = EtatFeu.ORANGE
                self.duree_etat = float('inf')

            # Gérer le clignotement
            self.temps_clignotement += delta_t
            if self.temps_clignotement >= 0.5:  # Clignotement chaque 0.5s
                self.orange_visible = not self.orange_visible
                self.temps_clignotement = 0.0
            return  #  Sortir ici, ne rien faire d'autre!

        #  MODE NORMAL: Gérer les changements d'état
        self.duree_etat -= delta_t

        # Changement d'état automatique
        if self.duree_etat <= 0:
            self.changer_etat()

    def appliquer_scenario(self, scenario):
        """
        Applique un nouveau scénario et réinitialise les durées.

        Args:
            scenario: Nouveau scénario à appliquer
        """
        self._valider_scenario(scenario)
        self.scenario = scenario

        # CORRECTION: Si mode nuit, forcer ORANGE avec durée infinie
        if self.scenario.est_mode_nuit():
            self.etat_actuel = EtatFeu.ORANGE
            self.duree_etat = float('inf')
        elif self.est_rouge():
            self.duree_etat = self.scenario.duree_rouge
        elif self.est_vert():
            self.duree_etat = self.scenario.duree_vert
        else:
            self.duree_etat = self.scenario.duree_orange

        self.temps_clignotement = 0.0
        self.orange_visible = True

    def forcer_etat(self, nouvel_etat: EtatFeu):
        """
        Force le feu à un état spécifique (pour mode manuel).

        Args:
            nouvel_etat: EtatFeu à forcer
        """
        if not isinstance(nouvel_etat, EtatFeu):
            raise ValueError("L'état doit être une instance de EtatFeu")

        self.etat_actuel = nouvel_etat

        # En mode nuit, durée infinie
        if self.scenario.est_mode_nuit():
            self.duree_etat = float('inf')
        elif self.est_rouge():
            self.duree_etat = self.scenario.duree_rouge
        elif self.est_vert():
            self.duree_etat = self.scenario.duree_vert
        else:
            self.duree_etat = self.scenario.duree_orange

        self.temps_clignotement = 0.0
        self.orange_visible = True

    def est_rouge(self) -> bool:
        """Vérifie si le feu est rouge."""
        return self.etat_actuel is EtatFeu.ROUGE

    def est_vert(self) -> bool:
        """Vérifie si le feu est vert."""
        return self.etat_actuel is EtatFeu.VERT

    def est_orange(self) -> bool:
        """Vérifie si le feu est orange."""
        return self.etat_actuel is EtatFeu.ORANGE

    def orange_est_visible(self) -> bool:
        """Retourne si l'orange doit être affiché (gestion du clignotement)."""
        return self.orange_visible

    def obtenir_etat_affichage(self) -> str:
        """
        Retourne l'état à afficher (gère le clignotement en mode nuit).

        Returns:
            État du feu: "ROUGE", "ORANGE", "VERT" ou "NOIR" (orange caché)
        """
        if self.etat_actuel is EtatFeu.ORANGE and not self.orange_visible:
            return "NOIR"  # Orange caché (clignotement)
        return self.etat_actuel.value

    def obtenir_duree_restante(self) -> float:
        """Retourne la durée restante avant changement d'état."""
        return max(0.0, self.duree_etat) if self.duree_etat != float('inf') else 0.0

    def obtenir_info_feu(self) -> dict:
        """Retourne un dictionnaire avec les infos du feu."""
        return {
            'etat': self.etat_actuel.value,
            'etat_affichage': self.obtenir_etat_affichage(),
            'duree_restante': self.obtenir_duree_restante(),
            'scenario': self.scenario.nom
        }

    def __repr__(self) -> str:
        duree = "∞" if self.duree_etat == float('inf') else f"{self.duree_etat:.2f}s"
        return f"<FeuTricolore etat={self.etat_actuel.value} reste={duree}>"

    def __str__(self) -> str:
        duree = "∞" if self.duree_etat == float('inf') else f"{self.obtenir_duree_restante():.1f}s"
        return f"Feu {self.etat_actuel.value} ({duree})"
