"""
Serviço de processamento de vídeos - FUNCIONALIDADE REAL
Extração de áudio e transcrição usando yt-dlp e whisper
"""
import os
import tempfile
import subprocess
import json
from typing import Dict, Optional, Tuple
import yt_dlp
import whisper
import streamlit as st


class VideoProcessor:
    """Classe para processamento real de vídeos"""
    
    def __init__(self):
        """Inicializa o processador de vídeo"""
        self.whisper_model = None
        self.temp_dir = tempfile.mkdtemp()
    
    def _load_whisper_model(self):
        """Carrega o modelo Whisper apenas quando necessário"""
        if self.whisper_model is None:
            try:
                self.whisper_model = whisper.load_model("base")
                st.info("🎯 Modelo Whisper carregado com sucesso")
            except Exception as e:
                st.error(f"❌ Erro ao carregar modelo Whisper: {str(e)}")
                return False
        return True
    
    def extract_video_metadata(self, url: str) -> Dict:
        """
        Extrai metadados reais do vídeo usando yt-dlp
        
        Args:
            url: URL do vídeo (YouTube, TikTok, Instagram)
            
        Returns:
            Dict com metadados do vídeo
        """
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                # Determina a plataforma
                platform = "YouTube"
                if "tiktok.com" in url:
                    platform = "TikTok"
                elif "instagram.com" in url:
                    platform = "Instagram"
                
                # Formata duração
                duration = info.get('duration', 0)
                duration_formatted = f"{duration // 60}:{duration % 60:02d}" if duration else "N/A"
                
                return {
                    'platform': platform,
                    'title': info.get('title', 'Título não disponível'),
                    'duration': duration_formatted,
                    'duration_seconds': duration,
                    'author': info.get('uploader', 'Autor não disponível'),
                    'description': info.get('description', ''),
                    'view_count': info.get('view_count', 0),
                    'upload_date': info.get('upload_date', ''),
                    'thumbnail': info.get('thumbnail', ''),
                    'url': url
                }
                
        except Exception as e:
            st.error(f"❌ Erro ao extrair metadados: {str(e)}")
            return {
                'platform': 'Desconhecida',
                'title': 'Erro ao extrair título',
                'duration': 'N/A',
                'duration_seconds': 0,
                'author': 'Erro ao extrair autor',
                'description': '',
                'view_count': 0,
                'upload_date': '',
                'thumbnail': '',
                'url': url,
                'error': str(e)
            }
    
    def download_audio(self, url: str) -> Optional[str]:
        """
        Baixa o áudio do vídeo usando yt-dlp
        
        Args:
            url: URL do vídeo
            
        Returns:
            Caminho para o arquivo de áudio baixado ou None se erro
        """
        try:
            audio_path = os.path.join(self.temp_dir, "audio.%(ext)s")
            
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': audio_path,
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'wav',
                    'preferredquality': '192',
                }],
                'quiet': True,
                'no_warnings': True,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            # Encontra o arquivo de áudio baixado
            for file in os.listdir(self.temp_dir):
                if file.startswith("audio") and file.endswith(".wav"):
                    return os.path.join(self.temp_dir, file)
            
            return None
            
        except Exception as e:
            st.error(f"❌ Erro ao baixar áudio: {str(e)}")
            return None
    
    def transcribe_audio(self, audio_path: str) -> Optional[str]:
        """
        Transcreve o áudio usando Whisper
        
        Args:
            audio_path: Caminho para o arquivo de áudio
            
        Returns:
            Texto transcrito ou None se erro
        """
        try:
            if not self._load_whisper_model():
                return None
            
            # Transcreve o áudio
            result = self.whisper_model.transcribe(audio_path)
            
            # Extrai o texto
            return result["text"].strip()
                
        except Exception as e:
            st.error(f"❌ Erro na transcrição: {str(e)}")
            return None
    
    def process_video_complete(self, url: str) -> Dict:
        """
        Processa completamente um vídeo: metadados + transcrição
        
        Args:
            url: URL do vídeo
            
        Returns:
            Dict com todas as informações processadas
        """
        st.info("🎥 Iniciando processamento do vídeo...")
        
        # 1. Extrair metadados
        st.info("📋 Extraindo metadados do vídeo...")
        metadata = self.extract_video_metadata(url)
        
        if 'error' in metadata:
            return metadata
        
        # 2. Baixar áudio
        st.info("🎵 Baixando áudio do vídeo...")
        audio_path = self.download_audio(url)
        
        if not audio_path:
            return {**metadata, 'transcription': None, 'error': 'Falha ao baixar áudio'}
        
        # 3. Transcrever áudio
        st.info("🎯 Transcrevendo áudio com Whisper...")
        transcription = self.transcribe_audio(audio_path)
        
        # 4. Limpar arquivos temporários
        try:
            if os.path.exists(audio_path):
                os.remove(audio_path)
        except:
            pass
        
        # 5. Retornar resultado completo
        result = {
            **metadata,
            'transcription': transcription,
            'transcription_success': transcription is not None,
            'word_count': len(transcription.split()) if transcription else 0
        }
        
        if transcription:
            st.success("✅ Vídeo processado com sucesso!")
        else:
            st.warning("⚠️ Metadados extraídos, mas falha na transcrição")
        
        return result
    
    def select_best_segment(self, transcription: str, target_words: int = 100) -> str:
        """
        Seleciona o melhor segmento da transcrição para o React
        
        Args:
            transcription: Texto completo da transcrição
            target_words: Número alvo de palavras para o segmento
            
        Returns:
            Segmento selecionado
        """
        if not transcription:
            return ""
        
        words = transcription.split()
        
        if len(words) <= target_words:
            return transcription
        
        # Procura por um segmento interessante no meio do vídeo
        # (evita introduções e finalizações)
        start_pos = len(words) // 4  # Começa após 25% do conteúdo
        end_pos = min(start_pos + target_words, len(words))
        
        # Tenta encontrar uma frase completa
        segment_words = words[start_pos:end_pos]
        segment_text = " ".join(segment_words)
        
        # Procura por ponto final para terminar em frase completa
        last_period = segment_text.rfind('.')
        if last_period > len(segment_text) * 0.7:  # Se o ponto está nos últimos 30%
            segment_text = segment_text[:last_period + 1]
        
        return segment_text.strip()
    
    def cleanup(self):
        """Limpa arquivos temporários"""
        try:
            import shutil
            if os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
        except:
            pass


# Instância global do processador
video_processor = VideoProcessor()


def process_video_url(url: str) -> Dict:
    """
    Função principal para processar URL de vídeo
    
    Args:
        url: URL do vídeo
        
    Returns:
        Dict com informações processadas
    """
    return video_processor.process_video_complete(url)


def extract_video_info_real(url: str) -> Dict:
    """
    Extrai apenas metadados do vídeo (mais rápido)
    
    Args:
        url: URL do vídeo
        
    Returns:
        Dict com metadados
    """
    return video_processor.extract_video_metadata(url)


def get_video_transcription(url: str) -> Optional[str]:
    """
    Obtém apenas a transcrição do vídeo
    
    Args:
        url: URL do vídeo
        
    Returns:
        Texto transcrito ou None
    """
    audio_path = video_processor.download_audio(url)
    if audio_path:
        transcription = video_processor.transcribe_audio(audio_path)
        # Limpar arquivo temporário
        try:
            os.remove(audio_path)
        except:
            pass
        return transcription
    return None


def select_engaging_segment(transcription: str, target_words: int = 100) -> str:
    """
    Seleciona segmento mais engajante da transcrição
    
    Args:
        transcription: Texto completo
        target_words: Número de palavras desejado
        
    Returns:
        Segmento selecionado
    """
    return video_processor.select_best_segment(transcription, target_words)

