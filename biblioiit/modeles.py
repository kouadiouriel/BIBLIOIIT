"""Module B : modèles de données."""
from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass(frozen=True)
class Livre:
    code: str
    titre: str
    auteur: str
    annee: int

    def __str__(self) -> str:
        return f"{self.code}  {self.titre} — {self.auteur} ({self.annee})"


@dataclass
class Emprunt:
    code_livre: str
    matricule: str
    date_emprunt: date
    date_retour_prevue: date
    date_retour_effective: Optional[date] = None

    @property
    def en_cours(self) -> bool:
        return self.date_retour_effective is None
