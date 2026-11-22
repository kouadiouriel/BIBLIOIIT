"""Module E : menu console. Point d'entrée : python console.py"""
from service import Bibliotheque, ErreurBiblio

MENU = """
=== BiblioIIT ===
1. Rechercher un livre   2. Emprunter
3. Rendre                4. Retards
5. Ajouter un livre      6. Livres disponibles
0. Quitter"""


def _fmt(d) -> str:
    return d.strftime("%d/%m/%Y")


def choisir_livre(biblio: Bibliotheque, entree, sortie):
    """Demande un code OU un mot-clé ; si plusieurs livres, on choisit dans une liste."""
    saisie = entree("Code ou mot-clé du livre : ").strip()
    trouves = biblio.trouver_livres(saisie)
    if not trouves:
        raise ErreurBiblio("Aucun livre trouvé")
    if len(trouves) == 1:
        return trouves[0]
    sortie("Plusieurs livres trouvés :")
    for i, livre in enumerate(trouves, 1):
        sortie(f"  {i}. {livre}")
    numero = entree("Numéro dans la liste : ").strip()
    if not numero.isdigit() or not 1 <= int(numero) <= len(trouves):
        raise ErreurBiblio("Numéro invalide")
    return trouves[int(numero) - 1]


def boucle(biblio: Bibliotheque, entree=input, sortie=print) -> None:
    while True:
        sortie(MENU)
        choix = entree("Votre choix : ").strip()
        try:
            if choix == "0":
                sortie("Au revoir.")
                return
            elif choix == "1":
                mot = entree("Mot-clé (vide = tous les livres) : ")
                trouves = biblio.rechercher(mot)
                for l in trouves:
                    etat = "disponible" if biblio.est_disponible(l.code) else "emprunté"
                    sortie(f"  {l}  [{etat}]")
                if not trouves:
                    sortie("  Aucun résultat.")
            elif choix == "2":
                livre = choisir_livre(biblio, entree, sortie)
                matricule = entree("Matricule : ").strip()
                retour = biblio.emprunter(livre.code, matricule)
                sortie(f"Emprunt enregistré. Retour prévu le {_fmt(retour)}.")
            elif choix == "3":
                livre = choisir_livre(biblio, entree, sortie)
                retard = biblio.rendre(livre.code)
                sortie("Retour enregistré." + (f" Retard : {retard} jour(s)." if retard else ""))
            elif choix == "4":
                liste = biblio.retards()
                for e, j in liste:
                    sortie(f"  {e.code_livre}  {e.matricule}  retard de {j} jour(s)")
                if not liste:
                    sortie("  Aucun retard.")
            elif choix == "5":
                titre = entree("Titre : ")
                auteur = entree("Auteur : ")
                annee = entree("Année : ")
                livre = biblio.ajouter_livre(titre, auteur, annee)
                sortie(f"Livre ajouté : {livre}")
            elif choix == "6":
                dispo = biblio.livres_disponibles()
                for l in dispo:
                    sortie(f"  {l}")
                if not dispo:
                    sortie("  Aucun livre disponible.")
            else:
                sortie("Choix invalide : tapez un chiffre du menu (0 à 6).")
                if choix and not choix.isdigit():
                    sortie("Astuce : pour chercher un livre, tapez d'abord 1, puis le mot-clé.")
        except ErreurBiblio as err:
            sortie(f"Impossible : {err}")


def main() -> None:
    from depot_sqlite import DepotSqlite

    depot = DepotSqlite("biblio.db")
    depot.charger_livres_initiaux()
    boucle(Bibliotheque(depot))
    depot.fermer()


if __name__ == "__main__":
    main()
