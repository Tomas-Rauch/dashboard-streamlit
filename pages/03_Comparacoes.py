import streamlit as st
import pandas as pd
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt

st.set_page_config(page_title="Comparações", layout="wide")
st.title("⚔ Comparações Entre Jogadores")

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

for col in ("player_height", "player_weight", "age", "pts", "reb", "ast"):
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

st.header("🎯 Filtros de Comparação")

col1, col2 = st.columns(2)

with col1:
    available_seasons = sorted(df["season"].dropna().unique()) if "season" in df.columns else []
    selected_season = st.selectbox("Selecione a temporada:", options=available_seasons) if available_seasons else None

with col2:
    metric_options = []
    for col in ["player_height", "player_weight", "age", "pts", "reb", "ast"]:
        if col in df.columns and df[col].notna().any():
            metric_options.append(col)
    
    selected_metric = st.selectbox("Métrica para comparação:", options=metric_options) if metric_options else None

if not selected_season or not selected_metric:
    st.info("Selecione uma temporada e métrica para ver as comparações.")
    st.stop()

df_season = df[df["season"] == selected_season] if selected_season else df

st.divider()

st.header("📊 Top Jogadores por Métrica")

if selected_metric in df_season.columns:
    top_players = df_season.nlargest(10, selected_metric)[['player_name', selected_metric]].dropna()
    
    if not top_players.empty:
        fig1 = px.bar(
            top_players,
            x=selected_metric,
            y='player_name',
            orientation='h',
            title=f"Top 10 Jogadores - {selected_metric.replace('_', ' ').title()} ({selected_season})",
            color=selected_metric,
            color_continuous_scale='viridis'
        )
        fig1.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig1, use_container_width=True)
    else:
        st.info(f"Não há dados de {selected_metric} para a temporada selecionada.")

st.divider()

st.header("📈 Distribuição da Métrica Selecionada")

col1, col2 = st.columns(2)

with col1:
    if selected_metric in df_season.columns:
        fig2 = px.histogram(
            df_season,
            x=selected_metric,
            nbins=20,
            title=f"Distribuição de {selected_metric.replace('_', ' ').title()}",
            color_discrete_sequence=['blue']
        )
        st.plotly_chart(fig2, use_container_width=True)

with col2:
    if selected_metric in df_season.columns:
        fig3 = px.box(
            df_season,
            y=selected_metric,
            title=f"Box Plot - {selected_metric.replace('_', ' ').title()}",
            color_discrete_sequence=['red']
        )
        st.plotly_chart(fig3, use_container_width=True)

st.divider()

st.header("🔄 Comparação entre Temporadas")

if "season" in df.columns and selected_metric in df.columns:
    season_stats = df.groupby('season')[selected_metric].mean().reset_index()
    
    if not season_stats.empty:
        fig4 = px.line(
            season_stats,
            x='season',
            y=selected_metric,
            title=f"Evolução da {selected_metric.replace('_', ' ').title()} ao Longo das Temporadas",
            markers=True
        )
        if selected_season in season_stats['season'].values:
            selected_value = season_stats[season_stats['season'] == selected_season][selected_metric].values[0]
            fig4.add_scatter(
                x=[selected_season],
                y=[selected_value],
                mode='markers',
                marker=dict(size=12, color='red'),
                name='Temporada Selecionada'
            )
        st.plotly_chart(fig4, use_container_width=True)

st.divider()

st.header("🎪 Comparação de Múltiplas Métricas")

if len(metric_options) >= 2:
    selected_metrics = st.multiselect(
        "Selecione métricas para comparar:",
        options=metric_options,
        default=metric_options[:2] if len(metric_options) >= 2 else metric_options
    )
    
    if len(selected_metrics) >= 2:
        corr_data = df_season[selected_metrics].corr()
        
        fig5, ax = plt.subplots(figsize=(8, 6))
        sns.heatmap(
            corr_data,
            annot=True,
            cmap="coolwarm",
            center=0,
            square=True,
            ax=ax
        )
        ax.set_title("Correlação entre Métricas Selecionadas")
        st.pyplot(fig5)

st.divider()

st.header("📋 Estatísticas Detalhadas")

col1, col2 = st.columns(2)

with col1:
    if selected_metric in df_season.columns:
        st.write(f"**Estatísticas de {selected_metric.replace('_', ' ').title()}:**")
        stats = df_season[selected_metric].describe()
        st.metric("Média", f"{stats['mean']:.2f}")
        st.metric("Mediana", f"{stats['50%']:.2f}")
        st.metric("Desvio Padrão", f"{stats['std']:.2f}")

with col2:
    if selected_metric in df_season.columns:
        st.write("**Valores Extremos:**")
        st.metric("Máximo", f"{stats['max']:.2f}")
        st.metric("Mínimo", f"{stats['min']:.2f}")
        st.metric("Contagem", f"{stats['count']:.0f}")

st.sidebar.markdown("---")
st.sidebar.info(
    "💡 **Dicas de Uso:**\n"
    "- Compare jogadores por diferentes métricas\n"
    "- Analise a evolução temporal das estatísticas\n"
    "- Veja correlações entre diferentes medidas de performance"
)