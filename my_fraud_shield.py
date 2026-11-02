import requests
import pandas as pd
import streamlit as st


# Configuration de la page
st.set_page_config(
    page_title="FraudShield Pro | Détection en Direct",
    page_icon="logo.jpg",  # Nom exact de votre logo dans le dossier
    layout="wide",
    initial_sidebar_state="expanded",
)

# En-tête principal 
st.markdown(
    '<p style="font-size: 2rem; font-weight: 700; color:'
    ' #1e293b;">FraudShield - Centre de Contrôle des Transactions</p>',
    unsafe_allow_html=True,
)
st.markdown(
    '<p style="color: #64748b; font-size: 1rem;">Interface de scoring et'
    " d'analyse du risque de fraude en temps réel via LightGBM et FastAPI.</p>",
    unsafe_allow_html=True,
)
st.divider()

# Barre latérale pour les paramètres de la transaction
with st.sidebar:
  

  st.header("Paramètres de la Transaction")
  st.markdown("Renseignez les détails du flux financier à analyser :")

  step = st.number_input("Étape temporelle", min_value=0, value=1)
  amount = st.number_input(
      "Montant", min_value=0.0, value=15000.0, format="%.2f"
  )

  st.subheader("Soldes du Compte Source")
  oldbalanceOrg = st.number_input(
      "Ancien solde", min_value=0.0, value=50000.0, format="%.2f"
  )
  newbalanceOrg = st.number_input(
      "Nouveau solde", min_value=0.0, value=35000.0, format="%.2f"
  )
  errorBalanceOrig = st.number_input(
      "Erreur solde source", value=0.0, format="%.2f"
  )

  st.subheader("Soldes du Compte Destinataire")
  oldbalanceDest = st.number_input(
      "Ancien solde (oldbalanceDest)", min_value=0.0, value=0.0, format="%.2f"
  )
  newbalanceDest = st.number_input(
      "Nouveau solde (newbalanceDest)", min_value=0.0, value=15000.0, format="%.2f"
  )
  errorBalanceDest = st.number_input(
      "Erreur solde destinataire (errorBalanceDest)", value=0.0, format="%.2f"
  )

  st.subheader("Contexte temporel et Type")
  hour = st.slider("Heure de la transaction (hour)", 0, 23, 14)
  type_TRANSFER = st.selectbox(
      "Type de transaction",
      options=[0, 1],
      format_func=lambda x: "TRANSFERT (1)" if x == 1 else "Autre type (0)",
  )

  analyze_btn = st.button(
      "Lancer l'analyse de risque", type="primary", use_container_width=True
  )

# Affichage principal en colonnes
col1, col2 = st.columns([2, 1])

with col1:
  st.subheader("Résumé des données soumises")
  # On affiche les informations sous forme de texte propre et structuré
  st.markdown(f"- **Step (Étape) :** {step}")
  st.markdown(f"- **Montant :** {amount:,.2f}")
  st.markdown(
      f"- **Soldes Source (Ancien / Nouveau) :** {oldbalanceOrg:,.2f} /"
      f" {newbalanceOrg:,.2f}"
  )
  st.markdown(
      f"- **Soldes Destinataire (Ancien / Nouveau) :** {oldbalanceDest:,.2f} /"
      f" {newbalanceDest:,.2f}"
  )
  st.markdown(
      f"- **Erreurs de solde (Org / Dest) :** {errorBalanceOrig} /"
      f" {errorBalanceDest}"
  )
  st.markdown(f"- **Heure :** {hour}h00")
  st.markdown(
      "- **Type de transaction :** "
      + ("TRANSFERT (1)" if type_TRANSFER == 1 else "Autre type (0)")
  )
  

with col2:
  st.subheader("Statut du Système")
  st.metric(label="Modèle actif", value="LightGBM v1.0")
  st.metric(label="Connexion API", value="En ligne (Port 8000)")

st.divider()

# Communication avec l'API FastAPI 
if analyze_btn:
  payload = {
      "step": int(step),
      "amount": float(amount),
      "oldbalanceOrg": float(oldbalanceOrg),
      "newbalanceOrig": float(newbalanceOrg),
      "oldbalanceDest": float(oldbalanceDest),
      "newbalanceDest": float(newbalanceDest),
      "errorBalanceOrig": float(errorBalanceOrig),
      "errorBalanceDest": float(errorBalanceDest),
      "hour": int(hour),
      "type_TRANSFER": int(type_TRANSFER),
  }

  with st.spinner("Analyse comportementale en cours par le modèle..."):
    try:
      response = requests.post("http://127.0.0.1:8000/predict", json=payload)

      if response.status_code == 200:
        resultat = response.json()
        st.subheader("Résultat de l'analyse de fraude")
        st.success("Analyse effectuée avec succès par l'API.")
        st.json(resultat)
      else:
        st.error(
            "Erreur de communication avec le serveur FastAPI (Code :"
            f" {response.status_code})"
        )
    except requests.exceptions.ConnectionError:
      st.error(
          "Impossible de joindre l'API. Vérifiez que votre serveur Uvicorn est"
          " bien actif dans le terminal."
      )
else:
  st.info(
      "Renseignez les paramètres dans la barre latérale à gauche puis cliquez"
      " sur 'Lancer l'analyse de risque' pour obtenir le verdict du modèle."
  )
