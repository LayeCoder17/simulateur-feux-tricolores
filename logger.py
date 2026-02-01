# logger.py

from datetime import datetime
import json
from pathlib import Path


class EventLogger:
    """Système de journalisation des événements de la simulation."""

    def __init__(self, fichier_log: str = "simulation.log"):
        """
        Initialise le logger.

        Args:
            fichier_log: Chemin du fichier de log
        """
        self.fichier_log = Path(fichier_log)
        self.events = []

        # Créer le fichier s'il n'existe pas
        if not self.fichier_log.exists():
            self.fichier_log.touch()

        # Charger les logs existants
        self._charger_logs()

    def _charger_logs(self):
        """Charge les logs existants du fichier."""
        try:
            if self.fichier_log.exists() and self.fichier_log.stat().st_size > 0:
                with open(self.fichier_log, 'r', encoding='utf-8') as f:
                    for ligne in f:
                        try:
                            event = json.loads(ligne.strip())
                            self.events.append(event)
                        except json.JSONDecodeError:
                            continue
        except Exception as e:
            print(f"Erreur lors du chargement des logs: {e}")

    def log_action(self, type_action: str, description: str, scenario: str = "", details: dict = None):
        """
        Enregistre une action dans les logs.

        Args:
            type_action: Type d'action (SIMULATION, SCÉNARIO, FEU, VOITURE, etc.)
            description: Description de l'action
            scenario: Scénario actif
            details: Détails supplémentaires (optionnel)
        """
        event = {
            'timestamp': datetime.now().isoformat(),
            'type_action': type_action,
            'description': description,
            'scenario': scenario,
            'details': details or {}
        }

        self.events.append(event)
        self._sauvegarder_event(event)

        # Afficher dans la console aussi
        self._afficher_log(event)

    def log_demarrage(self, scenario: str):
        """Enregistre le démarrage de la simulation."""
        self.log_action(
            type_action="SIMULATION",
            description="Démarrage de la simulation",
            scenario=scenario,
            details={'action': 'DEMARRAGE'}
        )

    def log_pause(self, scenario: str):
        """Enregistre la mise en pause."""
        self.log_action(
            type_action="SIMULATION",
            description="Simulation mise en pause",
            scenario=scenario,
            details={'action': 'PAUSE'}
        )

    def log_reprise(self, scenario: str):
        """Enregistre la reprise après pause."""
        self.log_action(
            type_action="SIMULATION",
            description="Simulation reprise",
            scenario=scenario,
            details={'action': 'REPRISE'}
        )

    def log_arret(self, scenario: str):
        """Enregistre l'arrêt de la simulation."""
        self.log_action(
            type_action="SIMULATION",
            description="Arrêt de la simulation",
            scenario=scenario,
            details={'action': 'ARRET'}
        )

    def log_reset(self, scenario: str):
        """Enregistre la réinitialisation."""
        self.log_action(
            type_action="SIMULATION",
            description="Réinitialisation de la simulation",
            scenario=scenario,
            details={'action': 'RESET'}
        )

    def log_changement_scenario(self, ancien_scenario: str, nouveau_scenario: str):
        """Enregistre le changement de scénario."""
        self.log_action(
            type_action="SCÉNARIO",
            description=f"Changement de scénario: {ancien_scenario} → {nouveau_scenario}",
            scenario=nouveau_scenario,
            details={
                'ancien_scenario': ancien_scenario,
                'nouveau_scenario': nouveau_scenario
            }
        )

    def log_changement_feu(self, ancien_etat: str, nouvel_etat: str, scenario: str):
        """Enregistre le changement d'état du feu."""
        self.log_action(
            type_action="FEU",
            description=f"Changement feu: {ancien_etat} → {nouvel_etat}",
            scenario=scenario,
            details={
                'ancien_etat': ancien_etat,
                'nouvel_etat': nouvel_etat
            }
        )

    def log_arret_voiture(self, id_voiture: int, raison: str, scenario: str):
        """Enregistre l'arrêt d'une voiture."""
        self.log_action(
            type_action="VOITURE",
            description=f"Voiture {id_voiture} arrêtée - Raison: {raison}",
            scenario=scenario,
            details={
                'id_voiture': id_voiture,
                'raison': raison
            }
        )

    def log_demarrage_voiture(self, id_voiture: int, scenario: str):
        """Enregistre le démarrage d'une voiture."""
        self.log_action(
            type_action="VOITURE",
            description=f"Voiture {id_voiture} démarrée",
            scenario=scenario,
            details={'id_voiture': id_voiture}
        )

    def log_generation_voiture(self, id_voiture: int, type_voiture: str, scenario: str):
        """Enregistre la génération d'une voiture."""
        self.log_action(
            type_action="VOITURE",
            description=f"Création voiture {id_voiture} ({type_voiture})",
            scenario=scenario,
            details={
                'id_voiture': id_voiture,
                'type_voiture': type_voiture
            }
        )

    def log_sortie_voiture(self, id_voiture: int, scenario: str):
        """Enregistre la sortie d'une voiture de l'écran."""
        self.log_action(
            type_action="VOITURE",
            description=f"Voiture {id_voiture} sortie de l'écran",
            scenario=scenario,
            details={'id_voiture': id_voiture}
        )

    def log_collision_evitee(self, id_voiture1: int, id_voiture2: int, scenario: str):
        """Enregistre une collision évitée."""
        self.log_action(
            type_action="SÉCURITÉ",
            description=f"Collision évitée entre voitures {id_voiture1} et {id_voiture2}",
            scenario=scenario,
            details={
                'voiture1': id_voiture1,
                'voiture2': id_voiture2
            }
        )

    def log_changement_phase(self, ancienne_phase: str, nouvelle_phase: str, scenario: str):
        """Enregistre le changement de phase du feu."""
        self.log_action(
            type_action="PHASE",
            description=f"Changement phase: {ancienne_phase} → {nouvelle_phase}",
            scenario=scenario,
            details={
                'ancienne_phase': ancienne_phase,
                'nouvelle_phase': nouvelle_phase
            }
        )

    def _sauvegarder_event(self, event: dict):
        """Sauvegarde un événement dans le fichier de log."""
        try:
            with open(self.fichier_log, 'a', encoding='utf-8') as f:
                f.write(json.dumps(event, ensure_ascii=False) + '\n')
        except Exception as e:
            print(f"Erreur lors de la sauvegarde du log: {e}")

    def _afficher_log(self, event: dict):
        """Affiche l'événement dans la console."""
        timestamp = event['timestamp']
        type_action = event['type_action']
        description = event['description']
        scenario = event['scenario']

        print(f"[{timestamp}] [{type_action:12}] {description:50} | Scénario: {scenario}")

    def obtenir_tous_les_events(self) -> list:
        """Retourne tous les événements enregistrés."""
        return self.events.copy()

    def obtenir_events_par_type(self, type_action: str) -> list:
        """
        Retourne les événements d'un type spécifique.

        Args:
            type_action: Type d'action à filtrer

        Returns:
            Liste des événements du type
        """
        return [e for e in self.events if e['type_action'] == type_action]

    def obtenir_events_par_scenario(self, scenario: str) -> list:
        """
        Retourne les événements d'un scénario spécifique.

        Args:
            scenario: Nom du scénario

        Returns:
            Liste des événements du scénario
        """
        return [e for e in self.events if e['scenario'] == scenario]

    def obtenir_events_recents(self, nombre: int = 10) -> list:
        """
        Retourne les N derniers événements.

        Args:
            nombre: Nombre d'événements à retourner

        Returns:
            Liste des N derniers événements
        """
        return self.events[-nombre:]

    def obtenir_statistiques(self) -> dict:
        """Retourne les statistiques des logs."""
        if not self.events:
            return {
                'total_events': 0,
                'types_actions': {},
                'scenarios': {},
                'premier_event': None,
                'dernier_event': None
            }

        types_actions = {}
        scenarios = {}

        for event in self.events:
            # Compter les types
            type_action = event['type_action']
            types_actions[type_action] = types_actions.get(type_action, 0) + 1

            # Compter les scénarios
            scenario = event['scenario']
            scenarios[scenario] = scenarios.get(scenario, 0) + 1

        return {
            'total_events': len(self.events),
            'types_actions': types_actions,
            'scenarios': scenarios,
            'premier_event': self.events[0]['timestamp'],
            'dernier_event': self.events[-1]['timestamp']
        }

    def exporter_csv(self, fichier_csv: str = "simulation_logs.csv"):
        """
        Exporte les logs en format CSV.

        Args:
            fichier_csv: Chemin du fichier CSV
        """
        try:
            import csv

            with open(fichier_csv, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(
                    f,
                    fieldnames=['timestamp', 'type_action', 'description', 'scenario', 'details']
                )
                writer.writeheader()

                for event in self.events:
                    event_copy = event.copy()
                    event_copy['details'] = json.dumps(event_copy['details'], ensure_ascii=False)
                    writer.writerow(event_copy)

            print(f" Logs exportés vers {fichier_csv}")
        except Exception as e:
            print(f" Erreur lors de l'export CSV: {e}")

    def nettoyer_logs(self):
        """Nettoie tous les logs (réinitialise le fichier)."""
        try:
            self.fichier_log.unlink()  # Supprimer le fichier
            self.fichier_log.touch()  # Recréer vide
            self.events = []
            print(" Logs nettoyés")
        except Exception as e:
            print(f" Erreur lors du nettoyage des logs: {e}")

    def __repr__(self) -> str:
        return f"<EventLogger {len(self.events)} events>"

    def __str__(self) -> str:
        stats = self.obtenir_statistiques()
        return f"EventLogger - {stats['total_events']} événements enregistrés"
