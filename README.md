# Projet TP : Systèmes d'information avancés

__Objectif :__ Concevoir un système de transactions électroniques avec une intégrité garantie, accessible
par le protocole HTTP.

__Auteurs :__
* David NAISSE (david_naisse@etu.u-bourgogne.fr)
* Benjamin SCORDEL (benjamin_scordel@etu.u-bourgogne.fr)

<hr />

## Exercice 3 : 
En utilisant Flask [3], réaliser une première version du système “Tchaï”.
Voici une liste des actions qui doivent être mises à la disposition via un API HTTP 
(voir TD-1) par votre système “Tchaï” : 
* (A1) Enregistrer une transaction. 
* (A2) Afficher une liste de toutes les transactions dans l’ordre chronologique. 
* (A3) Afficher une liste des transactions dans l’ordre chronologique liées à une 
  personne donnée. 
* (A4) Afficher le solde du compte de la personne donnée.  

## Solution :
Nous commençons par créer le fichier __readme.md__ auquel nous ajoutons 
nos noms. Nous implémentons ensuite un fichier __config.py__ qui contiendra toutes nos
variables globales afin de rendre plus pratique l'utilisation de notre programme.

Nous implémentons ensuite le fichier __app_v1.py__, qui contiendra notre code pour cet
exercice. Le fichier __database.py__ contient les informations nécessaires à la création 
de notre base de données.

Après avoir implémenté toutes les actions précédemment définies, voici la liste des 
commandes disponibles pour la __V1__ :
* __/add/from/to/pay__ (A1) : ajoute une transaction de __from__ à __to__ d'un montant de __pay__ €
* __/transactions__ (A2) : affiche toutes les transactions
* __/user/transactions__ (A3) : affiche toutes les transactions de l'utilisateur __user__
* __/uname__ (A4) : affiche les informations de l'utilisateur __uname__
* __/users__ : affiche la liste des utilisateurs enregistrés
* __/add/uname/pay__ : ajoute un utilisateur nommé __uname__ et possédant __pay__ €
* __/rmv/uname__ : supprime l'utilisateur __uname__
* __/create_database__ : initialise notre database

<hr />

## Exercice 4 - Test :
Attaquer le système en modifiant directement le fichier de données, en changeant le
montant d’une transaction.

## Solution :
Afin de réaliser ce genre d'attaque, nous rédigeons un script bash qui nous permettra d'attaquer la base de données 
directement depuis le terminal. La requête est traduite par la phrase suivante : 
* Modification du montant de la transaction n°4 à 9999€

Celle-ci est donc traduite en SQL par :
* UPDATE trans SET amount=9999 WHERE id=4

Nous obtenons donc le résultat suivant : 

![Screenshot](tests/img/test1_before.PNG)
![Screenshot](tests/img/test1_after.PNG) 

La transaction n°4 a bien vu son montant passer à 9999€.

<hr />

## Exercice 5 :
Nous ajoutons maintenant le hash d’une transaction dans son tuplet : (P1, P2, t, a, h), où a est égal à la
somme d’argent transférée de la personne P1 à la personne P2 au moment t et h correspond au hash
du tuple (P1, P2, t, a). Modifier votre programme afin d’intégrer la nouvelle structure des transactions.

## Solution :

Pour cet exercice, nous avons tout simplement à ajouter une colonne __hash__ dans la table __trans__ de notre database
puis à calculer au moment de l'ajout d'une transaction le hash correspondant au tuple (P1, P2, t, a). Après 
implémentation nous obtenons à chaque ajout d'une transaction un hash de la forme : 

![Screenshot](tests/img/hashcreation.PNG)

<hr />

## Exercice 6 :
Ajouter l’action suivante disponible en API HTTP :
(A5) Vérifier l’intégrité des données en recalculant les hashs à partir des données et en les comparant
avec les hashs stockés précédemment.

## Solution :

<hr />

## Exercice 7 :
Vérifiez que l’attaque précédente ne fonctionne plus.

## Solution :

<hr />

## Exercice 8 :
Attaquer le système en modifiant directement le fichier de données, en supprimant une
transaction. La possibilité de supprimer une transaction peut être très dangereuse, la suppression peut
entraîner la double dépense [9]

## Solution :

<hr />

## Exercice 9 :
Modifier la méthode de calcul de hash. Maintenant la valeur du hash hi+1 va dépendre
non seulement de la transaction en cours, mais également de la valeur du hash hi de la transaction
précédente.

## Solution :

<hr />

## Exercice 10 :
Vérifiez que les attaques précédentes ne fonctionnent plus.

## Solution :

<hr />

## Exercice 11 :
Attaquer le système en modifiant directement le fichier de données, en ajoutant, par
exemple, une transaction provenant d’une autre personne vers le compte de l’attaquant.

## Solution :

<hr />

## Exercice 12 :
Lire le message [4], le papier original de Satoshi Nakamoto [5] et la discussion ultérieure
sur la liste de diffusion ‘The Cryptography and Cryptography Policy Mailing List”.

## Solution :

<hr />

## Exercice 13 :
Utiliser la cryptographie asymétrique afin d’assurer l’authenticité de l’expéditeur.
## Solution :
