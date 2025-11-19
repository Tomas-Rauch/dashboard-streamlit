import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

st.set_page_config(page_title="Exploração", layout="wide")
st.title("🔎 Exploração dos Dados")

@st.cache_data
def load_data():
    try:
        df = pd.read_csv("data/all_seasons.csv")
        return df
    except FileNotFoundError:
        st.error("❌ Arquivo 'data/all_seasons.csv' não encontrado!")
        return pd.DataFrame()

df = load_data()

if df.empty:
    st.stop()

st.sidebar.header("🎛️ Filtros Gerais")

available_seasons = sorted(df["season"].dropna().unique()) if "season" in df.columns else []
if available_seasons:
    selected_seasons = st.sidebar.multiselect(
        "Selecionar Temporadas:",
        options=available_seasons,
        default=available_seasons[:3] if len(available_seasons) > 3 else available_seasons
    )
    if selected_seasons:
        df = df[df["season"].isin(selected_seasons)]

if "player_height" in df.columns:
    min_height = int(df["player_height"].min())
    max_height = int(df["player_height"].max())
    height_range = st.sidebar.slider(
        "Faixa de Altura (cm):",
        min_value=min_height,
        max_value=max_height,
        value=(min_height, max_height)
    )
    df = df[(df["player_height"] >= height_range[0]) & (df["player_height"] <= height_range[1])]

for col in ("player_height", "player_weight", "age", "draft_year"):
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

st.header("📈 Evolução Temporal")

if "season" in df.columns and "player_height" in df.columns:
    df_temporal = df.groupby("season").agg({
        "player_height": "mean",
        "player_weight": "mean",
        "player_name": "count"
    }).reset_index()
    
    df_temporal.columns = ["Temporada", "Altura Média", "Peso Médio", "Número de Jogadores"]
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig_height = px.line(
            df_temporal,
            x="Temporada",
            y="Altura Média",
            title="Evolução da Altura Média",
            markers=True
        )
        fig_height.update_layout(yaxis_title="Altura (cm)")
        st.plotly_chart(fig_height, use_container_width=True)
    
    with col2:
        if "player_weight" in df.columns:
            fig_weight = px.line(
                df_temporal,
                x="Temporada",
                y="Peso Médio",
                title="Evolução do Peso Médio",
                markers=True,
                color_discrete_sequence=["red"]
            )
            fig_weight.update_layout(yaxis_title="Peso (kg)")
            st.plotly_chart(fig_weight, use_container_width=True)

st.divider()

st.header("🧠 Análise de Correlação")

numeric_columns = []
for col in ["player_height", "player_weight", "age", "draft_year", "pts", "reb", "ast"]:
    if col in df.columns:
        numeric_df = df[col].apply(pd.to_numeric, errors='coerce')
        if numeric_df.notna().any():
            numeric_columns.append(col)

if len(numeric_columns) >= 2:
    df_numeric = df[numeric_columns].apply(pd.to_numeric, errors='coerce').dropna()
    
    if not df_numeric.empty and len(df_numeric.columns) >= 2:
        corr_matrix = df_numeric.corr()
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            fig, ax = plt.subplots(figsize=(10, 8))
            mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
            sns.heatmap(
                corr_matrix, 
                annot=True, 
                cmap="coolwarm", 
                center=0,
                fmt=".2f",
                square=True,
                mask=mask,
                ax=ax,
                cbar_kws={"shrink": 0.8}
            )
            ax.set_title("Matriz de Correlação", fontsize=14, fontweight='bold')
            plt.xticks(rotation=45)
            plt.yticks(rotation=0)
            st.pyplot(fig)
        
        with col2:
            st.write("**💡 Interpretação:**")
            st.write("Valores próximos de:")
            st.write("• **+1**: Correlação positiva forte")
            st.write("• **-1**: Correlação negativa forte")
            st.write("• **0**: Sem correlação")
            
            strong_correlations = []
            for i in range(len(corr_matrix.columns)):
                for j in range(i+1, len(corr_matrix.columns)):
                    corr_val = abs(corr_matrix.iloc[i, j])
                    if corr_val > 0.7:
                        col1_name = corr_matrix.columns[i]
                        col2_name = corr_matrix.columns[j]
                        strong_correlations.append(f"{col1_name} - {col2_name}: {corr_matrix.iloc[i, j]:.2f}")
            
            if strong_correlations:
                st.write("**🔗 Correlações Fortes:**")
                for corr in strong_correlations:
                    st.write(f"• {corr}")
    else:
        st.info("Dados numéricos insuficientes para calcular correlações.")
else:
    st.info("É necessário pelo menos 2 colunas numéricas para análise de correlação.")

st.divider()

st.header("📊 Distribuições por Temporada")

if "season" in df.columns and "player_height" in df.columns:
    selected_season_dist = st.selectbox(
        "Selecione uma temporada para análise detalhada:",
        options=available_seasons
    )
    
    if selected_season_dist:
        df_season = df[df["season"] == selected_season_dist]
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig_hist = px.histogram(
                df_season,
                x="player_height",
                title=f"Distribuição de Altura - {selected_season_dist}",
                nbins=20,
                color_discrete_sequence=["blue"]
            )
            fig_hist.update_layout(xaxis_title="Altura (cm)", yaxis_title="Número de Jogadores")
            st.plotly_chart(fig_hist, use_container_width=True)
        
        with col2:
            if "player_weight" in df.columns:
                fig_scatter = px.scatter(
                    df_season,
                    x="player_height",
                    y="player_weight",
                    title=f"Relação Altura x Peso - {selected_season_dist}",
                    opacity=0.6,
                    color_discrete_sequence=["green"]
                )
                fig_scatter.update_layout(xaxis_title="Altura (cm)", yaxis_title="Peso (kg)")
                st.plotly_chart(fig_scatter, use_container_width=True)

st.divider()

st.header("📋 Visualização dos Dados")

tab1, tab2 = st.tabs(["Dados Filtrados", "Estatísticas Descritivas"])

with tab1:
    st.write(f"**Dataset filtrado:** {len(df)} registros")
    st.dataframe(df.head(100), use_container_width=True)

with tab2:
    if not df.empty:
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            st.write("**Estatísticas das variáveis numéricas:**")
            st.dataframe(df[numeric_cols].describe(), use_container_width=True)
        else:
            st.info("Nenhuma coluna numérica encontrada para análise estatística.")

st.sidebar.markdown("---")
st.sidebar.info(
    "💡 **Dicas:**\n"
    "- Use os filtros para focar em temporadas específicas\n"
    "- Explore as correlações entre diferentes métricas\n"
    "- Compare a evolução temporal das estatísticas"
)