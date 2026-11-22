import pytest
from console import boucle
from depot_sqlite import DepotSqlite
from service import Bibliotheque


def lancer(saisies):
    d = DepotSqlite(":memory:")
    d.charger_livres_initiaux()
    it = iter(saisies)
    sortie = []
    boucle(Bibliotheque(d), entree=lambda _: next(it), sortie=sortie.append)
    return "\n".join(sortie)


def test_session_du_sujet():
    out = lancer(["1", "Kourouma", "2", "L002", "E2026-001", "2", "L002", "E2026-002", "0"])
    assert "Allah n'est pas obligé" in out
    assert "Emprunt enregistré. Retour prévu le" in out
    assert "Impossible : Le livre « Les Soleils des indépendances » est déjà emprunté" in out


def test_choix_invalide():
    assert "Choix invalide" in lancer(["9", "0"])


def test_ajouter_puis_emprunter_par_titre():
    out = lancer(["5", "Python facile", "Jay", "2024",
                  "2", "python", "E2026-001", "0"])
    assert "Livre ajouté : L005" in out
    assert "Emprunt enregistré" in out


def test_choix_dans_liste():
    out = lancer(["2", "Kourouma", "1", "E2026-001", "0"])
    assert "Plusieurs livres trouvés" in out
    assert "Emprunt enregistré" in out


def test_texte_au_menu_donne_astuce():
    assert "tapez d'abord 1" in lancer(["Kourouma", "0"])


def test_option_livres_disponibles():
    out = lancer(["2", "L002", "E2026-001", "6", "1", "soleils", "0"])
    disponibles = out.split("Emprunt enregistré")[1]
    assert "L004" in disponibles
    assert "[emprunté]" in out
