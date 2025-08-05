"""
Página de Histórico - Lista elegante de roteiros salvos
"""
import streamlit as st
import base64
from datetime import datetime, date
from utils.helpers import (
    carregar_historico, salvar_historico, salvar_alteracoes_roteiro, excluir_roteiro
)


def render_historico_page():
    """Renderiza a página de histórico com filtros e lista elegante"""    
    
    ## === TÍTULO PRINCIPAL === ##
    with open("icons/clock.svg", "rb") as f:
        svg_base64 = base64.b64encode(f.read()).decode()
    
    st.markdown(f""" 
        <div style="display: flex; align-items: center; gap: 18px; margin-bottom: 1.5rem;">
            <img src="data:image/svg+xml;base64,{svg_base64}" width="48" height="48" style="margin-top: 4px;" />
            <h2 style="margin: 0; font-size: 2.8rem; font-weight: 700;">Histórico</h2>
        </div>
    """, unsafe_allow_html=True)
    
    # Carrega histórico
    historico = carregar_historico()
    
    if not historico:
        st.info("🖺 Nenhum roteiro salvo ainda. Comece criando seu primeiro roteiro!")
        return
    
    # Seção de filtros
    render_filtros_historico(historico)
    
    # Lista de roteiros
    render_lista_roteiros(historico)


def render_filtros_historico(historico):
    """Renderiza os filtros básicos para o histórico"""
    
    st.markdown("### 🔍 Filtros")
    
    col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
    
    # Valores padrão para os filtros
    valor_busca = ""
    valor_formato = "Todos"
    valor_data = None
    
    # Verifica se deve usar valores limpos
    if st.session_state.get('filtros_limpos', False):
        # Remove a flag após usar
        del st.session_state['filtros_limpos']
    else:
        # Usa valores do session_state se existirem
        valor_busca = st.session_state.get('filtro_busca', "")
        valor_formato = st.session_state.get('filtro_formato', "Todos")
        valor_data = st.session_state.get('filtro_data', None)
    
    with col1:
        filtro_busca = st.text_input(
            "Busca livre",
            placeholder="Digite título ou conteúdo...",
            value=valor_busca,
            key="filtro_busca"
        )
    
    with col2:
        # Extrai formatos únicos do histórico
        formatos = list(set([r.get('formato', 'Não especificado') for r in historico]))
        formatos.insert(0, "Todos")
        
        # Garante que o valor está na lista
        if valor_formato not in formatos:
            valor_formato = "Todos"
        
        filtro_formato = st.selectbox(
            "Tipo de roteiro",
            formatos,
            index=formatos.index(valor_formato),
            key="filtro_formato"
        )
    
    with col3:
        filtro_data = st.date_input(
            "Data",
            value=valor_data,
            key="filtro_data"
        )
    
    with col4:
        st.markdown("<br>", unsafe_allow_html=True)  # Espaçamento
        if st.button("Limpar", key="limpar_filtros"):
            # Define flag para usar valores limpos na próxima execução
            st.session_state['filtros_limpos'] = True
            # Remove as chaves dos filtros
            for key in ['filtro_busca', 'filtro_formato', 'filtro_data']:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
    
    # Aplica filtros
    historico_filtrado = aplicar_filtros(
        historico, 
        filtro_busca, 
        filtro_formato, 
        filtro_data
    )
    
    # Armazena no session_state para uso na lista
    st.session_state.historico_filtrado = historico_filtrado
    
    # Mostra estatísticas
    st.markdown(f"**🖺 {len(historico_filtrado)} roteiro(s) encontrado(s) de {len(historico)} total**")


def aplicar_filtros(historico, busca, formato, data_filtro):
    """Aplica os filtros ao histórico"""
    
    resultado = historico.copy()
    
    # Filtro por busca livre
    if busca:
        busca = busca.lower()
        resultado = [
            r for r in resultado 
            if busca in r.get('titulo', '').lower() or 
               busca in r.get('conteudo', '').lower()
        ]
    
    # Filtro por formato
    if formato and formato != "Todos":
        resultado = [
            r for r in resultado 
            if r.get('formato', 'Não especificado') == formato
        ]
    
    # Filtro por data
    if data_filtro:
        data_str = str(data_filtro)
        resultado = [
            r for r in resultado 
            if r.get('data', '').startswith(data_str) or
               r.get('timestamp', '').startswith(data_str)
        ]
    
    # Ordena por data (mais recente primeiro)
    resultado = sorted(
        resultado, 
        key=lambda x: x.get('timestamp', x.get('data', '')), 
        reverse=True
    )
    
    return resultado


def render_lista_roteiros(historico):
    """Renderiza a lista elegante de roteiros com expanders"""
    
    # Pega histórico filtrado
    historico_filtrado = st.session_state.get('historico_filtrado', historico)
    
    if not historico_filtrado:
        st.info("🔍 Nenhum roteiro encontrado com os filtros aplicados.")
        return
        
    # CSS para os expanders
    st.markdown("""
    <style>

    /* Estilo do container do expander (details) */
    details {
        margin-bottom: 16px !important;   /* Adiciona espaçamento entre os expanders */
    }

    /* Estilo do título (fechado ou aberto) */
    summary {
        background-color: #182433 !important;
        color: #f0f2f5 !important;
        border-radius: 10px !important;
        padding: 12px 16px !important;
        font-weight: 600 !important;
        border: 1px solid #223344 !important;
        list-style: none;
        cursor: pointer;
    }

    /* Remove o símbolo padrão do navegador (triângulo) */
    summary::-webkit-details-marker {
        display: none;
    }

    /* Estilo para o conteúdo aberto (dentro do expander) */
    details[open] > div {
        background-color: #151f2c !important;
        padding: 20px !important;
        border-radius: 10px !important;
        border: 1px solid #223344 !important;
        margin-top: -10px !important;
    }

    </style>
    """, unsafe_allow_html=True)
    
    for i, roteiro in enumerate(historico_filtrado):
        # Formata data
        try:
            timestamp = roteiro.get('timestamp', roteiro.get('data', ''))
            if timestamp:
                if 'T' in timestamp:
                    data_obj = datetime.fromisoformat(timestamp.replace('Z', ''))
                else:
                    data_obj = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
                data_formatada = data_obj.strftime('%d/%m/%Y às %H:%M')
            else:
                data_formatada = 'Data não disponível'
        except:
            data_formatada = 'Data inválida'
        
        titulo = roteiro.get('titulo', 'Roteiro sem título')
        formato = roteiro.get('formato', 'Não especificado')
        conteudo = roteiro.get('conteudo', 'Conteúdo não disponível')
        
        # Header do expander com informações resumidas
        header_text = f"**{titulo[:50]}{'...' if len(titulo) > 50 else ''}** | {formato} | {data_formatada}"
        
        # Expander fechado por padrão
        with st.expander(header_text, expanded=False):
            
            # Informações detalhadas
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"**◉ Título:** {titulo}")
                st.markdown(f"**◉ Formato:** {formato}")
                st.markdown(f"**◉ Data:** {data_formatada}")
                
                if roteiro.get('instrucao'):
                    st.markdown(f"**◉ Instrução:** {roteiro['instrucao']}")
            
            with col2:
                # Estatísticas rápidas
                palavras = len(conteudo.split())
                caracteres = len(conteudo)
                
                st.metric("Palavras", palavras)
                st.metric("Caracteres", caracteres)         
            
            # Campo editável para o conteúdo
            conteudo_editado = st.text_area(
                "Editar conteúdo:",
                value=conteudo,
                height=200,
                key=f"conteudo_{i}_{roteiro.get('id', i)}"
            )
            
            # Campo editável para o título
            titulo_editado = st.text_input(
                "Editar título:",
                value=titulo,
                key=f"titulo_{i}_{roteiro.get('id', i)}"
            )
            
            # Botões de ação
            col_btn1, col_btn2, col_btn3 = st.columns(3)
            
            with col_btn1:
                if st.button("Salvar Alterações", key=f"salvar_{i}_{roteiro.get('id', i)}"):
                    if titulo_editado != titulo or conteudo_editado != conteudo:
                        salvar_alteracoes_roteiro(
                            roteiro, titulo_editado, conteudo_editado, historico
                        )
                        st.success("✅ Alterações salvas!")
                        st.rerun()
                    else:
                        st.info("ℹ️ Nenhuma alteração detectada.")      
            
            with col_btn3:
                # Confirmação de exclusão
                if f"confirmar_exclusao_{i}" not in st.session_state:
                    if st.button("🗑️ Excluir", key=f"excluir_{i}_{roteiro.get('id', i)}"):
                        st.session_state[f"confirmar_exclusao_{i}"] = True
                        st.rerun()
                else:
                    st.warning("⚠️ Confirmar exclusão?")
                    col_conf1, col_conf2 = st.columns(2)
                    
                    with col_conf1:
                        if st.button("✅ Sim", key=f"confirmar_sim_{i}"):
                            excluir_roteiro(roteiro, historico)
                            del st.session_state[f"confirmar_exclusao_{i}"]
                            st.success("🗑️ Roteiro excluído!")
                            st.rerun()
                    
                    with col_conf2:
                        if st.button("❌ Não", key=f"confirmar_nao_{i}"):
                            del st.session_state[f"confirmar_exclusao_{i}"]
                            st.rerun()


if __name__ == "__main__":
    render_historico_page()

