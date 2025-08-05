#!/usr/bin/env python3
"""
Página Dashboard - Métricas e Visão Geral do Sistema
Seção 1: 3 Cards de Métricas
Seção 2: Gráfico de Linhas (Roteiros ao longo do tempo)
Seção 3: Lista dos últimos 5 roteiros
"""

import streamlit as st
import json
import os
import base64
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px
from utils.helpers import carregar_historico, carregar_perfil

st.markdown("""
<style>
/* Estilo exclusivo para os botões da dashboard */
.stButton > button {
    background-color: #FF0050 !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 6px !important;
}

/* Evita herança de hover verde */
.stButton > button:hover {
    background-color: #cc0042 !important;
    color: white !important;
}
</style>
""", unsafe_allow_html=True)

def calcular_metricas_dashboard():
    """Calcula métricas principais para o dashboard"""
    historico = carregar_historico()
    perfil = carregar_perfil()
    
    # Métrica 1: Total de roteiros gerados
    total_roteiros = len(historico)
    
    # Métrica 2: Roteiros esta semana
    hoje = datetime.now()
    inicio_semana = hoje - timedelta(days=7)
    
    roteiros_semana = 0
    for roteiro in historico:
        try:
            # Tenta primeiro 'data', depois 'timestamp' para compatibilidade
            data_str = roteiro.get('data', '') or roteiro.get('timestamp', '')
            if data_str:
                # Converte string para datetime
                if ' ' in data_str:  # Formato: "2025-07-22 18:30:00"
                    data_roteiro = datetime.strptime(data_str, "%Y-%m-%d %H:%M:%S")
                else:  # Formato ISO
                    data_roteiro = datetime.fromisoformat(data_str)
                
                if data_roteiro >= inicio_semana:
                    roteiros_semana += 1
        except:
            continue
    
    # Métrica 3: Completude do perfil
    campos_preenchidos = 0
    total_campos = 0
    
    for secao in perfil.values():
        if isinstance(secao, dict):
            for valor in secao.values():
                total_campos += 1
                if valor and str(valor).strip():
                    campos_preenchidos += 1
    
    completude_perfil = int((campos_preenchidos / max(total_campos, 1)) * 100)
    
    return {
        'total_roteiros': total_roteiros,
        'roteiros_semana': roteiros_semana,
        'completude_perfil': completude_perfil
    }

def gerar_dados_grafico_tempo():
    """Gera dados para o gráfico de roteiros ao longo do tempo"""
    historico = carregar_historico()
    
    # Agrupa roteiros por data
    roteiros_por_data = {}
    
    for roteiro in historico:
        try:
            # Tenta primeiro 'data', depois 'timestamp' para compatibilidade
            data_str = roteiro.get('data', '') or roteiro.get('timestamp', '')
            if data_str:
                # Converte string para datetime
                if ' ' in data_str:  # Formato: "2025-07-22 18:30:00"
                    data_roteiro = datetime.strptime(data_str, "%Y-%m-%d %H:%M:%S")
                else:  # Formato ISO
                    data_roteiro = datetime.fromisoformat(data_str)
                
                data_key = data_roteiro.strftime('%Y-%m-%d')
                
                if data_key in roteiros_por_data:
                    roteiros_por_data[data_key] += 1
                else:
                    roteiros_por_data[data_key] = 1
        except Exception as e:
            # Se der erro, tenta usar a data atual como fallback
            hoje = datetime.now().strftime('%Y-%m-%d')
            if hoje in roteiros_por_data:
                roteiros_por_data[hoje] += 1
            else:
                roteiros_por_data[hoje] = 1
            continue
    
    # Preenche últimos 30 dias
    hoje = datetime.now()
    datas = []
    valores = []
    
    for i in range(30, 0, -1):
        data = hoje - timedelta(days=i)
        data_str = data.strftime('%Y-%m-%d')
        datas.append(data_str)
        valores.append(roteiros_por_data.get(data_str, 0))
    
    return datas, valores

def render_cards_metricas():
    """Renderiza os 3 cards de métricas principais"""
    # Título "Métricas Principais" em HTML com ícone SVG
    with open("icons/signal-alt-1.svg", "rb") as f:
        chart_svg = base64.b64encode(f.read()).decode()

    st.markdown(f"""
        <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 1.5rem;">
            <img src="data:image/svg+xml;base64,{chart_svg}" width="26" height="26" style="margin-top: 2px;" />
            <h3 style="margin: 0; font-size: 1.6rem; font-weight: 600;">Métricas Principais</h3>
        </div>
     """, unsafe_allow_html=True)
    
    metricas = calcular_metricas_dashboard()
    
    # Estilo de fundo degradê (de cima mais escuro para baixo mais claro)
    metric_style = """
        background: linear-gradient(to bottom, #182433, #223344);
        padding: 16px;
        border-radius: 12px;
        color:FF0050;
        text-align: center;
        margin: 10px 0;
    """
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
            <div class="metric-container" style="{metric_style}">
                <div class="metric-value" style="font-size: 2.5rem; font-weight: bold;">🗎  {metricas['total_roteiros']}</div>
                <div class="metric-label" style="font-size: 1rem; opacity: 0.9;">Total de Roteiros</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
            <div class="metric-container" style="{metric_style}">
                <div class="metric-value" style="font-size: 2.5rem; font-weight: bold;">▦ {metricas['roteiros_semana']}</div>
                <div class="metric-label" style="font-size: 1rem; opacity: 0.9;">Esta Semana</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
            <div class="metric-container" style="{metric_style}">
                <div class="metric-value" style="font-size: 2.5rem; font-weight: bold;">◉─ {metricas['completude_perfil']}%</div>
                <div class="metric-label" style="font-size: 1rem; opacity: 0.9;">Perfil Completo</div>
            </div>
        """, unsafe_allow_html=True)

def render_grafico_tempo():
    """Renderiza gráfico de roteiros ao longo do tempo"""
    # Título do Gráfico com ícone SVG
    with open("icons/chart-line-up.svg", "rb") as f:
        chart_svg = base64.b64encode(f.read()).decode()
    
    st.markdown(f"""
        <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 1.5rem;">
            <img src="data:image/svg+xml;base64,{chart_svg}" width="26" height="26" style="margin-top: 2px;" />
            <h3 style="margin: 0; font-size: 1.6rem; font-weight: 600;">Roteiros ao Longo do Tempo (Últimos 30 dias)</h3>
        </div>
    """, unsafe_allow_html=True)
    
    datas, valores = gerar_dados_grafico_tempo()    
   
    # Cria gráfico com Plotly usando o estilo visual do app (rosa #FF0050)
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=datas,
        y=valores,
        mode='lines+markers',
        name='Roteiros Gerados',
        line=dict(color='#FF0050', width=3),                     # Cor da linha principal
        marker=dict(size=6, color='#FF0050'),                    # Cor dos marcadores
        fill='tozeroy',
        fillcolor='rgba(255, 0, 80, 0.2)'                        # Degradê translúcido do fundo
    ))

    fig.update_layout(
        height=350,
        margin=dict(l=20, r=20, t=40, b=20),
        plot_bgcolor='rgba(0,0,0,0)',                            # Fundo transparente
        paper_bgcolor='rgba(0,0,0,0)',                           # Fundo do canvas também transparente
        font_color='#FF0050',                                    # Texto rosa vibrante
        showlegend=False,
        xaxis_title="Data",
        yaxis_title="Roteiros Gerados"
    )

    fig.update_xaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor='rgba(255, 0, 80, 0.2)',                       # Grid leve na cor base
        tickangle=45
    )

    fig.update_yaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor='rgba(255, 0, 80, 0.2)'                        # Grid leve na cor base
    )

    st.plotly_chart(fig, use_container_width=True)

## == ÚLTIMOS 5 ROTEIROS == ##
def render_ultimos_roteiros():
    """Renderiza os últimos 5 roteiros com expanders e botão de edição"""

    # Título
    with open("icons/clock.svg", "rb") as f:
        chart_svg = base64.b64encode(f.read()).decode()

    st.markdown(f"""
        <div style="display: flex; align-items: center; gap: 12px; margin-top: 0; margin-bottom: 1.5rem;">
            <img src="data:image/svg+xml;base64,{chart_svg}" width="26" height="26" />
            <h3 style="margin: 0; font-size: 1.6rem; font-weight: 600;">Últimos Roteiros</h3>
        </div>
    """, unsafe_allow_html=True)


    # Se estiver em modo edição, mostra formulário
    if st.session_state.get("modo_edicao"):
        render_editor_roteiro()
        return

    historico = carregar_historico()

    if not historico:
        st.info("📝 Nenhum roteiro gerado ainda.")
        return

    historico_ordenado = sorted(historico, key=lambda x: x.get('data', '') or x.get('timestamp', ''), reverse=True)

    for i, roteiro in enumerate(historico_ordenado[:5]):
        titulo = roteiro.get("titulo", "Sem título")
        formato = roteiro.get("formato", "Desconhecido")
        conteudo = roteiro.get("conteudo", "")

        data_str = roteiro.get("data", "") or roteiro.get("timestamp", "")
        try:
            if ' ' in data_str:
                data = datetime.strptime(data_str, "%Y-%m-%d %H:%M:%S")
            else:
                data = datetime.fromisoformat(data_str)
            data_formatada = data.strftime('%d/%m/%Y')
        except:
            data_formatada = "Data inválida"

        resumo = f"**{titulo[:40]}{'...' if len(titulo) > 40 else ''}  —  {data_formatada}  |   {formato}**"

        with st.container():
            with st.expander(resumo, expanded=False):
                st.markdown(f"**Título:** {titulo}")
                st.markdown(f"**Data:** {data_formatada}")
                st.markdown(f"**Formato:** {formato}")
                st.markdown("**Conteúdo:**")
                st.code(conteudo, language="markdown")

                col1, col2 = st.columns(2)
                with col1:
                    if st.button("✏️ Editar", key=f"editar_{i}"):
                        st.session_state["roteiro_em_edicao"] = roteiro
                        st.session_state["modo_edicao"] = True
                        st.rerun()
                with col2:
                    if st.button("🗑️ Excluir", key=f"excluir_{i}"):
                        historico.remove(roteiro)
                        st.session_state["historico"] = historico
                        st.success("Roteiro excluído!")
                        st.rerun()

def render_editor_roteiro():
    roteiro = st.session_state.get("roteiro_em_edicao", {})

    st.markdown("### ✏️ Editando Roteiro")

    novo_titulo = st.text_input("Título", value=roteiro.get("titulo", ""))
    novo_conteudo = st.text_area("Conteúdo", value=roteiro.get("conteudo", ""), height=200)
    novo_formato = st.selectbox("Formato", ["Reels", "TikTok", "YouTube Shorts"], index=0)

    col1, col2 = st.columns(2)

    with col1:
        if st.button("💾 Salvar alterações"):
            roteiro["titulo"] = novo_titulo
            roteiro["conteudo"] = novo_conteudo
            roteiro["formato"] = novo_formato
            st.success("Alterações salvas!")
            st.session_state["modo_edicao"] = False
            st.rerun()

    with col2:
        if st.button("🗑️ Excluir roteiro"):
            historico = st.session_state.get("historico", [])
            historico = [r for r in historico if r != roteiro]
            st.session_state["historico"] = historico
            st.session_state["modo_edicao"] = False
            st.rerun()


def render_dashboard_page():
    """Renderiza a página principal do dashboard"""

    
    # === DASHBOARD (HEADER PRINCIPAL) === ##
    st.markdown("""                                                                                                           
        <div style="margin: 0; padding: 0;">
            <h1 style="margin: 0; padding: 0; font-size: 2.6rem; font-weight: 700;">Dashboard</h1>
        </div>
    """, unsafe_allow_html=True)
    
    
    # Seção 1: Cards de métricas
    render_cards_metricas()
    
    # Adiciona espaçamento vertical
    st.markdown("<div style='margin-top: 30px;'></div>", unsafe_allow_html=True)
    
    # Seção 2: Gráfico de tempo
    render_grafico_tempo()
    
    # Adiciona espaçamento vertical
    st.markdown("<div style='margin-top: 30px;'></div>", unsafe_allow_html=True)
    
    # Seção 3: Últimos roteiros
    historico = carregar_historico()
    historico_ordenado = sorted(
        historico,
        key=lambda x: x.get('data', '') or x.get('timestamp', ''),
        reverse=True
    )
    render_ultimos_roteiros()
        
    # Botão de atualização
    st.markdown("<div style='margin-top: 30px;'></div>", unsafe_allow_html=True)
    if st.button("↻ Atualizar Dashboard", type="primary"):
        st.rerun()

if __name__ == "__main__":
    render_dashboard_page()

