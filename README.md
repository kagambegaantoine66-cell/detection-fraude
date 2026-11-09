## FraudShield — Détection et scoring de fraude financière en temps réel
Un modèle LightGBM qui détecte 99 % des fraudes sur transactions de paiement mobile, exposé via une API FastAPI et consommé par un tableau de bord Streamlit.

### Sommaire

### Présentation
Architecture & composants
Liens d'accès direct
Jeu de données & features
Résultats
Installation & exécution locale
Limites & pistes d'amélioration
Auteur

 ### Présentation
 
FraudShield est un outil d'aide à la décision destiné aux équipes de gestion des risques. Basé sur le jeu de données PaySim (Kaggle), il vise à détecter les transactions frauduleuses tout en limitant les fausses alertes.
Points clés de l'étude
- 6 362 620 transactions analysées, dont seulement 0,13 % de fraudes.
- Les fraudes concernent deux types d'opérations : `TRANSFER` et `CASH_OUT`, soit 2 770 409 transactions retenues pour la modélisation.
- Création de deux variables (`errorBalanceOrig` et `errorBalanceDest`) pour détecter les incohérences dans les soldes.
- LightGBM atteint un rappel de 99 %, dépassant l'objectif initial de 80 %, et réduit d'environ 87 % les alertes à examiner par rapport à la régression logistique.
- Déploiement du modèle via une API REST sur Render et une interface Streamlit sur Streamlit Community Cloud.

### Architecture & composants

Le projet repose sur une architecture découplée. Le moteur de scoring (backend) fonctionne indépendamment de l'interface utilisateur (frontend). Les deux communiquent via des requêtes HTTP au format JSON.
| Composant          | Rôle                                                                                                                                      | Technologie                            | Fichier                           |
| ------------------ | ----------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------- | --------------------------------- |
| Données & modèle   | Exploration des données, création de variables, entraînement et évaluation du modèle.                                                     | Python, pandas, scikit-learn, LightGBM | Notebook / scripts d'entraînement |
| Backend de scoring | Charge le modèle, reçoit les transactions au format JSON et renvoie un score de risque ainsi qu'une décision.                             | FastAPI + Uvicorn                      | `fraud_app.py`                    |
| Interface métier   | Tableau de bord interactif pour consulter et suivre les transactions analysées. Elle interroge l'API sans exécuter directement le modèle. | Streamlit                              | `my_fraud_shield.py` 


### Pourquoi cette séparation ?

Évolutivité & maintenance : chaque composant peut être redimensionné ou mis à jour indépendamment.
Réutilisation : l'API peut être consommée par d'autres systèmes (systèmes de paiement, applications mobiles).
Séparation des responsabilités : le backend gère calcul et décision, l'interface gère l'affichage.

## Liens d'accès direct

| Service                                | URL                                                                                                                       |
| -------------------------------------- | ------------------------------------------------------------------------------------------------------------------------- |
|  API (FastAPI sur Render)            | [https://detection-fraude-7tej.onrender.com](https://detection-fraude-7tej.onrender.com?utm_source=chatgpt.com)           |
| Documentation interactive (Swagger) | [https://detection-fraude-7tej.onrender.com/docs](https://detection-fraude-7tej.onrender.com/docs?utm_source=chatgpt.com) |
| Interface Streamlit                 | https://my-fraud-shield.streamlit.app/                                                                     |
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

### Feature engineering — conservation des soldes
text
errorBalanceOrig = newbalanceOrig + amount - oldbalanceOrg
errorBalanceDest = oldbalanceDest + amount - newbalanceDest

### Résultats

Évaluation sur le jeu de test (554 082 transactions, 1 643 fraudes). L'accuracy est volontairement écartée : avec 0,13 % de fraudes, elle est trompeuse.

| Modèle                                            | Rappel (fraude) | Précision (fraude) | Fraudes détectées | Faux positifs | F1 macro |
| ------------------------------------------------- | --------------- | ------------------ | ----------------- | ------------- | -------- |
| Régression logistique (`class_weight='balanced'`) | ≈ 91 %          | ≈ 5 %              | 1 497 / 1 643     | 30 527        | 0,53     |
| LightGBM (`is_unbalance=True`)                    | 99 %            | 39 %               | 1 624 / 1 643     | 2 550         | 0,78     

Objectif initial (≥ 80 % de fraudes détectées) largement dépassé.
Seulement 19 fraudes manquées ; moins de 0,5 % des transactions légitimes signalées à tort.
Environ 4 alertes sur 10 sont de véritables fraudes, contre 1 sur 20 pour le modèle de référence.

# Installation & exécution locale
# Prérequis
Python 3.10+
git et pip
# 1. Cloner le dépôt
bash
git clone https://github.com/<votre-utilisateur>/<nom-du-depot>.git
cd <nom-du-depot>

# 2. Créer un environnement virtuel (recommandé)
bash
python -m venv venv

# Linux / macOS
source venv/bin/activate

# Windows
venv\Scripts\activate

# 3. Installer les dépendances
bash
pip install -r requirements.txt
# 4. Lancer l'API FastAPI (terminal n°1)
bash
uvicorn fraud_app:app --reload --host 0.0.0.0 --port 8000
API : http://127.0.0.1:8000
Documentation Swagger : http://127.0.0.1:8000/docs
# 5. Lancer l'interface Streamlit (terminal n°2)
bash
streamlit run my_fraud_shield.py

Configuration de l'API : dans `my_fraud_shield.py`, remplacez l'URL de l'API par `http://127.0.0.1:8000` pour effectuer des tests en local. Pour utiliser la version déployée, conservez `https://detection-fraude-7tej.onrender.com`.

### Exemple d'appel direct à l'API

```
# Adaptez le chemin de l'endpoint et les champs à votre fraud_app.py
curl -X POST "https://detection-fraude-7tej.onrender.com/predict" \
  -H "Content-Type: application/json" \
  -d '{
        "step": 1,
        "type": "TRANSFER",
        "amount": 181000.0,
        "oldbalanceOrg": 181000.0,
        "newbalanceOrig": 0.0,
        "oldbalanceDest": 0.0,
        "newbalanceDest": 0.0
      }'
```

### Structure du dépôt

```
.
├── fraud_app.py          # API FastAPI : chargement du modèle LightGBM et scoring
├── my_fraud_shield.py    # Interface Streamlit : communication avec l'API
├── requirements.txt      # Dépendances Python
├── models/               # Modèle LightGBM sauvegardé
├── notebooks/            # Analyse exploratoire et entraînement
└── README.md
```

# À adapter selon l'organisation réelle du dépôt.

## Limites & pistes d'amélioration

# Limites

- Les données PaySim sont simulées. Une validation sur des données réelles reste indispensable avant toute mise en production.
- La variable `step` arrive en tête de l'importance des variables. Cela peut toutefois refléter une particularité du simulateur.
- L'importance affichée correspond probablement au split count de LightGBM, qui peut sous-estimer le rôle des variables binaires comme `type_TRANSFER`.
- La précision de 39 % reste le principal point faible : une partie des alertes concerne encore des transactions légitimes.

# Pistes d'amélioration

- Évaluer l'importance des variables avec le Gain ou les valeurs SHAP pour mieux interpréter les prédictions.
- Adapter les seuils de décision selon le montant des transactions et leur niveau de risque.
- Filtrer en amont les opérations non concernées (`CASH_IN`, `DEBIT`, `PAYMENT`).
- Mettre en place un réentraînement régulier (démarche MLOps) pour suivre l'évolution des comportements frauduleux.

## Auteur

KAGAMBEGA W.Antoine
Github: https://github.com/kagambeagaantoine66-cell
Linkeldn: https://www.linkedin.com/in/antoine-kagambèga-67a85635b?utm_source=share_via&utm_content=profile&utm_medium=member_android
