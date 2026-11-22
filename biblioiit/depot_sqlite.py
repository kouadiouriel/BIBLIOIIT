"""Module C : accès à la base SQLite (seul module qui écrit du SQL)."""
import sqlite3
import unicodedata
from datetime import date
from typing import List, Optional

from modeles import Emprunt, Livre

LIVRES_INITIAUX = [
    Livre("L001", "Le Vieux Nègre et la médaille", "Ferdinand Oyono", 1956),
    Livre("L002", "Les Soleils des indépendances", "Ahmadou Kourouma", 1968),
    Livre("L003", "Une si longue lettre", "Mariama Bâ", 1979),
    Livre("L004", "Allah n'est pas obligé", "Ahmadou Kourouma", 2000),
]


def _normaliser(texte: str) -> str:
    """minuscules + sans accents : 'Indépendances' -> 'independances'."""
    sans_accents = unicodedata.normalize("NFD", texte)
    return "".join(c for c in sans_accents if unicodedata.category(c) != "Mn").lower()


class DepotSqlite:
    def __init__(self, chemin: str = "biblio.db"):
        self.conn = sqlite3.connect(chemin)
        self.conn.row_factory = sqlite3.Row
        self._creer_tables()

    def _creer_tables(self) -> None:
        self.conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS livres (
                code TEXT PRIMARY KEY, titre TEXT NOT NULL,
                auteur TEXT NOT NULL, annee INTEGER NOT NULL);
            CREATE TABLE IF NOT EXISTS emprunts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code_livre TEXT NOT NULL REFERENCES livres(code),
                matricule TEXT NOT NULL,
                date_emprunt TEXT NOT NULL,
                date_retour_prevue TEXT NOT NULL,
                date_retour_effective TEXT);
            """
        )
        self.conn.commit()

    def charger_livres_initiaux(self) -> None:
        for livre in LIVRES_INITIAUX:
            self.ajouter_livre(livre)

    def ajouter_livre(self, livre: Livre) -> None:
        self.conn.execute(
            "INSERT OR IGNORE INTO livres VALUES (?, ?, ?, ?)",
            (livre.code, livre.titre, livre.auteur, livre.annee),
        )
        self.conn.commit()

    def get_livre(self, code: str) -> Optional[Livre]:
        r = self.conn.execute("SELECT * FROM livres WHERE code = ?", (code,)).fetchone()
        return Livre(**dict(r)) if r else None

    def tous_les_livres(self) -> List[Livre]:
        rows = self.conn.execute("SELECT * FROM livres ORDER BY code").fetchall()
        return [Livre(**dict(r)) for r in rows]

    def rechercher(self, mot_cle: str) -> List[Livre]:
        """Recherche sans tenir compte des majuscules ni des accents."""
        mot = _normaliser(mot_cle)
        return [
            l for l in self.tous_les_livres()
            if mot in _normaliser(l.titre) or mot in _normaliser(l.auteur)
        ]

    def prochain_code(self) -> str:
        """Prochain code libre : L005, L006, ..."""
        dernier = 0
        for l in self.tous_les_livres():
            if l.code[1:].isdigit():
                dernier = max(dernier, int(l.code[1:]))
        return f"L{dernier + 1:03d}"

    @staticmethod
    def _emprunt(r: sqlite3.Row) -> Emprunt:
        eff = r["date_retour_effective"]
        return Emprunt(
            r["code_livre"], r["matricule"],
            date.fromisoformat(r["date_emprunt"]),
            date.fromisoformat(r["date_retour_prevue"]),
            date.fromisoformat(eff) if eff else None,
        )

    def emprunt_en_cours(self, code_livre: str) -> Optional[Emprunt]:
        r = self.conn.execute(
            "SELECT * FROM emprunts WHERE code_livre = ? AND date_retour_effective IS NULL",
            (code_livre,),
        ).fetchone()
        return self._emprunt(r) if r else None

    def nb_emprunts_en_cours(self, matricule: str) -> int:
        return self.conn.execute(
            "SELECT COUNT(*) FROM emprunts WHERE matricule = ? AND date_retour_effective IS NULL",
            (matricule,),
        ).fetchone()[0]

    def enregistrer_emprunt(self, e: Emprunt) -> None:
        self.conn.execute(
            "INSERT INTO emprunts (code_livre, matricule, date_emprunt, date_retour_prevue) "
            "VALUES (?, ?, ?, ?)",
            (e.code_livre, e.matricule, e.date_emprunt.isoformat(),
             e.date_retour_prevue.isoformat()),
        )
        self.conn.commit()

    def cloturer_emprunt(self, code_livre: str, date_retour: date) -> None:
        self.conn.execute(
            "UPDATE emprunts SET date_retour_effective = ? "
            "WHERE code_livre = ? AND date_retour_effective IS NULL",
            (date_retour.isoformat(), code_livre),
        )
        self.conn.commit()

    def emprunts_en_cours(self) -> List[Emprunt]:
        rows = self.conn.execute(
            "SELECT * FROM emprunts WHERE date_retour_effective IS NULL"
        ).fetchall()
        return [self._emprunt(r) for r in rows]

    def fermer(self) -> None:
        self.conn.close()
