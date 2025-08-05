"""
Serviços de integração com IA - Claude 3.5 Sonnet
Agora com contexto do Cérebro e processamento real de vídeos
"""
import os
import anthropic
import streamlit as st
from modules.cerebro import get_cerebro_context
from services.video_processing import process_video_url, select_engaging_segment


def get_anthropic_client():
    """Retorna cliente Anthropic configurado"""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        st.error("❌ Chave da API Anthropic não configurada!")
        return None
    
    return anthropic.Anthropic(api_key=api_key)


def generate_script_with_context(formato, instrucao="", perfil_data=None):
    """
    Gera roteiro usando contexto do Cérebro
    
    Args:
        formato: Formato do roteiro
        instrucao: Instruções específicas do usuário
        perfil_data: Dados do perfil (opcional, usa Cérebro se não fornecido)
    """
    client = get_anthropic_client()
    if not client:
        return None
    
    try:
        # Obtém contexto do Cérebro
        cerebro_context = get_cerebro_context()
        
        # Prompt personalizado com contexto
        prompt = f"""
{cerebro_context}

TAREFA: Gerar roteiro para vídeo curto ({formato})

INSTRUÇÕES ESPECÍFICAS: {instrucao if instrucao else "Use as informações do perfil para criar conteúdo relevante"}

FORMATO: {formato}

DIRETRIZES:
1. Use o tom de voz e estilo de comunicação do perfil
2. Aborde temas de interesse do usuário
3. Fale diretamente com o público-alvo definido
4. Inclua elementos dos diferenciais e experiências
5. Mantenha duração entre 60-90 segundos
6. Use linguagem adequada às plataformas definidas

Gere um roteiro completo e personalizado:
"""
        
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return response.content[0].text
        
    except Exception as e:
        st.error(f"❌ Erro na API do Claude: {str(e)}")
        return None


def generate_react_script_real(video_url, description, style, perfil_data=None):
    """
    Gera roteiro React usando processamento REAL de vídeo
    
    Args:
        video_url: URL do vídeo
        description: Descrição/instruções do usuário
        style: Estilo do React (Padrão ou Bate-Bola)
        perfil_data: Dados do perfil
    """
    client = get_anthropic_client()
    if not client:
        return None
    
    try:
        # 1. PROCESSAR VÍDEO REAL
        st.info("🎥 Processando vídeo real...")
        video_data = process_video_url(video_url)
        
        if 'error' in video_data:
            st.error(f"❌ Erro no processamento: {video_data['error']}")
            return None
        
        # 2. VERIFICAR SE TRANSCRIÇÃO FOI OBTIDA
        if not video_data.get('transcription'):
            st.error("❌ Não foi possível obter transcrição do vídeo")
            return None
        
        # 3. SELECIONAR SEGMENTO ENGAJANTE
        segment = select_engaging_segment(video_data['transcription'], target_words=100)
        
        # 4. OBTER CONTEXTO DO CÉREBRO
        cerebro_context = get_cerebro_context()
        
        # 5. GERAR ROTEIRO COM IA
        if style == "React Padrão":
            prompt = f"""
{cerebro_context}

VÍDEO PROCESSADO:
- Plataforma: {video_data['platform']}
- Título: {video_data['title']}
- Autor: {video_data['author']}
- Duração: {video_data['duration']}

TRANSCRIÇÃO COMPLETA:
{video_data['transcription']}

SEGMENTO SELECIONADO PARA REACT:
{segment}

INSTRUÇÕES DO USUÁRIO: {description}

TAREFA: Criar roteiro React Padrão personalizado

ESTRUTURA OBRIGATÓRIA:
1. TRECHO DO VÍDEO (30-50s) - Use o segmento selecionado
2. HEADLINE (3-10s) - Crie headline impactante baseada no conteúdo
3. CONTEÚDO PRINCIPAL (15-30s) - Sua reação/análise personalizada
4. POSICIONAMENTO + CTA (10-20s) - Use informações do seu perfil

DIRETRIZES:
- Use seu tom de voz e estilo de comunicação
- Conecte com seu público-alvo
- Inclua seus diferenciais e experiências
- Mantenha autenticidade e relevância
- Duração total: 60-90 segundos

Gere o roteiro completo:
"""
        else:  # React Bate-Bola
            prompt = f"""
{cerebro_context}

VÍDEO PROCESSADO:
- Plataforma: {video_data['platform']}
- Título: {video_data['title']}
- Autor: {video_data['author']}
- Duração: {video_data['duration']}

TRANSCRIÇÃO COMPLETA:
{video_data['transcription']}

SEGMENTO SELECIONADO PARA REACT:
{segment}

INSTRUÇÕES DO USUÁRIO: {description}

TAREFA: Criar roteiro React Bate-Bola personalizado

ESTRUTURA OBRIGATÓRIA:
1. HEADLINE (3-5s) - Headline chamativa
2. BATE-BOLA (60-70s):
   - Trecho do vídeo
   - SUA REAÇÃO imediata
   - Trecho do vídeo
   - SUA REAÇÃO
   - Continue alternando
3. POSICIONAMENTO + CTA (10-15s)

DIRETRIZES:
- Reações autênticas e espontâneas
- Use seu tom de voz natural
- Conecte com experiências pessoais
- Mantenha energia alta
- Duração total: 75-90 segundos

Gere o roteiro completo:
"""
        
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return {
            'script': response.content[0].text,
            'video_data': video_data,
            'segment_used': segment,
            'style': style
        }
        
    except Exception as e:
        st.error(f"❌ Erro ao gerar roteiro React: {str(e)}")
        return None


def analisar_conteudo_com_ia(conteudo, url=""):
    """
    Analisa conteúdo web usando contexto do Cérebro
    
    Args:
        conteudo: Conteúdo extraído da web
        url: URL original
    """
    client = get_anthropic_client()
    if not client:
        return None
    
    try:
        cerebro_context = get_cerebro_context()
        
        prompt = f"""
{cerebro_context}

CONTEÚDO PARA ANÁLISE:
URL: {url}
CONTEÚDO: {conteudo[:3000]}...

TAREFA: Analisar este conteúdo considerando meu perfil e objetivos

ANÁLISE SOLICITADA:
1. RELEVÂNCIA: Como este conteúdo se relaciona com minha área de atuação?
2. OPORTUNIDADES: Que oportunidades de conteúdo posso extrair?
3. INSIGHTS: Quais insights são valiosos para meu público?
4. TENDÊNCIAS: Que tendências posso identificar?
5. APLICAÇÃO: Como posso aplicar isso em meus conteúdos?

FORMATO DE RESPOSTA:
- Seja específico e prático
- Conecte com meus objetivos
- Sugira ações concretas
- Use linguagem do meu perfil

Faça a análise completa:
"""
        
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1500,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return response.content[0].text
        
    except Exception as e:
        st.error(f"❌ Erro na análise: {str(e)}")
        return None


def gerar_relatorio_consolidado(analises):
    """
    Gera relatório consolidado usando contexto do Cérebro
    
    Args:
        analises: Lista de análises individuais
    """
    client = get_anthropic_client()
    if not client:
        return None
    
    try:
        cerebro_context = get_cerebro_context()
        
        analises_texto = "\n\n".join([
            f"ANÁLISE {i+1}:\n{analise}" 
            for i, analise in enumerate(analises)
        ])
        
        prompt = f"""
{cerebro_context}

ANÁLISES INDIVIDUAIS:
{analises_texto}

TAREFA: Criar relatório consolidado personalizado

ESTRUTURA DO RELATÓRIO:
1. RESUMO EXECUTIVO
2. PRINCIPAIS TENDÊNCIAS IDENTIFICADAS
3. OPORTUNIDADES DE CONTEÚDO
4. RECOMENDAÇÕES ESTRATÉGICAS
5. PRÓXIMOS PASSOS

DIRETRIZES:
- Conecte tudo com meus objetivos
- Seja prático e acionável
- Use meu tom de voz
- Foque no meu público-alvo
- Inclua métricas quando possível

Gere o relatório completo:
"""
        
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=2500,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return response.content[0].text
        
    except Exception as e:
        st.error(f"❌ Erro no relatório: {str(e)}")
        return None

