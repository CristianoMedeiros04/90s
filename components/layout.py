"""
Componentes de layout reutilizáveis para o aplicativo
"""
import streamlit as st
import base64
from streamlit_option_menu import option_menu


def setup_page_config():
    """Configuração padrão da página"""
    st.set_page_config(
        page_title="90s",
        page_icon="🎬",
        layout="wide",
        initial_sidebar_state="expanded"
    )

def render_sidebar_navigation():
    """Renderiza o menu de navegação lateral usando option_menu"""
    with st.sidebar:
        
        # === LOGO DO APP === #       
        logo_path = "icons/logo_90s.png"        
        with open(logo_path, "rb") as img_file:
            encoded_logo = base64.b64encode(img_file.read()).decode()       

        st.markdown(f"""
            <div style="display: flex; justify-content: center; align-items: center; padding: 1.5rem 0;">
                <img src="data:image/png;base64,{encoded_logo}" alt="Logo 90s" style="height: 80px;">
            </div>
        """, unsafe_allow_html=True)


        # Menu de navegação usando option_menu
        selected = option_menu(
            menu_title=None,
            options=["Dashboard", "Cérebro", "Reels e TikTok", "React", "Stalker", "Raio-X", "Histórico"],
            icons=["speedometer2", "cpu", "camera-reels-fill", "emoji-laughing", "incognito", "x-diamond", "clock-history"],
            menu_icon="cast",
            default_index=0,
            styles={
                "container": {"padding": "0!important", "background-color": "transparent"},
                "icon": {"color": "#c4c7ca", "font-size": "18px"},
                "nav-link": {"color": "#c4c7ca", "font-size": "16px", "text-align": "left", "margin": "0px", "--hover-color": "transparent"},
                "nav-link-selected": {"background-color": "#151F2C", "color": "#c4c7ca"},
            }
        )
        
        # Adiciona botão de logout no final da sidebar
        from auth.login import render_logout_button
        render_logout_button()
        
        return selected


def render_metrics_row(col1_metric, col2_metric, col3_metric):
    """Renderiza uma linha de métricas"""
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label=col1_metric["label"],
            value=col1_metric["value"],
            delta=col1_metric.get("delta")
        )
    
    with col2:
        st.metric(
            label=col2_metric["label"],
            value=col2_metric["value"],
            delta=col2_metric.get("delta")
        )
    
    with col3:
        st.metric(
            label=col3_metric["label"],
            value=col3_metric["value"],
            delta=col3_metric.get("delta")
        )


def render_status_card(title, content, status="info"):
    """Renderiza um card de status"""
    if status == "success":
        st.success(f"**{title}**\n\n{content}")
    elif status == "warning":
        st.warning(f"**{title}**\n\n{content}")
    elif status == "error":
        st.error(f"**{title}**\n\n{content}")
    else:
        st.info(f"**{title}**\n\n{content}")


def render_expandable_content(title, content, expanded=False):
    """Renderiza conteúdo em um expander"""
    with st.expander(title, expanded=expanded):
        st.markdown(content)


def render_roteiro_display(roteiro_data, editable=False):
    """Renderiza a exibição de um roteiro"""
    if not roteiro_data:
        st.warning("Nenhum roteiro para exibir")
        return None
    
    # Verifica se roteiro_data é uma string (conteúdo direto) ou dicionário
    if isinstance(roteiro_data, str):
        # Se for string, cria um dicionário simples
        roteiro_dict = {
            "conteudo": roteiro_data,
            "formato": "N/A",
            "duracao": "N/A"
        }
    else:
        # Se for dicionário, usa como está
        roteiro_dict = roteiro_data
    
    st.markdown("### 📝 Roteiro Gerado")
    
    # Informações do roteiro
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"**Formato:** {roteiro_dict.get('formato', 'N/A')}")
        st.markdown(f"**Duração estimada:** {roteiro_dict.get('duracao', 'N/A')}")
    
    with col2:
        conteudo = roteiro_dict.get('conteudo', '')
        st.markdown(f"**Palavras:** {len(conteudo.split())}")
        st.markdown(f"**Caracteres:** {len(conteudo)}")
    
    # Conteúdo do roteiro
    st.markdown("---")
    
    if editable:
        # Permite edição do roteiro
        conteudo_editado = st.text_area(
            "Edite o roteiro:",
            value=roteiro_dict.get('conteudo', ''),
            height=300,
            key=f"roteiro_edit_{roteiro_dict.get('id', 'temp')}"
        )
        return conteudo_editado
    else:
        # Apenas exibe o roteiro
        st.markdown(roteiro_dict.get('conteudo', 'Conteúdo não disponível'))
        return None


def render_statistics_section(stats_data):
    """Renderiza seção de estatísticas"""
    if not stats_data:
        return
    
    st.markdown("### 📊 Estatísticas")
    
    # Se stats_data for uma string (conteúdo do roteiro), calcula as estatísticas
    if isinstance(stats_data, str):
        conteudo = stats_data
        stats_dict = {
            "Palavras": len(conteudo.split()),
            "Caracteres": len(conteudo),
            "Parágrafos": len([p for p in conteudo.split('\n') if p.strip()]),
            "Duração (seg)": len(conteudo.split()) * 0.5  # Aproximadamente 2 palavras por segundo
        }
    else:
        # Se for dicionário, usa como está
        stats_dict = stats_data
    
    cols = st.columns(len(stats_dict))
    
    for i, (key, value) in enumerate(stats_dict.items()):
        with cols[i]:
            if key == "Duração (seg)":
                st.metric(key, f"{int(value)}s")
            else:
                st.metric(key, value)

