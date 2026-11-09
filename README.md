FraudShield — Détection et scoring de fraude financière en temps réel
Un modèle LightGBM qui détecte 99 % des fraudes sur transactions de paiement mobile, exposé via une API FastAPI et consommé par un tableau de bord Streamlit.

Sommaire

Présentation
Architecture & composants
Liens d'accès direct
Jeu de données & features
Résultats
Installation & exécution locale
Limites & pistes d'amélioration
Auteur

 Présentation
 
FraudShield est un outil d'aide à la décision destiné aux équipes de gestion des risques. Basé sur le jeu de données PaySim (Kaggle), il vise à détecter les transactions frauduleuses tout en limitant les fausses alertes.
Points clés de l'étude
- 6 362 620 transactions analysées, dont seulement 0,13 % de fraudes.
- Les fraudes concernent deux types d'opérations : `TRANSFER` et `CASH_OUT`, soit 2 770 409 transactions retenues pour la modélisation.
- Création de deux variables (`errorBalanceOrig` et `errorBalanceDest`) pour détecter les incohérences dans les soldes.
- LightGBM atteint un rappel de 99 %, dépassant l'objectif initial de 80 %, et réduit d'environ 87 % les alertes à examiner par rapport à la régression logistique.
- Déploiement du modèle via une API REST sur Render et une interface Streamlit sur Streamlit Community Cloud.

Architecture & composants

Le projet repose sur une architecture découplée. Le moteur de scoring (backend) fonctionne indépendamment de l'interface utilisateur (frontend). Les deux communiquent via des requêtes HTTP au format JSON.
| Composant          | Rôle                                                                                                                                      | Technologie                            | Fichier                           |
| ------------------ | ----------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------- | --------------------------------- |
| Données & modèle   | Exploration des données, création de variables, entraînement et évaluation du modèle.                                                     | Python, pandas, scikit-learn, LightGBM | Notebook / scripts d'entraînement |
| Backend de scoring | Charge le modèle, reçoit les transactions au format JSON et renvoie un score de risque ainsi qu'une décision.                             | FastAPI + Uvicorn                      | `fraud_app.py`                    |
| Interface métier   | Tableau de bord interactif pour consulter et suivre les transactions analysées. Elle interroge l'API sans exécuter directement le modèle. | Streamlit                              | `my_fraud_shield.py` 


Pourquoi cette séparation ?

Évolutivité & maintenance : chaque composant peut être redimensionné ou mis à jour indépendamment.
Réutilisation : l'API peut être consommée par d'autres systèmes (systèmes de paiement, applications mobiles).
Séparation des responsabilités : le backend gère calcul et décision, l'interface gère l'affichage.

## Liens d'accès direct

| Service                  | URL                                                                                                             |
| ------------------------ | --------------------------------------------------------------------------------------------------------------- |
| API (FastAPI sur Render) | [https://detection-fraude-7tej.onrender.com](https://detection-fraude-7tej.onrender.com?utm_source=chatgpt.com) |
| Interface Streamlit      | [https://my-fraud-shield.streamlit.app/](https://my-fraud-shield.streamlit.app/?utm_source=chatgpt.com)         |

Jeu de données & features
Source
Dataset: PaySim — Synthetic Financial Datasets For Fraud Detection (Kaggle)
Volume : 6 362 620 transactions · Cible : isFraud (0,13 % de fraudes)
Périmètre retenu : TRANSFER et CASH_OUT uniquement → 2 770 409 transactions
Découpage : 80 % entraînement (2 216 327) / 20 % test (554 082, dont 1 643 fraudes), avec stratify=y
Identifiants supprimés : nameOrig et nameDest (risque de surapprentissage sur des comptes particuliers)

### Les 10 variables retenues

| #  | Variable           | Nature                           | Justification                                                                          |
| -- | ------------------ | -------------------------------- | -------------------------------------------------------------------------------------- |
| 1  | `step`             | Temporelle                       | Situe la transaction dans le temps (1 pas = 1 heure).                                  |
| 2  | `hour`             | Temporelle dérivée (`step % 24`) | Identifie les rythmes journaliers et les activités nocturnes suspectes.                |
| 3  | `amount`           | Montant                          | Les fraudes portent sur des montants plus élevés (environ 8 fois la moyenne légitime). |
| 4  | `oldbalanceOrg`    | Solde émetteur                   | Permet de repérer les comptes vidés.                                                   |
| 5  | `newbalanceOrig`   | Solde émetteur                   | Permet de suivre le solde restant après la transaction.                                |
| 6  | `oldbalanceDest`   | Solde destinataire               | Aide à identifier les comptes de passage.                                              |
| 7  | `newbalanceDest`   | Solde destinataire               | Permet de vérifier l'évolution du solde après réception.                               |
| 8  | `errorBalanceOrig` | Variable dérivée                 | Mesure les incohérences comptables chez l'émetteur.                                    |
| 9  | `errorBalanceDest` | Variable dérivée                 | Révèle les incohérences comptables chez le destinataire (signal majeur).               |
| 10 | `type_TRANSFER`    | Binaire                          | Distingue les virements, plus risqués en proportion, des retraits.                     |

Feature engineering — conservation des soldes
text
errorBalanceOrig = newbalanceOrig + amount - oldbalanceOrg
errorBalanceDest = oldbalanceDest + amount - newbalanceDest
