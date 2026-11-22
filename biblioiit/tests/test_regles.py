from datetime import date
import regles


def test_date_retour_prevue():
    assert regles.date_retour_prevue(date(2026, 10, 1)) == date(2026, 10, 15)


def test_retard():
    assert regles.jours_de_retard(date(2026, 10, 15), date(2026, 10, 20)) == 5
    assert regles.jours_de_retard(date(2026, 10, 15), date(2026, 10, 10)) == 0
    assert regles.est_en_retard(date(2026, 10, 15), date(2026, 10, 16))


def test_matricule():
    assert regles.matricule_valide("E2026-001")
    assert not regles.matricule_valide("2026-001")
    assert not regles.matricule_valide("")


def test_quota():
    assert regles.quota_atteint(3)
    assert not regles.quota_atteint(2)
