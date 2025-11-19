import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Configuração da página
st.set_page_config(
    page_title="🏀 NBA Players Analytics",
    page_icon="🏀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Aplicar estilo customizado
def apply_custom_style():
    st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: bold;
    }
    .section-header {
        font-size: 1.5rem;
        color: #2e86ab;
        margin: 1rem 0;
        font-weight: bold;
    }
    .metric-container {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
        border-left: 4px solid #1f77b4;
    }
    </style>
    """, unsafe_allow_html=True)

apply_custom_style()

# Título principal
st.markdown('<h1 class="main-header">🏀 NBA Players Analytics Dashboard</h1>', unsafe_allow_html=True)

# Carregar dados
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("data/all_seasons.csv")
        return df
    except FileNotFoundError:
        st.error("❌ Arquivo 'data/all_seasons.csv' não encontrado!")
        st.info("💡 Certifique-se de que o arquivo está na pasta 'data'")
        return pd.DataFrame()

df = load_data()

if df.empty:
    st.stop()

st.sidebar.header("🎛️ Filtros")

# Filtro por temporada
if 'season' in df.columns:
    seasons = sorted(df['season'].unique())
    selected_seasons = st.sidebar.multiselect(
        "Selecionar Temporadas:",
        options=seasons,
        default=seasons[:3] if len(seasons) > 3 else seasons
    )
    if selected_seasons:
        df = df[df['season'].isin(selected_seasons)]

# Filtro por altura
if 'player_height' in df.columns:
    min_height = int(df['player_height'].min())
    max_height = int(df['player_height'].max())
    height_range = st.sidebar.slider(
        "Faixa de Altura (cm):",
        min_value=min_height,
        max_value=max_height,
        value=(min_height, max_height)
    )
    df = df[(df['player_height'] >= height_range[0]) & 
            (df['player_height'] <= height_range[1])]

st.markdown('<h2 class="section-header">📊 Métricas Principais</h2>', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    total_players = df.shape[0]
    unique_players = df["player_name"].nunique()
    st.metric(
        label="👥 Total de Registros",
        value=f"{total_players:,}",
        delta=f"{unique_players:,} jogadores únicos"
    )

with col2:
    avg_height = df['player_height'].mean()
    height_std = df['player_height'].std()
    st.metric(
        label="📏 Altura Média",
        value=f"{avg_height:.1f} cm",
        delta=f"±{height_std:.1f} cm"
    )

with col3:
    avg_weight = df['player_weight'].mean()
    weight_std = df['player_weight'].std()
    st.metric(
        label="⚖️ Peso Médio",
        value=f"{avg_weight:.1f} kg",
        delta=f"±{weight_std:.1f} kg"
    )

with col4:
    if 'age' in df.columns:
        avg_age = df['age'].mean()
        age_std = df['age'].std()
        st.metric(
            label="🎂 Idade Média",
            value=f"{avg_age:.1f} anos",
            delta=f"±{age_std:.1f} anos"
        )
    elif 'team_position' in df.columns:
        positions = df['team_position'].nunique()
        st.metric("🏆 Posições", f"{positions}")
    else:
        st.metric("📈 Dados", "Disponíveis")

st.divider()

tab1, tab2, tab3 = st.tabs(["📈 Distribuições", "⚖️ Relações", "📊 Análises"])

with tab1:
    st.markdown('<h3 class="section-header">Distribuição de Altura</h3>', unsafe_allow_html=True)
    
    col_config, col_chart = st.columns([1, 3])
    
    with col_config:
        st.markdown('<div class="metric-container">', unsafe_allow_html=True)
        st.write("**Configurações do Gráfico:**")
        bins = st.slider("Número de intervalos", 10, 50, 25, key="height_bins")
        show_density = st.checkbox("Mostrar linha de densidade", True, key="height_density")
        color_scheme = st.selectbox("Cor do gráfico", 
                                   ["#1f77b4", "#2ca02c", "#d62728", "#9467bd", "#ff7f0e"])
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Estatísticas rápidas
        st.write("**Estatísticas de Altura:**")
        height_stats = df['player_height'].describe()
        st.write(f"• Mínimo: **{height_stats['min']:.1f} cm**")
        st.write(f"• Máximo: **{height_stats['max']:.1f} cm**")
        st.write(f"• Mediana: **{height_stats['50%']:.1f} cm**")
    
    with col_chart:
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Histograma simples
        n, bins, patches = ax.hist(df["player_height"].dropna(), bins=bins, alpha=0.7, 
                                  color=color_scheme, edgecolor='white', linewidth=0.5,
                                  density=show_density)
        
        if show_density:
            # Linha de densidade simplificada usando numpy
            hist, bin_edges = np.histogram(df["player_height"].dropna(), bins=bins, density=True)
            bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
            ax.plot(bin_centers, hist, 'r-', linewidth=2, label='Densidade')
            ax.legend()
        
        ax.set_xlabel("Altura (cm)", fontweight='bold', fontsize=12)
        ax.set_ylabel("Densidade" if show_density else "Número de Jogadores", 
                     fontweight='bold', fontsize=12)
        ax.set_title("Distribuição de Altura dos Jogadores", fontweight='bold', fontsize=14)
        ax.grid(True, alpha=0.3)
        ax.set_facecolor('#f8f9fa')
        
        st.pyplot(fig)

with tab2:
    st.markdown('<h3 class="section-header">Relação Altura vs Peso</h3>', unsafe_allow_html=True)
    
    col_config, col_chart = st.columns([1, 3])
    
    with col_config:
        st.markdown('<div class="metric-container">', unsafe_allow_html=True)
        st.write("**Configurações:**")
        alpha = st.slider("Transparência", 0.1, 1.0, 0.6, key="scatter_alpha")
        show_regression = st.checkbox("Mostrar linha de tendência", True, key="scatter_reg")
        
        color_options = ["Nenhum"]
        if 'team_position' in df.columns:
            color_options.append("Posição")
        if 'season' in df.columns:
            color_options.append("Temporada")
            
        color_by = st.selectbox("Colorir por:", color_options)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Análise de correlação
        st.write("**Análise de Correlação:**")
        if 'player_height' in df.columns and 'player_weight' in df.columns:
            correlation = df['player_height'].corr(df['player_weight'])
            st.write(f"Correlação: **{correlation:.3f}**")
            
            if correlation > 0.7:
                st.write("→ **Forte correlação positiva**")
            elif correlation > 0.3:
                st.write("→ **Correlação moderada**")
            else:
                st.write("→ **Correlação fraca**")
    
    with col_chart:
        fig, ax = plt.subplots(figsize=(10, 6))
        
        hue_column = None
        if color_by == "Posição" and 'team_position' in df.columns:
            hue_column = 'team_position'
        elif color_by == "Temporada" and 'season' in df.columns:
            hue_column = 'season'
        
        # Scatter plot
        if hue_column:
            scatter = sns.scatterplot(data=df, x="player_height", y="player_weight", 
                           hue=hue_column, alpha=alpha, s=60, ax=ax, palette="viridis")
            ax.legend(title=hue_column, bbox_to_anchor=(1.05, 1), loc='upper left')
        else:
            scatter = sns.scatterplot(data=df, x="player_height", y="player_weight", 
                           alpha=alpha, s=60, ax=ax, color='#1f77b4')
        
        # Linha de regressão
        if show_regression:
            sns.regplot(data=df, x="player_height", y="player_weight", 
                       scatter=False, ax=ax, color='red', line_kws={'linewidth': 2})
        
        ax.set_xlabel("Altura (cm)", fontweight='bold', fontsize=12)
        ax.set_ylabel("Peso (kg)", fontweight='bold', fontsize=12)
        ax.set_title("Relação entre Altura e Peso", fontweight='bold', fontsize=14)
        ax.grid(True, alpha=0.3)
        ax.set_facecolor('#f8f9fa')
        
        st.pyplot(fig)

with tab3:
    st.markdown('<h3 class="section-header">Análise por Métrica</h3>', unsafe_allow_html=True)
    
    # Selecionar métricas disponíveis
    available_metrics = []
    numeric_metrics = ['player_height', 'player_weight']
    categorical_metrics = []
    
    # Verificar quais colunas existem no dataset
    for col in df.columns:
        if col in numeric_metrics:
            available_metrics.append(col)
        elif df[col].dtype == 'object' or df[col].nunique() < 20:
            categorical_metrics.append(col)
    
    # Adicionar algumas colunas comuns se existirem
    for col in ['age', 'pts', 'reb', 'ast', 'draft_round', 'team_position', 'country']:
        if col in df.columns and col not in available_metrics:
            if df[col].dtype in ['int64', 'float64']:
                numeric_metrics.append(col)
            else:
                categorical_metrics.append(col)
            available_metrics.append(col)
    
    col_metric, col_chart = st.columns([1, 2])
    
    with col_metric:
        st.markdown('<div class="metric-container">', unsafe_allow_html=True)
        selected_metric = st.selectbox("Selecione a métrica:", available_metrics)
        st.markdown('</div>', unsafe_allow_html=True)
        
        if selected_metric in df.columns:
            # Estatísticas básicas
            metric_data = df[selected_metric].dropna()
            
            st.write("**📋 Estatísticas:**")
            
            if pd.api.types.is_numeric_dtype(metric_data):
                col_stat1, col_stat2 = st.columns(2)
                with col_stat1:
                    st.metric("Média", f"{metric_data.mean():.2f}")
                    st.metric("Mínimo", f"{metric_data.min():.2f}")
                with col_stat2:
                    st.metric("Mediana", f"{metric_data.median():.2f}")
                    st.metric("Máximo", f"{metric_data.max():.2f}")
                
                st.metric("Desvio Padrão", f"±{metric_data.std():.2f}")
            else:
                st.write(f"Valores únicos: **{metric_data.nunique()}**")
                if not metric_data.empty:
                    top_value = metric_data.mode().iloc[0]
                    top_count = (metric_data == top_value).sum()
                    st.write(f"Moda: **{top_value}** ({top_count} ocorrências)")
    
    with col_chart:
        if selected_metric in df.columns:
            fig, ax = plt.subplots(figsize=(10, 6))
            metric_data = df[selected_metric].dropna()
            
            if pd.api.types.is_numeric_dtype(metric_data):
                # Gráfico para métricas numéricas
                plot_type = st.radio("Tipo de gráfico:", 
                                    ["Histograma", "Box Plot", "Densidade"], 
                                    horizontal=True, key="num_plot")
                
                if plot_type == "Histograma":
                    sns.histplot(metric_data, kde=True, ax=ax, color='skyblue', bins=20)
                    ax.set_xlabel(selected_metric, fontweight='bold')
                    ax.set_ylabel("Frequência", fontweight='bold')
                elif plot_type == "Box Plot":
                    sns.boxplot(y=metric_data, ax=ax, color='lightgreen')
                    ax.set_ylabel(selected_metric, fontweight='bold')
                else:
                    sns.histplot(metric_data, kde=True, ax=ax, color='coral', 
                                stat='density', alpha=0.5)
                    ax.set_xlabel(selected_metric, fontweight='bold')
                    ax.set_ylabel("Densidade", fontweight='bold')
                    
            else:
                # Gráfico para métricas categóricas
                top_categories = metric_data.value_counts().head(8)
                plot_type = st.radio("Tipo de gráfico:", 
                                    ["Barras", "Pizza"], 
                                    horizontal=True, key="cat_plot")
                
                if plot_type == "Barras":
                    sns.barplot(x=top_categories.values, y=top_categories.index, 
                               ax=ax, palette='viridis')
                    ax.set_xlabel("Frequência", fontweight='bold')
                    ax.set_ylabel(selected_metric, fontweight='bold')
                else:
                    wedges, texts, autotexts = ax.pie(top_categories.values, 
                                                     labels=top_categories.index, 
                                                     autopct='%1.1f%%', 
                                                     startangle=90,
                                                     colors=sns.color_palette('viridis', len(top_categories)))
                    ax.set_ylabel('')
            
            title = f"Distribuição de {selected_metric}"
            ax.set_title(title, fontweight='bold', fontsize=14)
            ax.grid(True, alpha=0.3)
            ax.set_facecolor('#f8f9fa')
            
            st.pyplot(fig)

st.divider()
st.markdown('<h3 class="section-header">📋 Resumo do Dataset</h3>', unsafe_allow_html=True)

col_info1, col_info2 = st.columns(2)

with col_info1:
    st.markdown('<div class="metric-container">', unsafe_allow_html=True)
    st.write("**📊 Informações Gerais:**")
    st.write(f"- **Total de registros:** {len(df):,}")
    st.write(f"- **Jogadores únicos:** {df['player_name'].nunique()}")
    
    if 'season' in df.columns:
        seasons_covered = df['season'].nunique()
        st.write(f"- **Temporadas:** {seasons_covered}")
    
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    st.write(f"- **Variáveis numéricas:** {len(numeric_cols)}")
    st.markdown('</div>', unsafe_allow_html=True)

with col_info2:
    st.markdown('<div class="metric-container">', unsafe_allow_html=True)
    st.write("**💡 Dicas de Uso:**")
    st.write("• Use os filtros para análises específicas")
    st.write("• Explore diferentes tipos de gráficos")
    st.write("• Passe o mouse para ver detalhes")
    st.write("• Valores ± indicam desvio padrão")
    st.markdown('</div>', unsafe_allow_html=True)

st.divider()
st.markdown("""
<div style='text-align: center; color: #666; padding: 1rem;'>
    <p>🏀 Dashboard NBA Players Analytics | Desenvolvido com Streamlit</p>
</div>
""", unsafe_allow_html=True)

# Dicas na sidebar
st.sidebar.markdown("---")
st.sidebar.info("""
💡 **Dicas de Uso:**
- Use os filtros para análises específicas
- Explore todas as abas de gráficos
- Passe o mouse para ver detalhes
- **Valores ±** indicam desvio padrão
""")