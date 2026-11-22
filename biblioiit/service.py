"""Module D : logique applicative (rechercher, emprunter, rendre, retards)."""
from datetime import date
from typing import List, Optional, Tuple

import regles
from modeles import Emprunt, Livre


class ErreurBiblio(Exception):
    """Erreur métier dont le message est affichable tel quel à l'utilisateur."""


class Bibliotheque:
    def __init__(self, depot):
        self.depot = depot

    def rechercher(self, mot_cle: str) -> List[Livre]:
        return self.depot.rechercher(mot_cle.strip())

    def ajouter_livre(self, titre: str, auteur: str, annee) -> Livre:
        """Ajoute un livre ; le code (L005, L006...) est généré automatiquement."""
        titre, auteur = titre.strip(), auteur.strip()
        if not titre or not auteur:
            raise ErreurBiblio("Le titre et l'auteur sont obligatoires")
        try:
            annee = int(annee)
        except (TypeError, ValueError):
            raise ErreurBiblio("L'année doit être un nombre (ex : 1968)")
        if not regles.annee_valide(annee):
            raise ErreurBiblio(f"Année invalide : {annee}")
        livre = Livre(self.depot.prochain_code(), titre, auteur, annee)
        self.depot.ajouter_livre(livre)
        return livre

    def est_disponible(self, code: str) -> bool:
        return self.depot.emprunt_en_cours(code) is None

    def livres_disponibles(self) -> List[Livre]:
        """Tous les livres qui ne sont pas actuellement empruntés."""
        return [l for l in self.depot.tous_les_livres() if self.est_disponible(l.code)]

    def trouver_livres(self, saisie: str) -> List[Livre]:
        """Accepte un code exact (L002) OU un mot du titre/auteur."""
        saisie = saisie.strip()
        livre = self.depot.get_livre(saisie.upper())
        return [livre] if livre else self.depot.rechercher(saisie)

    def emprunter(self, code: str, matricule: str, aujourdhui: Optional[date] = None) -> date:
        aujourdhui = aujourdhui or date.today()
        if not regles.matricule_valide(matricule):
            raise ErreurBiblio(f"Matricule invalide : {matricule}")
        livre = self.depot.get_livre(code)
        if livre is None:
            raise ErreurBiblio(f"Livre introuvable : {code}")
        if self.depot.emprunt_en_cours(code):
            raise ErreurBiblio(f"Le livre « {livre.titre} » est déjà emprunté")
        if regles.quota_atteint(self.depot.nb_emprunts_en_cours(matricule)):
            raise ErreurBiblio(f"Quota atteint ({regles.MAX_EMPRUNTS_PAR_MEMBRE} livres max)")
        retour = regles.date_retour_prevue(aujourdhui)
        self.depot.enregistrer_emprunt(Emprunt(code, matricule, aujourdhui, retour))
        return retour

    def rendre(self, code: str, aujourdhui: Optional[date] = None) -> int:
        """Enregistre le retour ; renvoie les jours de retard (0 si à l'heure)."""
        aujourdhui = aujourdhui or date.today()
        emprunt = self.depot.emprunt_en_cours(code)
        if emprunt is None:
            raise ErreurBiblio(f"Aucun emprunt en cours pour {code}")
        self.depot.cloturer_emprunt(code, aujourdhui)
        return regles.jours_de_retard(emprunt.date_retour_prevue, aujourdhui)

    def retards(self, aujourdhui: Optional[date] = None) -> List[Tuple[Emprunt, int]]:
        aujourdhui = aujourdhui or date.today()
        resultat = []
        for e in self.depot.emprunts_en_cours():
            j = regles.jours_de_retard(e.date_retour_prevue, aujourdhui)
            if j > 0:
                resultat.append((e, j))
        return resultat
