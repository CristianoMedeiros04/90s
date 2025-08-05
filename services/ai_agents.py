"""
Serviços de integração com IA (Claude 3.5 Sonnet)
"""
import os
import streamlit as st
import anthropic
import requests
from bs4 import BeautifulSoup
import uuid
from datetime import datetime
from utils.helpers import salvar_historico


# Inicialização do cliente Anthropic
def get_anthropic_client():
    """Retorna cliente Anthropic configurado"""
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            st.error("❌ Chave da API do Anthropic não encontrada. Configure no arquivo .env")
            return None
            
        return anthropic.Anthropic(api_key=api_key)
    except Exception as e:
        st.error(f"❌ Erro ao inicializar cliente Anthropic: {e}")
        return None


def gerar_roteiro_com_ia(perfil, instrucao_adicional="", formato="Automático"):
    """Gera um roteiro usando a API do Claude com base no perfil e instruções"""
    
    # Monta o contexto do usuário
    contexto_usuario = montar_contexto_perfil(perfil)
    
    # Monta as orientações baseadas no material fornecido
    orientacoes_gerais = """Você é uma IA especialista em estratégias de persuasão e copywriting, com expertise em construir e engajar audiências nas redes sociais por meio da criação de vídeos virais.

Utilize todas as informações fornecidas sobre o especialista, seu público, suas crenças e inimigos, e seu conhecimento técnico, como contexto para criar um roteiro altamente personalizado e eficaz.

O roteiro será para um vídeo a ser postado no Instagram Reels ou TikTok, com duração máxima de 1 minuto e 20 segundos (cerca de 80 segundos). Mantenha o roteiro conciso e dentro desse limite de tempo.

**Instruções de conteúdo e estilo:**
- Nos primeiros **3 segundos**, inclua um elemento extremamente chamativo e específico para prender a atenção imediatamente (um gatilho que libere dopamina na audiência).
- Use uma linguagem simples, **fácil** de entender e prática, para que qualquer pessoa do público alvo compreenda. Explique conceitos de forma acessível.
- Explore gatilhos de atenção como mistério, recompensa, popularidade, polêmica, identificação de crenças, etc., ao longo do roteiro.

**Estrutura do Roteiro (seguir exatamente esta ordem):**
1. **Headline (Chamada inicial):** Uma frase de impacto para abrir o vídeo, contendo gatilhos de atenção que façam o público querer continuar assistindo.
2. **Intensificador de Mistério:** Uma continuação que aprofunde o interesse ou mistério iniciado na headline, mantendo as pessoas curiosas sobre a solução ou ponto principal.
3. **Posicionamento Influente:** Uma breve apresentação que estabelece a autoridade/confiança do especialista. Exemplo: "Eu sou Dr. X, advogado trabalhista, e estou aqui para te ajudar a entender os seus direitos. Então já salva esse vídeo e me segue para mais dicas." (Incluindo um sutil CTA para seguir/salvar já nesse meio).
4. **Conteúdo Notável:** O corpo principal do vídeo. Entregue algo de muito valor e novo: pode ser uma dica, um método, uma revelação ou insight que gere identificação e faça a audiência pensar "uau, isso faz muito sentido!". Deve ser algo replicável ou que mostre o "por trás das cortinas" de um assunto complexo de forma simples.
5. **Chamado para Envolvimento (CTA final):** Uma conclusão com call-to-action para engajar o público. Por exemplo, pedir para compartilhar o vídeo, marcar alguém, ou comentar, ressaltando a importância ou benefício do que foi apresentado.

**Formatos de copy disponíveis:**"""
    
    # Adiciona informações sobre formatos baseado no material
    if formato != "Automático":
        orientacoes_gerais += f"\n\n**Formato solicitado: {formato}**\n"
        
        formatos_info = {
            "Lista útil": "Formato que entrega uma lista de dicas ou passos práticos que o espectador pode usar no dia a dia para resolver um problema ou atingir um desejo.",
            "Lista de reconhecimento": "Formato que lista comportamentos padrões que as pessoas já têm, criando conexão e conscientização para evitar problemas ou resolvê-los.",
            "Análise de popularidade": "Formato que relata algo que esteja acontecendo no momento, assuntos que estejam estourando de popularidade.",
            "Defesa de crença": "Formato que aponta uma opinião forte sobre determinada crença, fazendo com que as pessoas repensem ou argumentem, gerando engajamento.",
            "Substituição de crença": "Formato focado em mudar a visão das pessoas, com foco na solução e em como deveria ser.",
            "O que acontece quando": "Formato focado em um problema específico e suas causas e efeitos, trazendo reconhecimento das situações.",
            "História de sucesso": "Formato focado em prova social, casos de sucesso da carreira ou jornada de vida empacotados em storytelling interessante.",
            "Revelação Progressiva": "Formato que constrói tensão através de informações liberadas gradualmente, mantendo o espectador grudado até o final. Trabalha com o gatilho da curiosidade crescente. Estrutura: [Teaser inicial] → [Primeira pista] → [Posicionamento influente] → [Segunda revelação] → [Revelação final] → [CTA]",
            "Contradição Intencional": "Formato que inicia com uma afirmação aparentemente contraditória ou polêmica para quebrar padrões mentais. Gera engajamento através do choque inicial e curiosidade. Estrutura: [Contradição inicial] → [Posicionamento influente] → [Justificativa paradoxal] → [Explicação lógica] → [Nova perspectiva] → [CTA]",
            "Jornada de Transformação": "Formato que mostra uma evolução completa de um estado para outro, criando identificação através da vulnerabilidade inicial e inspiração através da superação. Estrutura: [Estado inicial problemático] → [Momento de virada] → [Processo de mudança] → [Posicionamento influente] → [Estado atual] → [CTA]",
            "Segredo de Bastidores": "Formato que revela informações 'exclusivas' ou processos internos que normalmente não são compartilhados. Trabalha com o gatilho da exclusividade e acesso privilegiado. Estrutura: [Posicionamento influente] → [Promessa de exclusividade] → [Revelação do bastidor] → [Consequências práticas] → [Aplicação pessoal] → [CTA]",
            "Falha e Aprendizado": "Formato focado em vulnerabilidade e lições extraídas de erros. Gera conexão emocional através da honestidade e oferece valor através das lições aprendidas. Estrutura: [Confissão do erro] → [Detalhamento da falha] → [Reflexão e aprendizado] → [Posicionamento influente] → [Valor para o público] → [CTA]",
            "Previsão e Validação": "Formato que estabelece autoridade através de previsões que se confirmaram ou insights antecipados. Trabalha com o gatilho da credibilidade e confiança. Estrutura: [Previsão passada] → [Confirmação atual] → [Posicionamento influente] → [Análise do acerto] → [Nova previsão] → [CTA]",
            "Dilema e Resolução": "Formato que apresenta um problema complexo com múltiplas perspectivas antes de oferecer uma solução clara. Trabalha com o gatilho da incerteza seguido de alívio. Estrutura: [Apresentação do dilema] → [Complicação do problema] → [Tensão máxima] → [Solução revelada] → [Posicionamento influente] → [Validação da solução] → [CTA]"
        }
        
        if formato in formatos_info:
            orientacoes_gerais += formatos_info[formato]
    
    # Adiciona instruções específicas se fornecidas
    if instrucao_adicional:
        orientacoes_gerais += f"\n\n**Instrução específica do usuário:** {instrucao_adicional}"
    
    orientacoes_gerais += """\n\nUse o formato que achar mais adequado ou uma combinação sutil deles, conforme o contexto fornecido. **Não mencione explicitamente cada etapa** (não diga "Headline:" no texto, simplesmente escreva o roteiro seguindo a estrutura). Mantenha um tom persuasivo, autêntico e engajador, como se fosse realmente o especialista falando.

Agora, elabore o roteiro completo seguindo essas diretrizes:"""
    
    # Monta a mensagem final
    mensagem_usuario = contexto_usuario + "\n\n" + orientacoes_gerais
    
    try:
        # Obtém cliente Anthropic
        client = get_anthropic_client()
        if not client:
            return None
            
        # Chama a API do Claude
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1500,
            temperature=0.7,
            messages=[
                {"role": "user", "content": mensagem_usuario}
            ]
        )
        
        return response.content[0].text
        
    except Exception as e:
        st.error(f"Erro na API do Claude: {str(e)}")
        return None


def generate_react_script(transcription, instrucoes, estilo_react):
    """Gera roteiro estilo React baseado na transcrição do vídeo"""
    
    if estilo_react == "React Padrão":
        prompt_estilo = """Você é um especialista em criação de vídeos estilo React para Reels e TikTok de até 90 segundos.

Baseando-se na transcrição abaixo, siga esta estrutura:

1. **Trecho do vídeo (30 a 50s)**: apenas mostrar, sem falas.
2. **Headline (3 a 10s)**: isca com gatilhos de atenção.
3. **Conteúdo principal (15 a 30s)**: desenvolve a headline com conteúdo útil e engajador.
4. **Posicionamento + CTA**: "Sou [nome], e ajudo você em... Compartilhe este vídeo se fez sentido pra você."

Crie um roteiro seguindo exatamente essa estrutura."""
    
    else:  # React Bate-Bola
        prompt_estilo = """Você é um criador profissional de vídeos React no estilo Bate-Bola para Reels e TikTok (até 90s).

Estrutura:

1. **Headline (3 a 5s)**: isca com gatilhos de atenção.
2. **Bate-bola**: Exiba o trecho e logo em seguida a reação. Exemplo:

Trecho: "O banco me adoeceu."  
Reação: "Vocês percebem que isso não é exagero?"

3. **Posicionamento + CTA**: "Sou [nome] e ajudo pessoas como você a entenderem isso. Compartilhe."

Crie um roteiro seguindo exatamente essa estrutura."""
    
    # Monta o prompt final
    prompt_final = f"""{prompt_estilo}

Transcrição do vídeo:
{transcription}

Instruções específicas do usuário:
{instrucoes}

Gere um roteiro completo e detalhado seguindo a estrutura do estilo {estilo_react}."""
    
    try:
        # Obtém cliente Anthropic
        client = get_anthropic_client()
        if not client:
            return None
            
        # Chama a API do Claude
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1200,
            temperature=0.7,
            messages=[
                {"role": "user", "content": prompt_final}
            ]
        )
        
        return response.content[0].text
        
    except Exception as e:
        st.error(f"Erro na API do Claude: {str(e)}")
        return None


def montar_contexto_perfil(perfil):
    """Monta o contexto do perfil do usuário para enviar à IA"""
    
    contexto = "**CONTEXTO DO ESPECIALISTA E SEU PÚBLICO:**\n\n"
    
    # Seção 1: Perfil do Especialista
    contexto += "**PERFIL DO ESPECIALISTA:**\n"
    if perfil.get("bio"):
        contexto += f"- Quem é: {perfil['bio']}\n"
    if perfil.get("formacao"):
        contexto += f"- Formação: {perfil['formacao']}\n"
    if perfil.get("desejos_conquistas"):
        contexto += f"- Conquistas: {perfil['desejos_conquistas']}\n"
    if perfil.get("dores_enfrentadas"):
        contexto += f"- Desafios enfrentados: {perfil['dores_enfrentadas']}\n"
    if perfil.get("qualidades"):
        contexto += f"- Qualidades: {perfil['qualidades']}\n"
    if perfil.get("defeitos"):
        contexto += f"- Pontos fracos: {perfil['defeitos']}\n"
    if perfil.get("tecnicas_realiza"):
        contexto += f"- Técnicas que realiza: {perfil['tecnicas_realiza']}\n"
    if perfil.get("tecnicas_nao_recomenda"):
        contexto += f"- Técnicas que NÃO recomenda: {perfil['tecnicas_nao_recomenda']}\n"
    if perfil.get("habitos_recomenda"):
        contexto += f"- Hábitos recomendados: {perfil['habitos_recomenda']}\n"
    if perfil.get("habitos_nao_recomenda"):
        contexto += f"- Hábitos NÃO recomendados: {perfil['habitos_nao_recomenda']}\n"
    
    # Seção 2: Público-Alvo
    contexto += "\n**PÚBLICO-ALVO:**\n"
    if perfil.get("demo_publico"):
        contexto += f"- Demografia: {perfil['demo_publico']}\n"
    if perfil.get("desejos_publico"):
        contexto += f"- Desejos: {perfil['desejos_publico']}\n"
    if perfil.get("dores_publico"):
        contexto += f"- Dores: {perfil['dores_publico']}\n"
    if perfil.get("qualidades_publico"):
        contexto += f"- Qualidades: {perfil['qualidades_publico']}\n"
    if perfil.get("defeitos_publico"):
        contexto += f"- Defeitos/Dificuldades: {perfil['defeitos_publico']}\n"
    if perfil.get("objecoes_publico"):
        contexto += f"- Objeções comuns: {perfil['objecoes_publico']}\n"
    if perfil.get("medos_publico"):
        contexto += f"- Medos: {perfil['medos_publico']}\n"
    if perfil.get("referencias_culturais"):
        contexto += f"- Referências culturais: {perfil['referencias_culturais']}\n"
    if perfil.get("pessoas_publico"):
        contexto += f"- Pessoas que admiram: {perfil['pessoas_publico']}\n"
    if perfil.get("produtos_publico"):
        contexto += f"- Produtos que consomem: {perfil['produtos_publico']}\n"
    
    # Seção 3: Crenças do Especialista
    contexto += "\n**CRENÇAS E VALORES DO ESPECIALISTA:**\n"
    if perfil.get("valores_inegociaveis"):
        contexto += f"- Valores inegociáveis: {perfil['valores_inegociaveis']}\n"
    if perfil.get("crencas_centrais"):
        contexto += f"- Crenças centrais: {perfil['crencas_centrais']}\n"
    if perfil.get("crencas_defende"):
        contexto += f"- Crenças que defende: {perfil['crencas_defende']}\n"
    if perfil.get("opiniao_impopular"):
        contexto += f"- Opinião controversa: {perfil['opiniao_impopular']}\n"
    if perfil.get("mitos_combatidos"):
        contexto += f"- Mitos que combate: {perfil['mitos_combatidos']}\n"
    
    # Seção 4: Inimigos
    contexto += "\n**'INIMIGOS' QUE COMBATE:**\n"
    if perfil.get("inimigo_principal"):
        contexto += f"- Inimigo principal: {perfil['inimigo_principal']}\n"
    if perfil.get("comportamentos_inimigos"):
        contexto += f"- Comportamentos prejudiciais do público: {perfil['comportamentos_inimigos']}\n"
    if perfil.get("inimigos_instituicoes"):
        contexto += f"- Instituições/pessoas adversárias: {perfil['inimigos_instituicoes']}\n"
    if perfil.get("praticas_criticadas"):
        contexto += f"- Práticas que critica: {perfil['praticas_criticadas']}\n"
    
    # Seção 5: Conhecimento técnico
    if perfil.get("conhecimento_extra"):
        contexto += f"\n**CONHECIMENTO TÉCNICO ADICIONAL:**\n{perfil['conhecimento_extra'][:5000]}\n"
    
    return contexto


def salvar_roteiro_no_historico(roteiro, titulo, instrucao, formato):
    """Salva o roteiro no histórico"""
    
    # Gera título automático se não fornecido
    if not titulo or not titulo.strip():
        # Tenta extrair uma headline do roteiro
        linhas = roteiro.split('\n')
        primeira_linha = next((linha.strip() for linha in linhas if linha.strip()), "")
        if primeira_linha and len(primeira_linha) < 100:
            titulo = primeira_linha[:50] + "..." if len(primeira_linha) > 50 else primeira_linha
        else:
            titulo = f"Roteiro {datetime.now().strftime('%d/%m/%Y %H:%M')}"
    
    # Cria o item do histórico
    novo_item = {
        "id": str(uuid.uuid4()),
        "titulo": titulo.strip(),
        "conteudo": roteiro,
        "instrucao": instrucao,
        "formato": formato,
        "data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "data_formatada": datetime.now().strftime("%d/%m/%Y às %H:%M")
    }
    
    # Adiciona ao histórico
    historico = st.session_state.get("historico", [])
    historico.append(novo_item)
    st.session_state["historico"] = historico
    
    # Salva em arquivo
    salvar_historico(historico)


def analisar_temas_quentes(links):
    """Analisa uma lista de links e gera relatório de insights"""
    
    insights = []
    erros = []
    
    # Processa cada link
    for i, url in enumerate(links, 1):
        try:
            st.write(f"🔍 Analisando link {i}/{len(links)}...")
            
            # Faz a requisição HTTP
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=15)
            
            if response.status_code != 200:
                erros.append(f"Link {i}: Erro HTTP {response.status_code}")
                continue
            
            # Extrai o conteúdo com BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove scripts e estilos
            for script in soup(["script", "style", "noscript", "nav", "footer", "header"]):
                script.extract()
            
            # Extrai título
            titulo = soup.title.string.strip() if soup.title else f"Artigo {i}"
            
            # Extrai texto principal
            texto = soup.get_text(separator=" ").strip()
            texto_limpo = " ".join(texto.split())  # Remove espaços extras
            
            if not texto_limpo or len(texto_limpo) < 100:
                erros.append(f"Link {i}: Conteúdo insuficiente ou não encontrado")
                continue
            
            # Limita o tamanho para não sobrecarregar a IA
            if len(texto_limpo) > 8000:
                texto_limpo = texto_limpo[:8000] + "..."
            
            # Analisa com IA
            insight = analisar_conteudo_com_ia(titulo, texto_limpo, i)
            
            if insight:
                insights.append(f"**{titulo}**\n{insight}")
            else:
                erros.append(f"Link {i}: Erro na análise por IA")
                
        except requests.exceptions.Timeout:
            erros.append(f"Link {i}: Timeout - site muito lento")
        except requests.exceptions.RequestException as e:
            erros.append(f"Link {i}: Erro de conexão - {str(e)[:50]}")
        except Exception as e:
            erros.append(f"Link {i}: Erro inesperado - {str(e)[:50]}")
    
    # Gera relatório consolidado
    if insights:
        relatorio_final = gerar_relatorio_consolidado(insights)
        
        # Adiciona erros se houver
        if erros:
            relatorio_final += "\n\n---\n**⚠️ Problemas encontrados:**\n"
            for erro in erros:
                relatorio_final += f"- {erro}\n"
        
        return relatorio_final
    else:
        return None


def analisar_conteudo_com_ia(titulo, texto, numero):
    """Analisa um conteúdo específico usando IA"""
    
    prompt = f"""Analise o seguinte artigo e extraia:

1. **Resumo:** Um breve resumo dos pontos principais (2-3 frases)
2. **Insights interessantes:** Dados, curiosidades ou informações que chamam atenção
3. **Potencial para vídeo:** Como este conteúdo poderia inspirar um vídeo curto e engajante

**Título:** {titulo}

**Conteúdo:**
{texto}

**Instruções:**
- Seja conciso e direto
- Foque no que é mais interessante e viral
- Pense em como transformar isso em conteúdo para redes sociais
- Use linguagem simples e acessível

**Resposta:**"""
    
    try:
        # Obtém cliente Anthropic
        client = get_anthropic_client()
        if not client:
            return None
            
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=800,
            temperature=0.6,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        return response.content[0].text
        
    except Exception as e:
        st.error(f"Erro na análise do conteúdo {numero}: {str(e)}")
        return None


def gerar_relatorio_consolidado(insights):
    """Gera um relatório consolidado com base nos insights individuais"""
    
    # Junta todos os insights
    conteudo_completo = "\n\n".join(insights)
    
    prompt = f"""Com base nas análises individuais dos artigos abaixo, crie um relatório consolidado que inclua:

1. **📈 Tendências Identificadas:** Quais temas ou padrões aparecem com frequência
2. **💡 Ideias de Vídeo:** 5-7 sugestões específicas de vídeos curtos baseados nos insights
3. **🎯 Oportunidades:** Ângulos únicos ou abordagens que podem gerar engajamento
4. **⚡ Urgência:** Temas que estão "quentes" agora e devem ser aproveitados rapidamente

**Análises dos artigos:**
{conteudo_completo}

**Instruções:**
- Seja estratégico e focado em resultados
- Priorize ideias que podem viralizar
- Use emojis para tornar mais visual
- Mantenha linguagem clara e acionável
- Limite cada seção a pontos essenciais

**Relatório Consolidado:**"""
    
    try:
        # Obtém cliente Anthropic
        client = get_anthropic_client()
        if not client:
            return "Erro: Cliente Anthropic não disponível."
            
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1200,
            temperature=0.7,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        return response.content[0].text
        
    except Exception as e:
        st.error(f"Erro na consolidação do relatório: {str(e)}")
        return "Erro ao gerar relatório consolidado."

