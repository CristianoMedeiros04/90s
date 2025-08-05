"""
🔥 Temas Quentes - Painel de Inteligência Estética e Estratégica
Página inicial redesenhada com métricas visuais e cards elegantes
"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import logging

# Importa calculador de métricas
from utils.metrics_calculator import MetricsCalculator

logger = logging.getLogger(__name__)

def render_temas_quentes_page():
    """Renderiza a página Temas Quentes como painel de inteligência"""
    
    # Aplica CSS customizado para a página
    apply_page_css()
    
    # Inicializa calculador de métricas
    metrics_calc = MetricsCalculator()
    
    # Cabeçalho principal
    render_main_header()
    
    # Painel de métricas globais
    render_metrics_panel(metrics_calc)
    
    # Seção de publicações virais
    render_viral_posts_section(metrics_calc)
    
    # Rodapé com ações
    render_footer_actions()

def apply_page_css():
    """Aplica CSS customizado para a página"""
    st.markdown("""
    <style>
    /* Estilo geral da página */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem 1.5rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
        box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3);
    }
    
    .main-title {
        font-size: 2.8rem;
        font-weight: 700;
        margin: 0;
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
        letter-spacing: -0.5px;
    }
    
    .main-subtitle {
        font-size: 1.2rem;
        opacity: 0.9;
        margin-top: 0.5rem;
        font-weight: 300;
    }
    
    /* Cards de métricas */
    .metrics-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1.5rem;
        margin-bottom: 2rem;
    }
    
    .metric-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        border: 1px solid #f0f0f0;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 30px rgba(0,0,0,0.12);
    }
    
    .metric-value {
        font-size: 2.2rem;
        font-weight: 700;
        color: #2c3e50;
        margin-bottom: 0.5rem;
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: #7f8c8d;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .metric-icon {
        font-size: 1.5rem;
        margin-bottom: 0.5rem;
        display: block;
    }
    
    /* Cards de posts virais */
    .viral-post-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        border: 1px solid #f0f0f0;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    
    .viral-post-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 30px rgba(0,0,0,0.12);
    }
    
    .post-header {
        display: flex;
        align-items: center;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid #f8f9fa;
    }
    
    .platform-icon {
        font-size: 1.3rem;
        margin-right: 0.5rem;
    }
    
    .post-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: #2c3e50;
        margin: 0;
        flex-grow: 1;
    }
    
    .post-author {
        font-size: 0.9rem;
        color: #7f8c8d;
        margin-bottom: 1rem;
    }
    
    .post-metrics {
        display: flex;
        flex-wrap: wrap;
        gap: 1rem;
        margin-bottom: 1rem;
    }
    
    .metric-item {
        display: flex;
        align-items: center;
        font-size: 0.85rem;
        color: #5a6c7d;
    }
    
    .metric-item span {
        margin-left: 0.3rem;
        font-weight: 500;
    }
    
    .post-link {
        display: inline-flex;
        align-items: center;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 6px;
        text-decoration: none;
        font-size: 0.85rem;
        font-weight: 500;
        transition: opacity 0.2s ease;
    }
    
    .post-link:hover {
        opacity: 0.9;
        text-decoration: none;
        color: white;
    }
    
    /* Seções */
    .section-title {
        font-size: 1.8rem;
        font-weight: 600;
        color: #2c3e50;
        margin-bottom: 1.5rem;
        display: flex;
        align-items: center;
    }
    
    .section-icon {
        margin-right: 0.5rem;
        font-size: 1.5rem;
    }
    
    /* Gráficos */
    .chart-container {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        border: 1px solid #f0f0f0;
        margin-bottom: 2rem;
    }
    
    /* Botões de ação */
    .action-buttons {
        display: flex;
        gap: 1rem;
        justify-content: center;
        margin-top: 2rem;
        padding-top: 2rem;
        border-top: 1px solid #f0f0f0;
    }
    
    .action-button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.75rem 1.5rem;
        border-radius: 8px;
        font-weight: 500;
        cursor: pointer;
        transition: opacity 0.2s ease;
    }
    
    .action-button:hover {
        opacity: 0.9;
    }
    
    /* Responsividade */
    @media (max-width: 768px) {
        .main-title {
            font-size: 2.2rem;
        }
        
        .metrics-container {
            grid-template-columns: repeat(2, 1fr);
        }
        
        .post-metrics {
            gap: 0.5rem;
        }
        
        .action-buttons {
            flex-direction: column;
            align-items: center;
        }
    }
    </style>
    """, unsafe_allow_html=True)

def render_main_header():
    """Renderiza cabeçalho principal da página"""
    st.markdown("""
    <div class="main-header">
        <h1 class="main-title">🔥 Temas Quentes</h1>
        <p class="main-subtitle">Painel de Inteligência para Conteúdos Virais</p>
    </div>
    """, unsafe_allow_html=True)

def render_metrics_panel(metrics_calc: MetricsCalculator):
    """Renderiza painel de métricas globais"""
    st.markdown('<h2 class="section-title"><span class="section-icon">📊</span>Métricas Globais</h2>', unsafe_allow_html=True)
    
    # Obtém métricas
    metrics = metrics_calc.get_global_metrics()
    
    # Grid de métricas principais
    col1, col2, col3 = st.columns(3)
    
    with col1:
        render_metric_card("📈", metrics['total_posts'], "Posts Virais", "#e74c3c")
        render_metric_card("❤️", metrics['avg_likes'], "Média de Curtidas", "#e91e63")
    
    with col2:
        render_metric_card("👁️", metrics['total_views'], "Total de Views", "#9c27b0")
        render_metric_card("📱", metrics['top_platform'], "Top Plataforma", "#673ab7")
    
    with col3:
        render_metric_card("🚀", metrics['avg_engagement'], "Engajamento Médio", "#3f51b5")
        render_metric_card("🏷️", metrics['trending_topic'], "Tema em Alta", "#2196f3")
    
    # Gráficos de distribuição e tendência
    render_charts(metrics)

def render_metric_card(icon: str, value: str, label: str, color: str):
    """Renderiza card individual de métrica"""
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-icon">{icon}</div>
        <div class="metric-value" style="color: {color};">{value}</div>
        <div class="metric-label">{label}</div>
    </div>
    """, unsafe_allow_html=True)

def render_charts(metrics: dict):
    """Renderiza gráficos de distribuição e tendência"""
    col1, col2 = st.columns(2)
    
    with col1:
        # Gráfico de distribuição por plataforma
        if metrics['platform_distribution']:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.subheader("📊 Distribuição por Plataforma")
            
            platforms = list(metrics['platform_distribution'].keys())
            values = list(metrics['platform_distribution'].values())
            
            if platforms and values:
                fig_pie = px.pie(
                    values=values,
                    names=platforms,
                    color_discrete_sequence=['#667eea', '#764ba2', '#f093fb', '#f5576c']
                )
                fig_pie.update_layout(
                    height=300,
                    margin=dict(t=20, b=20, l=20, r=20),
                    font=dict(size=12)
                )
                st.plotly_chart(fig_pie, use_container_width=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        # Gráfico de tendência de engajamento
        if metrics['engagement_trend']:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.subheader("📈 Tendência de Engajamento")
            
            trend_data = metrics['engagement_trend']
            days = [item['day'] for item in trend_data]
            engagement = [item['engagement'] for item in trend_data]
            
            if days and engagement:
                fig_line = go.Figure()
                fig_line.add_trace(go.Scatter(
                    x=days,
                    y=engagement,
                    mode='lines+markers',
                    line=dict(color='#667eea', width=3),
                    marker=dict(size=8, color='#764ba2'),
                    fill='tonexty',
                    fillcolor='rgba(102, 126, 234, 0.1)'
                ))
                
                fig_line.update_layout(
                    height=300,
                    margin=dict(t=20, b=20, l=20, r=20),
                    xaxis_title="Dia da Semana",
                    yaxis_title="Engajamento (%)",
                    font=dict(size=12),
                    showlegend=False
                )
                st.plotly_chart(fig_line, use_container_width=True)
            
            st.markdown('</div>', unsafe_allow_html=True)

def render_viral_posts_section(metrics_calc: MetricsCalculator):
    """Renderiza seção de publicações virais"""
    st.markdown('<h2 class="section-title"><span class="section-icon">🔥</span>Publicações em Alta</h2>', unsafe_allow_html=True)
    
    # Obtém posts virais
    viral_posts = metrics_calc.get_viral_posts_sample(limit=12)
    
    if not viral_posts:
        st.warning("⚠️ Nenhuma publicação viral encontrada no momento.")
        return
    
    # Organiza posts em grid responsivo
    cols = st.columns(2)
    
    for i, post in enumerate(viral_posts):
        col = cols[i % 2]
        
        with col:
            render_viral_post_card(post)

def render_viral_post_card(post: dict):
    """Renderiza card individual de post viral"""
    platform_icon = post['platform_icon']
    title = post['title']
    author = post['author']
    link = post['link']
    
    # Métricas do post
    likes = post['likes']
    views = post['views']
    comments = post['comments']
    saves = post['saves']
    shares = post['shares']
    
    st.markdown(f"""
    <div class="viral-post-card">
        <div class="post-header">
            <span class="platform-icon">{platform_icon}</span>
            <h3 class="post-title">{title}</h3>
        </div>
        
        <div class="post-author">{author}</div>
        
        <div class="post-metrics">
            <div class="metric-item">
                👁️ <span>{views}</span>
            </div>
            <div class="metric-item">
                ❤️ <span>{likes}</span>
            </div>
            <div class="metric-item">
                💬 <span>{comments}</span>
            </div>
            <div class="metric-item">
                📌 <span>{saves}</span>
            </div>
            <div class="metric-item">
                🔁 <span>{shares}</span>
            </div>
        </div>
        
        <a href="{link}" target="_blank" class="post-link">
            ➡️ Assistir Agora
        </a>
    </div>
    """, unsafe_allow_html=True)

def render_footer_actions():
    """Renderiza rodapé com botões de ação"""
    st.markdown("""
    <div class="action-buttons">
        <button class="action-button" onclick="window.location.reload()">
            🔄 Atualizar Painel
        </button>
    </div>
    """, unsafe_allow_html=True)
    
    # Informações de atualização
    st.markdown(f"""
    <div style="text-align: center; margin-top: 1rem; color: #7f8c8d; font-size: 0.85rem;">
        📅 Última atualização: {datetime.now().strftime('%d/%m/%Y às %H:%M')}
    </div>
    """, unsafe_allow_html=True)

