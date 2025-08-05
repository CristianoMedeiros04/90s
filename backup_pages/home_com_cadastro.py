"""
Página principal - Reels e TikTok (funcionalidade original)
"""
import streamlit as st
import uuid
from datetime import datetime
from utils.helpers import (
    carregar_perfil, salvar_perfil, carregar_historico, salvar_historico,
    calcular_completude_perfil, extrair_texto_arquivo, aplicar_filtros_historico,
    salvar_alteracoes_roteiro, excluir_roteiro
)
from services.ai_agents import (
    gerar_roteiro_com_ia, salvar_roteiro_no_historico, analisar_temas_quentes
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
        st.warning("⚠️ Complete seu perfil na tela 'Reels e TikTok' para gerar roteiros mais personalizados!")
    elif completude < 80:
        st.info("ℹ️ Preencha mais informações no seu perfil para roteiros ainda melhores!")
    else:
        st.success("✅ Seu perfil está bem completo! Você pode gerar roteiros altamente personalizados.")


def render_reels_tiktok_page():
    """Renderiza a página principal de geração de roteiros (antiga funcionalidade)"""
    
    # Verifica qual sub-página mostrar
    if "sub_pagina" not in st.session_state:
        st.session_state["sub_pagina"] = "cadastro"
    
    # Menu de sub-páginas
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        if st.button("👤 Cadastro", use_container_width=True):
            st.session_state["sub_pagina"] = "cadastro"
    
    with col2:
        if st.button("✨ Gerar Roteiro", use_container_width=True):
            st.session_state["sub_pagina"] = "gerar"
    
    with col3:
        if st.button("🔥 Temas Quentes", use_container_width=True):
            st.session_state["sub_pagina"] = "temas"
    
    with col4:
        if st.button("📚 Histórico", use_container_width=True):
            st.session_state["sub_pagina"] = "historico"
    
    with col5:
        if st.button("🏠 Dashboard", use_container_width=True):
            st.session_state["sub_pagina"] = "dashboard"
    
    st.markdown("---")
    
    # Renderiza a sub-página selecionada
    if st.session_state["sub_pagina"] == "cadastro":
        render_cadastro_section()
    elif st.session_state["sub_pagina"] == "gerar":
        render_gerar_roteiro_section()
    elif st.session_state["sub_pagina"] == "temas":
        render_temas_quentes_section()
    elif st.session_state["sub_pagina"] == "historico":
        render_historico_section()
    elif st.session_state["sub_pagina"] == "dashboard":
        render_home_page()


def render_cadastro_section():
    """Renderiza a seção de cadastro do perfil"""
    st.header("👤 Cadastro do Perfil")
    st.markdown("Preencha o formulário abaixo o mais completamente possível. Essas informações serão usadas pela IA para criar roteiros personalizados.")
    
    # Carrega perfil existente se houver
    perfil_atual = st.session_state.get("perfil", {})
    
    with st.form("form_perfil"):
        st.markdown("### 📋 Formulário de Perfil")
        
        # Seção 1: Quem é você?
        with st.expander("🧑‍💼 Seção 1: Quem é você?", expanded=True):
            st.markdown("**Conte-nos sobre você, suas experiências e características:**")
            
            desejos_conquistas = st.text_area(
                "Desejos e conquistas que você já realizou",
                value=perfil_atual.get("desejos_conquistas", ""),
                placeholder="Ex: Abrir minha própria empresa de consultoria, completar um Ironman, comprar minha casa própria...",
                height=100
            )
            
            dores_enfrentadas = st.text_area(
                "Situações dolorosas ou desafios que você enfrentou",
                value=perfil_atual.get("dores_enfrentadas", ""),
                placeholder="Ex: Perda de emprego, problemas de saúde, dificuldades financeiras...",
                height=100
            )
            
            formacao = st.text_area(
                "Sua formação profissional e acadêmica",
                value=perfil_atual.get("formacao", ""),
                placeholder="Ex: Graduação em Administração, MBA em Marketing, Certificação em Coaching...",
                height=100
            )
            
            bio = st.text_area(
                "Quem é você? (idade, estado civil, nacionalidade, etc.)",
                value=perfil_atual.get("bio", ""),
                placeholder="Ex: Tenho 35 anos, sou casado, brasileiro, pai de dois filhos...",
                height=100
            )
            
            qualidades = st.text_area(
                "Suas principais qualidades e pontos fortes",
                value=perfil_atual.get("qualidades", ""),
                placeholder="Ex: Determinação, empatia, capacidade analítica, liderança...",
                height=100
            )
            
            defeitos = st.text_area(
                "Seus defeitos ou pontos fracos (seja honesto)",
                value=perfil_atual.get("defeitos", ""),
                placeholder="Ex: Impaciência, perfeccionismo excessivo, dificuldade para delegar...",
                height=100
            )
            
            tecnicas_realiza = st.text_area(
                "Técnicas, métodos ou práticas que você realiza",
                value=perfil_atual.get("tecnicas_realiza", ""),
                placeholder="Ex: Meditação diária, planejamento semanal, networking ativo...",
                height=100
            )
            
            tecnicas_nao_recomenda = st.text_area(
                "Técnicas ou práticas que você NÃO recomenda",
                value=perfil_atual.get("tecnicas_nao_recomenda", ""),
                placeholder="Ex: Trabalhar sem pausas, investir sem conhecimento, pular refeições...",
                height=100
            )
            
            habitos_recomenda = st.text_area(
                "Hábitos que você recomenda para seu público",
                value=perfil_atual.get("habitos_recomenda", ""),
                placeholder="Ex: Leitura diária, exercícios regulares, organização financeira...",
                height=100
            )
            
            habitos_nao_recomenda = st.text_area(
                "Hábitos que você NÃO recomenda",
                value=perfil_atual.get("habitos_nao_recomenda", ""),
                placeholder="Ex: Procrastinação, gastos impulsivos, sedentarismo...",
                height=100
            )
        
        # Seção 2: Seu público-alvo
        with st.expander("🎯 Seção 2: Seu público-alvo"):
            st.markdown("**Descreva detalhadamente quem é seu público:**")
            
            demo_publico = st.text_area(
                "Demografia do seu público (idade, gênero, localização, etc.)",
                value=perfil_atual.get("demo_publico", ""),
                placeholder="Ex: Mulheres de 25-40 anos, classe média, grandes centros urbanos...",
                height=100
            )
            
            desejos_publico = st.text_area(
                "Principais desejos e aspirações do seu público",
                value=perfil_atual.get("desejos_publico", ""),
                placeholder="Ex: Independência financeira, equilíbrio vida-trabalho, reconhecimento profissional...",
                height=100
            )
            
            dores_publico = st.text_area(
                "Principais dores e problemas que seu público enfrenta",
                value=perfil_atual.get("dores_publico", ""),
                placeholder="Ex: Falta de tempo, estresse, dificuldades financeiras...",
                height=100
            )
            
            qualidades_publico = st.text_area(
                "Qualidades e características positivas do seu público",
                value=perfil_atual.get("qualidades_publico", ""),
                placeholder="Ex: Determinação, vontade de aprender, responsabilidade...",
                height=100
            )
            
            defeitos_publico = st.text_area(
                "Defeitos ou dificuldades comuns do seu público",
                value=perfil_atual.get("defeitos_publico", ""),
                placeholder="Ex: Procrastinação, falta de foco, impaciência...",
                height=100
            )
            
            objecoes_publico = st.text_area(
                "Principais objeções que seu público tem",
                value=perfil_atual.get("objecoes_publico", ""),
                placeholder="Ex: 'Não tenho tempo', 'É muito caro', 'Já tentei e não funcionou'...",
                height=100
            )
            
            medos_publico = st.text_area(
                "Medos e receios do seu público",
                value=perfil_atual.get("medos_publico", ""),
                placeholder="Ex: Medo do fracasso, de julgamento, de mudanças...",
                height=100
            )
            
            referencias_culturais = st.text_area(
                "Referências culturais que seu público consome",
                value=perfil_atual.get("referencias_culturais", ""),
                placeholder="Ex: Netflix, Instagram, podcasts, livros de autoajuda...",
                height=100
            )
            
            pessoas_publico = st.text_area(
                "Pessoas que seu público admira ou segue",
                value=perfil_atual.get("pessoas_publico", ""),
                placeholder="Ex: Influenciadores, empresários, celebridades...",
                height=100
            )
            
            produtos_publico = st.text_area(
                "Produtos e serviços que seu público consome",
                value=perfil_atual.get("produtos_publico", ""),
                placeholder="Ex: Cursos online, aplicativos, suplementos...",
                height=100
            )
        
        # Seção 3: Suas crenças
        with st.expander("💭 Seção 3: Suas crenças e valores"):
            st.markdown("**Compartilhe suas convicções e valores:**")
            
            valores_inegociaveis = st.text_area(
                "Seus valores inegociáveis",
                value=perfil_atual.get("valores_inegociaveis", ""),
                placeholder="Ex: Honestidade, família, integridade...",
                height=100
            )
            
            crencas_centrais = st.text_area(
                "Suas crenças centrais sobre a vida",
                value=perfil_atual.get("crencas_centrais", ""),
                placeholder="Ex: O trabalho duro sempre compensa, a educação transforma vidas...",
                height=100
            )
            
            crencas_defende = st.text_area(
                "Crenças que você defende publicamente",
                value=perfil_atual.get("crencas_defende", ""),
                placeholder="Ex: Empreendedorismo é para todos, saúde mental é prioridade...",
                height=100
            )
            
            opiniao_impopular = st.text_area(
                "Uma opinião sua que pode ser controversa",
                value=perfil_atual.get("opiniao_impopular", ""),
                placeholder="Ex: Nem todo mundo precisa empreender, trabalho remoto não é para todos...",
                height=100
            )
            
            mitos_combatidos = st.text_area(
                "Mitos ou crenças limitantes que você combate",
                value=perfil_atual.get("mitos_combatidos", ""),
                placeholder="Ex: 'Dinheiro não traz felicidade', 'Só os jovens podem mudar de carreira'...",
                height=100
            )
        
        # Seção 4: Seus inimigos
        with st.expander("⚔️ Seção 4: Seus 'inimigos' (o que você combate)"):
            st.markdown("**Identifique o que você combate ou critica:**")
            
            inimigo_principal = st.text_area(
                "Seu principal 'inimigo' ou o que mais combate",
                value=perfil_atual.get("inimigo_principal", ""),
                placeholder="Ex: A mentalidade de vítima, a cultura do imediatismo...",
                height=100
            )
            
            comportamentos_inimigos = st.text_area(
                "Comportamentos prejudiciais que seu público tem",
                value=perfil_atual.get("comportamentos_inimigos", ""),
                placeholder="Ex: Procrastinação, gastos desnecessários, falta de planejamento...",
                height=100
            )
            
            inimigos_instituicoes = st.text_area(
                "Instituições, pessoas ou grupos que você critica",
                value=perfil_atual.get("inimigos_instituicoes", ""),
                placeholder="Ex: Bancos tradicionais, gurus do get-rich-quick...",
                height=100
            )
            
            praticas_criticadas = st.text_area(
                "Práticas ou métodos que você critica",
                value=perfil_atual.get("praticas_criticadas", ""),
                placeholder="Ex: Dietas milagrosas, esquemas de pirâmide...",
                height=100
            )
        
        # Seção 5: Fontes de conhecimento
        with st.expander("📚 Seção 5: Suas fontes de conhecimento"):
            st.markdown("**Envie documentos que contenham seu conhecimento técnico:**")
            
            arquivos = st.file_uploader(
                "Envie documentos de texto com suas fontes de conhecimento (DOCX ou TXT)",
                type=['docx', 'txt'],
                accept_multiple_files=True,
                help="Máximo 5 arquivos. Estes documentos serão usados para enriquecer o contexto dos roteiros."
            )
            
            conhecimento_extra = ""
            if arquivos:
                if len(arquivos) > 5:
                    st.warning("⚠️ Máximo 5 arquivos permitidos. Apenas os primeiros 5 serão processados.")
                    arquivos = arquivos[:5]
                
                for arquivo in arquivos:
                    texto_extraido = extrair_texto_arquivo(arquivo)
                    if texto_extraido:
                        conhecimento_extra += f"\n\n--- {arquivo.name} ---\n{texto_extraido}"
                
                if conhecimento_extra:
                    st.success(f"✅ {len(arquivos)} arquivo(s) processado(s) com sucesso!")
                    st.text_area(
                        "Prévia do conteúdo extraído:",
                        value=conhecimento_extra[:1000] + "..." if len(conhecimento_extra) > 1000 else conhecimento_extra,
                        height=200,
                        disabled=True
                    )
        
        # Botão de salvar
        if st.form_submit_button("💾 Salvar Perfil", type="primary"):
            # Monta o perfil completo
            perfil_completo = {
                "desejos_conquistas": desejos_conquistas,
                "dores_enfrentadas": dores_enfrentadas,
                "formacao": formacao,
                "bio": bio,
                "qualidades": qualidades,
                "defeitos": defeitos,
                "tecnicas_realiza": tecnicas_realiza,
                "tecnicas_nao_recomenda": tecnicas_nao_recomenda,
                "habitos_recomenda": habitos_recomenda,
                "habitos_nao_recomenda": habitos_nao_recomenda,
                "demo_publico": demo_publico,
                "desejos_publico": desejos_publico,
                "dores_publico": dores_publico,
                "qualidades_publico": qualidades_publico,
                "defeitos_publico": defeitos_publico,
                "objecoes_publico": objecoes_publico,
                "medos_publico": medos_publico,
                "referencias_culturais": referencias_culturais,
                "pessoas_publico": pessoas_publico,
                "produtos_publico": produtos_publico,
                "valores_inegociaveis": valores_inegociaveis,
                "crencas_centrais": crencas_centrais,
                "crencas_defende": crencas_defende,
                "opiniao_impopular": opiniao_impopular,
                "mitos_combatidos": mitos_combatidos,
                "inimigo_principal": inimigo_principal,
                "comportamentos_inimigos": comportamentos_inimigos,
                "inimigos_instituicoes": inimigos_instituicoes,
                "praticas_criticadas": praticas_criticadas,
                "conhecimento_extra": conhecimento_extra,
                "data_atualizacao": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # Salva o perfil
            st.session_state["perfil"] = perfil_completo
            salvar_perfil(perfil_completo)
            
            # Mostra completude
            completude = calcular_completude_perfil(perfil_completo)
            st.success(f"✅ Perfil salvo com sucesso! Completude: {completude}%")
            
            if completude >= 20:
                st.info("🎉 Agora você pode gerar roteiros personalizados!")


def render_gerar_roteiro_section():
    """Renderiza a seção de geração de roteiros"""
    st.header("✨ Gerar Roteiro")
    st.markdown("Use a IA para gerar roteiros personalizados baseados no seu perfil.")
    
    # Verifica se o perfil está preenchido
    perfil = st.session_state.get("perfil", {})
    completude = calcular_completude_perfil(perfil)
    
    if completude < 20:
        st.warning("⚠️ Para gerar roteiros personalizados, é recomendado preencher pelo menos 20% do seu perfil na tela 'Cadastro'.")
        
        if st.button("📝 Ir para Cadastro"):
            st.session_state["sub_pagina"] = "cadastro"
            st.rerun()
        return
    
    # Formulário de geração
    with st.form("form_gerar_roteiro"):
        st.markdown("### 🎬 Configurações do Roteiro")
        
        col1, col2 = st.columns(2)
        
        with col1:
            formato = st.selectbox(
                "Formato do roteiro:",
                ["Automático", "Lista útil", "Lista de reconhecimento", "Análise de popularidade", 
                 "Defesa de crença", "Substituição de crença", "O que acontece quando", "História de sucesso"],
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
        
        if st.form_submit_button("🚀 Gerar Roteiro", type="primary"):
            with st.spinner("🤖 Gerando roteiro personalizado..."):
                roteiro = gerar_roteiro_com_ia(perfil, instrucao_adicional, formato)
                
                if roteiro:
                    st.session_state["roteiro_atual"] = {
                        "conteudo": roteiro,
                        "titulo": titulo_roteiro,
                        "instrucao": instrucao_adicional,
                        "formato": formato
                    }
                    st.success("✅ Roteiro gerado com sucesso!")
                else:
                    st.error("❌ Erro ao gerar roteiro. Verifique sua conexão e tente novamente.")
    
    # Exibe o roteiro gerado
    if "roteiro_atual" in st.session_state:
        st.markdown("---")
        st.subheader("📝 Roteiro Gerado")
        
        roteiro_data = st.session_state["roteiro_atual"]
        
        # Título editável
        titulo_editado = st.text_input(
            "Título:",
            value=roteiro_data.get("titulo", ""),
            key="titulo_edicao"
        )
        
        # Conteúdo editável
        conteudo_editado = st.text_area(
            "Conteúdo do Roteiro:",
            value=roteiro_data.get("conteudo", ""),
            height=400,
            key="conteudo_edicao"
        )
        
        # Estatísticas
        render_statistics_section(conteudo_editado)
        
        # Botões de ação
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("💾 Salvar no Histórico", type="primary"):
                salvar_roteiro_no_historico(
                    conteudo_editado,
                    titulo_editado,
                    roteiro_data.get("instrucao", ""),
                    roteiro_data.get("formato", "")
                )
                st.success("✅ Roteiro salvo no histórico!")
        
        with col2:
            st.download_button(
                "⬇️ Baixar Roteiro",
                data=conteudo_editado,
                file_name=f"{titulo_editado or 'roteiro'}.txt",
                mime="text/plain"
            )
        
        with col3:
            if st.button("🔄 Gerar Novo"):
                if "roteiro_atual" in st.session_state:
                    del st.session_state["roteiro_atual"]
                st.rerun()


def render_temas_quentes_section():
    """Renderiza a seção de análise de temas quentes"""
    st.header("🔥 Temas Quentes")
    st.markdown("Analise tendências e conteúdos populares para inspirar seus próximos vídeos.")
    
    st.markdown("**Como funciona:**")
    st.markdown("1. Cole até 5 links de artigos, notícias ou conteúdos relevantes")
    st.markdown("2. A IA analisará o conteúdo e extrairá insights interessantes")
    st.markdown("3. Receba sugestões de temas para seus próximos vídeos")
    
    # Formulário de análise
    with st.form("form_temas_quentes"):
        st.markdown("### 🔗 Links para Análise")
        
        col1, col2 = st.columns(2)
        
        with col1:
            link1 = st.text_input("Link 1:", placeholder="https://exemplo.com/artigo-1")
            link2 = st.text_input("Link 2:", placeholder="https://exemplo.com/artigo-2")
            link3 = st.text_input("Link 3:", placeholder="https://exemplo.com/artigo-3")
        
        with col2:
            link4 = st.text_input("Link 4:", placeholder="https://exemplo.com/artigo-4")
            link5 = st.text_input("Link 5:", placeholder="https://exemplo.com/artigo-5")
            
            # Dicas na lateral
            st.markdown("### 💡 Dicas")
            st.markdown("**Tipos de links ideais:**")
            st.markdown("- Notícias recentes")
            st.markdown("- Artigos virais")
            st.markdown("- Posts populares")
            st.markdown("- Tendências do momento")
            st.markdown("- Conteúdos da sua área")
            
            st.markdown("**Evite:**")
            st.markdown("- Links quebrados")
            st.markdown("- Páginas com paywall")
            st.markdown("- Conteúdo muito técnico")
        
        if st.form_submit_button("🔍 Analisar Conteúdos", type="primary"):
            # Coleta links válidos
            links = [link for link in [link1, link2, link3, link4, link5] if link.strip()]
            
            if not links:
                st.error("❌ Adicione pelo menos um link para análise.")
            else:
                with st.spinner(f"🔍 Analisando {len(links)} link(s)..."):
                    relatorio = analisar_temas_quentes(links)
                    
                    if relatorio:
                        st.session_state["relatorio_temas"] = relatorio
                        st.success("✅ Análise concluída!")
                    else:
                        st.error("❌ Não foi possível analisar os links. Verifique se são válidos e acessíveis.")
    
    # Exibe o relatório
    if "relatorio_temas" in st.session_state:
        st.markdown("---")
        st.subheader("📊 Relatório de Análise")
        
        relatorio = st.session_state["relatorio_temas"]
        
        # Exibe o relatório
        st.markdown(relatorio)
        
        # Botões de ação
        col1, col2 = st.columns(2)
        
        with col1:
            st.download_button(
                "⬇️ Baixar Relatório",
                data=relatorio,
                file_name=f"relatorio_temas_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                mime="text/plain"
            )
        
        with col2:
            if st.button("🔄 Nova Análise"):
                if "relatorio_temas" in st.session_state:
                    del st.session_state["relatorio_temas"]
                st.rerun()


def render_historico_section():
    """Renderiza a seção de histórico de roteiros"""
    st.header("📚 Histórico de Roteiros")
    st.markdown("Visualize e gerencie todos os roteiros já gerados.")
    
    # Carrega histórico
    historico = st.session_state.get("historico", [])
    
    if not historico:
        st.info("📝 Nenhum roteiro salvo ainda. Vá para a tela 'Gerar Roteiro' para criar seu primeiro roteiro!")
        return
    
    # Filtros
    st.markdown("### 🔍 Filtros")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        filtro_texto = st.text_input("Buscar por título ou conteúdo:", placeholder="Digite para buscar...")
    
    with col2:
        formatos_disponiveis = ["Todos"] + list(set([r.get('formato', 'Não especificado') for r in historico]))
        filtro_formato = st.selectbox("Filtrar por formato:", formatos_disponiveis)
    
    with col3:
        filtro_data = st.date_input("Filtrar por data:", value=None)
    
    # Aplica filtros
    historico_filtrado = aplicar_filtros_historico(historico, filtro_texto, filtro_formato, filtro_data)
    
    # Estatísticas
    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total de Roteiros", len(historico))
    
    with col2:
        st.metric("Filtrados", len(historico_filtrado))
    
    with col3:
        if historico_filtrado:
            palavras_total = sum(len(r.get('conteudo', '').split()) for r in historico_filtrado)
            st.metric("Total de Palavras", palavras_total)
        else:
            st.metric("Total de Palavras", 0)
    
    with col4:
        formatos_unicos = len(set([r.get('formato', 'Não especificado') for r in historico]))
        st.metric("Formatos Únicos", formatos_unicos)
    
    # Lista de roteiros
    st.markdown("---")
    st.markdown("### 📋 Roteiros")
    
    if not historico_filtrado:
        st.info("🔍 Nenhum roteiro encontrado com os filtros aplicados.")
        return
    
    # Ordena por data (mais recente primeiro)
    historico_ordenado = sorted(historico_filtrado, key=lambda x: x.get('data', ''), reverse=True)
    
    for i, roteiro in enumerate(historico_ordenado):
        with st.expander(f"📄 {roteiro.get('titulo', 'Sem título')} - {roteiro.get('data_formatada', 'Data não disponível')}"):
            
            # Informações do roteiro
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.write(f"**📅 Data:** {roteiro.get('data_formatada', 'N/A')}")
            
            with col2:
                st.write(f"**🎬 Formato:** {roteiro.get('formato', 'N/A')}")
            
            with col3:
                palavras = len(roteiro.get('conteudo', '').split())
                st.write(f"**📊 Palavras:** {palavras}")
            
            if roteiro.get('instrucao'):
                st.write(f"**💡 Instrução:** {roteiro.get('instrucao')}")
            
            # Conteúdo
            st.markdown("**Conteúdo:**")
            conteudo_preview = roteiro.get('conteudo', '')
            if len(conteudo_preview) > 300:
                st.write(conteudo_preview[:300] + "...")
                if st.button(f"Ver completo", key=f"ver_completo_{i}"):
                    st.text_area("Conteúdo completo:", value=conteudo_preview, height=300, key=f"conteudo_completo_{i}")
            else:
                st.write(conteudo_preview)
            
            # Botões de ação
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                if st.button("✏️ Editar", key=f"editar_{i}"):
                    st.session_state[f"editando_{i}"] = True
            
            with col2:
                st.download_button(
                    "⬇️ Baixar",
                    data=roteiro.get('conteudo', ''),
                    file_name=f"{roteiro.get('titulo', 'roteiro')}.txt",
                    mime="text/plain",
                    key=f"download_{i}"
                )
            
            with col3:
                if st.button("🔄 Gerar Variação", key=f"variar_{i}"):
                    # Implementar geração de variação
                    st.info("Funcionalidade em desenvolvimento")
            
            with col4:
                if st.button("🗑️ Excluir", key=f"excluir_{i}"):
                    st.session_state[f"confirmar_exclusao_{i}"] = True
            
            # Modal de edição
            if st.session_state.get(f"editando_{i}"):
                st.markdown("---")
                st.markdown("**✏️ Editando Roteiro:**")
                
                novo_titulo = st.text_input("Título:", value=roteiro.get('titulo', ''), key=f"novo_titulo_{i}")
                novo_conteudo = st.text_area("Conteúdo:", value=roteiro.get('conteudo', ''), height=300, key=f"novo_conteudo_{i}")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("💾 Salvar Alterações", key=f"salvar_{i}"):
                        salvar_alteracoes_roteiro(roteiro, novo_titulo, novo_conteudo, historico)
                        st.session_state[f"editando_{i}"] = False
                        st.success("✅ Alterações salvas!")
                        st.rerun()
                
                with col2:
                    if st.button("❌ Cancelar", key=f"cancelar_{i}"):
                        st.session_state[f"editando_{i}"] = False
                        st.rerun()
            
            # Confirmação de exclusão
            if st.session_state.get(f"confirmar_exclusao_{i}"):
                st.warning("⚠️ Tem certeza que deseja excluir este roteiro?")
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("✅ Sim, excluir", key=f"confirmar_sim_{i}"):
                        excluir_roteiro(roteiro, historico)
                        st.success("✅ Roteiro excluído!")
                        st.rerun()
                
                with col2:
                    if st.button("❌ Cancelar", key=f"confirmar_nao_{i}"):
                        st.session_state[f"confirmar_exclusao_{i}"] = False
                        st.rerun()

