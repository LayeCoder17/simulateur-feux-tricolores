"""
 SIMULATEUR DE CARREFOUR INTELLIGENT
Système de gestion du trafic avec feux tricolores coordonnés

"""

import sys
import tkinter as tk
from pathlib import Path
from datetime import datetime

# Imports locaux
from gui import SimulationGUI
from logger import EventLogger
from database import DatabaseManager


class ApplicationDeMarrage:
    """Classe pour gérer le démarrage et l'arrêt de l'application."""

    def __init__(self):
        self.logger = None
        self.db_manager = None

    def afficher_bienvenue(self):
        """Affiche le message de bienvenue avec style."""
        print("\n" + "=" * 75)
        print(" SIMULATEUR DE CARREFOUR INTELLIGENT".center(75))
        print("=" * 75)
        print("\n  Système de gestion du trafic avec feux tricolores coordonnés")
        print(" Objectif: Optimiser la circulation aux carrefours urbains")
        print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("\n" + "=" * 75 + "\n")

    def verifier_environnement(self):
        """Vérifie que tous les fichiers nécessaires sont présents."""
        print("🔍 Vérification de l'environnement...\n")

        fichiers_requis = [
            "scenarios.py",
            "traffic_light.py",
            "vehicules.py",
            "traffic_manager.py",
            "traffic_light_manager.py",
            "simulation.py",
            "turtle_scene.py",
            "gui.py",
            "logger.py",
            "database.py",
        ]

        fichiers_manquants = []
        for fichier in fichiers_requis:
            chemin = Path(fichier)
            if chemin.exists():
                print(f"   {fichier}")
            else:
                print(f"    {fichier} (MANQUANT)")
                fichiers_manquants.append(fichier)

        if fichiers_manquants:
            print(f"\n {len(fichiers_manquants)} fichier(s) manquant(s):")
            for fichier in fichiers_manquants:
                print(f"   - {fichier}")
            return False

        print("\n Tous les fichiers requis sont présents\n")
        return True

    def initialiser_systemes(self):
        """Initialise les systèmes de log et base de données."""
        print("🔧 Initialisation des systèmes...\n")

        try:
            # Logger
            self.logger = EventLogger("simulation.log")
            print("    Système de logging initialisé")
            print("       Fichier: simulation.log")

            # Base de données
            self.db_manager = DatabaseManager("simulation_carrefour.db")
            print("    Base de données initialisée")
            print("       Fichier: simulation_carrefour.db")

            # Log de démarrage système
            self.logger.log_action(
                type_action="SYSTÈME",
                description="Démarrage de l'application",
                scenario="",
                details={
                    "version": "1.0",
                    "timestamp": datetime.now().isoformat(),
                    "status": "DEMARRAGE"
                }
            )

            self.db_manager.enregistrer_action(
                type_action="SYSTÈME",
                description="Démarrage de l'application",
                details={"version": "1.0", "status": "DEMARRAGE"}
            )

            print("\n Systèmes initialisés avec succès!\n")
            print("=" * 75 + "\n")
            return True

        except Exception as e:
            print(f"\n  Erreur lors de l'initialisation: {e}\n")
            import traceback
            traceback.print_exc()
            return False

    def afficher_conseils(self):
        """Affiche les conseils d'utilisation."""
        print("=" * 75)
        print("💡 GUIDE D'UTILISATION".center(75))
        print("=" * 75)

        def afficher_conseils(self):
            """Affiche les conseils d'utilisation."""
            print("""
        Commandes :
        - Play : Lancer
        - Pause : Mettre en pause
        - Stop : Arreter
        - Reset : Reinitialiser

        Scenarios disponibles :
        - Normal : Trafic standard
        - Heure de pointe : Trafic dense
        - Mode nuit : Trafic faible

        Fichiers de sortie :
        - simulation.log : Historique
        - simulation_carrefour.db : Base de donnees
        - export_*.csv : Pour Excel

        Note : Les fichiers CSV sont generes a la fermeture.
        """)

        print("=" * 75 + "\n")

    def lancer_application(self):
        """Lance l'application graphique principale."""
        print(" Lancement de l'interface graphique...\n")

        try:
            # Créer la fenêtre principale Tkinter
            root = tk.Tk()

            # Créer l'instance de l'interface
            app = SimulationGUI(root)

            print(" Interface graphique lancée avec succès!\n")

            # Afficher les conseils
            self.afficher_conseils()

            # Lancer la boucle principale
            app.run()

            # Log de fermeture
            if self.logger:
                self.logger.log_action(
                    type_action="SYSTÈME",
                    description="Fermeture de l'application",
                    scenario="",
                    details={"status": "FERMETURE", "timestamp": datetime.now().isoformat()}
                )
            if self.db_manager:
                self.db_manager.enregistrer_action(
                    type_action="SYSTÈME",
                    description="Fermeture de l'application",
                    details={"status": "FERMETURE"}
                )

            return True

        except Exception as e:
            print(f"\n❌ Erreur lors du lancement: {e}")
            import traceback
            traceback.print_exc()
            return False

    def afficher_au_revoir(self):
        """Affiche le message de fermeture et les fichiers générés."""
        print("\n" + "=" * 75)
        print(" Merci d'avoir utilisé le Simulateur de Carrefour!".center(75))
        print("=" * 75)
        print("\n Fichiers générés et disponibles:\n")

        fichiers_info = [
            ("simulation.log", "Logs détaillés de tous les événements"),
            ("simulation_carrefour.db", "Base de données SQLite complète"),
            ("export_events.csv", "Exportation des événements (CSV)"),
            ("export_voitures.csv", "Exportation des données voitures (CSV)"),
            ("export_etats_feu.csv", "Exportation des états des feux (CSV)"),
        ]

        for fichier, emoji, description in fichiers_info:
            chemin = Path(fichier)
            if chemin.exists():
                taille = chemin.stat().st_size
                taille_str = f"{taille/1024:.1f} KB" if taille > 1024 else f"{taille} B"
                print(f"   {emoji} {fichier:<30} ({taille_str})")
                print(f"      └─ {description}")
            else:
                print(f"   {emoji} {fichier:<30} (non généré)")
                print(f"      └─ {description}")

        print("\n" + "=" * 75)
        print(" CONSEILS POUR ANALYSER LES DONNÉES".center(75))
        print("=" * 75)
        print("""
        CONSEILS POUR L'ANALYSE DES DONNEES

        1. Consulter les logs :
           Ouvrir simulation.log avec un editeur de texte pour voir l'historique
           des evenements et les changements de feux.

        2. Base de donnees :
           Le fichier simulation_carrefour.db contient toutes les tables
           (actions, voitures, feux). A ouvrir avec DB Browser for SQLite.

        3. Fichiers CSV :
           Les fichiers export_*.csv peuvent etre ouverts dans Excel pour
           faire des graphiques ou comparer les scenarios.

        4. Pistes d'analyse :
           - Calculer la vitesse moyenne par scenario
           - Compter le nombre total de voitures
           - Verifier la duree des cycles de feux

        5. Tests a faire :
           Modifier les durees des phases (Vertical/Horizontal) pour voir
           l'impact sur la fluidite du trafic.
        """)

        print("\n" + "=" * 75 + "\n")


def main():
    """Point d'entrée principal de l'application."""
    app = ApplicationDeMarrage()

    try:
        # 1️Bienvenue
        app.afficher_bienvenue()

        # 2️Verifier l'environnement
        if not app.verifier_environnement():
            print(" Impossible de continuer. Vérifiez les fichiers manquants.")
            sys.exit(1)

        # 3️ Initialiser les systèmes
        if not app.initialiser_systemes():
            print(" Impossible de continuer. Erreur d'initialisation.")
            sys.exit(1)

        # 4️Lancer l'application
        if not app.lancer_application():
            print(" Erreur lors de l'exécution de l'application.")
            sys.exit(1)

        # 5️Au revoir et infos
        app.afficher_au_revoir()

    except KeyboardInterrupt:
        print("\n\n   Interruption utilisateur (Ctrl+C détecté)")
        print(" Arrêt gracieux de l'application...\n")

        # Log l'interruption
        if app.logger:
            app.logger.log_action(
                type_action="SYSTÈME",
                description="Interruption utilisateur (Ctrl+C)",
                scenario="",
                details={"status": "INTERRUPTION"}
            )

        sys.exit(0)

    except Exception as e:
        print(f"\n Erreur non gérée: {e}")
        import traceback
        traceback.print_exc()

        # Log l'erreur
        if app.logger:
            app.logger.log_action(
                type_action="ERREUR",
                description=f"Erreur non gérée: {str(e)}",
                scenario="",
                details={"status": "ERREUR", "error": str(e)}
            )

        sys.exit(1)


if __name__ == "__main__":
    main()