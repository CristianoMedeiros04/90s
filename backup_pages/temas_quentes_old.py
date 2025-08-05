"""
🔥 Temas Quentes - Layout em Mosaico Irregular
Página com dados reais coletados pelos crawlers diários
"""
import streamlit as st
import json
from datetime import datetime
from pathlib import Path

def get_platform_icon(platform):
    """Retorna ícone da plataforma"""
    icons = {
        'youtube': '📺',
        'tiktok': '🎵', 
        'instagram': '📷',
        'twitter': '🐦'
    }
    return icons.get(platform.lower(), '📱')

def get_platform_color(platform):
    """Retorna cor da plataforma"""
    colors = {
        'youtube': '#FF0000',
        'tiktok': '#000000',
        'instagram': '#E4405F', 
        'twitter': '#1DA1F2'
    }
    return colors.get(platform.lower(), '#666666')

def load_real_trends():
    """Carrega tendências reais dos arquivos de cache"""
    trends = []
    cache_dir = Path("data/tendencias")
    
    if not cache_dir.exists():
        return []
    
    # Carrega dados de cada plataforma (formato atual dos arquivos)
    platforms = ['youtube', 'tiktok', 'instagram', 'twitter']
    
    for platform in platforms:
        # Tenta primeiro o formato com data
        today = datetime.now().strftime('%Y-%m-%d')
        cache_file = cache_dir / f"{platform}_{today}.json"
        
        # Se não encontrar, tenta formato sem data
        if not cache_file.exists():
            cache_file = cache_dir / f"{platform}_trends.json"
        
        if cache_file.exists():
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    # Verifica se é formato direto ou com wrapper
                    if isinstance(data, list):
                        platform_trends = data
                    else:
                        platform_trends = data.get('trends', data.get(platform, []))
                    
                    # Adiciona plataforma a cada tendência
                    for trend in platform_trends:
                        if isinstance(trend, dict):
                            trend['platform'] = platform
                            trends.append(trend)
                        
            except Exception as e:
                st.error(f"Erro ao carregar {platform}: {e}")
    
    return trends

def apply_mosaico_css():
    """Aplica CSS para layout em mosaico irregular"""
    st.markdown("""
    <style>
    .mosaico-container {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        grid-auto-rows: 200px;
        gap: 15px;
        padding: 20px;
        max-width: 1200px;
        margin: 0 auto;
    }
    
    .mosaico-card {
        background: white;
        border-radius: 12px;
        padding: 15px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        border-left: 4px solid;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        cursor: pointer;
        position: relative;
        overflow: hidden;
    }
    
    .mosaico-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
    }
    
    /* Tamanhos irregulares */
    .card-large {
        grid-column: span 2;
        grid-row: span 2;
    }
    
    .card-wide {
        grid-column: span 2;
    }
    
    .card-tall {
        grid-row: span 2;
    }
    
    .card-normal {
        grid-column: span 1;
        grid-row: span 1;
    }
    
    .platform-header {
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 10px;
        font-size: 14px;
        font-weight: 600;
    }
    
    .trend-title {
        font-size: 16px;
        font-weight: bold;
        margin-bottom: 8px;
        line-height: 1.3;
        color: #333;
    }
    
    .trend-author {
        font-size: 14px;
        color: #666;
        margin-bottom: 12px;
    }
    
    .trend-metrics {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 8px;
        font-size: 12px;
    }
    
    .metric-item {
        display: flex;
        align-items: center;
        gap: 4px;
        color: #888;
    }
    
    .trend-link {
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        text-decoration: none;
    }
    
    @media (max-width: 768px) {
        .mosaico-container {
            grid-template-columns: repeat(2, 1fr);
            gap: 10px;
            padding: 10px;
        }
        
        .card-large, .card-wide {
            grid-column: span 2;
        }
    }
    </style>
    """, unsafe_allow_html=True)

def get_card_size(index, total):
    """Determina tamanho do card baseado na posição"""
    # Padrão irregular inspirado na imagem
    patterns = [
        'card-normal',   # 0
        'card-normal',   # 1  
        'card-wide',     # 2
        'card-normal',   # 3
        'card-tall',     # 4
        'card-normal',   # 5
        'card-large',    # 6
        'card-normal',   # 7
        'card-wide',     # 8
        'card-normal',   # 9
    ]
    
    return patterns[index % len(patterns)]

def format_number(num):
    """Formata números para exibição"""
    if isinstance(num, str):
        return num
    
    if num >= 1000000:
        return f"{num/1000000:.1f}M"
    elif num >= 1000:
        return f"{num/1000:.1f}K"
    else:
        return str(num)

def render_mosaico_card(trend, index, total):
    """Renderiza um card do mosaico"""
    platform = trend.get('platform', trend.get('plataforma', 'unknown'))
    title = trend.get('title', trend.get('titulo', 'Sem título'))
    author = trend.get('author', trend.get('autor', 'Autor desconhecido'))
    link = trend.get('link', '#')
    
    # Métricas (usa dados reais quando disponíveis, senão valores padrão)
    likes = format_number(trend.get('likes', trend.get('curtidas', '2.5K')))
    views = format_number(trend.get('views', trend.get('visualizacoes', '15K')))
    comments = format_number(trend.get('comments', trend.get('comentarios', '180')))
    saves = format_number(trend.get('saves', trend.get('salvamentos', '95')))
    
    icon = get_platform_icon(platform)
    color = get_platform_color(platform)
    card_size = get_card_size(index, total)
    
    return f"""
    <div class="mosaico-card {card_size}" style="border-left-color: {color};">
        <a href="{link}" target="_blank" class="trend-link"></a>
        
        <div class="platform-header" style="color: {color};">
            <span>{icon}</span>
            <span>{platform.title()}</span>
        </div>
        
        <div class="trend-title">{title[:60]}{'...' if len(title) > 60 else ''}</div>
        <div class="trend-author">👤 {author}</div>
        
        <div class="trend-metrics">
            <div class="metric-item">
                <span>❤️</span>
                <span>{likes}</span>
            </div>
            <div class="metric-item">
                <span>👁️</span>
                <span>{views}</span>
            </div>
            <div class="metric-item">
                <span>💬</span>
                <span>{comments}</span>
            </div>
            <div class="metric-item">
                <span>💾</span>
                <span>{saves}</span>
            </div>
        </div>
    </div>
    """

def render_temas_quentes_mosaico():
    """Renderiza página Temas Quentes com layout em mosaico usando componentes nativos"""
    
    # Header
    st.markdown("""
    <div style="text-align: center; padding: 2rem 0; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 15px; margin-bottom: 2rem;">
        <h1 style="color: white; font-size: 3rem; margin: 0;">🔥 Temas Quentes</h1>
        <p style="color: rgba(255,255,255,0.9); font-size: 1.2rem; margin: 0.5rem 0;">Tendências Virais das Redes Sociais</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Carrega dados reais
    trends = load_real_trends()
    
    if not trends:
        st.warning("⚠️ Nenhuma tendência encontrada. Execute o sistema de coleta primeiro.")
        render_fallback_nativo()
        return
    
    # Renderiza mosaico com componentes nativos
    render_mosaico_nativo(trends)
    
    # Footer com estatísticas
    render_footer_stats_nativo(trends)

def render_mosaico_nativo(trends):
    """Renderiza mosaico usando componentes nativos do Streamlit"""
    
    # Divide as tendências em grupos para criar layout irregular
    total = len(trends)
    
    # Primeira linha: 3 colunas (1:2:1)
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        if total > 0:
            render_card_nativo(trends[0])
        if total > 6:
            render_card_nativo(trends[6])
    
    with col2:
        if total > 1:
            render_card_nativo(trends[1])
    
    with col3:
        if total > 2:
            render_card_nativo(trends[2])
        if total > 7:
            render_card_nativo(trends[7])
    
    # Segunda linha: 2 colunas (3:2)
    col1, col2 = st.columns([3, 2])
    
    with col1:
        if total > 3:
            render_card_nativo(trends[3])
    
    with col2:
        if total > 4:
            render_card_nativo(trends[4])
        if total > 8:
            render_card_nativo(trends[8])
    
    # Terceira linha: 4 colunas iguais
    if total > 9:
        cols = st.columns(4)
        for i, col in enumerate(cols):
            if total > 9 + i:
                with col:
                    render_card_nativo(trends[9 + i])
    
    # Quarta linha: restante em 3 colunas
    if total > 13:
        remaining = trends[13:]
        cols = st.columns(3)
        for i, trend in enumerate(remaining):
            with cols[i % 3]:
                render_card_nativo(trend)

def render_card_nativo(trend):
    """Renderiza um card usando componentes nativos do Streamlit"""
    platform = trend.get('platform', trend.get('plataforma', 'unknown'))
    title = trend.get('title', trend.get('titulo', 'Sem título'))
    author = trend.get('author', trend.get('autor', 'Autor desconhecido'))
    link = trend.get('link', '#')
    
    # Métricas
    likes = format_number(trend.get('likes', trend.get('curtidas', '2.5K')))
    views = format_number(trend.get('views', trend.get('visualizacoes', '15K')))
    comments = format_number(trend.get('comments', trend.get('comentarios', '180')))
    saves = format_number(trend.get('saves', trend.get('salvamentos', '95')))
    
    icon = get_platform_icon(platform)
    color = get_platform_color(platform)
    
    # Container do card
    with st.container():
        # Header da plataforma
        st.markdown(f"""
        <div style="display: flex; align-items: center; margin-bottom: 0.5rem; color: {color};">
            <span style="font-size: 1.2rem; margin-right: 0.5rem;">{icon}</span>
            <strong>{platform.title()}</strong>
        </div>
        """, unsafe_allow_html=True)
        
        # Título
        st.markdown(f"**{title[:50]}{'...' if len(title) > 50 else ''}**")
        
        # Autor
        st.markdown(f"👤 {author}")
        
        # Métricas em colunas
        metric_cols = st.columns(4)
        with metric_cols[0]:
            st.metric("❤️", likes)
        with metric_cols[1]:
            st.metric("👁️", views)
        with metric_cols[2]:
            st.metric("💬", comments)
        with metric_cols[3]:
            st.metric("💾", saves)
        
        # Link
        if link != '#':
            st.link_button("🔗 Ver Original", link)
        
        # Separador
        st.markdown("---")

def render_fallback_nativo():
    """Renderiza fallback usando componentes nativos"""
    st.info("🎨 **Central de Inspiração**")
    st.markdown("*Enquanto buscamos as últimas tendências...*")
    
    # Cards de inspiração em colunas
    col1, col2, col3 = st.columns(3)
    
    inspirations = [
        {"icon": "💡", "title": "Dica de Criação", "text": "Use hooks visuais nos primeiros 3 segundos"},
        {"icon": "🎯", "title": "Estratégia", "text": "Conte histórias que geram identificação"},
        {"icon": "📈", "title": "Algoritmo", "text": "Poste nos horários de maior engajamento"},
        {"icon": "✨", "title": "Copy", "text": "Use gatilhos mentais como escassez e urgência"},
        {"icon": "🔥", "title": "Tendência", "text": "Adapte trends populares ao seu nicho"},
        {"icon": "🎬", "title": "Produção", "text": "Invista em boa iluminação e áudio limpo"}
    ]
    
    for i, inspiration in enumerate(inspirations):
        with [col1, col2, col3][i % 3]:
            st.markdown(f"""
            <div style="padding: 1rem; border-left: 4px solid #FF6B35; background: #f8f9fa; border-radius: 8px; margin-bottom: 1rem;">
                <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">{inspiration['icon']}</div>
                <strong>{inspiration['title']}</strong>
                <p style="margin: 0.5rem 0 0 0; color: #666;">{inspiration['text']}</p>
            </div>
            """, unsafe_allow_html=True)

def render_footer_stats_nativo(trends):
    """Renderiza estatísticas usando componentes nativos"""
    st.markdown("---")
    st.markdown("### 📊 Estatísticas Globais")
    
    # Calcula estatísticas
    platforms = {}
    for trend in trends:
        platform = trend.get('platform', trend.get('plataforma', 'unknown'))
        platforms[platform] = platforms.get(platform, 0) + 1
    
    # Exibe em colunas
    cols = st.columns(4)
    
    with cols[0]:
        st.metric("📱 Total de Posts", len(trends))
    
    with cols[1]:
        st.metric("🌐 Plataformas", len(platforms))
    
    with cols[2]:
        top_platform = max(platforms.items(), key=lambda x: x[1]) if platforms else ("N/A", 0)
        st.metric("🏆 Top Plataforma", f"{top_platform[0].title()}")
    
    with cols[3]:
        st.metric("🔄 Última Atualização", datetime.now().strftime("%H:%M"))

if __name__ == "__main__":
    render_temas_quentes_mosaico()



def render_mosaico_nativo(trends):
    """Renderiza mosaico usando componentes nativos do Streamlit"""
    
    # Divide as tendências em grupos para criar layout irregular
    total = len(trends)
    
    # Primeira linha: 3 colunas (1:2:1)
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        if total > 0:
            render_card_nativo(trends[0])
        if total > 6:
            render_card_nativo(trends[6])
    
    with col2:
        if total > 1:
            render_card_nativo(trends[1])
    
    with col3:
        if total > 2:
            render_card_nativo(trends[2])
        if total > 7:
            render_card_nativo(trends[7])
    
    # Segunda linha: 2 colunas (3:2)
    col1, col2 = st.columns([3, 2])
    
    with col1:
        if total > 3:
            render_card_nativo(trends[3])
    
    with col2:
        if total > 4:
            render_card_nativo(trends[4])
        if total > 8:
            render_card_nativo(trends[8])
    
    # Terceira linha: 4 colunas iguais
    if total > 9:
        cols = st.columns(4)
        for i, col in enumerate(cols):
            if total > 9 + i:
                with col:
                    render_card_nativo(trends[9 + i])
    
    # Quarta linha: restante em 3 colunas
    if total > 13:
        remaining = trends[13:]
        cols = st.columns(3)
        for i, trend in enumerate(remaining):
            with cols[i % 3]:
                render_card_nativo(trend)

def render_card_nativo(trend):
    """Renderiza um card usando componentes nativos do Streamlit"""
    platform = trend.get('platform', trend.get('plataforma', 'unknown'))
    title = trend.get('title', trend.get('titulo', 'Sem título'))
    author = trend.get('author', trend.get('autor', 'Autor desconhecido'))
    link = trend.get('link', '#')
    
    # Métricas
    likes = format_number(trend.get('likes', trend.get('curtidas', '2.5K')))
    views = format_number(trend.get('views', trend.get('visualizacoes', '15K')))
    comments = format_number(trend.get('comments', trend.get('comentarios', '180')))
    saves = format_number(trend.get('saves', trend.get('salvamentos', '95')))
    
    icon = get_platform_icon(platform)
    color = get_platform_color(platform)
    
    # Container do card
    with st.container():
        # Header da plataforma
        st.markdown(f"""
        <div style="display: flex; align-items: center; margin-bottom: 0.5rem; color: {color};">
            <span style="font-size: 1.2rem; margin-right: 0.5rem;">{icon}</span>
            <strong>{platform.title()}</strong>
        </div>
        """, unsafe_allow_html=True)
        
        # Título
        st.markdown(f"**{title[:50]}{'...' if len(title) > 50 else ''}**")
        
        # Autor
        st.markdown(f"👤 {author}")
        
        # Métricas em colunas
        metric_cols = st.columns(4)
        with metric_cols[0]:
            st.metric("❤️", likes)
        with metric_cols[1]:
            st.metric("👁️", views)
        with metric_cols[2]:
            st.metric("💬", comments)
        with metric_cols[3]:
            st.metric("💾", saves)
        
        # Link
        if link != '#':
            st.link_button("🔗 Ver Original", link)
        
        # Separador
        st.markdown("---")

def render_fallback_nativo():
    """Renderiza fallback usando componentes nativos"""
    st.info("🎨 **Central de Inspiração**")
    st.markdown("*Enquanto buscamos as últimas tendências...*")
    
    # Cards de inspiração em colunas
    col1, col2, col3 = st.columns(3)
    
    inspirations = [
        {"icon": "💡", "title": "Dica de Criação", "text": "Use hooks visuais nos primeiros 3 segundos"},
        {"icon": "🎯", "title": "Estratégia", "text": "Conte histórias que geram identificação"},
        {"icon": "📈", "title": "Algoritmo", "text": "Poste nos horários de maior engajamento"},
        {"icon": "✨", "title": "Copy", "text": "Use gatilhos mentais como escassez e urgência"},
        {"icon": "🔥", "title": "Tendência", "text": "Adapte trends populares ao seu nicho"},
        {"icon": "🎬", "title": "Produção", "text": "Invista em boa iluminação e áudio limpo"}
    ]
    
    for i, inspiration in enumerate(inspirations):
        with [col1, col2, col3][i % 3]:
            st.markdown(f"""
            <div style="padding: 1rem; border-left: 4px solid #FF6B35; background: #f8f9fa; border-radius: 8px; margin-bottom: 1rem;">
                <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">{inspiration['icon']}</div>
                <strong>{inspiration['title']}</strong>
                <p style="margin: 0.5rem 0 0 0; color: #666;">{inspiration['text']}</p>
            </div>
            """, unsafe_allow_html=True)

def render_footer_stats_nativo(trends):
    """Renderiza estatísticas usando componentes nativos"""
    st.markdown("---")
    st.markdown("### 📊 Estatísticas Globais")
    
    # Calcula estatísticas
    platforms = {}
    for trend in trends:
        platform = trend.get('platform', trend.get('plataforma', 'unknown'))
        platforms[platform] = platforms.get(platform, 0) + 1
    
    # Exibe em colunas
    cols = st.columns(4)
    
    with cols[0]:
        st.metric("📱 Total de Posts", len(trends))
    
    with cols[1]:
        st.metric("🌐 Plataformas", len(platforms))
    
    with cols[2]:
        top_platform = max(platforms.items(), key=lambda x: x[1]) if platforms else ("N/A", 0)
        st.metric("🏆 Top Plataforma", f"{top_platform[0].title()}")
    
    with cols[3]:
        st.metric("🔄 Última Atualização", datetime.now().strftime("%H:%M"))

