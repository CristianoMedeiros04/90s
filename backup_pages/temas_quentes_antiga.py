"""
Nova Página Temas Quentes - Home Page do App
Interface profissional otimizada para performance com sistema de fallback estético
"""
import streamlit as st
from datetime import datetime
import json
from typing import Dict, List
import sys
import os

# Adiciona o diretório raiz ao path para importações
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.trends_manager import TrendsManager

def apply_custom_css():
    """Aplica CSS customizado otimizado para performance"""
    st.markdown("""
    <style>
    /* Reset e base */
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
        max-width: 1200px;
    }
    
    /* Header principal */
    .trends-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem 1.5rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
    }
    
    .trends-title {
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }
    
    .trends-subtitle {
        font-size: 1.1rem;
        opacity: 0.9;
        margin-top: 0.5rem;
    }
    
    /* Grid de tendências */
    .trends-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 1.5rem;
        margin: 2rem 0;
    }
    
    /* Cards de plataforma */
    .platform-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 2px 12px rgba(0,0,0,0.08);
        border: 1px solid #f0f0f0;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    
    .platform-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 20px rgba(0,0,0,0.12);
    }
    
    .platform-header {
        display: flex;
        align-items: center;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #f8f9fa;
    }
    
    .platform-icon {
        font-size: 1.5rem;
        margin-right: 0.5rem;
    }
    
    .platform-name {
        font-size: 1.2rem;
        font-weight: 600;
        margin: 0;
    }
    
    /* Items de tendência */
    .trend-item {
        background: #f8f9fa;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 0.75rem;
        border-left: 4px solid #667eea;
        transition: background-color 0.2s ease;
    }
    
    .trend-item:hover {
        background: #e9ecef;
    }
    
    .trend-title {
        font-weight: 600;
        color: #2c3e50;
        margin-bottom: 0.25rem;
        font-size: 0.95rem;
    }
    
    .trend-description {
        color: #6c757d;
        font-size: 0.85rem;
        line-height: 1.4;
    }
    
    .trend-link {
        display: inline-block;
        margin-top: 0.5rem;
        padding: 0.25rem 0.75rem;
        background: #667eea;
        color: white;
        text-decoration: none;
        border-radius: 4px;
        font-size: 0.8rem;
        transition: background-color 0.2s ease;
    }
    
    .trend-link:hover {
        background: #5a6fd8;
        color: white;
        text-decoration: none;
    }
    
    /* Fallback - Central de Inspiração */
    .inspiration-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
        gap: 1.5rem;
        margin: 2rem 0;
    }
    
    .inspiration-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 4px 15px rgba(240, 147, 251, 0.3);
        transition: transform 0.2s ease;
    }
    
    .inspiration-card:hover {
        transform: translateY(-3px);
    }
    
    .inspiration-icon {
        font-size: 2rem;
        margin-bottom: 1rem;
    }
    
    .inspiration-title {
        font-size: 1.1rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    
    .inspiration-description {
        font-size: 0.9rem;
        opacity: 0.9;
        line-height: 1.4;
    }
    
    /* Status indicator para admin */
    .admin-status {
        position: fixed;
        top: 10px;
        right: 10px;
        background: rgba(255,255,255,0.9);
        padding: 0.5rem;
        border-radius: 50%;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        z-index: 1000;
    }
    
    /* Responsividade */
    @media (max-width: 768px) {
        .trends-title {
            font-size: 2rem;
        }
        
        .trends-grid,
        .inspiration-grid {
            grid-template-columns: 1fr;
            gap: 1rem;
        }
        
        .platform-card,
        .inspiration-card {
            padding: 1rem;
        }
    }
    
    /* Animações sutis */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .platform-card,
    .inspiration-card {
        animation: fadeIn 0.3s ease-out;
    }
    </style>
    """, unsafe_allow_html=True)

def render_platform_card(platform_name: str, trends: List[Dict], platform_config: Dict):
    """Renderiza card de uma plataforma específica usando componentes Streamlit nativos"""
    if not trends:
        return
    
    icon = platform_config.get('icon', '📱')
    color = platform_config.get('color', '#667eea')
    display_name = platform_config.get('name', platform_name.title())
    
    # Container principal com estilo
    with st.container():
        # Header da plataforma
        st.markdown(f"""
        <div style="
            background: white;
            border-radius: 12px;
            padding: 1.5rem;
            box-shadow: 0 2px 12px rgba(0,0,0,0.08);
            border: 1px solid #f0f0f0;
            margin-bottom: 1rem;
        ">
            <div style="
                display: flex;
                align-items: center;
                margin-bottom: 1rem;
                padding-bottom: 0.5rem;
                border-bottom: 2px solid #f8f9fa;
            ">
                <span style="font-size: 1.5rem; margin-right: 0.5rem;">{icon}</span>
                <h3 style="font-size: 1.2rem; font-weight: 600; margin: 0; color: {color};">{display_name}</h3>
            </div>
        """, unsafe_allow_html=True)
        
        # Tendências usando componentes nativos
        for i, trend in enumerate(trends[:5]):
            title = trend.get('titulo', 'Sem título')[:60]
            description = trend.get('descricao', 'Sem descrição')[:100]
            link = trend.get('link', '#')
            
            # Cada tendência como um expander
            with st.expander(f"📈 {title}", expanded=False):
                st.write(description)
                if link != '#':
                    st.markdown(f"🔗 [Ver mais]({link})")
        
        st.markdown("</div>", unsafe_allow_html=True)

def render_fallback_content(fallback_data: List[Dict]):
    """Renderiza conteúdo de fallback estético usando componentes nativos"""
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem 1.5rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
    ">
        <h1 style="font-size: 2.5rem; font-weight: 700; margin: 0; text-shadow: 0 2px 4px rgba(0,0,0,0.3);">🎨 Central de Inspiração</h1>
        <p style="font-size: 1.1rem; opacity: 0.9; margin-top: 0.5rem;">Enquanto buscamos as últimas tendências, inspire-se com dicas valiosas</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Grid de inspiração usando colunas nativas
    cols = st.columns(2)
    
    for i, item in enumerate(fallback_data[:8]):  # Limita a 8 para performance
        col = cols[i % 2]
        
        with col:
            icon = item.get('icon', '✨')
            title = item.get('titulo', 'Dica')
            description = item.get('descricao', 'Conteúdo inspiracional')
            
            # Card de inspiração usando container nativo
            with st.container():
                st.markdown(f"""
                <div style="
                    background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                    color: white;
                    border-radius: 12px;
                    padding: 1.5rem;
                    text-align: center;
                    box-shadow: 0 4px 15px rgba(240, 147, 251, 0.3);
                    margin-bottom: 1rem;
                ">
                    <div style="font-size: 2rem; margin-bottom: 1rem;">{icon}</div>
                    <div style="font-size: 1.1rem; font-weight: 600; margin-bottom: 0.5rem;">{title}</div>
                    <div style="font-size: 0.9rem; opacity: 0.9; line-height: 1.4;">{description}</div>
                </div>
                """, unsafe_allow_html=True)

def render_admin_status(is_fallback: bool, last_update: datetime = None):
    """Renderiza indicador de status para admin"""
    if is_fallback:
        status_icon = "🔧"
        tooltip = "Sistema em modo de manutenção"
    else:
        status_icon = "✅"
        tooltip = f"Última atualização: {last_update.strftime('%H:%M') if last_update else 'N/A'}"
    
    st.markdown(f"""
    <div class="admin-status" title="{tooltip}">
        {status_icon}
    </div>
    """, unsafe_allow_html=True)

def render_temas_quentes_page():
    """Renderiza a nova página Temas Quentes (Home Page)"""
    
    # Aplica CSS customizado
    apply_custom_css()
    
    # Inicializa gerenciador de tendências
    trends_manager = TrendsManager()
    
    # Coleta tendências com cache inteligente
    with st.spinner("🔄 Carregando tendências..."):
        all_trends = trends_manager.collect_all_trends()
    
    # Verifica se está em modo fallback
    is_fallback = all_trends.get('fallback_active', False)
    last_update = trends_manager.get_last_update_time()
    
    # Renderiza indicador de status para admin
    render_admin_status(is_fallback, last_update)
    
    if is_fallback:
        # Modo fallback - Central de Inspiração
        render_fallback_content(all_trends.get('inspiracao', []))
    else:
        # Modo normal - Tendências das redes sociais
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 2rem 1.5rem;
            border-radius: 12px;
            margin-bottom: 2rem;
            text-align: center;
            color: white;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        ">
            <h1 style="font-size: 2.5rem; font-weight: 700; margin: 0; text-shadow: 0 2px 4px rgba(0,0,0,0.3);">🔥 Temas Quentes</h1>
            <p style="font-size: 1.1rem; opacity: 0.9; margin-top: 0.5rem;">Descubra o que está bombando nas redes sociais agora</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Configuração das plataformas
        platform_configs = {
            'twitter': {
                'name': 'Twitter (X)',
                'icon': '🐦',
                'color': '#1DA1F2'
            },
            'tiktok': {
                'name': 'TikTok',
                'icon': '🎵',
                'color': '#FF0050'
            },
            'youtube': {
                'name': 'YouTube',
                'icon': '📺',
                'color': '#FF0000'
            },
            'instagram': {
                'name': 'Instagram',
                'icon': '📸',
                'color': '#E4405F'
            }
        }
        
        # Grid de plataformas
        cols = st.columns(2)
        
        platform_list = list(platform_configs.keys())
        for i, platform in enumerate(platform_list):
            if platform in all_trends and all_trends[platform]:
                col = cols[i % 2]
                
                with col:
                    render_platform_card(
                        platform, 
                        all_trends[platform], 
                        platform_configs[platform]
                    )
    
    # Informações adicionais
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "📊 Plataformas Monitoradas", 
            "4",
            help="Twitter, TikTok, YouTube, Instagram"
        )
    
    with col2:
        total_trends = sum(
            len(trends) for key, trends in all_trends.items() 
            if key not in ['fallback_active', 'inspiracao'] and isinstance(trends, list)
        )
        st.metric(
            "🔥 Tendências Ativas", 
            total_trends,
            help="Total de tendências coletadas hoje"
        )
    
    with col3:
        update_time = last_update.strftime('%H:%M') if last_update else "N/A"
        st.metric(
            "🕐 Última Atualização", 
            update_time,
            help="Horário da última coleta de dados"
        )

if __name__ == "__main__":
    render_temas_quentes_page()

