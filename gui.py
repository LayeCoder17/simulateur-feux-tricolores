# GUI.PY - VERSION FINALE AVEC TURTLE INTÉGRÉ DANS LA MÊME FENÊTRE

import tkinter as tk
from tkinter import ttk
from scenarios import obtenir_tous_les_scenarios, obtenir_scenario_par_nom
from simulation import Simulation
from turtle_scene import SceneTurtle  # ← Version intégrée (avec parent_frame)
from traffic_light import EtatFeu

try:
    from logger import EventLogger
except ImportError:
    EventLogger = None

try:
    from database import DatabaseManager
except ImportError:
    DatabaseManager = None


class SimulationGUI:
    """Interface graphique pour la simulation du carrefour - Tout dans une seule fenêtre."""

    def __init__(self, root):
        """Initialise l'interface graphique."""
        self.root = root
        self.root.title("🚦 Simulateur de Carrefour - Gestion du Trafic")
        self.root.geometry("1600x950")  # Large pour Turtle + contrôles
        self.root.configure(bg="#0d1117")

        # Logging optionnel
        self.logger = EventLogger() if EventLogger else None
        self.db_manager = DatabaseManager() if DatabaseManager else None

        # Simulation
        self.scenario_actuel = obtenir_tous_les_scenarios()["normal"]
        self.simulation = Simulation(self.scenario_actuel)

        # État
        self.en_cours = False
        self.en_pause = False
        self.animation_active = False

        # Créer l'interface (Turtle intégré directement ici)
        self._creer_interface()

        # Boucle de simulation
        self._loop_simulation()

    def _creer_interface(self):
        """Crée l'interface : Turtle à gauche, contrôles + infos à droite."""
        main_frame = tk.Frame(self.root, bg="#0d1117")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Titre
        titre_label = tk.Label(
            main_frame,
            text="🚦 SIMULATEUR DE CARREFOUR INTELLIGENT",
            bg="#0d1117",
            fg="#34c759",
            font=("Arial", 18, "bold")
        )
        titre_label.pack(pady=(0, 20))

        # Container principal : 2 colonnes
        container = tk.Frame(main_frame, bg="#0d1117")
        container.pack(fill=tk.BOTH, expand=True)

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=4)  # Turtle plus large
        container.grid_columnconfigure(1, weight=1)

        # === TURTLE À GAUCHE ===
        frame_turtle = tk.Frame(container, bg="#0d1117")
        frame_turtle.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        self.scene_turtle = SceneTurtle(frame_turtle)  # ← Turtle intégré ici !

        # === CONTRÔLES ET INFOS À DROITE ===
        frame_right = tk.Frame(container, bg="#0d1117")
        frame_right.grid(row=0, column=1, sticky="ns")

        # Contrôle simulation
        control_frame = tk.LabelFrame(
            frame_right,
            text="🎮 Contrôle de Simulation",
            bg="#1a1a1a",
            fg="#ffffff",
            font=("Arial", 12, "bold"),
            padx=10,
            pady=10
        )
        control_frame.pack(fill=tk.X, pady=(0, 10))

        # Boutons Play/Pause/Stop/Reset
        buttons_frame = tk.Frame(control_frame, bg="#1a1a1a")
        buttons_frame.pack(fill=tk.X, pady=10)

        self.btn_play = tk.Button(
            buttons_frame,
            text="▶️ Play",
            command=self._demarrer,
            bg="#34c759",
            fg="#ffffff",
            font=("Arial", 11, "bold"),
            width=12,
            padx=10,
            pady=8
        )
        self.btn_play.pack(side=tk.LEFT, padx=5)

        self.btn_pause = tk.Button(
            buttons_frame,
            text="⏸️ Pause",
            command=self._pause,
            bg="#ff9500",
            fg="#ffffff",
            font=("Arial", 11, "bold"),
            width=12,
            padx=10,
            pady=8,
            state=tk.DISABLED
        )
        self.btn_pause.pack(side=tk.LEFT, padx=5)

        self.btn_stop = tk.Button(
            buttons_frame,
            text="⏹️ Stop",
            command=self._arreter,
            bg="#ff3b30",
            fg="#ffffff",
            font=("Arial", 11, "bold"),
            width=12,
            padx=10,
            pady=8
        )
        self.btn_stop.pack(side=tk.LEFT, padx=5)

        self.btn_reset = tk.Button(
            buttons_frame,
            text="🔄 Reset",
            command=self._reinitialiser,
            bg="#5ac8fa",
            fg="#ffffff",
            font=("Arial", 11, "bold"),
            width=12,
            padx=10,
            pady=8
        )
        self.btn_reset.pack(side=tk.LEFT, padx=5)

        # Sélecteur scénario
        scenario_frame = tk.Frame(control_frame, bg="#1a1a1a")
        scenario_frame.pack(fill=tk.X, pady=10)

        scenario_label = tk.Label(
            scenario_frame,
            text="📍 Scénario:",
            bg="#1a1a1a",
            fg="#ffffff",
            font=("Arial", 11, "bold")
        )
        scenario_label.pack(side=tk.LEFT, padx=5)

        scenarios = obtenir_tous_les_scenarios()
        noms_scenarios = list(scenarios.keys())

        self.combo_scenario = ttk.Combobox(
            scenario_frame,
            values=noms_scenarios,
            state="readonly",
            font=("Arial", 11),
            width=25
        )
        self.combo_scenario.set("normal")
        self.combo_scenario.pack(side=tk.LEFT, padx=5)
        self.combo_scenario.bind("<<ComboboxSelected>>", self._changer_scenario)

        # Mode manuel
        manual_frame = tk.LabelFrame(
            control_frame,
            text="🎮 Mode Manuel - Changement des Feux",
            bg="#1a1a1a",
            fg="#ffffff",
            font=("Arial", 11, "bold"),
            padx=10,
            pady=10
        )
        manual_frame.pack(fill=tk.X, pady=10)

        self.btn_feu_rouge = tk.Button(
            manual_frame,
            text="🔴 ROUGE",
            command=lambda: self._forcer_feu_manuel("ROUGE"),
            bg="#ff3b30",
            fg="#ffffff",
            font=("Arial", 10, "bold"),
            width=12,
            padx=10,
            pady=6
        )
        self.btn_feu_rouge.pack(side=tk.LEFT, padx=5)

        self.btn_feu_orange = tk.Button(
            manual_frame,
            text="🟠 ORANGE",
            command=lambda: self._forcer_feu_manuel("ORANGE"),
            bg="#ff9500",
            fg="#ffffff",
            font=("Arial", 10, "bold"),
            width=12,
            padx=10,
            pady=6
        )
        self.btn_feu_orange.pack(side=tk.LEFT, padx=5)

        self.btn_feu_vert = tk.Button(
            manual_frame,
            text="🟢 VERT",
            command=lambda: self._forcer_feu_manuel("VERT"),
            bg="#34c759",
            fg="#ffffff",
            font=("Arial", 10, "bold"),
            width=12,
            padx=10,
            pady=6
        )
        self.btn_feu_vert.pack(side=tk.LEFT, padx=5)

        # Infos en temps réel
        info_frame = tk.LabelFrame(
            frame_right,
            text="📊 Informations en Temps Réel",
            bg="#1a1a1a",
            fg="#ffffff",
            font=("Arial", 12, "bold"),
            padx=15,
            pady=15
        )
        info_frame.pack(fill=tk.BOTH, expand=True)

        info_grid = tk.Frame(info_frame, bg="#1a1a1a")
        info_grid.pack(fill=tk.BOTH, expand=True)

        # Toutes tes infos (exactement comme avant)
        feu_label = tk.Label(info_grid, text="🚦 État Feu:", bg="#1a1a1a", fg="#ffffff", font=("Arial", 10, "bold"))
        feu_label.grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
        self.label_etat_feu = tk.Label(info_grid, text="ROUGE", bg="#1a1a1a", fg="#ff3b30", font=("Arial", 13, "bold"))
        self.label_etat_feu.grid(row=1, column=0, sticky=tk.W, padx=10, pady=3)

        phase_label = tk.Label(info_grid, text="📐 Phase:", bg="#1a1a1a", fg="#ffffff", font=("Arial", 10, "bold"))
        phase_label.grid(row=0, column=1, sticky=tk.W, padx=10, pady=5)
        self.label_phase = tk.Label(info_grid, text="VERTICAL", bg="#1a1a1a", fg="#34c759", font=("Arial", 13, "bold"))
        self.label_phase.grid(row=1, column=1, sticky=tk.W, padx=10, pady=3)

        voitures_label = tk.Label(info_grid, text="🚗 Voitures:", bg="#1a1a1a", fg="#ffffff", font=("Arial", 10, "bold"))
        voitures_label.grid(row=0, column=2, sticky=tk.W, padx=10, pady=5)
        self.label_voitures = tk.Label(info_grid, text="0", bg="#1a1a1a", fg="#5ac8fa", font=("Arial", 13, "bold"))
        self.label_voitures.grid(row=1, column=2, sticky=tk.W, padx=10, pady=3)

        temps_label = tk.Label(info_grid, text="⏱️ Temps:", bg="#1a1a1a", fg="#ffffff", font=("Arial", 10, "bold"))
        temps_label.grid(row=0, column=3, sticky=tk.W, padx=10, pady=5)
        self.label_temps = tk.Label(info_grid, text="0.0s", bg="#1a1a1a", fg="#ffff00", font=("Arial", 13, "bold"))
        self.label_temps.grid(row=1, column=3, sticky=tk.W, padx=10, pady=3)

        scenario_actif_label = tk.Label(info_grid, text="📌 Scénario Actif:", bg="#1a1a1a", fg="#ffffff", font=("Arial", 10, "bold"))
        scenario_actif_label.grid(row=2, column=0, sticky=tk.W, padx=10, pady=5)
        self.label_scenario = tk.Label(info_grid, text="Circulation normale", bg="#1a1a1a", fg="#ff9500", font=("Arial", 11, "bold"))
        self.label_scenario.grid(row=3, column=0, sticky=tk.W, padx=10, pady=3)

        etat_label = tk.Label(info_grid, text="🔘 État:", bg="#1a1a1a", fg="#ffffff", font=("Arial", 10, "bold"))
        etat_label.grid(row=2, column=1, sticky=tk.W, padx=10, pady=5)
        self.label_etat_simu = tk.Label(info_grid, text="ARRÊTÉE", bg="#1a1a1a", fg="#999999", font=("Arial", 11, "bold"))
        self.label_etat_simu.grid(row=3, column=1, sticky=tk.W, padx=10, pady=3)

        vitesse_label = tk.Label(info_grid, text="⚡ Vitesse Moy.:", bg="#1a1a1a", fg="#ffffff", font=("Arial", 10, "bold"))
        vitesse_label.grid(row=2, column=2, sticky=tk.W, padx=10, pady=5)
        self.label_vitesse = tk.Label(info_grid, text="0.0 px/s", bg="#1a1a1a", fg="#ff9500", font=("Arial", 11, "bold"))
        self.label_vitesse.grid(row=3, column=2, sticky=tk.W, padx=10, pady=3)

        cycles_label = tk.Label(info_grid, text="🔄 Cycles Feu:", bg="#1a1a1a", fg="#ffffff", font=("Arial", 10, "bold"))
        cycles_label.grid(row=2, column=3, sticky=tk.W, padx=10, pady=5)
        self.label_cycles = tk.Label(info_grid, text="0.0", bg="#1a1a1a", fg="#5ac8fa", font=("Arial", 11, "bold"))
        self.label_cycles.grid(row=3, column=3, sticky=tk.W, padx=10, pady=3)

    # === TOUTES LES MÉTHODES SUIVANTES RESTENT IDENTIQUES ===
    def _demarrer(self):
        if not self.en_cours:
            self.simulation.demarrer()
            self.en_cours = True
            self.en_pause = False
            self.animation_active = True
            self.btn_play.config(state=tk.DISABLED)
            self.btn_pause.config(state=tk.NORMAL)
            self.btn_stop.config(state=tk.NORMAL)
            if self.logger:
                self.logger.log_demarrage(self.scenario_actuel.nom)
            if self.db_manager:
                self.db_manager.enregistrer_action("DEMARRAGE", "Simulation démarrée", self.scenario_actuel.nom)
            print(f"✅ Simulation démarrée - Scénario: {self.scenario_actuel.nom}")

    def _pause(self):
        if self.en_cours and not self.en_pause:
            self.simulation.pause()
            self.en_cours = False
            self.en_pause = True
            self.btn_play.config(state=tk.NORMAL)
            self.btn_pause.config(state=tk.DISABLED)
            if self.logger:
                self.logger.log_pause(self.scenario_actuel.nom)
            if self.db_manager:
                self.db_manager.enregistrer_action("PAUSE", "Simulation en pause", self.scenario_actuel.nom)
            print("⏸️  Simulation en pause")

    def _arreter(self):
        if self.en_cours or self.en_pause:
            self.simulation.arreter()
            self.en_cours = False
            self.en_pause = False
            self.animation_active = False
            self.btn_play.config(state=tk.NORMAL)
            self.btn_pause.config(state=tk.DISABLED)
            if self.logger:
                self.logger.log_arret(self.scenario_actuel.nom)
            if self.db_manager:
                self.db_manager.enregistrer_action("ARRÊT", "Simulation arrêtée", self.scenario_actuel.nom)
            print("⏹️  Simulation arrêtée")

    def _reinitialiser(self):
        self.simulation.reinitialiser()
        self.en_cours = False
        self.en_pause = False
        self.animation_active = False
        self.btn_play.config(state=tk.NORMAL)
        self.btn_pause.config(state=tk.DISABLED)
        if self.scene_turtle is not None:
            self.scene_turtle.effacer_toutes_les_voitures()
        if self.logger:
            self.logger.log_reset(self.scenario_actuel.nom)
        if self.db_manager:
            self.db_manager.enregistrer_action("RÉINITIALISATION", "Simulation réinitialisée", self.scenario_actuel.nom)
        print("🔄 Simulation réinitialisée")

    def _changer_scenario(self, event=None):
        nom_scenario = self.combo_scenario.get()
        nouveau_scenario = obtenir_scenario_par_nom(nom_scenario)
        if nouveau_scenario:
            ancien_scenario = self.scenario_actuel.nom
            self.scenario_actuel = nouveau_scenario
            self.simulation.changer_scenario(nouveau_scenario)
            self.simulation.mode_manuel = nouveau_scenario.est_mode_manuel()
            self.simulation.scenario = nouveau_scenario
            if self.logger:
                self.logger.log_changement_scenario(ancien_scenario, nom_scenario)
            if self.db_manager:
                self.db_manager.enregistrer_action("CHANGEMENT_SCÉNARIO", f"Passage à {nom_scenario}", nom_scenario)
            print(f"📍 Scénario changé: {ancien_scenario} → {nom_scenario}")

    def _forcer_feu_manuel(self, nouvel_etat):
        if self.scenario_actuel.est_mode_manuel():
            etat_enum = EtatFeu[nouvel_etat]
            bascule = self.simulation.forcer_etat_feu_manuel(etat_enum)
            if bascule:
                self.root.after(3000, bascule)
            if self.logger:
                self.logger.log_action(type_action="FEU", description=f"Feu forcé à {nouvel_etat}", scenario=self.scenario_actuel.nom)
            if self.db_manager:
                self.db_manager.enregistrer_action(type_action="MANUEL", description=f"Feu changé en {nouvel_etat}", scenario=self.scenario_actuel.nom)
            print(f"🎮 Feu forcé en MANUEL: {nouvel_etat}")
        else:
            print("⚠️ Mode manuel non activé")

    def _mettre_a_jour_etat(self):
        try:
            etats_feux = self.simulation.obtenir_tous_les_etats_feux_affichage()
            etat_principal = etats_feux.get("NE", "ROUGE")
            self.label_etat_feu.config(text=etat_principal)
            couleurs_etat = {"ROUGE": "#ff3b30", "ORANGE": "#ff9500", "VERT": "#34c759", "NOIR": "#999999"}
            self.label_etat_feu.config(fg=couleurs_etat.get(etat_principal, "#ffffff"))

            self.label_phase.config(text=self.simulation.obtenir_phase_actuelle())
            self.label_voitures.config(text=str(self.simulation.obtenir_nombre_voitures()))
            self.label_temps.config(text=f"{self.simulation.obtenir_temps_elapsed():.1f}s")
            self.label_scenario.config(text=self.scenario_actuel.nom)

            stats = self.simulation.obtenir_statistiques()
            self.label_vitesse.config(text=f"{stats.get('vitesse_moyenne', 0.0):.1f} px/s")
            self.label_cycles.config(text=f"{stats.get('nombre_cycles_feu', 0.0):.1f}")

            if self.en_cours:
                etat_text, couleur_etat = "EN COURS ▶️", "#34c759"
            elif self.en_pause:
                etat_text, couleur_etat = "EN PAUSE ⏸️", "#ff9500"
            else:
                etat_text, couleur_etat = "ARRÊTÉE ⏹️", "#999999"
            self.label_etat_simu.config(text=etat_text, fg=couleur_etat)

            # Mise à jour Turtle
            if self.scene_turtle is not None:
                try:
                    self.scene_turtle.mettre_a_jour_tous_les_feux(etats_feux)
                    voitures = self.simulation.obtenir_voitures()
                    self.scene_turtle.mettre_a_jour_voitures(voitures)
                    self.scene_turtle.rafraichir()
                except Exception as e:
                    print(f"⚠️ Erreur Turtle: {e}")
        except Exception as e:
            print(f"⚠️ Erreur mise à jour état: {e}")

    def _loop_simulation(self):
        if self.animation_active:
            try:
                self.simulation.tick()
                self._mettre_a_jour_etat()
            except Exception as e:
                print(f"⚠ Erreur boucle: {e}")
        self.root.after(50, self._loop_simulation)

    def run(self):
        self.root.mainloop()


def main():
    root = tk.Tk()
    app = SimulationGUI(root)
    app.run()


if __name__ == "__main__":
    main()