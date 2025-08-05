"""
Aplicativo Principal - Gerador de Roteiros para Vídeos Curtos
Arquitetura modular com funcionalidades REAIS implementadas
"""
import streamlit as st
import os
from dotenv import load_dotenv

# Importa sistema de autenticação
from auth.login import check_authentication

# Importa componentes modulares
from components.layout import setup_page_config, render_sidebar_navigation
from modules.home import render_home_page, render_reels_tiktok_page
from modules.react_real import render_react_page
from modules.cerebro import show_cerebro_page
from modules.dashboard import render_dashboard_page  # Nova página principal
from modules.stalker import render_stalker_page
from modules.raiox import render_raiox_page
from utils.helpers import carregar_perfil, carregar_historico

st.markdown("""
<style>

/* === ZERA TODAS AS ANIMAÇÕES (otimização) === */
*, *::before, *::after {
    transition: none !important;
    animation: none !important;
}

/* === ESTILO GERAL DOS BOTÕES === */
.stButton > button {
    color: #ffffff !important;              /* Cor branca no texto */
    background: #FF0050 !important;         /* Cor de fundo rosa principal */
    border: none !important;
    border-radius: 6px !important;
    padding: 0.5rem 1rem !important;
    font-weight: 500 !important;
    box-shadow: none !important;
}
.stButton > button:hover {
    background: FF0050 !important;         /* Cor de fundo ao passar o mouse */
}
.stButton > button:focus {
    outline: none !important;
    box-shadow: 0 0 0 2px #cce5e2 !important;
}

/* === BOTÃO "❮ SAIR" NA SIDEBAR (FORÇA TEXTO BRANCO) === */
section[data-testid="stSidebar"] .stButton > button {
    color: #ffffff !important;              /* Força branco no texto da sidebar */
    background: #FF0050 !important;
}
section[data-testid="stSidebar"] .stButton > button:hover {
    background: #cc0042 !important;         /* Hover mais escuro dentro da sidebar */
    color: #ffffff !important;
}

/* === FORMULÁRIOS ESCUROS === */
div[data-testid="stForm"] {
    background-color: #182433 !important;
    padding: 1.5rem !important;
    border-radius: 12px !important;
    border: 1px solid #223344 !important;
}

/* === CONTÊINERS DOS CAMPOS === */
div[data-testid="stTextInput"],
div[data-testid="stTextArea"],
div[data-testid="stSelectbox"],
div[data-testid="stNumberInput"] {
    background-color: #151f2c !important;
    border-radius: 6px !important;
    padding: 0.5rem !important;
    border: 1px solid #223344 !important;
}

/* === CAMPO INTERNO REAL === */
input, textarea, select, div[contenteditable="true"] {
    background-color: #151f2c !important;
    color: #f0f2f5 !important;
    border: none !important;
}

/* === COR DO PLACEHOLDER === */
input::placeholder, textarea::placeholder {
    color: #b0b3b8 !important;
    opacity: 1 !important;
}

/* === FOCO DO CAMPO === */
input:focus, textarea:focus, select:focus {
    outline: none !important;
    background-color: #151f2c !important;
    border: 1.5px solid #8bbdb7 !important;
    box-shadow: 0 0 0 2px rgba(139, 189, 183, 0.2) !important;
}

/* === SIDEBAR ESCURA === */
section[data-testid="stSidebar"] {
    background-color: #182433 !important;
    border-right: 2px solid #1f2f41 !important;
    padding-right: 8px !important;
    height: 100vh !important;
}
section[data-testid="stSidebar"] * {
    color: #c4c7ca !important;
}

/* === CARDS ESCUROS COM TEXTO CLARO === */
.card {
    background: linear-gradient(to bottom, #182433, #223344);
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
    box-shadow: 0 2px 8px rgba(24, 36, 51, 0.2);
    border: 1px solid #223344;
    color: #c4c7ca;
    transition: all 0.3s ease;
}
.card * {
    color: #f0f2f5 !important;
}
.card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 16px rgba(24, 36, 51, 0.3);
}

</style>
""", unsafe_allow_html=True)

# Carrega variáveis de ambiente
load_dotenv()

# Configuração da página
setup_page_config()

# Inicialização do estado da sessão
def initialize_session_state():
    """Inicializa o estado da sessão com dados necessários"""
    if "perfil" not in st.session_state:
        st.session_state["perfil"] = carregar_perfil()
    
    if "historico" not in st.session_state:
        st.session_state["historico"] = carregar_historico()
    
    # Verifica status da API
    api_key = os.getenv("ANTHROPIC_API_KEY")
    st.session_state["api_status"] = bool(api_key)

# Interface principal
def main():
    """Função principal do aplicativo"""
    
    # Verificar autenticação ANTES de tudo
    check_authentication()
    
    # Inicializa estado da sessão
    initialize_session_state()
    
    # Renderiza navegação lateral e obtém página selecionada
    pagina_selecionada = render_sidebar_navigation()
    
    # Roteamento das páginas
    if pagina_selecionada == "Dashboard":  # Página principal
        render_dashboard_page()
    elif pagina_selecionada == "Cérebro":
        show_cerebro_page()
    elif pagina_selecionada == "Reels e TikTok":
        render_reels_tiktok_page()
    elif pagina_selecionada == "React":
        render_react_page()
    elif pagina_selecionada == "Stalker":
        render_stalker_page()
    elif pagina_selecionada == "Raio-X":
        render_raiox_page()
    elif pagina_selecionada == "Histórico":
        from modules.historico import render_historico_page
        render_historico_page()

if __name__ == "__main__":
    main()

