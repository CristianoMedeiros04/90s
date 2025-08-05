"""
Tela Cérebro - Formulário de Perfil Central
Este é o banco de contexto usado por todas as páginas de geração de copy
"""
import streamlit as st
import json
import os
from datetime import datetime
from utils.helpers import extrair_texto_arquivo

def load_cerebro_data():
    """Carrega os dados do cérebro (perfil completo do usuário)"""
    cerebro_file = "data/cerebro.json"
    if os.path.exists(cerebro_file):
        with open(cerebro_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_cerebro_data(data):
    """Salva os dados do cérebro"""
    os.makedirs("data", exist_ok=True)
    with open("data/cerebro.json", 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_cerebro_context():
    """Retorna o contexto do cérebro formatado para uso em prompts de IA"""
    data = load_cerebro_data()
    if not data:
        return "Perfil não configurado. Use informações genéricas."
    
    context = f"""
CONTEXTO DO USUÁRIO (CÉREBRO):

=== INFORMAÇÕES PESSOAIS ===
Nome: {data.get('nome', 'Não informado')}
Idade: {data.get('idade', 'Não informado')}
Profissão: {data.get('profissao', 'Não informado')}
Localização: {data.get('localizacao', 'Não informado')}

=== NEGÓCIO/PROJETO ===
Área de Atuação: {data.get('area_atuacao', 'Não informado')}
Público-Alvo: {data.get('publico_alvo', 'Não informado')}
Principais Produtos/Serviços: {data.get('produtos_servicos', 'Não informado')}
Diferenciais: {data.get('diferenciais', 'Não informado')}

=== OBJETIVOS E METAS ===
Objetivos Principais: {data.get('objetivos', 'Não informado')}
Metas de Curto Prazo: {data.get('metas_curto_prazo', 'Não informado')}
Metas de Longo Prazo: {data.get('metas_longo_prazo', 'Não informado')}

=== CONTEÚDO E COMUNICAÇÃO ===
Tom de Voz: {data.get('tom_voz', 'Não informado')}
Temas de Interesse: {data.get('temas_interesse', 'Não informado')}
Estilo de Comunicação: {data.get('estilo_comunicacao', 'Não informado')}
Palavras-chave: {data.get('palavras_chave', 'Não informado')}

=== EXPERIÊNCIAS E CONQUISTAS ===
Desejos e Conquistas: {data.get('desejos_conquistas', 'Não informado')}
Experiências Relevantes: {data.get('experiencias', 'Não informado')}
Histórias Pessoais: {data.get('historias', 'Não informado')}

INSTRUÇÕES: Use essas informações para personalizar TODOS os conteúdos gerados.
"""
    return context

def calcular_completude_perfil(perfil):
    """Calcula a porcentagem de completude do perfil"""
    if not perfil:
        return 0
    
    total_campos = 37  # Total de campos do perfil conforme especificação
    campos_preenchidos = sum(1 for valor in perfil.values() if valor and str(valor).strip())
    return int((campos_preenchidos / total_campos) * 100) if total_campos > 0 else 0

def show_cerebro_page():
    """Renderiza a tela Cérebro - Formulário de Perfil Central"""
    
    st.title("🧠 Cérebro")
    st.markdown("**Preencha o formulário abaixo o mais completamente possível. Essas informações serão usadas pela IA para criar roteiros personalizados.**")
    
    # Carrega dados existentes
    perfil = load_cerebro_data()
    
    # Calcula completude
    completude = calcular_completude_perfil(perfil)
    
    # Barra de progresso
    st.subheader("📊 Completude do Perfil")
    progress_col1, progress_col2 = st.columns([3, 1])
    
    with progress_col1:
        st.progress(completude / 100)
    
    with progress_col2:
        st.metric("Completo", f"{completude}%")
    
    if completude < 20:
        st.error("❌ Perfil muito incompleto. Preencha pelo menos 20% para gerar roteiros personalizados.")
    elif completude < 50:
        st.warning("⚠️ Perfil parcialmente completo. Preencha mais campos para melhores resultados.")
    elif completude < 80:
        st.info("ℹ️ Bom progresso! Continue preenchendo para roteiros ainda mais personalizados.")
    else:
        st.success("✅ Perfil muito completo! Você terá roteiros altamente personalizados.")
    
    st.markdown("---")
    
    # Formulário em abas
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "👤 Pessoal", 
        "💼 Negócio", 
        "🎯 Objetivos", 
        "📝 Conteúdo", 
        "🏆 Experiências"
    ])
    
    # ABA 1: INFORMAÇÕES PESSOAIS
    with tab1:
        st.subheader("👤 Informações Pessoais")
        
        col1, col2 = st.columns(2)
        
        with col1:
            nome = st.text_input("Nome completo:", value=perfil.get('nome', ''))
            idade = st.number_input("Idade:", min_value=0, max_value=120, value=perfil.get('idade', 0))
            profissao = st.text_input("Profissão:", value=perfil.get('profissao', ''))
        
        with col2:
            localizacao = st.text_input("Localização (cidade/estado):", value=perfil.get('localizacao', ''))
            estado_civil = st.selectbox("Estado civil:", 
                ["", "Solteiro(a)", "Casado(a)", "Divorciado(a)", "Viúvo(a)", "União estável"],
                index=0 if not perfil.get('estado_civil') else 
                ["", "Solteiro(a)", "Casado(a)", "Divorciado(a)", "Viúvo(a)", "União estável"].index(perfil.get('estado_civil', '')))
            
            escolaridade = st.selectbox("Escolaridade:", 
                ["", "Ensino Fundamental", "Ensino Médio", "Superior Incompleto", "Superior Completo", "Pós-graduação", "Mestrado", "Doutorado"],
                index=0 if not perfil.get('escolaridade') else 
                ["", "Ensino Fundamental", "Ensino Médio", "Superior Incompleto", "Superior Completo", "Pós-graduação", "Mestrado", "Doutorado"].index(perfil.get('escolaridade', '')))
        
        personalidade = st.text_area("Descreva sua personalidade:", 
            value=perfil.get('personalidade', ''),
            placeholder="Ex: Sou uma pessoa extrovertida, criativa, que gosta de desafios...")
        
        hobbies = st.text_area("Hobbies e interesses pessoais:", 
            value=perfil.get('hobbies', ''),
            placeholder="Ex: Leitura, viagens, culinária, esportes...")
    
    # ABA 2: NEGÓCIO/PROJETO
    with tab2:
        st.subheader("💼 Negócio/Projeto")
        
        col1, col2 = st.columns(2)
        
        with col1:
            area_atuacao = st.text_input("Área de atuação:", value=perfil.get('area_atuacao', ''))
            tempo_mercado = st.text_input("Tempo no mercado:", value=perfil.get('tempo_mercado', ''))
            tamanho_empresa = st.selectbox("Tamanho da empresa/projeto:",
                ["", "Pessoa física", "MEI", "Micro empresa", "Pequena empresa", "Média empresa", "Grande empresa"],
                index=0 if not perfil.get('tamanho_empresa') else 
                ["", "Pessoa física", "MEI", "Micro empresa", "Pequena empresa", "Média empresa", "Grande empresa"].index(perfil.get('tamanho_empresa', '')))
        
        with col2:
            publico_alvo = st.text_area("Público-alvo:", 
                value=perfil.get('publico_alvo', ''),
                placeholder="Ex: Mulheres de 25-40 anos, interessadas em empreendedorismo...")
            
            faturamento = st.selectbox("Faixa de faturamento mensal:",
                ["", "Até R$ 5.000", "R$ 5.001 - R$ 20.000", "R$ 20.001 - R$ 50.000", "R$ 50.001 - R$ 100.000", "Acima de R$ 100.000"],
                index=0 if not perfil.get('faturamento') else 
                ["", "Até R$ 5.000", "R$ 5.001 - R$ 20.000", "R$ 20.001 - R$ 50.000", "R$ 50.001 - R$ 100.000", "Acima de R$ 100.000"].index(perfil.get('faturamento', '')))
        
        produtos_servicos = st.text_area("Principais produtos/serviços:", 
            value=perfil.get('produtos_servicos', ''),
            placeholder="Ex: Consultoria em marketing digital, cursos online...")
        
        diferenciais = st.text_area("Seus principais diferenciais:", 
            value=perfil.get('diferenciais', ''),
            placeholder="Ex: 10 anos de experiência, metodologia própria...")
        
        concorrentes = st.text_area("Principais concorrentes:", 
            value=perfil.get('concorrentes', ''),
            placeholder="Ex: Empresa X, Influencer Y...")
    
    # ABA 3: OBJETIVOS E METAS
    with tab3:
        st.subheader("🎯 Objetivos e Metas")
        
        objetivos = st.text_area("Objetivos principais:", 
            value=perfil.get('objetivos', ''),
            placeholder="Ex: Aumentar vendas em 50%, expandir para novos mercados...")
        
        col1, col2 = st.columns(2)
        
        with col1:
            metas_curto_prazo = st.text_area("Metas de curto prazo (3-6 meses):", 
                value=perfil.get('metas_curto_prazo', ''),
                placeholder="Ex: Lançar novo produto, atingir 10k seguidores...")
        
        with col2:
            metas_longo_prazo = st.text_area("Metas de longo prazo (1-2 anos):", 
                value=perfil.get('metas_longo_prazo', ''),
                placeholder="Ex: Abrir filial, ser referência no setor...")
        
        desafios = st.text_area("Principais desafios atuais:", 
            value=perfil.get('desafios', ''),
            placeholder="Ex: Gerar mais leads, melhorar conversão...")
        
        motivacao = st.text_area("O que te motiva:", 
            value=perfil.get('motivacao', ''),
            placeholder="Ex: Ajudar pessoas, crescimento pessoal, independência financeira...")
    
    # ABA 4: CONTEÚDO E COMUNICAÇÃO
    with tab4:
        st.subheader("📝 Conteúdo e Comunicação")
        
        col1, col2 = st.columns(2)
        
        with col1:
            tom_voz = st.selectbox("Tom de voz preferido:",
                ["", "Formal", "Informal", "Descontraído", "Profissional", "Amigável", "Autoritativo", "Inspirador"],
                index=0 if not perfil.get('tom_voz') else 
                ["", "Formal", "Informal", "Descontraído", "Profissional", "Amigável", "Autoritativo", "Inspirador"].index(perfil.get('tom_voz', '')))
            
            estilo_comunicacao = st.selectbox("Estilo de comunicação:",
                ["", "Direto", "Storytelling", "Educativo", "Humorístico", "Emocional", "Técnico", "Conversacional"],
                index=0 if not perfil.get('estilo_comunicacao') else 
                ["", "Direto", "Storytelling", "Educativo", "Humorístico", "Emocional", "Técnico", "Conversacional"].index(perfil.get('estilo_comunicacao', '')))
        
        with col2:
            linguagem = st.selectbox("Linguagem preferida:",
                ["", "Simples", "Técnica", "Jovem", "Corporativa", "Regional", "Internacional"],
                index=0 if not perfil.get('linguagem') else 
                ["", "Simples", "Técnica", "Jovem", "Corporativa", "Regional", "Internacional"].index(perfil.get('linguagem', '')))
            
            formato_preferido = st.multiselect("Formatos de conteúdo preferidos:",
                ["Vídeos curtos", "Stories", "Posts", "Carrosséis", "Reels", "Lives", "Podcasts"],
                default=perfil.get('formato_preferido', []))
        
        temas_interesse = st.text_area("Temas de interesse para conteúdo:", 
            value=perfil.get('temas_interesse', ''),
            placeholder="Ex: Empreendedorismo, produtividade, lifestyle...")
        
        palavras_chave = st.text_area("Palavras-chave importantes:", 
            value=perfil.get('palavras_chave', ''),
            placeholder="Ex: inovação, qualidade, resultados, transformação...")
        
        evitar = st.text_area("Palavras/temas a evitar:", 
            value=perfil.get('evitar', ''),
            placeholder="Ex: política, religião, temas polêmicos...")
    
    # ABA 5: EXPERIÊNCIAS E CONQUISTAS
    with tab5:
        st.subheader("🏆 Experiências e Conquistas")
        
        desejos_conquistas = st.text_area("Desejos e conquistas:", 
            value=perfil.get('desejos_conquistas', ''),
            placeholder="Ex: Sempre sonhei em ter meu próprio negócio, conquistei minha independência financeira...")
        
        experiencias = st.text_area("Experiências relevantes:", 
            value=perfil.get('experiencias', ''),
            placeholder="Ex: Trabalhei 10 anos em multinacional, fui gerente de vendas...")
        
        historias = st.text_area("Histórias pessoais marcantes:", 
            value=perfil.get('historias', ''),
            placeholder="Ex: Comecei vendendo na porta de casa, superei uma grande dificuldade...")
        
        conquistas = st.text_area("Principais conquistas:", 
            value=perfil.get('conquistas', ''),
            placeholder="Ex: Prêmio de melhor vendedor, empresa com 6 dígitos...")
        
        aprendizados = st.text_area("Principais aprendizados:", 
            value=perfil.get('aprendizados', ''),
            placeholder="Ex: Aprendi que persistência é fundamental, descobri minha paixão por ensinar...")
        
        valores = st.text_area("Valores pessoais/profissionais:", 
            value=perfil.get('valores', ''),
            placeholder="Ex: Honestidade, qualidade, compromisso com resultados...")
    
    # Upload de documentos para enriquecer conhecimento
    st.markdown("---")
    st.subheader("📎 Documentos Adicionais")
    st.markdown("Faça upload de documentos que possam enriquecer o conhecimento sobre você:")
    
    uploaded_files = st.file_uploader(
        "Escolha arquivos (DOCX, TXT):",
        type=['docx', 'txt'],
        accept_multiple_files=True,
        help="Documentos como biografia, apresentações, materiais de marketing, etc."
    )
    
    documentos_texto = ""
    if uploaded_files:
        for arquivo in uploaded_files:
            texto_extraido = extrair_texto_arquivo(arquivo)
            if texto_extraido:
                documentos_texto += f"\n\n=== {arquivo.name} ===\n{texto_extraido}"
    
    # Botão para salvar
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if st.button("💾 Salvar Perfil", type="primary", use_container_width=True):
            # Coleta todos os dados
            perfil_completo = {
                # Pessoal
                'nome': nome,
                'idade': idade,
                'profissao': profissao,
                'localizacao': localizacao,
                'estado_civil': estado_civil,
                'escolaridade': escolaridade,
                'personalidade': personalidade,
                'hobbies': hobbies,
                
                # Negócio
                'area_atuacao': area_atuacao,
                'tempo_mercado': tempo_mercado,
                'tamanho_empresa': tamanho_empresa,
                'publico_alvo': publico_alvo,
                'faturamento': faturamento,
                'produtos_servicos': produtos_servicos,
                'diferenciais': diferenciais,
                'concorrentes': concorrentes,
                
                # Objetivos
                'objetivos': objetivos,
                'metas_curto_prazo': metas_curto_prazo,
                'metas_longo_prazo': metas_longo_prazo,
                'desafios': desafios,
                'motivacao': motivacao,
                
                # Conteúdo
                'tom_voz': tom_voz,
                'estilo_comunicacao': estilo_comunicacao,
                'linguagem': linguagem,
                'formato_preferido': formato_preferido,
                'temas_interesse': temas_interesse,
                'palavras_chave': palavras_chave,
                'evitar': evitar,
                
                # Experiências
                'desejos_conquistas': desejos_conquistas,
                'experiencias': experiencias,
                'historias': historias,
                'conquistas': conquistas,
                'aprendizados': aprendizados,
                'valores': valores,
                
                # Documentos
                'documentos_adicionais': documentos_texto,
                
                # Metadados
                'data_atualizacao': datetime.now().isoformat(),
                'completude': calcular_completude_perfil(perfil_completo)
            }
            
            # Salva os dados
            save_cerebro_data(perfil_completo)
            
            # Atualiza estado da sessão
            st.session_state["perfil"] = perfil_completo
            
            # Feedback
            nova_completude = calcular_completude_perfil(perfil_completo)
            st.success(f"✅ Perfil salvo com sucesso! Completude: {nova_completude}%")
            
            if nova_completude >= 20:
                st.info("🎯 Agora você pode gerar roteiros personalizados nas outras telas!")
            
            st.rerun()
    
    # Informações sobre uso do perfil
    st.markdown("---")
    st.subheader("ℹ️ Como seu perfil é usado")
    
    st.markdown("""
    **Seu perfil é o cérebro do sistema!** Todas as páginas de geração de copy usam essas informações:
    
    - **🎬 Reels e TikTok:** Roteiros personalizados baseados no seu público e estilo
    - **🎭 React:** Reações autênticas usando sua personalidade e experiências  
    - **🔥 Temas Quentes:** Análises conectadas aos seus interesses e objetivos
    - **🧬 Raio-X:** Copies adaptadas ao seu tom de voz e público-alvo
    
    **Quanto mais completo, melhores os resultados!**
    """)

# Função para compatibilidade
def render_cerebro_page():
    """Função de compatibilidade"""
    show_cerebro_page()

