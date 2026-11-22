from datetime import date
import pytest
from depot_sqlite import DepotSqlite
from service import Bibliotheque, ErreurBiblio

JOUR = date(2026, 10, 1)


@pytest.fixture
def biblio():
    d = DepotSqlite(":memory:")
    d.charger_livres_initiaux()
    yield Bibliotheque(d)
    d.fermer()


def test_emprunt_ok(biblio):
    assert biblio.emprunter("L002", "E2026-001", JOUR) == date(2026, 10, 15)


def test_deja_emprunte(biblio):
    biblio.emprunter("L002", "E2026-001", JOUR)
    with pytest.raises(ErreurBiblio, match="déjà emprunté"):
        biblio.emprunter("L002", "E2026-002", JOUR)


def test_livre_inconnu_et_matricule_invalide(biblio):
    with pytest.raises(ErreurBiblio):
        biblio.emprunter("L999", "E2026-001", JOUR)
    with pytest.raises(ErreurBiblio):
        biblio.emprunter("L001", "abc", JOUR)


def test_quota(biblio):
    for c in ("L001", "L002", "L003"):
        biblio.emprunter(c, "E2026-001", JOUR)
    with pytest.raises(ErreurBiblio, match="Quota"):
        biblio.emprunter("L004", "E2026-001", JOUR)


def test_rendre_et_retards(biblio):
    biblio.emprunter("L002", "E2026-001", JOUR)
    assert [(e.code_livre, j) for e, j in biblio.retards(date(2026, 10, 20))] == [("L002", 5)]
    assert biblio.rendre("L002", date(2026, 10, 20)) == 5
    assert biblio.retards(date(2026, 10, 20)) == []
    with pytest.raises(ErreurBiblio):
        biblio.rendre("L002")


def test_ajouter_livre(biblio):
    l = biblio.ajouter_livre("Python", "Moi", "2020")
    assert l.code == "L005"
    assert biblio.rechercher("python")[0].code == "L005"
    with pytest.raises(ErreurBiblio):
        biblio.ajouter_livre("", "Moi", "2020")
    with pytest.raises(ErreurBiblio):
        biblio.ajouter_livre("X", "Y", "abc")


def test_trouver_par_code_ou_mot(biblio):
    assert [l.code for l in biblio.trouver_livres("l002")] == ["L002"]
    assert [l.code for l in biblio.trouver_livres("soleils")] == ["L002"]


def test_livres_disponibles(biblio):
    assert len(biblio.livres_disponibles()) == 4
    biblio.emprunter("L002", "E2026-001", JOUR)
    assert "L002" not in [l.code for l in biblio.livres_disponibles()]
    assert not biblio.est_disponible("L002")
