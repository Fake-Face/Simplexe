from Modele import *
import sys

class Simplexe:
    def __init__(self, modele):
        print("\n__init__\n")
        #On récupère le modèle forme normale
        self.modele = modele
        
        #On créé le tableau + on le transforme en forme standard
        self.c_ligne = []
        self.tableau = self.create_initial_tableau()
        self.coeff_z = [0] * self.modele.m


    def iteration(self, c):
        print("TODO")        

        # Étape 1 : Sélection de la colonne pivot (variable à entrer)
        pivot_col = self.select_pivot_column(c)
        if pivot_col < 0:
            print("Aucun coefficient adéquat dans la ligne objectif. Solution optimale trouvée.")
            return False

        # Étape 2 : Sélection de la ligne pivot (variable à sortir)
        pivot_row = self.select_pivot_row(pivot_col)
        if pivot_row < 0:
            print("Aucune ligne pivot valide trouvée. La solution est non bornée.")
            return False
        
        print("Le pivot est donc : ", self.tableau[pivot_row][pivot_col])

        # Étape 3 : Effectuer des opérations sur les lignes pour former un nouveau tableau
        self.form_new_tableau(pivot_row, pivot_col)
        return True

    def select_pivot_column(self, c):
        # Sélection de la colonne avec le coefficient maximum dans c
        print("\nselect_pivot_column")
        max_value = 0
        pivot_col = -1
        for i in range(len(c)):
            if c[i] > max_value:
                max_value = c[i]
                pivot_col = i

        print("max value = ", max_value)
        return pivot_col

    def select_pivot_row(self, pivot_col):
        print("\nselect_pivot_row")
        # Sélection de la ligne pivot basée sur le test du ratio minimum
        min_ratio = float('inf')
        pivot_row = -1
        for i in range(1, self.modele.m+1):
            if self.tableau[i][pivot_col] > 0:  # Ignorer les éléments négatifs ou nuls
                #print(self.tableau[i][pivot_col])
                ratio = self.tableau[i][self.modele.m+self.modele.n] / self.tableau[i][pivot_col]
                print("ratio = ", ratio)
                if ratio < min_ratio:
                    min_ratio = ratio
                    pivot_row = i
                    print("min_ratio = ", min_ratio)

        return pivot_row

    def form_new_tableau(self, pivot_row, pivot_col):

        print("\nform_new_tableau")
        # Réorganiser le tableau pour la nouvelle base
        pivot_element = self.tableau[pivot_row][pivot_col]

        # Normaliser la ligne pivot
        for j in range(len(self.tableau[1])):
            self.tableau[pivot_row][j] /= pivot_element
            #print(self.tableau[pivot_row][j])

        # Modifier les autres lignes
        for i in range(1, self.modele.m):
            if i != pivot_row:
                factor = self.tableau[i][pivot_col]
                for j in range(len(self.tableau[1])):
                    self.tableau[i][j] -= factor * self.tableau[pivot_row][j]

        #On modifie la base
        self.coeff_z[pivot_row-1] = self.c_ligne[pivot_col]
        
        
        #On remplie la ligne z_i
        self.tableau[len(self.tableau)-2] = [0] * (self.modele.m+self.modele.n)
        for k in range(0, self.modele.m+self.modele.n):
            for l in range(len(self.coeff_z)):
                self.tableau[len(self.tableau)-2][k] += (self.coeff_z[l] * self.tableau[l+1][k])
        
        #On actualise la dernière ligne
        for m in range(0, self.modele.m+self.modele.n):
            self.c_ligne[m] = self.tableau[0][m] - self.tableau[len(self.tableau)-2][m]
            #print(self.c_ligne[m])
            
        self.tableau[len(self.tableau)-1] = self.c_ligne

    def create_initial_tableau(self):
        tableau = []
        sens = []
        tableau.append(self.modele.c + ([0] * self.modele.m))

        # Ajout des contraintes au tableau
        for i in range(self.modele.m):
            
            sens = [0] * self.modele.m 
            if(self.modele.sens[i]):
                sens[i] = -1
            else:
                sens[i] = 1

            row = self.modele.a[i]+ sens + [self.modele.b[i]]
            tableau.append(row)

        #Ajout de l'avant-dernière ligne contenant les coefficients zi
        z_row = [0] * (self.modele.m + self.modele.n + 1)
        tableau.append(z_row)

        # Ajout de la fonction objectif au tableau
        objective_row = self.modele.c + ([0] * (self.modele.m+1))
        tableau.append(objective_row)
        self.c_ligne = objective_row

        return tableau

    def optimisation(self):
        print("\noptimisation\n")
        iteration = 1
        #self.print()
        #self.iteration(self.c_ligne)

        #Condition d'arrêt : on regarde s'il reste des valeurs positives non nulles à la dernière ligne. Si non on s'arrête
        if self.modele.maximisation:
            while self.isDoneMax(self.tableau[len(self.tableau)-1]) == False:
                print("Iteration n°", iteration)
                self.print()
                self.iteration(self.c_ligne)
                iteration += 1
        else:
            while self.isDoneMin(self.tableau[len(self.tableau)-1]) == False:
                print("Iteration n°", iteration)
                self.print()
                self.iteration(self.c_ligne)
                iteration += 1
        
        #self.print()
        #self.iteration(self.c_ligne)
        self.print()
        Z = self.calculSol()
        print("\nNous avons trouvé une solution optimale du problème!")
        print("Elle vaut Z = ", Z)
        sys.exit()
        

    def print(self):
        print("\nprint\n")
        nb_lignes = self.modele.m + 3
        #nb_colonnes = self.modele.m + self.modele.n + 1
        for row in self.tableau:
            row_str = " | ".join(map(str, row))
            print(f"| {row_str} |")
            print("-" * (len(row_str) + nb_lignes))

        
        print("\nCoeff. Z")
        row_str = " | ".join(map(str, self.coeff_z))
        print("-" * (len(row_str) + 5))
        print(f"| {row_str} |")
        print("-" * (len(row_str) + 5))

    def isDoneMax(self, row):

        for variable in row:
            if variable > 0:
                return False
        return True
    
    def isDoneMin(self, row):
        for variable in row:
            if variable < 0:
                return False
        return True


    def calculSol(self):
        result = 0
        for i in range(1, len(self.coeff_z)+1):
            result += self.tableau[i][len(self.tableau[1])-1] * self.coeff_z[i-1]

        return result

###################
# Version Dimitri #
###################


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


