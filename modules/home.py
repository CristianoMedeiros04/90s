"""
Página principal - Reels e TikTok (apenas geração de roteiros)
Formulário de perfil foi movido para a tela Cérebro
"""
import streamlit as st
import uuid
import base64
from datetime import datetime
from utils.helpers import (
    carregar_perfil, salvar_perfil, carregar_historico, salvar_historico,
    calcular_completude_perfil, aplicar_filtros_historico,
    salvar_alteracoes_roteiro, excluir_roteiro, salvar_roteiro
)
from services.ai_agents import (
    gerar_roteiro_com_ia, analisar_temas_quentes
)
from components.layout import (
    render_metrics_row, render_status_card, render_expandable_content,
    render_roteiro_display, render_statistics_section
)


def render_home_page():
    """Renderiza a página principal (Home/Dashboard)"""
    st.header("📊 Dashboard")
    
    # Carrega dados
    perfil = st.session_state.get("perfil", {})
    historico = st.session_state.get("historico", [])
    
    # Métricas principais
    col1, col2, col3 = st.columns(3)
    
    with col1:
        total_roteiros = len(historico)
        st.metric("Roteiros Gerados", total_roteiros)
    
    with col2:
        if historico:
            ultimo_roteiro = max(historico, key=lambda x: x.get('data', ''))
            data_ultimo = ultimo_roteiro.get('data', 'Nunca')[:10] if ultimo_roteiro else 'Nunca'
        else:
            data_ultimo = 'Nunca'
        st.metric("Último Roteiro", data_ultimo)
    
    with col3:
        completude = calcular_completude_perfil(perfil)
        st.metric("Perfil Completo", f"{completude}%")
    
    st.markdown("---")
    
    # Últimos roteiros gerados
    st.subheader("📝 Últimos Roteiros Gerados")
    
    if historico:
        # Mostra os últimos 5 roteiros
        ultimos = sorted(historico, key=lambda x: x.get('data', ''), reverse=True)[:5]
        
        for roteiro in ultimos:
            with st.expander(f"📄 {roteiro.get('titulo', 'Sem título')} - {roteiro.get('data', '')[:10]}"):
                st.write(roteiro.get('conteudo', '')[:200] + "..." if len(roteiro.get('conteudo', '')) > 200 else roteiro.get('conteudo', ''))
        
        if st.button("📚 Ver histórico completo"):
            st.session_state["pagina_selecionada"] = "Histórico"
            st.rerun()
    else:
        st.info("Nenhum roteiro gerado ainda. Vá para a tela 'Reels e TikTok' para começar!")
    
    # Dicas para o usuário
    st.markdown("---")
    st.subheader("💡 Dicas")
    
    if completude < 50:
        st.markdown("⚠️ Complete seu perfil na tela **Cérebro** para gerar roteiros mais personalizados!")
    elif completude < 80:
        st.markdown("ℹ️ Preencha mais informações no seu perfil para roteiros ainda melhores!")
    else:
        st.markdown("✅ Seu perfil está bem completo! Você pode gerar roteiros altamente personalizados.")

def render_reels_tiktok_page():
    """Renderiza a página Reels e TikTok - APENAS GERAÇÃO DE ROTEIROS"""
    
    ## === TÍTULO PRINCIPAL === ##
    with open("icons/camera-movie.svg", "rb") as f:
        svg_base64 = base64.b64encode(f.read()).decode()
    
    st.markdown(f""" 
        <div style="display: flex; align-items: center; gap: 18px; margin-bottom: 1.5rem;">
            <img src="data:image/svg+xml;base64,{svg_base64}" width="48" height="48" style="margin-top: 4px;" />
            <h2 style="margin: 0; font-size: 2.8rem; font-weight: 700;">Reels e TikTok</h2>
        </div>
    """, unsafe_allow_html=True)
    
    
    
    # Verifica se o perfil está preenchido
    perfil = carregar_perfil()
    completude = calcular_completude_perfil(perfil)
    
    # Status do perfil    
    progress_bar_html = f"""
    <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.8rem;">
        <div style="flex-grow: 1;">
            <div style="background-color: #223344; border-radius: 10px; height: 22px; width: 100%;">
                <div style="
                    height: 100%;
                    width: {completude}%;
                    background: linear-gradient(90deg, #FF0050 0%, #cc0042 100%);
                    border-radius: 10px;
                    text-align: right;
                    padding-right: 10px;
                    color: white;
                    font-weight: 600;
                    font-size: 0.9rem;
                    line-height: 22px;
                ">
                    {completude}%
                </div>
            </div>
        </div>
    </div>
    """
    st.markdown(progress_bar_html, unsafe_allow_html=True)
    
    if completude < 20:
        st.error("❌ **Perfil incompleto!** Preencha pelo menos 20% do seu perfil na tela 'Cérebro' para gerar roteiros personalizados.")        
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🧠 Ir para Cérebro", type="primary", use_container_width=True):
                st.session_state["pagina_atual"] = "Cérebro"
                st.rerun()
        return
    
    if completude < 50:
        st.markdown("⚠️ Para melhores resultados, complete mais campos do seu perfil na tela 'Cérebro'.")
    
    st.markdown("---")   
       
    # Formulário de geração
    with st.form("form_gerar_roteiro"):
        st.markdown("### ⛭ Configurações do Roteiro")
        
        col1, col2 = st.columns(2)
        
        with col1:
            formato = st.selectbox(
                "Formato do roteiro:",
                ["Automático", "Lista útil", "Lista de reconhecimento", "Análise de popularidade", 
                 "Defesa de crença", "Substituição de crença", "O que acontece quando", "História de sucesso",
                 "Revelação Progressiva", "Contradição Intencional", "Jornada de Transformação", 
                 "Segredo de Bastidores", "Falha e Aprendizado", "Previsão e Validação", "Dilema e Resolução"],
                help="Escolha um formato específico ou deixe 'Automático' para a IA decidir"
            )
        
        with col2:
            titulo_roteiro = st.text_input(
                "Título do roteiro (opcional):",
                placeholder="Ex: Como investir sem medo",
                help="Se não preenchido, será gerado automaticamente"
            )
        
        instrucao_adicional = st.text_area(
            "Instruções específicas (opcional):",
            placeholder="Ex: Foque em pessoas que estão começando a investir, use exemplos práticos...",
            height=100,
            help="Adicione instruções específicas para personalizar ainda mais o roteiro"
        )
        
        if st.form_submit_button("Gerar Roteiro", type="primary"):
            with st.spinner("Gerando roteiro personalizado..."):
                roteiro = gerar_roteiro_com_ia(perfil, instrucao_adicional, formato)
                
                if roteiro:
                    st.session_state["roteiro_atual"] = {
                        "conteudo": roteiro,
                        "titulo": titulo_roteiro,
                        "instrucao": instrucao_adicional,
                        "formato": formato
                    }
                    st.success("✔︎ Roteiro gerado com sucesso!")
                else:
                    st.error("❌ Erro ao gerar roteiro. Verifique sua conexão e tente novamente.")
    
    # Exibe o roteiro gerado
    if "roteiro_atual" in st.session_state:
        st.markdown("---")
        st.subheader("✔︎ Roteiro Gerado")
        
        roteiro_data = st.session_state["roteiro_atual"]
        
        # Permite edição do roteiro
        roteiro_editado = render_roteiro_display(roteiro_data, editable=True)
        
        if roteiro_editado:
            # Estatísticas do roteiro
            render_statistics_section(roteiro_editado)
            
            # Botões de ação
            st.markdown("---")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("💾 Salvar no Histórico", type="primary", use_container_width=True):
                    roteiro_final = {
                        "id": str(uuid.uuid4()),
                        "titulo": roteiro_data.get('titulo', 'Roteiro sem título'),
                        "conteudo": roteiro_editado,
                        "formato": roteiro_data.get('formato', 'Automático'),
                        "instrucao": roteiro_data.get('instrucao', ''),
                        "data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "data_formatada": datetime.now().strftime("%d/%m/%Y às %H:%M")
                    }
                    
                    salvar_roteiro(roteiro_final)
                    st.success("✅ Roteiro salvo no histórico!")
                    
                    # Limpa o roteiro atual
                    if "roteiro_atual" in st.session_state:
                        del st.session_state["roteiro_atual"]
                    
                    st.rerun()
            
            with col2:
                # Botão de download
                st.download_button(
                    label="📥 Baixar Roteiro",
                    data=roteiro_editado,
                    file_name=f"roteiro_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain",
                    use_container_width=True
                )
            
            with col3:
                if st.button("🔄 Gerar Novo", use_container_width=True):
                    if "roteiro_atual" in st.session_state:
                        del st.session_state["roteiro_atual"]
                    st.rerun()
    
    # Seção de histórico resumido
    st.markdown("---")
    st.subheader("🗎 Últimos Roteiros")
    
    historico = carregar_historico()
    
    if historico:
        # Mostra os últimos 3 roteiros
        ultimos = sorted(historico, key=lambda x: x.get('data', ''), reverse=True)[:3]
        
        for roteiro in ultimos:
            with st.expander(f"◉ {roteiro.get('titulo', 'Sem título')} - {roteiro.get('data_formatada', '')}"):
                st.write(roteiro.get('conteudo', '')[:300] + "..." if len(roteiro.get('conteudo', '')) > 300 else roteiro.get('conteudo', ''))
                
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Formato:** {roteiro.get('formato', 'N/A')}")
                with col2:
                    if roteiro.get('instrucao'):
                        st.write(f"**Instrução:** {roteiro.get('instrucao')[:50]}...")
        
        if st.button(" Ver histórico completo"):
            st.session_state["pagina_atual"] = "Histórico"
            st.rerun()
    else:
        st.info("Nenhum roteiro salvo ainda. Gere seu primeiro roteiro acima!")   
    

def render_temas_quentes_section():
    """Renderiza a seção de temas quentes (mantida para compatibilidade)"""
    st.header("🔥 Temas Quentes")
    st.markdown("Analise tendências e gere conteúdo baseado em temas atuais.")
    
    # Verifica perfil
    perfil = carregar_perfil()
    completude = calcular_completude_perfil(perfil)
    
    if completude < 20:
        st.markdown("⚠️ Complete pelo menos 20% do seu perfil no Cérebro para análises personalizadas.")
        return
    
    # Interface para análise de temas
    with st.form("form_temas_quentes"):
        st.markdown("### 🌐 Análise de Conteúdo Web")
        
        urls = st.text_area(
            "Cole até 5 links de conteúdos relevantes (um por linha):",
            placeholder="https://exemplo1.com\nhttps://exemplo2.com\nhttps://exemplo3.com",
            height=150,
            help="Analise artigos, posts, vídeos ou qualquer conteúdo web relevante ao seu nicho"
        )
        
        if st.form_submit_button("🔍 Analisar Temas", type="primary"):
            if urls.strip():
                urls_lista = [url.strip() for url in urls.split('\n') if url.strip()]
                
                if len(urls_lista) > 5:
                    st.markdown("⚠️ Máximo 5 URLs. Analisando apenas as primeiras 5.")
                    urls_lista = urls_lista[:5]
                
                with st.spinner("🤖 Analisando conteúdos e gerando insights..."):
                    resultado = analisar_temas_quentes(urls_lista, perfil)
                    
                    if resultado:
                        st.markdown("✅ Análise concluída!")
                        st.markdown("### 📊 Relatório de Análise")
                        st.markdown(resultado)
                        
                        # Botão de download
                        st.download_button(
                            label="📥 Baixar Relatório",
                            data=resultado,
                            file_name=f"analise_temas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                            mime="text/plain"
                        )
                    else:
                        st.error("❌ Erro na análise. Verifique os links e tente novamente.")
            else:
                st.error("❌ Por favor, insira pelo menos um link para análise.")


def render_historico_section():
    """Renderiza a seção de histórico (mantida para compatibilidade)"""
    st.header("📚 Histórico de Roteiros")
    st.markdown("Gerencie todos os seus roteiros salvos.")
    
    # Carrega histórico
    historico = carregar_historico()
    
    if not historico:
        st.info("📝 Nenhum roteiro salvo ainda. Vá para 'Gerar Roteiro' para criar seu primeiro!")
        return
    
    # Filtros
    col1, col2, col3 = st.columns(3)
    
    with col1:
        filtro_formato = st.selectbox(
            "Filtrar por formato:",
            ["Todos"] + list(set([r.get('formato', 'N/A') for r in historico]))
        )
    
    with col2:
        filtro_data = st.date_input("Filtrar por data:", value=None)
    
    with col3:
        busca_texto = st.text_input("Buscar no conteúdo:", placeholder="Digite para buscar...")
    
    # Aplica filtros
    historico_filtrado = aplicar_filtros_historico(
        historico, filtro_formato, filtro_data, busca_texto
    )
    
    # Estatísticas
    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total de Roteiros", len(historico))
    
    with col2:
        st.metric("Filtrados", len(historico_filtrado))
    
    with col3:
        if historico:
            palavras_total = sum(len(r.get('conteudo', '').split()) for r in historico)
            st.metric("Palavras Total", f"{palavras_total:,}")
    
    with col4:
        if historico:
            formatos_unicos = len(set(r.get('formato', 'N/A') for r in historico))
            st.metric("Formatos Únicos", formatos_unicos)
    
    # Lista de roteiros
    st.markdown("---")
    
    for roteiro in historico_filtrado:
        with st.expander(f"📄 {roteiro.get('titulo', 'Sem título')} - {roteiro.get('data_formatada', '')}"):
            
            # Informações do roteiro
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.write(f"**📅 Data:** {roteiro.get('data_formatada', 'N/A')}")
            
            with col2:
                st.write(f"**🎬 Formato:** {roteiro.get('formato', 'N/A')}")
            
            with col3:
                if roteiro.get('instrucao'):
                    st.write(f"**💡 Instrução:** {roteiro.get('instrucao')[:50]}...")
                else:
                    st.write("**💡 Instrução:** Nenhuma")
            
            # Conteúdo editável
            roteiro_editado = render_roteiro_display(roteiro, editable=True)
            
            if roteiro_editado:
                # Estatísticas
                render_statistics_section(roteiro_editado)
                
                # Botões de ação
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if st.button(f"🖫 Salvar Alterações", key=f"salvar_{roteiro['id']}"):
                        salvar_alteracoes_roteiro(roteiro['id'], roteiro_editado)
                        st.markdown("✅ Alterações salvas!")
                        st.rerun()
                
                with col2:
                    st.download_button(
                        label="📥 Baixar",
                        data=roteiro_editado,
                        file_name=f"{roteiro.get('titulo', 'roteiro')}.txt",
                        mime="text/plain",
                        key=f"download_{roteiro['id']}"
                    )
                
                with col3:
                    if st.button(f"🗑️ Excluir", key=f"excluir_{roteiro['id']}", type="secondary"):
                        excluir_roteiro(roteiro['id'])
                        st.markdown("✅ Roteiro excluído!")
                        st.rerun()

