"""
Página React - Geração de roteiros baseados em vídeos REAIS
Agora com processamento real usando yt-dlp e Whisper
"""
import streamlit as st
import os
import base64
import json
from datetime import datetime
import yt_dlp
import whisper


def get_cerebro_context():
    """Retorna o contexto do cérebro formatado para uso em prompts de IA"""
    cerebro_file = "data/cerebro.json"
    if os.path.exists(cerebro_file):
        with open(cerebro_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    else:
        data = {}
    
    if not data:
        return "Perfil não configurado. Use informações genéricas."
    
    context = f"""
CONTEXTO DO USUÁRIO (CÉREBRO):

=== INFORMAÇÕES PESSOAIS ===
Nome: {data.get('nome', 'Não informado')}
Profissão: {data.get('profissao', 'Não informado')}

=== NEGÓCIO/PROJETO ===
Área de Atuação: {data.get('area_atuacao', 'Não informado')}
Público-Alvo: {data.get('publico_alvo', 'Não informado')}

=== OBJETIVOS E METAS ===
Objetivos Principais: {data.get('objetivos', 'Não informado')}

=== CONTEÚDO E COMUNICAÇÃO ===
Tom de Voz: {data.get('tom_voz', 'Não informado')}
Temas de Interesse: {data.get('temas_interesse', 'Não informado')}
"""
    return context


def extract_video_metadata(url):
    """Extrai metadados reais do vídeo usando yt-dlp"""
    try:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            duration = info.get('duration', 0)
            duration_formatted = f"{duration // 60}:{duration % 60:02d}" if duration else "N/A"
            
            return {
                'platform': 'YouTube',
                'title': info.get('title', 'Título não disponível'),
                'duration': duration_formatted,
                'duration_seconds': duration,
                'author': info.get('uploader', 'Autor não disponível'),
                'description': info.get('description', ''),
                'view_count': info.get('view_count', 0),
                'url': url
            }
            
    except Exception as e:
        st.error(f"❌ Erro ao extrair metadados: {str(e)}")
        return None


def download_and_transcribe_video(url):
    """Baixa áudio e transcreve usando Whisper"""
    try:
        import tempfile
        import os
        
        # Criar diretório temporário
        temp_dir = tempfile.mkdtemp()
        audio_path = os.path.join(temp_dir, "audio.wav")
        
        # Configurar yt-dlp para baixar áudio
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': audio_path.replace('.wav', '.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'wav',
                'preferredquality': '192',
            }],
            'quiet': True,
            'no_warnings': True,
        }
        
        # Baixar áudio
        st.info("🎵 Baixando áudio do vídeo...")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        # Encontrar arquivo de áudio baixado
        audio_file = None
        for file in os.listdir(temp_dir):
            if file.endswith('.wav'):
                audio_file = os.path.join(temp_dir, file)
                break
        
        if not audio_file:
            st.error("❌ Não foi possível baixar o áudio")
            return None
        
        # Carregar modelo Whisper
        st.info("🎯 Carregando modelo Whisper...")
        model = whisper.load_model("base")
        
        # Transcrever áudio
        st.info("📝 Transcrevendo áudio...")
        result = model.transcribe(audio_file)
        
        # Limpar arquivos temporários
        try:
            import shutil
            shutil.rmtree(temp_dir)
        except:
            pass
        
        return result["text"].strip()
        
    except Exception as e:
        st.error(f"❌ Erro na transcrição: {str(e)}")
        return None


def generate_react_script_with_ai(video_data, transcription, description, style):
    """Gera roteiro React usando Claude"""
    import anthropic
    
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        st.error("❌ Chave da API Anthropic não configurada!")
        return None
    
    try:
        client = anthropic.Anthropic(api_key=api_key)
        
        # Selecionar segmento engajante (primeiras 100 palavras)
        words = transcription.split()
        segment = " ".join(words[:100]) if len(words) > 100 else transcription
        
        # Obter contexto do cérebro
        cerebro_context = get_cerebro_context()
        
        if style == "React Padrão":
            prompt = f"""
{cerebro_context}

VÍDEO PROCESSADO:
- Título: {video_data['title']}
- Autor: {video_data['author']}
- Duração: {video_data['duration']}
- Plataforma: {video_data['platform']}

TRANSCRIÇÃO COMPLETA:
{transcription}

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
- Título: {video_data['title']}
- Autor: {video_data['author']}
- Duração: {video_data['duration']}
- Plataforma: {video_data['platform']}

TRANSCRIÇÃO COMPLETA:
{transcription}

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
            'transcription': transcription,
            'segment_used': segment,
            'style': style
        }
        
    except Exception as e:
        st.error(f"❌ Erro ao gerar roteiro: {str(e)}")
        return None


def render_react_page():
    """Renderiza a página React com funcionalidade REAL"""
    
        ## === TÍTULO PRINCIPAL === ##
    with open("icons/theater-masks.svg", "rb") as f:
        svg_base64 = base64.b64encode(f.read()).decode()
    
    st.markdown(f""" 
        <div style="display: flex; align-items: center; gap: 18px; margin-bottom: 1.5rem;">
            <img src="data:image/svg+xml;base64,{svg_base64}" width="48" height="48" style="margin-top: 4px;" />
            <h2 style="margin: 0; font-size: 2.8rem; font-weight: 700;">React</h2>
        </div>
    """, unsafe_allow_html=True)    
 
    # Configuração do React
    st.subheader("⛭ Configuração do React")
    
    # Campo para URL do vídeo
    video_url = st.text_input(
        "**🔗 Link do vídeo:**",
        placeholder="https://www.youtube.com/watch?v=...",
        help="Cole aqui o link do YouTube"
    )
    
    # Campo para descrição (opcional)
    description = st.text_area(
        "**🗎 Descreva o vídeo e o tipo de abordagem desejada:**",
        placeholder="Ex: Quero criar um react sobre este vídeo, focando na minha experiência pessoal...",
        help="Opcional: Descreva como você quer abordar o conteúdo"
    )    
    
    col1, col2 = st.columns(2)
    
    with col1:
        react_style = st.radio(
            "*◉─ Escolha o estilo:*",
            ["React Padrão", "React Bate-Bola"],
            index=0,
            key="react_style"
        )
    
    with col2:
        if react_style == "React Padrão":
            st.info("""
            **React Padrão:**
            1. Trecho do vídeo (30-50s)
            2. Headline (3-10s)
            3. Conteúdo principal (15-30s)
            4. Posicionamento + CTA
            """)
        else:
            st.info("""
            **React Bate-Bola:**
            1. Headline (3-5s)
            2. Bate-bola: Trecho + Reação
            3. Posicionamento + CTA
            """)
    
    # Botão para gerar roteiro
    if st.button("Gerar Roteiro", type="primary"):
        if not video_url:
            st.error("❌ Por favor, insira o link do vídeo!")
            return
        
        # Verificar se o contexto do Cérebro existe
        cerebro_context = get_cerebro_context()
        if "Perfil não configurado" in cerebro_context:
            st.warning("⚠️ Configure seu perfil na tela **Cérebro** para obter roteiros mais personalizados!")
        
        # Processar vídeo e gerar roteiro
        with st.spinner("🎥 Processando vídeo real..."):
            try:
                # 1. Extrair metadados
                st.info("📋 Extraindo metadados do vídeo...")
                video_data = extract_video_metadata(video_url)
                
                if not video_data:
                    st.error("❌ Erro ao extrair metadados do vídeo")
                    return
                
                # Mostrar informações do vídeo
                st.success("✅ Metadados extraídos com sucesso!")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.write(f"**📱 Plataforma:** {video_data['platform']}")
                    st.write(f"**⏱️ Duração:** {video_data['duration']}")
                
                with col2:
                    st.write(f"**📝 Título:** {video_data['title'][:50]}...")
                    st.write(f"**👤 Autor:** {video_data['author']}")
                
                with col3:
                    st.write(f"**👀 Visualizações:** {video_data.get('view_count', 0):,}")
                
                # 2. Baixar e transcrever áudio
                transcription = download_and_transcribe_video(video_url)
                
                if not transcription:
                    st.error("❌ Erro ao transcrever o vídeo")
                    return
                
                st.success(f"✅ Transcrição concluída! {len(transcription.split())} palavras extraídas")
                
                # Mostrar prévia da transcrição
                with st.expander("📜 Prévia da transcrição"):
                    st.text_area("Transcrição completa:", value=transcription[:500] + "...", height=100, disabled=True)
                
                # 3. Gerar roteiro com IA
                st.info("🤖 Gerando roteiro personalizado com IA...")
                result = generate_react_script_with_ai(video_data, transcription, description, react_style)
                
                if result:
                    # Exibir resultado
                    display_react_result(result)
                else:
                    st.error("❌ Erro ao gerar roteiro com IA")
                    
            except Exception as e:
                st.error(f"❌ Erro inesperado: {str(e)}")


def display_react_result(result):
    """Exibe o resultado do processamento React"""
    
    st.success("✅ Roteiro React gerado com sucesso!")
    
    # Informações do vídeo processado
    st.subheader("🎬 Roteiro React Gerado")
    
    video_data = result['video_data']
    
    # Configuração usada
    st.markdown("⚙️ **Configuração usada:**")
    col1, col2 = st.columns(2)
    
    with col1:
        st.write(f"**🎭 Estilo:** {result['style']}")
    
    with col2:
        st.write(f"**📊 Palavras da transcrição:** {len(result['transcription'].split())}")
    
    # Roteiro gerado
    st.markdown("---")
    st.subheader("📝 Roteiro Gerado")
    
    # Campo editável para o roteiro
    roteiro_editado = st.text_area(
        "Roteiro (editável):",
        value=result['script'],
        height=400,
        key="roteiro_react_editado"
    )
    
    # Estatísticas do roteiro
    st.subheader("📊 Estatísticas do Roteiro")
    
    col1, col2, col3, col4 = st.columns(4)
    
    palavras = len(roteiro_editado.split())
    caracteres = len(roteiro_editado)
    tempo_leitura = max(1, palavras // 150)
    duracao_estimada = max(10, int(palavras * 0.5))
    
    with col1:
        st.metric("Palavras", palavras)
    
    with col2:
        st.metric("Caracteres", caracteres)
    
    with col3:
        st.metric("Tempo de Leitura", f"{tempo_leitura} min")
    
    with col4:
        st.metric("Duração Estimada", f"{duracao_estimada}s")
    
    # Segmento do vídeo usado
    if result.get('segment_used'):
        st.subheader("📄 Segmento do vídeo usado")
        st.text_area(
            "Trecho selecionado da transcrição:",
            value=result['segment_used'],
            height=100,
            disabled=True
        )
    
    # Transcrição completa (expansível)
    with st.expander("📜 Transcrição completa do vídeo"):
        st.text_area(
            "Transcrição completa:",
            value=result['transcription'],
            height=200,
            disabled=True
        )
    
    # Botões de ação
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.download_button(
            "⬇️ Baixar Roteiro",
            data=roteiro_editado,
            file_name=f"react_{result['style'].lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
            mime="text/plain"
        )
    
    with col2:
        if st.button("📋 Copiar"):
            st.code(roteiro_editado, language="text")
            st.info("📋 Roteiro exibido acima para cópia manual.")
    
    with col3:
        if st.button("🔄 Novo React"):
            st.rerun()


# Função principal para compatibilidade
def show_react_page():
    """Função principal da página React"""
    render_react_page()

