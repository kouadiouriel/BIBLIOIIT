from datetime import date
from modeles import Emprunt, Livre


def test_livre_str():
    assert "Kourouma" in str(Livre("L002", "Les Soleils des indépendances", "Ahmadou Kourouma", 1968))


def test_emprunt_en_cours():
    e = Emprunt("L001", "E2026-001", date(2026, 10, 1), date(2026, 10, 15))
    assert e.en_cours
    e.date_retour_effective = date(2026, 10, 5)
    assert not e.en_cours
