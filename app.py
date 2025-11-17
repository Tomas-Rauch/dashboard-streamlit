import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="NBA Dashboard",
    page_icon="🏀",
    layout="wide"
)

st.title("🏀 Dashboard NBA - All Seasons")
st.write("Aplicação criada como trabalho de programação utilizando Streamlit + CSV.")
st.markdown("Os dados são carregados automaticamente do arquivo `data/all_seasons.csv`.")

# Carregamento automático do dataset
@st.cache_data
def load_data():
    return pd.read_csv("data/all_seasons.csv")

df = load_data()
st.session_state["df"] = df

st.success("Dataset carregado com sucesso!")

st.subheader("Pré-visualização dos dados")
st.dataframe(df.head())