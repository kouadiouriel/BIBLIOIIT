"""Module A : règles métier de la bibliothèque (aucune dépendance aux autres modules)."""
import re
from datetime import date, timedelta

DUREE_PRET_JOURS = 14
MAX_EMPRUNTS_PAR_MEMBRE = 3
FORMAT_MATRICULE = re.compile(r"^E\d{4}-\d{3}$")  # ex : E2026-001


def matricule_valide(matricule: str) -> bool:
    """Vrai si le matricule respecte le format E2026-001."""
    return bool(FORMAT_MATRICULE.match(matricule or ""))


def date_retour_prevue(date_emprunt: date) -> date:
    """Date d'emprunt + durée de prêt."""
    return date_emprunt + timedelta(days=DUREE_PRET_JOURS)


def jours_de_retard(date_retour: date, aujourdhui: date) -> int:
    """Nombre de jours de retard (0 si pas en retard)."""
    return max(0, (aujourdhui - date_retour).days)


def est_en_retard(date_retour: date, aujourdhui: date) -> bool:
    return jours_de_retard(date_retour, aujourdhui) > 0


def quota_atteint(nb_emprunts_en_cours: int) -> bool:
    return nb_emprunts_en_cours >= MAX_EMPRUNTS_PAR_MEMBRE


def annee_valide(annee: int) -> bool:
    """Année de publication plausible."""
    return 1000 <= annee <= date.today().year + 1
