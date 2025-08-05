"""
Tela Cérebro - Formulário de Perfil Central (37 campos)
Este é o formulário original que estava em Reels e TikTok
"""
import streamlit as st
import base64
from datetime import datetime
from utils.helpers import (
    carregar_perfil, salvar_perfil, calcular_completude_perfil, extrair_texto_arquivo
)

st.markdown("""
<style>
/* Placeholder com cor clara e fonte pequena */
::placeholder {
    color: #7a7f86 !important;       /* tom mais claro ainda */
    font-size: 0.85rem !important;   /* fonte menor */
    opacity: 0.5 !important;         /* mais translúcido */
}

/* Especificamente para áreas de texto */
textarea::placeholder {
    color: #7a7f86 !important;
    font-size: 0.85rem !important;
    opacity: 0.5 !important;
}

/* Compatibilidade com todos os navegadores */
input::placeholder,
textarea::placeholder {
    color: #7a7f86 !important;
    font-size: 0.85rem !important;
    opacity: 0.5 !important;
}
</style>
""", unsafe_allow_html=True)


def show_cerebro_page():
    """Renderiza a tela Cérebro - Formulário de Perfil Central"""

    ## === TÍTULO PRINCIPAL === ##
    with open("icons/brain-circuit.svg", "rb") as f:
        svg_base64 = base64.b64encode(f.read()).decode()
    
    st.markdown(f""" 
        <div style="display: flex; align-items: center; gap: 18px; margin-bottom: 1.5rem;">
            <img src="data:image/svg+xml;base64,{svg_base64}" width="48" height="48" style="margin-top: 4px;" />
            <h2 style="margin: 0; font-size: 2.8rem; font-weight: 700;;">Cérebro</h2>
        </div>
    """, unsafe_allow_html=True)

    # Carrega perfil existente se houver
    perfil_atual = carregar_perfil()

    # Calcula completude
    completude = calcular_completude_perfil(perfil_atual)

    # Barra de progresso personalizada com percentual ao lado
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

    # Feedback textual com base na completude
    if completude < 20:
        st.markdown("❌ Perfil muito incompleto. Preencha pelo menos 20% para gerar roteiros personalizados.")
    elif completude < 50:
        st.markdown("⚠️ Perfil parcialmente completo. Preencha mais campos para melhores resultados.")
    elif completude < 80:
        st.markdown("ℹ️ Bom progresso! Continue preenchendo para roteiros ainda mais personalizados.")
    else:
        st.markdown("✅ Perfil muito completo! Você terá roteiros altamente personalizados.")
    
    # Formulário principal
    with st.form("form_perfil"):
        st.markdown("### Formulário de Perfil")
        st.caption("Preencha o formulário com o máximo de informações para criar roteiros realmente personalizados")
        
        # Seção 1: Quem é você?
        with st.expander("**◉ Seção 1: Quem é você?**", expanded=True):      
            
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
        with st.expander("**◉ Seção 2: Seu público-alvo**"):            
            
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
        with st.expander("**◉ Seção 3: Suas crenças e valores**"):           
            
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
        with st.expander("**◉ Seção 4: Seus 'inimigos' (o que você combate)**"):           
            
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
        with st.expander("**◉ Seção 5: Suas fontes de conhecimento**"):            
            
            arquivos = st.file_uploader(
                "Envie documentos de texto com suas fontes de conhecimento (DOCX ou TXT)",
                type=['docx', 'txt'],
                accept_multiple_files=True,
                help="Máximo 5 arquivos. Estes documentos serão usados para enriquecer o contexto dos roteiros."
            )
            
            conhecimento_extra = ""
            if arquivos:
                if len(arquivos) > 5:
                    st.markdown("⚠️ Máximo 5 arquivos permitidos. Apenas os primeiros 5 serão processados.")
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
        if st.form_submit_button("Salvar Perfil", type="primary"): 
            # Monta o perfil completo com todos os 37 campos
            perfil_completo = {
                # Seção 1: Quem é você? (10 campos)
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
                
                # Seção 2: Seu público-alvo (10 campos)
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
                
                # Seção 3: Suas crenças (5 campos)
                "valores_inegociaveis": valores_inegociaveis,
                "crencas_centrais": crencas_centrais,
                "crencas_defende": crencas_defende,
                "opiniao_impopular": opiniao_impopular,
                "mitos_combatidos": mitos_combatidos,
                
                # Seção 4: Seus inimigos (4 campos)
                "inimigo_principal": inimigo_principal,
                "comportamentos_inimigos": comportamentos_inimigos,
                "inimigos_instituicoes": inimigos_instituicoes,
                "praticas_criticadas": praticas_criticadas,
                
                # Seção 5: Fontes de conhecimento (1 campo)
                "conhecimento_extra": conhecimento_extra,
                
                # Metadados
                "data_atualizacao": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # Salva o perfil
            salvar_perfil(perfil_completo)
            st.session_state["perfil"] = perfil_completo
            
            # Mostra completude atualizada
            nova_completude = calcular_completude_perfil(perfil_completo)
            st.success(f"✅ Perfil salvo com sucesso! Completude: {nova_completude}%")
            
            if nova_completude >= 20:
                st.info("🎉 Agora você pode gerar roteiros personalizados nas outras telas!")
            
            st.rerun()    
   

# Função para compatibilidade
def render_cerebro_page():
    """Função de compatibilidade"""
    show_cerebro_page()

def get_cerebro_context():
    """Retorna o contexto do perfil do Cérebro para uso em outras páginas"""
    perfil = carregar_perfil()
    
    if not perfil:
        return "Perfil não cadastrado. Complete o formulário na tela Cérebro."
    
    # Monta contexto detalhado baseado no perfil
    contexto = f"""
PERFIL DO USUÁRIO (CÉREBRO):

=== QUEM É VOCÊ ===
Bio: {perfil.get('bio', 'Não informado')}
Formação: {perfil.get('formacao', 'Não informado')}
Qualidades: {perfil.get('qualidades', 'Não informado')}
Defeitos: {perfil.get('defeitos', 'Não informado')}
Desejos/Conquistas: {perfil.get('desejos_conquistas', 'Não informado')}
Dores Enfrentadas: {perfil.get('dores_enfrentadas', 'Não informado')}

=== SEU PÚBLICO-ALVO ===
Demografia: {perfil.get('demo_publico', 'Não informado')}
Desejos do Público: {perfil.get('desejos_publico', 'Não informado')}
Dores do Público: {perfil.get('dores_publico', 'Não informado')}
Qualidades do Público: {perfil.get('qualidades_publico', 'Não informado')}
Defeitos do Público: {perfil.get('defeitos_publico', 'Não informado')}
Objeções: {perfil.get('objecoes_publico', 'Não informado')}
Medos: {perfil.get('medos_publico', 'Não informado')}

=== SUAS CRENÇAS ===
Valores Inegociáveis: {perfil.get('valores_inegociaveis', 'Não informado')}
Crenças Centrais: {perfil.get('crencas_centrais', 'Não informado')}
Crenças que Defende: {perfil.get('crencas_defende', 'Não informado')}
Opinião Controversa: {perfil.get('opiniao_impopular', 'Não informado')}
Mitos que Combate: {perfil.get('mitos_combatidos', 'Não informado')}

=== SEUS INIMIGOS ===
Inimigo Principal: {perfil.get('inimigo_principal', 'Não informado')}
Comportamentos Prejudiciais: {perfil.get('comportamentos_inimigos', 'Não informado')}
Instituições Criticadas: {perfil.get('inimigos_instituicoes', 'Não informado')}
Práticas Criticadas: {perfil.get('praticas_criticadas', 'Não informado')}

=== TÉCNICAS E HÁBITOS ===
Técnicas que Realiza: {perfil.get('tecnicas_realiza', 'Não informado')}
Técnicas que NÃO Recomenda: {perfil.get('tecnicas_nao_recomenda', 'Não informado')}
Hábitos que Recomenda: {perfil.get('habitos_recomenda', 'Não informado')}
Hábitos que NÃO Recomenda: {perfil.get('habitos_nao_recomenda', 'Não informado')}

=== CONHECIMENTO EXTRA ===
{perfil.get('conhecimento_extra', 'Nenhum documento adicional fornecido')}

=== REFERÊNCIAS CULTURAIS ===
{perfil.get('referencias_culturais', 'Não informado')}

=== PESSOAS QUE O PÚBLICO ADMIRA ===
{perfil.get('pessoas_publico', 'Não informado')}

=== PRODUTOS QUE O PÚBLICO CONSOME ===
{perfil.get('produtos_publico', 'Não informado')}
"""
    
    return contexto.strip()

def load_cerebro_data():
    """Carrega dados do Cérebro (alias para carregar_perfil)"""
    return carregar_perfil()

