# traffic_manager.py - VERSION FINALE (BUG 'est_orange' CORRIGÉ)

import itertools
import random
from vehicules import Voiture

DIST_MIN = 35.0  # Distance minimale STRICTE
MAX_VOITURES = 50
TOLERANCE_VOIE = 5.0  # Tolérance pour séparer les voies
LIGNE_ARRET = 40.0  # Point au-delà duquel on ignore le feu


class TrafficManager:
    """Gère la circulation des voitures dans le carrefour."""

    _id_generator = itertools.count(1)

    def __init__(self, scenario):
        """Initialise le gestionnaire de trafic avec un scénario."""
        self.scenario = scenario
        self.voitures: list[Voiture] = []
        self._temps_depuis_derniere_voiture = 0.0

        # Astuce pour simuler un feu vert infini quand on a passé la ligne
        class FauxFeuVert:
            def est_rouge(self):
                return False

            def est_orange(self):  # AJOUTÉ POUR CORRIGER LE BUG GUI
                return False

            def est_vert(self):  # AJOUTÉ PAR SÉCURITÉ
                return True

        self.faux_feu_vert = FauxFeuVert()

    def ajouter_voiture(self, voiture: Voiture) -> bool:
        """Ajoute une voiture à la circulation."""
        if len(self.voitures) >= MAX_VOITURES:
            return False
        self.voitures.append(voiture)
        return True

    def supprimer_voiture(self, voiture: Voiture) -> bool:
        """Supprime une voiture de la circulation."""
        if voiture in self.voitures:
            self.voitures.remove(voiture)
            return True
        return False

    def supprimer_voitures_hors_limites(self) -> int:
        """Supprime les voitures sorties de l'écran."""
        voitures_hors = [v for v in self.voitures if v.est_hors_limites()]
        for voiture in voitures_hors:
            self.supprimer_voiture(voiture)
        return len(voitures_hors)

    def mettre_a_jour_voitures(self, feu_vertical, feu_horizontal, delta_t: float) -> None:
        """
        Met à jour toutes les voitures.
         ORDRE CRITIQUE:
        1. Appliquer les feux (calcul vitesse SANS déplacer)
        2. CAR-FOLLOWING (adapter vitesse selon voiture devant)
        3. Avancer toutes les voitures
        4. Gerer les distances (anti-collision)
        5. Nettoyer les voitures hors limites
        """
        #  1. APPLIQUER LES FEUX (deplacer=False!)
        # CORRECTION BUG: On vérifie si la voiture a dépassé l'intersection
        for voiture in self.voitures:
            feu_a_utiliser = None

            if voiture.direction == "NORD_SUD":
                vrai_feu = feu_vertical
                # Si on descend (v<0) et qu'on a dépassé Y=40 -> C'est bon
                # Si on monte (v>0) et qu'on a dépassé Y=-40 -> C'est bon
                passe_ligne = (voiture.vitesse_max < 0 and voiture.position_y < LIGNE_ARRET) or \
                              (voiture.vitesse_max > 0 and voiture.position_y > -LIGNE_ARRET)

                if passe_ligne:
                    feu_a_utiliser = self.faux_feu_vert
                else:
                    feu_a_utiliser = vrai_feu

                voiture.mettre_a_jour(feu_a_utiliser, delta_t, deplacer=False)

            else:  # EST_OUEST
                vrai_feu = feu_horizontal
                # Si on va gauche (v<0) et qu'on a dépassé X=40 -> C'est bon
                # Si on va droite (v>0) et qu'on a dépassé X=-40 -> C'est bon
                passe_ligne = (voiture.vitesse_max < 0 and voiture.position_x < LIGNE_ARRET) or \
                              (voiture.vitesse_max > 0 and voiture.position_x > -LIGNE_ARRET)

                if passe_ligne:
                    feu_a_utiliser = self.faux_feu_vert
                else:
                    feu_a_utiliser = vrai_feu

                voiture.mettre_a_jour(feu_a_utiliser, delta_t, deplacer=False)

        #  2. CAR-FOLLOWING APRÈS les feux
        self._appliquer_car_following()

        #  3. AVANCER TOUTES LES VOITURES
        for voiture in self.voitures:
            voiture.avancer(delta_t)

        #  4. ANTI-COLLISION
        self._gerer_distances()

        #  5. NETTOYER
        self.supprimer_voitures_hors_limites()

    def generer_voitures_si_necessaire(self, delta_t: float) -> Voiture:
        """Génère une nouvelle voiture selon la fréquence du scénario."""
        freq = self.scenario.frequence_arrivee_voitures
        if freq <= 0:
            return None

        self._temps_depuis_derniere_voiture += delta_t
        intervalle_moyen = 1.0 / freq

        if self._temps_depuis_derniere_voiture >= intervalle_moyen:
            self._temps_depuis_derniere_voiture = 0.0
            nouvelle_voiture = self._creer_voiture()

            if self.ajouter_voiture(nouvelle_voiture):
                return nouvelle_voiture

        return None

    def _creer_voiture(self) -> Voiture:
        """
        Crée une voiture avec VOIES FIXES ET STRICTES.
        """
        nouvel_id = next(self._id_generator)
        direction_arrivee = random.choice(["NORD", "SUD", "EST", "OUEST"])

        if direction_arrivee == "NORD":
            position_x = -30.0
            position_y = 450.0
            direction = "NORD_SUD"
            vitesse = -self.scenario.vitesse_moyenne_voitures  # Descend

        elif direction_arrivee == "SUD":
            position_x = 30.0
            position_y = -450.0
            direction = "NORD_SUD"
            vitesse = self.scenario.vitesse_moyenne_voitures  # Monte

        elif direction_arrivee == "EST":
            position_x = 450.0
            position_y = 30.0
            direction = "EST_OUEST"
            vitesse = -self.scenario.vitesse_moyenne_voitures  # Gauche

        else:  # OUEST
            position_x = -450.0
            position_y = -30.0
            direction = "EST_OUEST"
            vitesse = self.scenario.vitesse_moyenne_voitures  # Droite

        type_voiture = random.choice(["citadine", "berline", "camion"])
        couleur = random.choice(["#e74c3c", "#3498db", "#ecf0f1", "#2c3e50"])

        return Voiture(
            id_voiture=nouvel_id,
            type_voiture=type_voiture,
            couleur=couleur,
            position_x=position_x,
            position_y=position_y,
            vitesse_max=vitesse,
            direction=direction,
        )

    def _gerer_distances(self) -> None:
        """ GÈRE LES 4 VOIES STRICTEMENT SÉPARÉES."""
        nord_voie_gauche = [v for v in self.voitures
                            if v.direction == "NORD_SUD" and abs(v.position_x - (-30)) < TOLERANCE_VOIE]
        sud_voie_droite = [v for v in self.voitures
                           if v.direction == "NORD_SUD" and abs(v.position_x - 30) < TOLERANCE_VOIE]
        est_voie_haute = [v for v in self.voitures
                          if v.direction == "EST_OUEST" and abs(v.position_y - 30) < TOLERANCE_VOIE]
        ouest_voie_basse = [v for v in self.voitures
                            if v.direction == "EST_OUEST" and abs(v.position_y - (-30)) < TOLERANCE_VOIE]

        self._traiter_voie_verticale(nord_voie_gauche)
        self._traiter_voie_verticale(sud_voie_droite)
        self._traiter_voie_horizontale(est_voie_haute)
        self._traiter_voie_horizontale(ouest_voie_basse)

    def _traiter_voie_verticale(self, voitures: list) -> None:
        """
         Traite une voie VERTICALE.
        CORRIGÉ : Adapte le tri et le décalage selon le sens (Monte/Descend).
        """
        if len(voitures) < 2:
            return

        # Détection du sens : si vitesse négative, on descend (NORD)
        sens_descendant = voitures[0].vitesse_max < 0

        voitures.sort(key=lambda v: v.position_y, reverse=not sens_descendant)

        for i in range(1, len(voitures)):
            voiture_devant = voitures[i - 1]
            voiture_derriere = voitures[i]

            distance = abs(voiture_devant.position_y - voiture_derriere.position_y)

            if distance < DIST_MIN:

                signe = 1 if sens_descendant else -1
                voiture_derriere.position_y = voiture_devant.position_y + (signe * DIST_MIN)
                voiture_derriere.arreter()

    def _traiter_voie_horizontale(self, voitures: list) -> None:
        """
         Traite une voie HORIZONTALE.
        CORRIGÉ : Adapte le tri et le décalage selon le sens (Gauche/Droite).
        """
        if len(voitures) < 2:
            return

        # Détection du sens : si vitesse négative, on va à gauche (EST)
        sens_gauche = voitures[0].vitesse_max < 0

        voitures.sort(key=lambda v: v.position_x, reverse=not sens_gauche)

        for i in range(1, len(voitures)):
            voiture_devant = voitures[i - 1]
            voiture_derriere = voitures[i]

            distance = abs(voiture_devant.position_x - voiture_derriere.position_x)

            if distance < DIST_MIN:
                #  POSITION :

                signe = 1 if sens_gauche else -1
                voiture_derriere.position_x = voiture_devant.position_x + (signe * DIST_MIN)
                voiture_derriere.arreter()

    def _appliquer_car_following(self) -> None:
        """Adapte la vitesse selon la voiture devant."""
        nord_voie_gauche = [v for v in self.voitures
                            if v.direction == "NORD_SUD" and abs(v.position_x - (-30)) < TOLERANCE_VOIE]
        sud_voie_droite = [v for v in self.voitures
                           if v.direction == "NORD_SUD" and abs(v.position_x - 30) < TOLERANCE_VOIE]
        est_voie_haute = [v for v in self.voitures
                          if v.direction == "EST_OUEST" and abs(v.position_y - 30) < TOLERANCE_VOIE]
        ouest_voie_basse = [v for v in self.voitures
                            if v.direction == "EST_OUEST" and abs(v.position_y - (-30)) < TOLERANCE_VOIE]

        self._car_following_vertical(nord_voie_gauche)
        self._car_following_vertical(sud_voie_droite)
        self._car_following_horizontal(est_voie_haute)
        self._car_following_horizontal(ouest_voie_basse)

    def _car_following_vertical(self, voitures: list) -> None:
        if len(voitures) < 2:
            return

        # Coreection traiter_voie_verticale
        sens_descendant = voitures[0].vitesse_max < 0
        voitures.sort(key=lambda v: v.position_y, reverse=not sens_descendant)

        for i in range(1, len(voitures)):
            distance = abs(voitures[i - 1].position_y - voitures[i].position_y)

            if voitures[i - 1].vitesse == 0.0:
                if distance < 50.0:
                    voitures[i].arreter()
            elif abs(voitures[i - 1].vitesse) < abs(voitures[i].vitesse):
                if distance < 50.0:
                    voitures[i].ralentir(0.3)

    def _car_following_horizontal(self, voitures: list) -> None:
        if len(voitures) < 2:
            return

        #Coreection  traiter_voie_horizontale
        sens_gauche = voitures[0].vitesse_max < 0
        voitures.sort(key=lambda v: v.position_x, reverse=not sens_gauche)

        for i in range(1, len(voitures)):
            distance = abs(voitures[i - 1].position_x - voitures[i].position_x)

            if voitures[i - 1].vitesse == 0.0:
                if distance < 50.0:
                    voitures[i].arreter()
            elif abs(voitures[i - 1].vitesse) < abs(voitures[i].vitesse):
                if distance < 50.0:
                    voitures[i].ralentir(0.3)

    def obtenir_voitures(self) -> list[Voiture]:
        return self.voitures.copy()

    def obtenir_nombre_voitures(self) -> int:
        return len(self.voitures)

    def obtenir_voitures_par_direction(self, direction: str) -> list[Voiture]:
        return [v for v in self.voitures if v.direction == direction]

    def reinitialiser(self) -> None:
        self.voitures.clear()
        self._temps_depuis_derniere_voiture = 0.0
        TrafficManager._id_generator = itertools.count(1)

    def __repr__(self) -> str:
        return f"<TrafficManager {len(self.voitures)} voitures>"

    def __str__(self) -> str:
        return f"Trafic: {len(self.voitures)} voitures"
