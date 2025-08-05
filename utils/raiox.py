"""
Utilitários para a tela Raio-X - Engenharia de Copy Viral
Análise de vídeos de sucesso e geração de copies similares
"""
import os
import re
import subprocess
import tempfile
import whisper
import yt_dlp
from urllib.parse import urlparse
import streamlit as st
from modules.cerebro import get_cerebro_context
from services.ai_agents import gerar_roteiro_com_ia
import anthropic
from dotenv import load_dotenv

load_dotenv()

def detect_platform(url):
    """Detecta a plataforma do vídeo baseado na URL"""
    url_lower = url.lower()
    
    if 'youtube.com' in url_lower or 'youtu.be' in url_lower:
        return 'YouTube'
    elif 'tiktok.com' in url_lower:
        return 'TikTok'
    elif 'instagram.com' in url_lower:
        return 'Instagram'
    elif 'facebook.com' in url_lower or 'fb.watch' in url_lower:
        return 'Facebook'
    elif 'twitter.com' in url_lower or 'x.com' in url_lower:
        return 'Twitter'
    else:
        return 'Desconhecido'

def validate_video_url(url):
    """Valida se a URL é de um vídeo suportado"""
    if not url or not url.strip():
        return False, "URL não fornecida"
    
    # Regex patterns para diferentes plataformas
    patterns = {
        'YouTube': [
            r'(?:https?://)?(?:www\.)?youtube\.com/watch\?v=[\w-]+',
            r'(?:https?://)?(?:www\.)?youtu\.be/[\w-]+',
            r'(?:https?://)?(?:www\.)?youtube\.com/embed/[\w-]+',
            r'(?:https?://)?(?:www\.)?youtube\.com/shorts/[\w-]+'
        ],
        'TikTok': [
            r'(?:https?://)?(?:www\.)?tiktok\.com/@[\w.-]+/video/\d+',
            r'(?:https?://)?vm\.tiktok\.com/[\w-]+',
            r'(?:https?://)?(?:www\.)?tiktok\.com/t/[\w-]+'
        ],
        'Instagram': [
            r'(?:https?://)?(?:www\.)?instagram\.com/p/[\w-]+',
            r'(?:https?://)?(?:www\.)?instagram\.com/reel/[\w-]+',
            r'(?:https?://)?(?:www\.)?instagram\.com/tv/[\w-]+'
        ]
    }
    
    for platform, platform_patterns in patterns.items():
        for pattern in platform_patterns:
            if re.match(pattern, url.strip()):
                return True, platform
    
    return False, "URL não suportada ou formato inválido"

def extract_video_metadata(url):
    """Extrai metadados do vídeo usando yt-dlp"""
    try:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            metadata = {
                'title': info.get('title', 'Título não disponível'),
                'uploader': info.get('uploader', 'Autor não disponível'),
                'duration': info.get('duration', 0),
                'view_count': info.get('view_count', 0),
                'like_count': info.get('like_count', 0),
                'description': info.get('description', ''),
                'upload_date': info.get('upload_date', ''),
                'thumbnail': info.get('thumbnail', ''),
                'platform': detect_platform(url)
            }
            
            return metadata
            
    except Exception as e:
        st.error(f"Erro ao extrair metadados: {str(e)}")
        return None

def download_video_audio(url, output_path):
    """Baixa o áudio do vídeo usando yt-dlp"""
    try:
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': output_path,
            'extractaudio': True,
            'audioformat': 'mp3',
            'quiet': True,
            'no_warnings': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
            
        return True
        
    except Exception as e:
        st.error(f"Erro ao baixar áudio: {str(e)}")
        return False

def transcribe_audio(audio_path):
    """Transcreve o áudio usando OpenAI Whisper"""
    try:
        # Carrega o modelo Whisper
        model = whisper.load_model("base")
        
        # Transcreve o áudio
        result = model.transcribe(audio_path, language='pt')
        
        return result["text"]
        
    except Exception as e:
        st.error(f"Erro na transcrição: {str(e)}")
        return None

def analyze_copy_structure(transcription, video_metadata):
    """Analisa a estrutura do copy usando IA"""
    try:
        client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        
        prompt = f"""
Analise a transcrição abaixo de um vídeo que performou bem e identifique a estrutura do copy:

METADADOS DO VÍDEO:
- Título: {video_metadata.get('title', 'N/A')}
- Autor: {video_metadata.get('uploader', 'N/A')}
- Visualizações: {video_metadata.get('view_count', 0):,}
- Curtidas: {video_metadata.get('like_count', 0):,}
- Duração: {video_metadata.get('duration', 0)} segundos

TRANSCRIÇÃO:
"{transcription}"

Por favor, identifique e extraia:

1. ESTRUTURA DETECTADA:
   - Headline/Gancho inicial
   - Quebra de padrão/Problema
   - Desenvolvimento/Solução
   - Prova social/Credibilidade
   - Call-to-Action final

2. ELEMENTOS DE ENGAJAMENTO:
   - Gatilhos mentais utilizados
   - Palavras de impacto
   - Ritmo e pausas estratégicas
   - Técnicas de persuasão

3. PADRÃO DE COMUNICAÇÃO:
   - Tom de voz
   - Estilo de linguagem
   - Tipo de abordagem

Seja específico e detalhado na análise.
"""
        
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return response.content[0].text
        
    except Exception as e:
        st.error(f"Erro na análise da estrutura: {str(e)}")
        return None

def generate_similar_copy(structure_analysis, transcription, video_metadata):
    """Gera uma copy similar baseada na estrutura analisada"""
    try:
        client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        
        # Obtém contexto do usuário
        user_context = get_cerebro_context()
        
        prompt = f"""
Com base na análise estrutural abaixo, crie uma nova copy seguindo o mesmo padrão de engajamento, mas adaptada ao contexto do usuário:

{user_context}

ANÁLISE ESTRUTURAL DO VÍDEO ORIGINAL:
{structure_analysis}

TRANSCRIÇÃO ORIGINAL (para referência):
"{transcription}"

INSTRUÇÕES:
1. Mantenha a MESMA ESTRUTURA de engajamento do vídeo original
2. Adapte o CONTEÚDO ao nicho e público do usuário
3. Use o TOM DE VOZ preferido do usuário
4. Inclua elementos da EXPERIÊNCIA e HISTÓRIAS do usuário
5. Mantenha a duração similar (máximo 90 segundos de fala)
6. Foque nos OBJETIVOS e DESAFIOS do usuário

FORMATO DA RESPOSTA:
🧠 ESTRUTURA DETECTADA:
[Resuma a estrutura identificada]

✍️ NOVA COPY INSPIRADA:
[Copy completa adaptada ao usuário]

📊 ELEMENTOS ADAPTADOS:
[Liste as principais adaptações feitas]

⏱️ DURAÇÃO ESTIMADA: [X] segundos
📝 PALAVRAS: [X] palavras
"""
        
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=3000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return response.content[0].text
        
    except Exception as e:
        st.error(f"Erro na geração da copy: {str(e)}")
        return None

def process_video_complete(url, progress_callback=None):
    """Processa o vídeo completo: download, transcrição e análise"""
    
    # Validação da URL
    if progress_callback:
        progress_callback("🔍 Validando URL...")
    
    is_valid, platform_or_error = validate_video_url(url)
    if not is_valid:
        return None, f"Erro: {platform_or_error}"
    
    # Extração de metadados
    if progress_callback:
        progress_callback("📋 Extraindo metadados...")
    
    metadata = extract_video_metadata(url)
    if not metadata:
        return None, "Erro ao extrair metadados do vídeo"
    
    # Criação de diretório temporário
    temp_dir = tempfile.mkdtemp()
    audio_path = os.path.join(temp_dir, "temp_audio.mp3")
    
    try:
        # Download do áudio
        if progress_callback:
            progress_callback("🔄 Baixando áudio do vídeo...")
        
        if not download_video_audio(url, audio_path):
            return None, "Erro ao baixar áudio do vídeo"
        
        # Transcrição
        if progress_callback:
            progress_callback("🧠 Transcrevendo áudio...")
        
        transcription = transcribe_audio(audio_path)
        if not transcription:
            return None, "Erro na transcrição do áudio"
        
        # Análise da estrutura
        if progress_callback:
            progress_callback("📊 Analisando estrutura do copy...")
        
        structure_analysis = analyze_copy_structure(transcription, metadata)
        if not structure_analysis:
            return None, "Erro na análise da estrutura"
        
        # Geração da nova copy
        if progress_callback:
            progress_callback("✍️ Gerando nova copy personalizada...")
        
        new_copy = generate_similar_copy(structure_analysis, transcription, metadata)
        if not new_copy:
            return None, "Erro na geração da nova copy"
        
        # Resultado final
        result = {
            'metadata': metadata,
            'transcription': transcription,
            'structure_analysis': structure_analysis,
            'new_copy': new_copy,
            'platform': platform_or_error
        }
        
        if progress_callback:
            progress_callback("✅ Processamento concluído!")
        
        return result, None
        
    except Exception as e:
        return None, f"Erro no processamento: {str(e)}"
    
    finally:
        # Limpeza dos arquivos temporários
        try:
            if os.path.exists(audio_path):
                os.remove(audio_path)
            os.rmdir(temp_dir)
        except:
            pass

def format_duration(seconds):
    """Formata duração em segundos para formato legível"""
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        minutes = seconds // 60
        remaining_seconds = seconds % 60
        return f"{minutes}m {remaining_seconds}s"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours}h {minutes}m"

def create_download_content(copy_text, video_metadata):
    """Cria conteúdo formatado para download"""
    content = f"""
COPY GERADA PELO RAIO-X
========================

VÍDEO ORIGINAL:
- Título: {video_metadata.get('title', 'N/A')}
- Autor: {video_metadata.get('uploader', 'N/A')}
- Plataforma: {video_metadata.get('platform', 'N/A')}
- Visualizações: {video_metadata.get('view_count', 0):,}
- Duração: {format_duration(video_metadata.get('duration', 0))}

COPY ADAPTADA:
==============

{copy_text}

========================
Gerado em: {os.path.basename(__file__)} - Raio-X
Data: {__import__('datetime').datetime.now().strftime('%d/%m/%Y %H:%M')}
"""
    return content

