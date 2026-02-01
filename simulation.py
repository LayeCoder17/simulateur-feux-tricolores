# simulation.py - VERSION COMPLÈTE AVEC MODE MANUEL

from traffic_light_manager import TrafficLightManager, EtatFeu
from scenarios import Scenario
from traffic_manager import TrafficManager


class Simulation:
    """Gère la simulation complète du carrefour avec 4 feux coordonnés."""

    def __init__(self, scenario: Scenario, delta_t: float = 0.1):
        """
        Initialise la simulation.

        Args:
            scenario: Scénario à utiliser
            delta_t: Intervalle de temps par tick (secondes)
        """
        self.scenario = scenario
        self.delta_t = delta_t
        self.feu_manager = TrafficLightManager(scenario)
        self.traffic_manager = TrafficManager(scenario)
        self.en_cours = False
        self.en_pause = False
        self.temps = 0.0
        self.mode_manuel = scenario.est_mode_manuel()
        self.nombre_ticks = 0

    def demarrer(self) -> None:
        """Démarre la simulation."""
        self.en_cours = True
        self.en_pause = False

    def pause(self) -> None:
        """Met la simulation en pause."""
        self.en_pause = True
        self.en_cours = False

    def reprendre(self) -> None:
        """Reprend la simulation après une pause."""
        self.en_cours = True
        self.en_pause = False

    def arreter(self) -> None:
        """Arrête complètement la simulation et la réinitialise."""
        self.en_cours = False
        self.en_pause = False
        self.temps = 0.0
        self.nombre_ticks = 0
        self.feu_manager = TrafficLightManager(self.scenario)
        self.traffic_manager = TrafficManager(self.scenario)

    def changer_scenario(self, nouveau_scenario: Scenario) -> None:
        """
        Change le scénario de la simulation.

        Args:
            nouveau_scenario: Nouveau scénario à appliquer
        """
        if not isinstance(nouveau_scenario, Scenario):
            raise ValueError("Le nouveau scénario doit être une instance de Scenario")

        self.scenario = nouveau_scenario
        self.mode_manuel = nouveau_scenario.est_mode_manuel()
        self.feu_manager.appliquer_scenario(nouveau_scenario)
        self.traffic_manager.scenario = nouveau_scenario

    def forcer_phase(self, phase: str) -> None:
        """
        Force une phase spécifique du feu (mode manuel uniquement).

        Args:
            phase: "VERTICAL" ou "HORIZONTAL"
        """
        if not self.mode_manuel:
            raise ValueError("Le forçage de phase n'est disponible qu'en mode manuel")
        self.feu_manager.forcer_phase(phase)

    def forcer_etat_feu(self, position: str, nouvel_etat: EtatFeu) -> None:
        """
        Force un feu spécifique à un état (mode manuel uniquement).

        Args:
            position: "NE", "NW", "SE" ou "SW"
            nouvel_etat: EtatFeu à forcer
        """
        if not self.mode_manuel:
            raise ValueError("Le forçage d'état n'est disponible qu'en mode manuel")
        self.feu_manager.feux[position].forcer_etat(nouvel_etat)

    def forcer_etat_feu_manuel(self, nouvel_etat: EtatFeu) -> None:
        """Force les feux en mode manuel avec basculement."""
        if self.scenario.est_mode_manuel():
            if nouvel_etat.value == "VERT" or nouvel_etat.value == "ROUGE":
                # Bascule VERTICAL ↔ HORIZONTAL
                if self.feu_manager.phase_actuelle == "VERTICAL":
                    # Passer à HORIZONTAL
                    self.feu_manager.feu_ne.forcer_etat(EtatFeu.VERT)
                    self.feu_manager.feu_sw.forcer_etat(EtatFeu.VERT)
                    self.feu_manager.feu_nw.forcer_etat(EtatFeu.ROUGE)
                    self.feu_manager.feu_se.forcer_etat(EtatFeu.ROUGE)
                    self.feu_manager.phase_actuelle = "HORIZONTAL"
                    print("🎮 Phase: HORIZONTAL")
                else:
                    # Passer à VERTICAL
                    self.feu_manager.feu_nw.forcer_etat(EtatFeu.VERT)
                    self.feu_manager.feu_se.forcer_etat(EtatFeu.VERT)
                    self.feu_manager.feu_ne.forcer_etat(EtatFeu.ROUGE)
                    self.feu_manager.feu_sw.forcer_etat(EtatFeu.ROUGE)
                    self.feu_manager.phase_actuelle = "VERTICAL"
                    print("🎮 Phase: VERTICAL")
            else:  # ORANGE
                # Tous en ORANGE
                for feu in self.feu_manager.feux.values():
                    feu.forcer_etat(EtatFeu.ORANGE)
                print("Tous les feux: ORANGE")

    def tick(self) -> bool:
        """
        Exécute une étape de simulation.

        Returns:
            True si la simulation s'est exécutée, False sinon
        """
        if not self.en_cours or self.en_pause:
            return False

        #  EN MODE MANUEL: NE PAS mettre à jour les feux automatiquement!
        if not self.scenario.est_mode_manuel():
            self.feu_manager.mettre_a_jour(self.delta_t)

        # Génération de nouvelles voitures
        self.traffic_manager.generer_voitures_si_necessaire(self.delta_t)

        # Mise à jour de toutes les voitures avec les bons feux
        # VERTICAL (NW + SE) pour direction NORD-SUD
        feu_vertical = self.feu_manager.feu_nw
        # HORIZONTAL (NE + SW) pour direction EST-OUEST
        feu_horizontal = self.feu_manager.feu_ne

        self.traffic_manager.mettre_a_jour_voitures(feu_vertical, feu_horizontal, self.delta_t)

        # Incrémentation du temps
        self.temps += self.delta_t
        self.nombre_ticks += 1

        return True

    def est_en_cours(self) -> bool:
        """Retourne True si la simulation est en cours."""
        return self.en_cours

    def est_en_pause(self) -> bool:
        """Retourne True si la simulation est en pause."""
        return self.en_pause

    def obtenir_temps_elapsed(self) -> float:
        """Retourne le temps écoulé en secondes."""
        return self.temps

    def obtenir_phase_actuelle(self) -> str:
        """Retourne la phase actuelle (VERTICAL ou HORIZONTAL)."""
        return self.feu_manager.obtenir_phase_actuelle()

    def obtenir_etat_feu(self, position: str) -> str:
        """
        Retourne l'état d'un feu spécifique.

        Args:
            position: "NE", "NW", "SE" ou "SW"

        Returns:
            État du feu (ROUGE, ORANGE, VERT)
        """
        return self.feu_manager.obtenir_etat_feu(position)

    def obtenir_etat_feu_affichage(self, position: str) -> str:
        """
        Retourne l'état d'affichage d'un feu (gère clignotement).

        Args:
            position: "NE", "NW", "SE" ou "SW"
        """
        return self.feu_manager.obtenir_etat_affichage_feu(position)

    def obtenir_tous_les_etats_feux(self) -> dict:
        """Retourne l'état de tous les 4 feux."""
        return self.feu_manager.obtenir_tous_les_etats()

    def obtenir_tous_les_etats_feux_affichage(self) -> dict:
        """Retourne l'état d'affichage de tous les 4 feux."""
        return self.feu_manager.obtenir_tous_les_etats_affichage()

    def obtenir_nombre_voitures(self) -> int:
        """Retourne le nombre total de voitures en circulation."""
        return self.traffic_manager.obtenir_nombre_voitures()

    def obtenir_voitures(self):
        """Retourne la liste de toutes les voitures."""
        return self.traffic_manager.obtenir_voitures()

    def obtenir_info_simulation(self) -> dict:
        """Retourne un dictionnaire avec l'état complet de la simulation."""
        etats_feux = self.obtenir_tous_les_etats_feux()
        return {
            'temps': self.temps,
            'ticks': self.nombre_ticks,
            'en_cours': self.en_cours,
            'en_pause': self.en_pause,
            'phase_actuelle': self.obtenir_phase_actuelle(),
            'etats_feux': etats_feux,
            'nombre_voitures': self.obtenir_nombre_voitures(),
            'scenario': self.scenario.nom,
            'mode_manuel': self.mode_manuel,
        }

    def obtenir_statistiques(self) -> dict:
        """Retourne les statistiques de la simulation."""
        voitures = self.traffic_manager.obtenir_voitures()
        voitures_ns = self.traffic_manager.obtenir_voitures_par_direction("NORD_SUD")
        voitures_eo = self.traffic_manager.obtenir_voitures_par_direction("EST_OUEST")

        vitesse_moyenne = 0.0
        if len(voitures) > 0:
            vitesse_moyenne = sum(v.vitesse for v in voitures) / len(voitures)

        duree_cycle = self.scenario.obtenir_duree_totale_cycle()
        nombre_cycles = (self.nombre_ticks * self.delta_t) / duree_cycle if duree_cycle > 0 else 0

        return {
            'total_voitures': len(voitures),
            'voitures_nord_sud': len(voitures_ns),
            'voitures_est_ouest': len(voitures_eo),
            'vitesse_moyenne': vitesse_moyenne,
            'temps_total': self.temps,
            'nombre_cycles_feu': nombre_cycles,
            'phase_actuelle': self.obtenir_phase_actuelle()
        }

    def reinitialiser(self) -> None:
        """Réinitialise complètement la simulation."""
        self.arreter()

    def __repr__(self) -> str:
        etat = "EN COURS" if self.en_cours else ("EN PAUSE" if self.en_pause else "ARRÊTÉE")
        etats = self.obtenir_tous_les_etats_feux()
        return (f"<Simulation {etat} | "
                f"Scénario: {self.scenario.nom} | "
                f"Phase: {self.obtenir_phase_actuelle()} | "
                f"Feux: NE={etats['NE']} NW={etats['NW']} "
                f"SE={etats['SE']} SW={etats['SW']} | "
                f"Voitures: {self.obtenir_nombre_voitures()} | "
                f"Temps: {self.temps:.1f}s>")

    def __str__(self) -> str:
        info = self.obtenir_info_simulation()
        return (f"Simulation [{info['scenario']}] - "
                f"Phase: {info['phase_actuelle']} | "
                f"Voitures: {info['nombre_voitures']} | "
                f"Temps: {info['temps']:.1f}s")