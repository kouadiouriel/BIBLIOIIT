from datetime import date
import pytest
from depot_sqlite import DepotSqlite
from modeles import Emprunt


@pytest.fixture
def depot():
    d = DepotSqlite(":memory:")
    d.charger_livres_initiaux()
    yield d
    d.fermer()


def test_rechercher(depot):
    assert {l.code for l in depot.rechercher("Kourouma")} == {"L002", "L004"}
    assert depot.rechercher("zzz") == []


def test_get_livre(depot):
    assert depot.get_livre("L002").annee == 1968
    assert depot.get_livre("X") is None


def test_cycle_emprunt(depot):
    e = Emprunt("L002", "E2026-001", date(2026, 10, 1), date(2026, 10, 15))
    depot.enregistrer_emprunt(e)
    assert depot.emprunt_en_cours("L002").matricule == "E2026-001"
    assert depot.nb_emprunts_en_cours("E2026-001") == 1
    depot.cloturer_emprunt("L002", date(2026, 10, 5))
    assert depot.emprunt_en_cours("L002") is None


def test_recherche_sans_accents_ni_majuscules(depot):
    assert [l.code for l in depot.rechercher("INDEPENDANCES")] == ["L002"]


def test_prochain_code(depot):
    assert depot.prochain_code() == "L005"
