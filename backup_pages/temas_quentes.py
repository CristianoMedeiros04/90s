#!/usr/bin/env python3
"""
Página Temas Quentes - Monitoramento Jurídico Específico
3 Sessões: Dr. Willian Godoy, Dr. Cristiano Medeiros, TikTok for Business
"""

import streamlit as st
import json
import os
from datetime import datetime
import time

def load_instagram_data(filename):
    """Carrega dados do Instagram"""
    try:
        filepath = f"data/instagram/{filename}"
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return []

def load_tiktok_data(filename):
    """Carrega dados do TikTok"""
    try:
        filepath = f"data/tiktok/{filename}"
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return []

def format_number(num):
    """Formata números para exibição"""
    if num >= 1000000:
        return f"{num/1000000:.1f}M"
    elif num >= 1000:
        return f"{num/1000:.1f}K"
    return str(num)

def render_post_card(post, platform="instagram"):
    """Renderiza card de post individual"""
    with st.container():
        # CSS para o card
        st.markdown("""
        <style>
        .post-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 15px;
            padding: 20px;
            margin: 10px 0;
            color: white;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            border: 1px solid rgba(255,255,255,0.1);
        }
        .post-header {
            display: flex;
            align-items: center;
            margin-bottom: 15px;
        }
        .platform-icon {
            font-size: 24px;
            margin-right: 10px;
        }
        .post-title {
            font-size: 18px;
            font-weight: bold;
            margin-bottom: 8px;
        }
        .post-author {
            font-size: 14px;
            opacity: 0.9;
            margin-bottom: 15px;
        }
        .metrics-row {
            display: flex;
            justify-content: space-between;
            margin-bottom: 15px;
        }
        .metric-item {
            text-align: center;
            flex: 1;
        }
        .metric-value {
            font-size: 16px;
            font-weight: bold;
        }
        .metric-label {
            font-size: 12px;
            opacity: 0.8;
        }
        .play-button {
            background: rgba(255,255,255,0.2);
            border: 2px solid white;
            border-radius: 25px;
            padding: 10px 20px;
            color: white;
            text-decoration: none;
            display: inline-block;
            margin-top: 10px;
            transition: all 0.3s ease;
        }
        .play-button:hover {
            background: white;
            color: #667eea;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Ícone da plataforma
        platform_icons = {
            "instagram": "📷",
            "tiktok": "🎵"
        }
        
        icon = platform_icons.get(platform, "📱")
        
        # Card HTML
        card_html = f"""
        <div class="post-card">
            <div class="post-header">
                <span class="platform-icon">{icon}</span>
                <span style="font-weight: bold;">{platform.title()}</span>
            </div>
            
            <div class="post-title">{post.get('title', 'Título não disponível')}</div>
            <div class="post-author">👤 {post.get('author', 'Autor desconhecido')}</div>
            
            <div class="metrics-row">
                <div class="metric-item">
                    <div class="metric-value">❤️ {format_number(post.get('likes', 0))}</div>
                    <div class="metric-label">Curtidas</div>
                </div>
                <div class="metric-item">
                    <div class="metric-value">👁️ {format_number(post.get('views', 0))}</div>
                    <div class="metric-label">Visualizações</div>
                </div>
                <div class="metric-item">
                    <div class="metric-value">💬 {format_number(post.get('comments', 0))}</div>
                    <div class="metric-label">Comentários</div>
                </div>
                <div class="metric-item">
                    <div class="metric-value">📊 {post.get('ctr', '0%')}</div>
                    <div class="metric-label">CTR</div>
                </div>
            </div>
            
            <div style="text-align: center;">
                <a href="{post.get('link', '#')}" target="_blank" class="play-button">
                    ▶️ Ver Original
                </a>
            </div>
        </div>
        """
        
        st.markdown(card_html, unsafe_allow_html=True)

def render_section_header(title, subtitle, icon):
    """Renderiza cabeçalho de seção"""
    st.markdown(f"""
    <div style="
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        margin: 20px 0;
        text-align: center;
        color: white;
    ">
        <h2 style="margin: 0; font-size: 24px;">{icon} {title}</h2>
        <p style="margin: 5px 0 0 0; opacity: 0.9;">{subtitle}</p>
    </div>
    """, unsafe_allow_html=True)

def render_temas_quentes_page():
    """Renderiza página principal de Temas Quentes (versão corrigida)"""
    
    # Header principal
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 40px 20px;
        border-radius: 15px;
        text-align: center;
        color: white;
        margin-bottom: 30px;
    ">
        <h1 style="margin: 0; font-size: 36px; color: white;">🔥 Temas Quentes</h1>
        <p style="margin: 10px 0 0 0; font-size: 18px; opacity: 0.9; color: white;">
            Monitoramento Jurídico Especializado
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Data atual
    today = datetime.now().strftime('%Y-%m-%d')
    
    # SESSÃO 1: Dr. Willian Godoy
    st.markdown(f"""
    <div style="
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        margin: 20px 0;
        text-align: center;
        color: white;
    ">
        <h2 style="margin: 0; font-size: 24px; color: white;">👨‍⚖️ Dr. Willian Godoy</h2>
        <p style="margin: 5px 0 0 0; opacity: 0.9; color: white;">Últimas 5 postagens do Instagram</p>
    </div>
    """, unsafe_allow_html=True)
    
    willian_data = load_instagram_data(f"willian_godoy_{today}.json")
    if willian_data:
        st.success(f"✅ {len(willian_data)} posts carregados do Dr. Willian Godoy")
        
        # Exibe posts em expanders
        for i, post in enumerate(willian_data[:5]):
            with st.expander(f"📄 {post.get('title', 'Post sem título')[:50]}..."):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("❤️ Curtidas", format_number(post.get('likes', 0)))
                    st.metric("👁️ Views", format_number(post.get('views', 0)))
                
                with col2:
                    st.metric("💬 Comentários", format_number(post.get('comments', 0)))
                    st.metric("💾 Salvamentos", format_number(post.get('saves', 0)))
                
                with col3:
                    st.metric("📊 CTR", post.get('ctr', '0%'))
                    st.metric("📈 Engajamento", post.get('engagement_rate', '0%'))
                
                st.markdown(f"👤 **Autor:** {post.get('author', 'N/A')}")
                st.markdown(f"🔗 **Link:** [Ver Original]({post.get('link', '#')})")
    else:
        st.warning("⚠️ Dados do Dr. Willian Godoy não encontrados. Execute a coleta primeiro.")
    
    st.markdown("---")
    
    # SESSÃO 2: Dr. Cristiano Medeiros
    st.markdown(f"""
    <div style="
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        margin: 20px 0;
        text-align: center;
        color: white;
    ">
        <h2 style="margin: 0; font-size: 24px; color: white;">⚖️ Dr. Cristiano Medeiros</h2>
        <p style="margin: 5px 0 0 0; opacity: 0.9; color: white;">Últimas 5 postagens do Instagram</p>
    </div>
    """, unsafe_allow_html=True)
    
    cristiano_data = load_instagram_data(f"cristiano_medeiros_{today}.json")
    if cristiano_data:
        st.success(f"✅ {len(cristiano_data)} posts carregados do Dr. Cristiano Medeiros")
        
        # Exibe posts em expanders
        for i, post in enumerate(cristiano_data[:5]):
            with st.expander(f"📄 {post.get('title', 'Post sem título')[:50]}..."):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("❤️ Curtidas", format_number(post.get('likes', 0)))
                    st.metric("👁️ Views", format_number(post.get('views', 0)))
                
                with col2:
                    st.metric("💬 Comentários", format_number(post.get('comments', 0)))
                    st.metric("💾 Salvamentos", format_number(post.get('saves', 0)))
                
                with col3:
                    st.metric("📊 CTR", post.get('ctr', '0%'))
                    st.metric("📈 Engajamento", post.get('engagement_rate', '0%'))
                
                st.markdown(f"👤 **Autor:** {post.get('author', 'N/A')}")
                st.markdown(f"🔗 **Link:** [Ver Original]({post.get('link', '#')})")
    else:
        st.warning("⚠️ Dados do Dr. Cristiano Medeiros não encontrados. Execute a coleta primeiro.")
    
    st.markdown("---")
    
    # SESSÃO 3: TikTok for Business
    st.markdown(f"""
    <div style="
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        margin: 20px 0;
        text-align: center;
        color: white;
    ">
        <h2 style="margin: 0; font-size: 24px; color: white;">🎯 TikTok for Business</h2>
        <p style="margin: 5px 0 0 0; opacity: 0.9; color: white;">Top 5 anúncios jurídicos - Brasil</p>
    </div>
    """, unsafe_allow_html=True)
    
    tiktok_data = load_tiktok_data(f"business_juridico_{today}.json")
    if tiktok_data:
        st.success(f"✅ {len(tiktok_data)} anúncios carregados do TikTok for Business")
        
        # Exibe anúncios em expanders
        for i, ad in enumerate(tiktok_data[:5]):
            with st.expander(f"🎯 {ad.get('title', 'Anúncio sem título')[:50]}..."):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("❤️ Curtidas", format_number(ad.get('likes', 0)))
                    st.metric("👁️ Views", format_number(ad.get('views', 0)))
                
                with col2:
                    st.metric("💬 Comentários", format_number(ad.get('comments', 0)))
                    st.metric("🔄 Compartilhamentos", format_number(ad.get('shares', 0)))
                
                with col3:
                    st.metric("📊 CTR", ad.get('ctr', '0%'))
                    st.metric("🎯 Conversão", ad.get('conversion_rate', '0%'))
                
                st.markdown(f"👤 **Anunciante:** {ad.get('author', 'N/A')}")
                st.markdown(f"📝 **Descrição:** {ad.get('description', 'N/A')}")
                st.markdown(f"🎯 **CTA:** {ad.get('cta', 'N/A')}")
                st.markdown(f"🌎 **Região:** {ad.get('region', 'N/A')}")
                st.markdown(f"🔗 **Link:** [Ver Original]({ad.get('link', '#')})")
    else:
        st.warning("⚠️ Dados do TikTok for Business não encontrados. Execute a coleta primeiro.")
    
    # Estatísticas finais
    st.markdown("---")
    st.markdown("### 📊 Resumo Geral")
    
    total_posts = len(willian_data) + len(cristiano_data) + len(tiktok_data)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📊 Total de Posts", total_posts)
    
    with col2:
        st.metric("👨‍⚖️ Dr. Willian", len(willian_data))
    
    with col3:
        st.metric("⚖️ Dr. Cristiano", len(cristiano_data))
    
    with col4:
        st.metric("🎯 TikTok Ads", len(tiktok_data))
    
    # Botão para atualizar dados
    if st.button("🔄 Atualizar Dados", type="primary"):
        with st.spinner("Coletando dados atualizados..."):
            # Executa crawlers reais
            import subprocess
            
            try:
                # Executa crawlers em sequência
                subprocess.run(["python3", "collectors/instagram_willian.py"], cwd="/home/ubuntu/roteiros_app")
                subprocess.run(["python3", "collectors/instagram_cristiano.py"], cwd="/home/ubuntu/roteiros_app")
                subprocess.run(["python3", "collectors/tiktok_business.py"], cwd="/home/ubuntu/roteiros_app")
                
                st.success("✅ Dados atualizados com sucesso!")
                time.sleep(2)
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ Erro ao atualizar dados: {e}")

if __name__ == "__main__":
    render_temas_quentes_page()

