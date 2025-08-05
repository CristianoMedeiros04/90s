"""
Serviço de Web Crawler - FUNCIONALIDADE REAL
Vasculha sites completos, extrai conteúdo e transcreve vídeos
"""
import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import json
import re
from services.video_processing import get_video_transcription


class WebCrawler:
    """Classe para web crawling completo"""
    
    def __init__(self):
        """Inicializa o web crawler"""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.driver = None
        self.visited_urls = set()
        self.max_pages = 10  # Limite de páginas por site
        
    def _setup_selenium(self):
        """Configura o Selenium WebDriver"""
        if self.driver is None:
            try:
                chrome_options = Options()
                chrome_options.add_argument('--headless')
                chrome_options.add_argument('--no-sandbox')
                chrome_options.add_argument('--disable-dev-shm-usage')
                chrome_options.add_argument('--disable-gpu')
                chrome_options.add_argument('--window-size=1920,1080')
                
                self.driver = webdriver.Chrome(
                    service=webdriver.chrome.service.Service(ChromeDriverManager().install()),
                    options=chrome_options
                )
                return True
            except Exception as e:
                st.error(f"❌ Erro ao configurar Selenium: {str(e)}")
                return False
        return True
    
    def extract_page_content(self, url):
        """
        Extrai conteúdo de uma página específica
        
        Args:
            url: URL da página
            
        Returns:
            Dict com conteúdo extraído
        """
        try:
            # Tentar primeiro com requests
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extrair informações básicas
            title = soup.find('title')
            title = title.get_text().strip() if title else "Sem título"
            
            # Remover scripts e estilos
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()
            
            # Extrair texto principal
            content_selectors = [
                'article', 'main', '.content', '.post', '.entry',
                '.article-content', '.post-content', '.entry-content'
            ]
            
            main_content = ""
            for selector in content_selectors:
                content_elem = soup.select_one(selector)
                if content_elem:
                    main_content = content_elem.get_text(separator=' ', strip=True)
                    break
            
            # Se não encontrou conteúdo específico, pega o body
            if not main_content:
                body = soup.find('body')
                if body:
                    main_content = body.get_text(separator=' ', strip=True)
            
            # Extrair links internos
            internal_links = []
            base_domain = urlparse(url).netloc
            
            for link in soup.find_all('a', href=True):
                href = link['href']
                full_url = urljoin(url, href)
                
                # Verificar se é link interno
                if urlparse(full_url).netloc == base_domain:
                    link_text = link.get_text().strip()
                    if link_text and len(link_text) > 5:  # Links com texto significativo
                        internal_links.append({
                            'url': full_url,
                            'text': link_text[:100]
                        })
            
            # Extrair vídeos
            videos = self._extract_videos(soup, url)
            
            # Extrair imagens
            images = self._extract_images(soup, url)
            
            return {
                'url': url,
                'title': title,
                'content': main_content[:5000],  # Limitar tamanho
                'word_count': len(main_content.split()),
                'internal_links': internal_links[:20],  # Limitar links
                'videos': videos,
                'images': images[:10],  # Limitar imagens
                'status': 'success'
            }
            
        except Exception as e:
            return {
                'url': url,
                'title': 'Erro ao extrair',
                'content': '',
                'word_count': 0,
                'internal_links': [],
                'videos': [],
                'images': [],
                'status': 'error',
                'error': str(e)
            }
    
    def _extract_videos(self, soup, base_url):
        """Extrai vídeos da página"""
        videos = []
        
        # YouTube embeds
        youtube_iframes = soup.find_all('iframe', src=re.compile(r'youtube\.com|youtu\.be'))
        for iframe in youtube_iframes:
            src = iframe.get('src', '')
            if 'youtube.com/embed/' in src:
                video_id = src.split('/embed/')[-1].split('?')[0]
                videos.append({
                    'platform': 'YouTube',
                    'url': f"https://www.youtube.com/watch?v={video_id}",
                    'embed_url': src,
                    'title': iframe.get('title', 'Vídeo YouTube')
                })
        
        # Vídeos HTML5
        video_tags = soup.find_all('video')
        for video in video_tags:
            src = video.get('src')
            if src:
                videos.append({
                    'platform': 'HTML5',
                    'url': urljoin(base_url, src),
                    'title': video.get('title', 'Vídeo HTML5')
                })
        
        return videos
    
    def _extract_images(self, soup, base_url):
        """Extrai imagens da página"""
        images = []
        
        img_tags = soup.find_all('img')
        for img in img_tags:
            src = img.get('src')
            if src:
                full_url = urljoin(base_url, src)
                alt_text = img.get('alt', '')
                
                # Filtrar imagens muito pequenas ou de sistema
                if not any(skip in src.lower() for skip in ['icon', 'logo', 'avatar', 'thumb']):
                    images.append({
                        'url': full_url,
                        'alt': alt_text,
                        'title': img.get('title', '')
                    })
        
        return images
    
    def crawl_website_complete(self, start_url, max_pages=5):
        """
        Vasculha um site completo
        
        Args:
            start_url: URL inicial
            max_pages: Máximo de páginas para vasculhar
            
        Returns:
            Lista com dados de todas as páginas
        """
        st.info(f"🕷️ Iniciando crawling completo de: {start_url}")
        
        pages_data = []
        urls_to_visit = [start_url]
        visited = set()
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i, url in enumerate(urls_to_visit[:max_pages]):
            if url in visited:
                continue
                
            visited.add(url)
            
            # Atualizar progresso
            progress = (i + 1) / min(len(urls_to_visit), max_pages)
            progress_bar.progress(progress)
            status_text.text(f"Processando página {i+1}/{min(len(urls_to_visit), max_pages)}: {url[:60]}...")
            
            # Extrair conteúdo da página
            page_data = self.extract_page_content(url)
            pages_data.append(page_data)
            
            # Adicionar links internos à lista de URLs para visitar
            if page_data['status'] == 'success':
                for link in page_data['internal_links']:
                    if link['url'] not in visited and len(urls_to_visit) < max_pages * 2:
                        urls_to_visit.append(link['url'])
            
            # Delay para não sobrecarregar o servidor
            time.sleep(1)
        
        progress_bar.progress(1.0)
        status_text.text(f"✅ Crawling concluído! {len(pages_data)} páginas processadas.")
        
        return pages_data
    
    def analyze_videos_in_pages(self, pages_data):
        """
        Analisa e transcreve vídeos encontrados nas páginas
        
        Args:
            pages_data: Lista de dados das páginas
            
        Returns:
            Lista com transcrições dos vídeos
        """
        video_transcriptions = []
        
        st.info("🎥 Analisando vídeos encontrados...")
        
        for page in pages_data:
            if page['videos']:
                st.write(f"📹 Encontrados {len(page['videos'])} vídeos em: {page['title']}")
                
                for video in page['videos'][:2]:  # Limitar a 2 vídeos por página
                    if video['platform'] == 'YouTube':
                        try:
                            st.info(f"🎯 Transcrevendo: {video['title']}")
                            transcription = get_video_transcription(video['url'])
                            
                            if transcription:
                                video_transcriptions.append({
                                    'page_url': page['url'],
                                    'page_title': page['title'],
                                    'video_url': video['url'],
                                    'video_title': video['title'],
                                    'transcription': transcription,
                                    'word_count': len(transcription.split())
                                })
                                st.success(f"✅ Vídeo transcrito: {len(transcription.split())} palavras")
                            else:
                                st.warning(f"⚠️ Não foi possível transcrever: {video['title']}")
                                
                        except Exception as e:
                            st.error(f"❌ Erro ao transcrever vídeo: {str(e)}")
        
        return video_transcriptions
    
    def generate_comprehensive_report(self, pages_data, video_transcriptions):
        """
        Gera relatório abrangente do crawling
        
        Args:
            pages_data: Dados das páginas
            video_transcriptions: Transcrições dos vídeos
            
        Returns:
            Dict com relatório completo
        """
        # Estatísticas gerais
        total_pages = len(pages_data)
        successful_pages = len([p for p in pages_data if p['status'] == 'success'])
        total_words = sum(p['word_count'] for p in pages_data)
        total_videos = sum(len(p['videos']) for p in pages_data)
        total_images = sum(len(p['images']) for p in pages_data)
        
        # Páginas mais relevantes (por quantidade de conteúdo)
        top_pages = sorted(
            [p for p in pages_data if p['status'] == 'success'],
            key=lambda x: x['word_count'],
            reverse=True
        )[:5]
        
        # Consolidar todo o conteúdo textual
        all_content = []
        for page in pages_data:
            if page['status'] == 'success' and page['content']:
                all_content.append(f"PÁGINA: {page['title']}\nURL: {page['url']}\nCONTEÚDO: {page['content']}\n\n")
        
        # Adicionar transcrições de vídeos
        video_content = []
        for video in video_transcriptions:
            video_content.append(f"VÍDEO: {video['video_title']}\nURL: {video['video_url']}\nTRANSCRIÇÃO: {video['transcription']}\n\n")
        
        return {
            'statistics': {
                'total_pages': total_pages,
                'successful_pages': successful_pages,
                'total_words': total_words,
                'total_videos': total_videos,
                'total_images': total_images,
                'transcribed_videos': len(video_transcriptions)
            },
            'top_pages': top_pages,
            'all_content': '\n'.join(all_content),
            'video_content': '\n'.join(video_content),
            'pages_data': pages_data,
            'video_transcriptions': video_transcriptions
        }
    
    def cleanup(self):
        """Limpa recursos"""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass


# Instância global do crawler
web_crawler = WebCrawler()


def crawl_multiple_sites(urls, max_pages_per_site=3):
    """
    Vasculha múltiplos sites
    
    Args:
        urls: Lista de URLs
        max_pages_per_site: Máximo de páginas por site
        
    Returns:
        Dict com dados consolidados
    """
    all_pages_data = []
    all_video_transcriptions = []
    
    st.info(f"🌐 Iniciando crawling de {len(urls)} sites...")
    
    for i, url in enumerate(urls):
        st.subheader(f"🔍 Site {i+1}/{len(urls)}: {url}")
        
        try:
            # Crawl do site
            pages_data = web_crawler.crawl_website_complete(url, max_pages_per_site)
            all_pages_data.extend(pages_data)
            
            # Analisar vídeos
            video_transcriptions = web_crawler.analyze_videos_in_pages(pages_data)
            all_video_transcriptions.extend(video_transcriptions)
            
            st.success(f"✅ Site processado: {len(pages_data)} páginas, {len(video_transcriptions)} vídeos transcritos")
            
        except Exception as e:
            st.error(f"❌ Erro ao processar site {url}: {str(e)}")
    
    # Gerar relatório consolidado
    report = web_crawler.generate_comprehensive_report(all_pages_data, all_video_transcriptions)
    
    return report


def extract_single_page_deep(url):
    """
    Extração profunda de uma única página
    
    Args:
        url: URL da página
        
    Returns:
        Dict com dados completos da página
    """
    st.info(f"🔍 Análise profunda de: {url}")
    
    page_data = web_crawler.extract_page_content(url)
    
    if page_data['status'] == 'success':
        # Analisar vídeos se houver
        video_transcriptions = []
        if page_data['videos']:
            video_transcriptions = web_crawler.analyze_videos_in_pages([page_data])
        
        # Gerar relatório
        report = web_crawler.generate_comprehensive_report([page_data], video_transcriptions)
        
        return report
    else:
        return {
            'statistics': {'total_pages': 0, 'successful_pages': 0},
            'error': page_data.get('error', 'Erro desconhecido')
        }

