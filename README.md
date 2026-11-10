# Simulateur de carrefour à feux tricolores

Un carrefour à quatre feux coordonnés et la circulation des voitures qui le traversent, simulés en Python avec une interface graphique.

## Ce que fait la simulation

- **Quatre feux, deux axes.** Les feux nord-sud et est-ouest alternent par phases. Avant chaque changement, tous les feux passent à l'orange.
- **Des voitures qui respectent le code.** Elles apparaissent sur les quatre voies, gardent une distance minimale avec la voiture de devant, s'arrêtent au feu rouge, et ne tiennent plus compte du feu une fois la ligne d'arrêt franchie.
- **Quatre scénarios**, que l'on peut changer pendant la simulation :

| Scénario | Vert | Orange | Arrivée des voitures |
|---|---|---|---|
| Circulation normale | 12 s | 4 s | 0,3 |
| Heure de pointe | 40 s | 3 s | 2,0 |
| Mode nuit | — | orange clignotant | 0,1 |
| Mode manuel | commandé par l'utilisateur | | 0,5 |

- **Un historique en base.** Les actions, les voitures, les changements d'état des feux et les statistiques sont enregistrés dans une base SQLite (4 tables), et peuvent être exportés en CSV.
- **Une interface de contrôle** en Tkinter : lecture, pause, arrêt, remise à zéro, choix du scénario, commande manuelle des feux, et indicateurs en temps réel (phase, nombre de voitures, vitesse moyenne, cycles). Le carrefour est dessiné et animé avec Turtle.

## Organisation du code

Chaque fichier a une seule responsabilité :

| Fichier | Rôle |
|---|---|
| `traffic_light.py` | Un feu seul : son état et son chronomètre |
| `traffic_light_manager.py` | Les quatre feux et l'alternance des phases |
| `vehicules.py` | Une voiture : position, vitesse, direction |
| `traffic_manager.py` | L'arrivée des voitures, les distances et l'arrêt au feu |
| `scenarios.py` | Les paramètres de chaque scénario |
| `simulation.py` | La boucle de simulation, qui fait avancer le temps |
| `database.py` | La base SQLite et l'export CSV |
| `logger.py` | Le journal des événements |
| `turtle_scene.py` | Le dessin du carrefour |
| `gui.py` | La fenêtre et ses commandes |
| `main.py` | Le point d'entrée |

Le feu ne connaît pas les autres feux, et la voiture ne connaît que le feu de sa voie : c'est le gestionnaire au-dessus qui coordonne.

## Lancer la simulation

Le projet n'utilise que la bibliothèque standard de Python (3.9 ou plus récent) : rien à installer.

```bash
python3 main.py
```

Sur certaines distributions Linux, Tkinter s'installe à part : `sudo apt install python3-tk`.

## Vérifié

Sur 300 secondes simulées dans chacun des quatre scénarios, les deux axes n'ont jamais été au vert en même temps, et un axe n'a jamais été au vert pendant que l'autre était à l'orange.
