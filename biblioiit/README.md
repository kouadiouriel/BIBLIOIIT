# BiblioIIT — gestion de bibliothèque (console, Python)

Lancer : `python console.py`  |  Tests : `pip install -r requirements.txt && pytest`

| Module | Rôle | Branche |
|---|---|---|
| regles.py | règles (durée de prêt, quota, retards) | feature/regles — A |
| modeles.py | classes Livre, Emprunt | feature/modeles — B |
| depot_sqlite.py | accès SQLite | feature/base — C |
| service.py | rechercher, emprunter, rendre, retards | feature/service — D |
| console.py | menu | feature/menu — E |
| tests/ | chacun ses tests | |

Livrable : dépôt partagé, ≥ 5 commits par membre, une PR relue par une autre personne, pipeline vert.
