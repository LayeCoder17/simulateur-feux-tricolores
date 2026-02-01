# database.py

import sqlite3
from datetime import datetime
from pathlib import Path
import json


class DatabaseManager:


    def __init__(self, nom_base: str = "simulation_carrefour.db"):

        self.nom_base = nom_base
        self.chemin_base = Path(nom_base)

        # Créer la base si elle n'existe pas
        self._initialiser_base()

    def _initialiser_base(self):
        """Crée la base de données et les tables si elles n'existent pas."""
        try:
            conn = sqlite3.connect(self.nom_base)
            cursor = conn.cursor()

            # Table des événements
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME NOT NULL,
                    type_action TEXT NOT NULL,
                    description TEXT NOT NULL,
                    etat_feu TEXT,
                    scenario TEXT,
                    details TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Table des voitures
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS voitures (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_voiture INTEGER NOT NULL,
                    type_voiture TEXT NOT NULL,
                    couleur TEXT NOT NULL,
                    position_x REAL,
                    position_y REAL,
                    vitesse REAL,
                    direction TEXT,
                    timestamp DATETIME NOT NULL,
                    scenario TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Table des états du feu
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS etats_feu (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME NOT NULL,
                    position TEXT NOT NULL,
                    etat TEXT NOT NULL,
                    phase TEXT,
                    scenario TEXT,
                    duree_secondes REAL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Table des statistiques
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS statistiques (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME NOT NULL,
                    scenario TEXT NOT NULL,
                    nombre_voitures INTEGER,
                    nombre_voitures_ns INTEGER,
                    nombre_voitures_eo INTEGER,
                    vitesse_moyenne REAL,
                    temps_total REAL,
                    nombre_cycles_feu REAL,
                    phase_actuelle TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Créer des index pour améliorer les performances
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON events(timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_type_action ON events(type_action)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_scenario ON events(scenario)')

            conn.commit()
            conn.close()
            print(f" Base de données '{self.nom_base}' initialisée")
        except Exception as e:
            print(f" Erreur lors de l'initialisation de la base: {e}")

    def enregistrer_action(self, type_action: str, description: str, scenario: str = "",
                           etat_feu: str = "", details: dict = None):
        """
        Enregistre une action dans la table events.

        Args:
            type_action: Type d'action (DEMARRAGE, PAUSE, ARRÊT, etc.)
            description: Description de l'action
            scenario: Scénario actif
            etat_feu: État du feu à ce moment
            details: Détails supplémentaires
        """
        try:
            conn = sqlite3.connect(self.nom_base)
            cursor = conn.cursor()

            timestamp = datetime.now()
            details_json = json.dumps(details or {})

            cursor.execute('''
                INSERT INTO events (timestamp, type_action, description, etat_feu, scenario, details)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (timestamp, type_action, description, etat_feu, scenario, details_json))

            conn.commit()
            conn.close()

            print(f" Action enregistrée: {type_action} - {description}")
        except Exception as e:
            print(f" Erreur lors de l'enregistrement de l'action: {e}")

    def enregistrer_voiture(self, id_voiture: int, type_voiture: str, couleur: str,
                            position_x: float, position_y: float, vitesse: float,
                            direction: str, scenario: str):
        """
        Enregistre l'état d'une voiture.

        Args:
            id_voiture: ID unique de la voiture
            type_voiture: Type (citadine, berline, camion)
            couleur: Couleur de la voiture
            position_x: Position X
            position_y: Position Y
            vitesse: Vitesse actuelle
            direction: Direction (NORD_SUD, EST_OUEST)
            scenario: Scénario actif
        """
        try:
            conn = sqlite3.connect(self.nom_base)
            cursor = conn.cursor()

            timestamp = datetime.now()

            cursor.execute('''
                INSERT INTO voitures (id_voiture, type_voiture, couleur, position_x, position_y, vitesse, direction, timestamp, scenario)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (id_voiture, type_voiture, couleur, position_x, position_y, vitesse, direction, timestamp, scenario))

            conn.commit()
            conn.close()
        except Exception as e:
            print(f" Erreur lors de l'enregistrement de la voiture: {e}")

    def enregistrer_etat_feu(self, position: str, etat: str, phase: str, scenario: str, duree_secondes: float = 0.0):
        """
        Enregistre l'état du feu.

        Args:
            position: Position du feu (NE, NW, SE, SW)
            etat: État du feu (ROUGE, ORANGE, VERT)
            phase: Phase actuelle (VERTICAL, HORIZONTAL)
            scenario: Scénario actif
            duree_secondes: Durée de cet état
        """
        try:
            conn = sqlite3.connect(self.nom_base)
            cursor = conn.cursor()

            timestamp = datetime.now()

            cursor.execute('''
                INSERT INTO etats_feu (timestamp, position, etat, phase, scenario, duree_secondes)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (timestamp, position, etat, phase, scenario, duree_secondes))

            conn.commit()
            conn.close()
        except Exception as e:
            print(f" Erreur lors de l'enregistrement de l'état du feu: {e}")

    def enregistrer_statistiques(self, scenario: str, nombre_voitures: int,
                                 nombre_voitures_ns: int, nombre_voitures_eo: int,
                                 vitesse_moyenne: float, temps_total: float,
                                 nombre_cycles_feu: float, phase_actuelle: str):
        """
        Enregistre les statistiques actuelles de la simulation.

        Args:
            scenario: Scénario actif
            nombre_voitures: Total des voitures
            nombre_voitures_ns: Voitures direction NORD_SUD
            nombre_voitures_eo: Voitures direction EST_OUEST
            vitesse_moyenne: Vitesse moyenne
            temps_total: Temps total écoulé
            nombre_cycles_feu: Nombre de cycles du feu
            phase_actuelle: Phase actuelle
        """
        try:
            conn = sqlite3.connect(self.nom_base)
            cursor = conn.cursor()

            timestamp = datetime.now()

            cursor.execute('''
                INSERT INTO statistiques (timestamp, scenario, nombre_voitures, nombre_voitures_ns, 
                                         nombre_voitures_eo, vitesse_moyenne, temps_total, 
                                         nombre_cycles_feu, phase_actuelle)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (timestamp, scenario, nombre_voitures, nombre_voitures_ns, nombre_voitures_eo,
                  vitesse_moyenne, temps_total, nombre_cycles_feu, phase_actuelle))

            conn.commit()
            conn.close()
        except Exception as e:
            print(f" Erreur lors de l'enregistrement des statistiques: {e}")

    def obtenir_tous_les_events(self) -> list:
        """Retourne tous les événements enregistrés."""
        try:
            conn = sqlite3.connect(self.nom_base)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute('SELECT * FROM events ORDER BY timestamp DESC')
            events = [dict(row) for row in cursor.fetchall()]

            conn.close()
            return events
        except Exception as e:
            print(f" Erreur lors de la récupération des événements: {e}")
            return []

    def obtenir_events_par_type(self, type_action: str) -> list:
        """Retourne les événements d'un type spécifique."""
        try:
            conn = sqlite3.connect(self.nom_base)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute('SELECT * FROM events WHERE type_action = ? ORDER BY timestamp DESC', (type_action,))
            events = [dict(row) for row in cursor.fetchall()]

            conn.close()
            return events
        except Exception as e:
            print(f" Erreur lors de la récupération des événements: {e}")
            return []

    def obtenir_events_par_scenario(self, scenario: str) -> list:
        """Retourne les événements d'un scénario spécifique."""
        try:
            conn = sqlite3.connect(self.nom_base)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute('SELECT * FROM events WHERE scenario = ? ORDER BY timestamp DESC', (scenario,))
            events = [dict(row) for row in cursor.fetchall()]

            conn.close()
            return events
        except Exception as e:
            print(f" Erreur lors de la récupération des événements: {e}")
            return []

    def obtenir_events_recents(self, nombre: int = 10) -> list:
        """Retourne les N derniers événements."""
        try:
            conn = sqlite3.connect(self.nom_base)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute('SELECT * FROM events ORDER BY timestamp DESC LIMIT ?', (nombre,))
            events = [dict(row) for row in cursor.fetchall()]

            conn.close()
            return events
        except Exception as e:
            print(f" Erreur lors de la récupération des événements: {e}")
            return []

    def obtenir_voitures_par_scenario(self, scenario: str) -> list:
        """Retourne l'historique des voitures pour un scénario."""
        try:
            conn = sqlite3.connect(self.nom_base)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute('SELECT * FROM voitures WHERE scenario = ? ORDER BY timestamp', (scenario,))
            voitures = [dict(row) for row in cursor.fetchall()]

            conn.close()
            return voitures
        except Exception as e:
            print(f" Erreur lors de la récupération des voitures: {e}")
            return []

    def obtenir_etats_feu_par_scenario(self, scenario: str) -> list:
        """Retourne l'historique des états du feu pour un scénario."""
        try:
            conn = sqlite3.connect(self.nom_base)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute('SELECT * FROM etats_feu WHERE scenario = ? ORDER BY timestamp', (scenario,))
            etats = [dict(row) for row in cursor.fetchall()]

            conn.close()
            return etats
        except Exception as e:
            print(f" Erreur lors de la récupération des états du feu: {e}")
            return []

    def obtenir_statistiques(self) -> dict:
        """Retourne les statistiques globales."""
        try:
            conn = sqlite3.connect(self.nom_base)
            cursor = conn.cursor()

            # Total d'événements
            cursor.execute('SELECT COUNT(*) as count FROM events')
            total_events = cursor.fetchone()[0]

            # Événements par type
            cursor.execute('SELECT type_action, COUNT(*) as count FROM events GROUP BY type_action')
            events_par_type = {row[0]: row[1] for row in cursor.fetchall()}

            # Événements par scénario
            cursor.execute('SELECT scenario, COUNT(*) as count FROM events GROUP BY scenario')
            events_par_scenario = {row[0]: row[1] for row in cursor.fetchall()}

            # Total de voitures générées
            cursor.execute('SELECT COUNT(DISTINCT id_voiture) as count FROM voitures')
            total_voitures = cursor.fetchone()[0]

            conn.close()

            return {
                'total_events': total_events,
                'events_par_type': events_par_type,
                'events_par_scenario': events_par_scenario,
                'total_voitures_generees': total_voitures
            }
        except Exception as e:
            print(f" Erreur lors de la récupération des statistiques: {e}")
            return {}

    def obtenir_statistiques_par_scenario(self, scenario: str) -> dict:
        """Retourne les statistiques pour un scénario spécifique."""
        try:
            conn = sqlite3.connect(self.nom_base)
            cursor = conn.cursor()

            # Nombre d'événements
            cursor.execute('SELECT COUNT(*) as count FROM events WHERE scenario = ?', (scenario,))
            nb_events = cursor.fetchone()[0]

            # Types d'événements
            cursor.execute('''
                SELECT type_action, COUNT(*) as count 
                FROM events 
                WHERE scenario = ? 
                GROUP BY type_action
            ''', (scenario,))
            types_events = {row[0]: row[1] for row in cursor.fetchall()}

            # Nombre de voitures générées
            cursor.execute('SELECT COUNT(DISTINCT id_voiture) as count FROM voitures WHERE scenario = ?', (scenario,))
            nb_voitures = cursor.fetchone()[0]

            # Vitesse moyenne des voitures
            cursor.execute('SELECT AVG(vitesse) as avg_vitesse FROM voitures WHERE scenario = ?', (scenario,))
            vitesse_avg = cursor.fetchone()[0] or 0.0

            conn.close()

            return {
                'scenario': scenario,
                'nombre_events': nb_events,
                'types_events': types_events,
                'nombre_voitures_generees': nb_voitures,
                'vitesse_moyenne_voitures': vitesse_avg
            }
        except Exception as e:
            print(f" Erreur lors de la récupération des statistiques: {e}")
            return {}

    def exporter_csv(self, type_export: str = "events", fichier_csv: str = None):
        """
        Exporte les données en format CSV.

        Args:
            type_export: Type de données à exporter (events, voitures, etats_feu, statistiques)
            fichier_csv: Chemin du fichier CSV (optionnel)
        """
        try:
            import csv

            if fichier_csv is None:
                fichier_csv = f"export_{type_export}.csv"

            conn = sqlite3.connect(self.nom_base)
            cursor = conn.cursor()

            if type_export == "events":
                cursor.execute('SELECT * FROM events ORDER BY timestamp DESC')
                fieldnames = ['id', 'timestamp', 'type_action', 'description', 'etat_feu', 'scenario', 'details',
                              'created_at']
            elif type_export == "voitures":
                cursor.execute('SELECT * FROM voitures ORDER BY timestamp DESC')
                fieldnames = ['id', 'id_voiture', 'type_voiture', 'couleur', 'position_x', 'position_y', 'vitesse',
                              'direction', 'timestamp', 'scenario', 'created_at']
            elif type_export == "etats_feu":
                cursor.execute('SELECT * FROM etats_feu ORDER BY timestamp DESC')
                fieldnames = ['id', 'timestamp', 'position', 'etat', 'phase', 'scenario', 'duree_secondes',
                              'created_at']
            elif type_export == "statistiques":
                cursor.execute('SELECT * FROM statistiques ORDER BY timestamp DESC')
                fieldnames = ['id', 'timestamp', 'scenario', 'nombre_voitures', 'nombre_voitures_ns',
                              'nombre_voitures_eo', 'vitesse_moyenne', 'temps_total', 'nombre_cycles_feu',
                              'phase_actuelle', 'created_at']
            else:
                print(f" Type d'export invalide: {type_export}")
                return

            rows = cursor.fetchall()
            conn.close()

            with open(fichier_csv, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(fieldnames)
                writer.writerows(rows)

            print(f" Données exportées vers {fichier_csv}")
        except Exception as e:
            print(f" Erreur lors de l'export: {e}")

    def nettoyer_base(self):
        """Nettoie complètement la base de données (supprime toutes les tables)."""
        try:
            conn = sqlite3.connect(self.nom_base)
            cursor = conn.cursor()

            cursor.execute('DROP TABLE IF EXISTS events')
            cursor.execute('DROP TABLE IF EXISTS voitures')
            cursor.execute('DROP TABLE IF EXISTS etats_feu')
            cursor.execute('DROP TABLE IF EXISTS statistiques')

            conn.commit()
            conn.close()

            # Réinitialiser
            self._initialiser_base()

            print(" Base de données nettoyée")
        except Exception as e:
            print(f" Erreur lors du nettoyage: {e}")

    def obtenir_nombre_events(self) -> int:
        """Retourne le nombre total d'événements."""
        try:
            conn = sqlite3.connect(self.nom_base)
            cursor = conn.cursor()

            cursor.execute('SELECT COUNT(*) FROM events')
            count = cursor.fetchone()[0]

            conn.close()
            return count
        except Exception as e:
            print(f" Erreur: {e}")
            return 0

    def __repr__(self) -> str:
        nb_events = self.obtenir_nombre_events()
        return f"<DatabaseManager {nb_events} events>"

    def __str__(self) -> str:
        nb_events = self.obtenir_nombre_events()
        return f"DatabaseManager - {nb_events} événements enregistrés dans '{self.nom_base}'"
