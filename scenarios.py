# scenarios.py - VERSION OPTIMISÉE (DURÉES ÉQUILIBRÉES)

class Scenario:


    def __init__(
            self,
            nom: str,
            duree_vert: float,
            duree_orange: float,
            duree_rouge: float,
            vitesse_moyenne_voitures: float,
            frequence_arrivee_voitures: float,
    ):

        self.nom = nom

        # Validation des durées des feux
        for label, duree in (
                ("vert", duree_vert),
                ("orange", duree_orange),
                ("rouge", duree_rouge),
        ):
            if duree <= 0:
                raise ValueError(f"La durée du feu {label} doit être > 0")

        self.duree_vert = duree_vert
        self.duree_orange = duree_orange
        self.duree_rouge = duree_rouge

        # Validation de la vitesse
        if vitesse_moyenne_voitures <= 0:
            raise ValueError("La vitesse moyenne doit être > 0")
        self.vitesse_moyenne_voitures = vitesse_moyenne_voitures

        # Validation de la fréquence
        if frequence_arrivee_voitures < 0:
            raise ValueError("La fréquence d'arrivée doit être >= 0")
        self.frequence_arrivee_voitures = frequence_arrivee_voitures

    def obtenir_duree_totale_cycle(self) -> float:
        """Retourne la durée totale du cycle du feu (R+V+O)."""
        return self.duree_rouge + self.duree_vert + self.duree_orange

    def obtenir_duree_phase(self) -> float:
        """Retourne la durée d'une phase (VERT + ORANGE)."""
        return self.duree_vert + self.duree_orange

    def obtenir_ratio_vert(self) -> float:
        """Retourne le ratio de temps vert dans un cycle (0.0 à 1.0)."""
        duree_totale = self.obtenir_duree_totale_cycle()
        return self.duree_vert / duree_totale if duree_totale > 0 else 0.0

    def obtenir_info_scenario(self) -> dict:
        """Retourne un dictionnaire avec toutes les infos du scénario."""
        return {
            'nom': self.nom,
            'duree_vert': self.duree_vert,
            'duree_orange': self.duree_orange,
            'duree_rouge': self.duree_rouge,
            'vitesse_moyenne': self.vitesse_moyenne_voitures,
            'frequence_arrivee': self.frequence_arrivee_voitures,
            'duree_cycle': self.obtenir_duree_totale_cycle(),
            'duree_phase': self.obtenir_duree_phase(),
            'ratio_vert': self.obtenir_ratio_vert()
        }

    def est_mode_manuel(self) -> bool:
        """Vérifie si le scénario est en mode manuel."""
        return self.nom.lower() == "mode manuel"

    def est_mode_nuit(self) -> bool:
        """Vérifie si le scénario est en mode nuit."""
        return self.nom.lower() == "mode nuit"

    def est_heure_pointe(self) -> bool:
        """Vérifie si le scénario est heure de pointe."""
        return self.nom.lower() == "heure de pointe"

    def __repr__(self) -> str:
        return (
            f"<Scenario {self.nom} "
            f"V:{self.duree_vert}s "
            f"O:{self.duree_orange}s "
            f"R:{self.duree_rouge}s "
            f"v_moy={self.vitesse_moyenne_voitures} "
            f"freq={self.frequence_arrivee_voitures}>"
        )

    def __str__(self) -> str:
        return f"Scénario: {self.nom} | Cycle: {self.obtenir_duree_totale_cycle():.1f}s"




# Scénario 1: Circulation normale (DURÉES AUGMENTÉES POUR SYNCHRONISATION)
SCENARIO_NORMAL = Scenario(
    nom="Circulation normale",
    duree_vert=12.0,
    duree_orange=4.0,
    duree_rouge=16.1,
    vitesse_moyenne_voitures=40.0,
    frequence_arrivee_voitures=0.3
)

SCENARIO_HEURE_POINTE = Scenario(
    nom="Heure de pointe",
    duree_vert=40.0,
    duree_orange=3.0,
    duree_rouge=43.1,
    vitesse_moyenne_voitures=40.0,
    frequence_arrivee_voitures=2.0
)



SCENARIO_MODE_NUIT = Scenario(
    nom="Mode nuit",
    duree_vert=8.0,
    duree_orange=2.0,
    duree_rouge=10.1,
    vitesse_moyenne_voitures=50.0,
    frequence_arrivee_voitures=0.1
)


SCENARIO_MANUEL = Scenario(
    nom="Mode manuel",
    duree_vert=12.0,
    duree_orange=4.0,
    duree_rouge=16.1,
    vitesse_moyenne_voitures=40.0,
    frequence_arrivee_voitures=0.5
)


def obtenir_tous_les_scenarios() -> dict:
    """Retourne tous les scénarios disponibles dans un dictionnaire."""
    return {
        "normal": SCENARIO_NORMAL,
        "heure_pointe": SCENARIO_HEURE_POINTE,
        "mode_nuit": SCENARIO_MODE_NUIT,
        "manuel": SCENARIO_MANUEL,
    }


def obtenir_scenario_par_nom(nom: str):

    scenarios = obtenir_tous_les_scenarios()
    return scenarios.get(nom.lower())


def lister_tous_les_noms_scenarios() -> list:
    """Retourne la liste de tous les noms de scénarios disponibles."""
    return list(obtenir_tous_les_scenarios().keys())