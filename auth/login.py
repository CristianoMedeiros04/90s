"""
Módulo de Autenticação Simples
Sistema de login básico com usuário e senha padrão
"""
import streamlit as st
import base64

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
    background: #7aaea8 !important;         /* Cor de fundo ao passar o mouse */
}
.stButton > button:focus {
    outline: none !important;
    box-shadow: 0 0 0 2px #cce5e2 !important;
}

/* === BOTÃO "SAIR" NA SIDEBAR (FORÇA TEXTO BRANCO) === */
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

# Credenciais padrão (hardcoded para simplicidade)
ADMIN_USER = "admin"
ADMIN_PASSWORD = "123"

def render_login():
    """Renderiza a tela de login simples e leve"""
    
   
    # Container principal
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        
        # Formulário de login
        with st.form("login_form", clear_on_submit=False):
            st.markdown("### 🔐 Acesso ao Sistema")
            
            usuario = st.text_input(
                "Usuário",
                placeholder="Digite o usuário",
                value="",
                key="login_user"
            )
            
            senha = st.text_input(
                "Senha",
                type="password",
                placeholder="Digite a senha",
                value="",
                key="login_password"
            )
            
            # Botão de login
            login_button = st.form_submit_button(
                "Entrar",
                type="primary",
                use_container_width=True
            )
            
            if login_button:
                if not usuario or not senha:
                    st.error("❌ Por favor, preencha usuário e senha")
                else:
                    # Verificar credenciais
                    if usuario == ADMIN_USER and senha == ADMIN_PASSWORD:
                        # Login bem-sucedido
                        st.session_state.logged_in = True
                        st.session_state.user_name = "Administrador"
                        st.session_state.user_type = "admin"
                        
                        st.success("✅ Login realizado com sucesso!")
                        st.rerun()
                    else:
                        st.error("❌ Usuário ou senha incorretos")       

def check_authentication():
    """Verifica se o usuário está autenticado"""
    if not st.session_state.get('logged_in', False):
        render_login()
        st.stop()

def logout():
    """Faz logout do usuário"""
    # Limpar variáveis de sessão relacionadas ao login
    keys_to_clear = ['logged_in', 'user_name', 'user_type']
    
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]
    
    st.rerun()

def render_logout_button():
    """Renderiza botão de logout na sidebar"""
    if st.session_state.get('logged_in', False):
        user_name = st.session_state.get('user_name', 'Usuário')
        
        st.markdown("---")
      
        svg_path = "icons/circle-user.svg"        
        with open(svg_path, "rb") as f:
            svg_base64 = base64.b64encode(f.read()).decode()
        st.markdown(f"""
            <div style="display: flex; align-items: center; gap: 10px; margin-top: 0.5rem; margin-bottom: 1rem;">
                <img src="data:image/svg+xml;base64,{svg_base64}" alt="Usuário" width="20" height="20" />
                <span style="font-weight: 600; color: #f0f2f5;">{user_name}</span>
            </div>
        """, unsafe_allow_html=True)

        if st.button("❮ Sair", type="secondary", use_container_width=True, key="logout_btn"):
            logout()

