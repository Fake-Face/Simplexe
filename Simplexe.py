class Simplexe:
    def __init__(self, modele):
        self.modele = modele
        self.tableau = []  # Le tableau du simplexe
        self.base = [None] * modele.m  # Variables en base
        self.non_base = [i for i in range(modele.n)]  # Variables hors base initiales

        # Initialisation des variables d'écart/excès
        for i in range(modele.m):
            self.non_base.append(modele.n + i)  # Ajouter les indices des variables d'écart/excès

        self.init_tableau()

    def iteration(self, c):
        # Étape 1 : Trouver la variable entrante en utilisant le vecteur de coût c
        entrant_index = self.trouver_variable_entrante(c)
        if entrant_index is None:
            return False  # Condition d'arrêt si aucune variable entrante trouvée

        # Étape 2 : Trouver la variable sortante
        sortant_index = self.trouver_variable_sortante(entrant_index)
        if sortant_index is None:
            raise Exception("Le problème est non borné.")

        # Étape 3 : Pivoter autour de la cellule choisie
        self.pivot(entrant_index, sortant_index)
        return True

    def init_tableau(self):
        # Initialiser le tableau avec des zéros
        self.tableau = [[0 for _ in range(self.modele.n + self.modele.m + 1)] for _ in range(self.modele.m + 1)]

        # Ajouter les coefficients des variables de décision et des variables d'écart/excès
        for i in range(self.modele.m):
            for j in range(self.modele.n):
                self.tableau[i][j] = self.modele.a[i][j]

            # Pour les contraintes '≥' et '≤', ajouter une variable d'écart
            if self.modele.sens[i]:
                # Ajouter une variable d'écart avec un coefficient de -1 pour '≥'
                self.tableau[i][self.modele.n + i] = -1 if self.modele.sens[i] else 1
            self.tableau[i][-1] = self.modele.b[i]  # Ajouter la valeur constante de la contrainte

        # Ajouter les coefficients de la fonction "objectif"
        for j in range(self.modele.n):
            self.tableau[-1][j] = -self.modele.c[j] if self.modele.maximisation else self.modele.c[j]

        # Définir les variables de base initiales (variables d'écart/excès)
        self.base = [self.modele.n + i for i in range(self.modele.m)]

    def trouver_variable_entrante(self, c):
        # Chercher la colonne avec le coût réduit le plus élevé positif en utilisant c
        max_cout = 0
        index = None
        for i in self.non_base:
            if i < len(c):  # Vérifier si l'index est dans la plage de c
                cout_reduit = c[i] - sum(
                    self.tableau[-1][j] * self.tableau[j][i] for j in range(self.modele.m))
                if cout_reduit > max_cout:
                    max_cout = cout_reduit
                    index = i
        return index

    def trouver_variable_sortante(self, entrant_index):
        # Chercher la ligne avec le rapport minimum positif
        min_ratio = float('inf')
        index_sortant = None

        for i in range(self.modele.m):
            if self.tableau[i][entrant_index] > 0:
                ratio = self.tableau[i][-1] / self.tableau[i][entrant_index]
                if ratio < min_ratio:
                    min_ratio = ratio
                    index_sortant = i

        return index_sortant

    def pivot(self, entrant_index, sortant_index):
        # Vérifier que les indices sont valides
        if entrant_index is None or sortant_index is None:
            raise ValueError("Les indices entrant et/ou sortant sont invalides.")

        # Vérifier que les indices sont des entiers
        if not isinstance(entrant_index, int) or not isinstance(sortant_index, int):
            raise TypeError("Les indices entrant et/ou sortant doivent être des entiers.")

        # Mise à jour de la variable en base
        self.base[sortant_index] = entrant_index

        # Pivoter autour de la cellule (sortant_index, entrant_index)
        pivot_value = self.tableau[sortant_index][entrant_index]

        # Mettre à jour la ligne de pivot
        for j in range(len(self.tableau[0])):
            self.tableau[sortant_index][j] /= pivot_value

        # Mettre à jour les autres lignes
        for i in range(len(self.tableau)):
            if i != sortant_index:
                ratio = self.tableau[i][entrant_index]
                for j in range(len(self.tableau[0])):
                    self.tableau[i][j] -= ratio * self.tableau[sortant_index][j]

        # Mise à jour des variables hors base
        if entrant_index in self.non_base:
            self.non_base.remove(entrant_index)
        if sortant_index not in self.non_base:
            self.non_base.append(sortant_index)

    def optimisation(self):

        iteration_compteur = 0
        while True:
            iteration_compteur += 1
            print(f"Iteration {iteration_compteur}")

            # Vérifier si le tableau est déjà optimal
            if self.est_optimal():
                print("Solution optimale trouvée.")
                break

            # Sélectionner la variable entrante en utilisant le vecteur de coût
            entrant_index = self.trouver_variable_entrante(self.modele.c)
            if entrant_index is None:
                print("Solution actuelle est optimale.")
                break

            # Sélectionner la variable sortante
            sortant_index = self.trouver_variable_sortante(entrant_index)
            if sortant_index is None:
                print("Le problème est non borné.")
                break

    def est_optimal(self):
        # Vérifier si tous les coûts réduits sont négatifs ou nuls
        for cout in self.tableau[-1][:-1]:
            if cout > 0:
                return False
        return True

    def print(self):
        solution = [0] * self.modele.n
        for i in range(self.modele.m):
            if self.base[i] < self.modele.n:
                solution[self.base[i]] = self.tableau[i][-1]

        # La valeur de la fonction objectif à l'optimum
        valeur_objectif = self.tableau[-1][-1] if not self.modele.maximisation else -self.tableau[-1][-1]
        print("Solution optimale:")
        for i in range(self.modele.n):
            print(f"X{i + 1} = {solution[i]}")
        print(f"Valeur de la fonction objectif: {valeur_objectif}")

        # Affichage du coefficient Z
        print(f"Coefficient Z (valeur de l'objectif à l'optimum): {valeur_objectif}")
