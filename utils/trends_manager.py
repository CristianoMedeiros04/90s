"""
Gerenciador de Tendências - Sistema de Cache e Fallback
Otimizado para performance e experiência do usuário
"""
import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging
from pathlib import Path

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TrendsManager:
    def __init__(self, data_dir: str = "data/tendencias"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.cache_duration = 24  # horas
    
    def get_cache_file(self, platform: str) -> Path:
        """Retorna o caminho do arquivo de cache para a plataforma"""
        today = datetime.now().strftime('%Y-%m-%d')
        return self.data_dir / f"{platform}_{today}.json"
    
    def is_cache_valid(self, platform: str) -> bool:
        """Verifica se o cache é válido (menos de 24h)"""
        cache_file = self.get_cache_file(platform)
        
        if not cache_file.exists():
            return False
        
        # Verifica idade do arquivo
        file_time = datetime.fromtimestamp(cache_file.stat().st_mtime)
        age_hours = (datetime.now() - file_time).total_seconds() / 3600
        
        return age_hours < self.cache_duration
    
    def save_trends(self, platform: str, trends: List[Dict]) -> bool:
        """Salva tendências no cache"""
        try:
            cache_file = self.get_cache_file(platform)
            
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'platform': platform,
                    'timestamp': datetime.now().isoformat(),
                    'trends': trends
                }, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Cache salvo para {platform}: {len(trends)} tendências")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao salvar cache para {platform}: {e}")
            return False
    
    def load_trends(self, platform: str) -> List[Dict]:
        """Carrega tendências do cache"""
        try:
            cache_file = self.get_cache_file(platform)
            
            if not cache_file.exists():
                return []
            
            with open(cache_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('trends', [])
                
        except Exception as e:
            logger.error(f"Erro ao carregar cache para {platform}: {e}")
            return []
    
    def get_fallback_content(self) -> Dict[str, List[Dict]]:
        """Retorna conteúdo de fallback estético"""
        return {
            'inspiracao': [
                {
                    'titulo': '💡 Dica de Copywriting',
                    'descricao': 'Use números específicos em suas headlines para aumentar credibilidade',
                    'categoria': 'copywriting',
                    'icon': '✍️'
                },
                {
                    'titulo': '🎯 Estratégia de Engajamento',
                    'descricao': 'Faça perguntas diretas nos primeiros 3 segundos do vídeo',
                    'categoria': 'engajamento',
                    'icon': '🎬'
                },
                {
                    'titulo': '📈 Insight de Algoritmo',
                    'descricao': 'Vídeos de 15-30 segundos têm 25% mais alcance no TikTok',
                    'categoria': 'algoritmo',
                    'icon': '📊'
                },
                {
                    'titulo': '✨ Frase Motivacional',
                    'descricao': '"O conteúdo é rei, mas o contexto é reino" - Gary Vaynerchuk',
                    'categoria': 'motivacao',
                    'icon': '👑'
                },
                {
                    'titulo': '🔥 Técnica Viral',
                    'descricao': 'Use o padrão "Problema → Agitação → Solução" em seus roteiros',
                    'categoria': 'viral',
                    'icon': '🚀'
                },
                {
                    'titulo': '🎨 Design de Conteúdo',
                    'descricao': 'Cores contrastantes aumentam a retenção visual em 40%',
                    'categoria': 'design',
                    'icon': '🎨'
                },
                {
                    'titulo': '📱 Tendência Mobile',
                    'descricao': 'Formato vertical é 9x mais eficaz que horizontal em redes sociais',
                    'categoria': 'mobile',
                    'icon': '📱'
                },
                {
                    'titulo': '🧠 Psicologia do Viewer',
                    'descricao': 'Primeiros 3 segundos determinam 80% da retenção do vídeo',
                    'categoria': 'psicologia',
                    'icon': '🧠'
                }
            ]
        }
    
    def collect_all_trends(self) -> Dict[str, List[Dict]]:
        """Coleta tendências de todas as plataformas com fallback inteligente"""
        import sys
        import os
        
        # Adiciona o diretório raiz ao path
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        sys.path.append(root_dir)
        
        try:
            from collectors.crawler_twitter import TwitterCrawler
            from collectors.crawler_tiktok import TikTokCrawler
            from collectors.crawler_youtube import YouTubeCrawler
            from collectors.crawler_instagram import InstagramCrawler
        except ImportError as e:
            logger.error(f"Erro ao importar crawlers: {e}")
            # Retorna fallback se não conseguir importar
            return {
                'fallback_active': True,
                **self.get_fallback_content()
            }
        
        all_trends = {}
        platforms = {
            'twitter': TwitterCrawler(),
            'tiktok': TikTokCrawler(),
            'youtube': YouTubeCrawler(),
            'instagram': InstagramCrawler()
        }
        
        # Coleta ou carrega do cache
        for platform_name, crawler in platforms.items():
            if self.is_cache_valid(platform_name):
                # Usa cache válido
                trends = self.load_trends(platform_name)
                logger.info(f"Usando cache para {platform_name}: {len(trends)} tendências")
            else:
                # Coleta novos dados
                try:
                    trends = crawler.collect_all()
                    if trends:
                        self.save_trends(platform_name, trends)
                    else:
                        # Se falhou, tenta carregar cache antigo
                        trends = self.load_trends(platform_name)
                except Exception as e:
                    logger.error(f"Erro ao coletar {platform_name}: {e}")
                    trends = self.load_trends(platform_name)
            
            all_trends[platform_name] = trends
        
        # Verifica se tem dados suficientes
        total_trends = sum(len(trends) for trends in all_trends.values())
        
        if total_trends < 10:  # Se muito poucos dados, ativa fallback
            logger.warning("Poucos dados coletados, ativando fallback estético")
            all_trends['fallback_active'] = True
            all_trends.update(self.get_fallback_content())
        else:
            all_trends['fallback_active'] = False
        
        return all_trends
    
    def get_last_update_time(self) -> Optional[datetime]:
        """Retorna o horário da última atualização"""
        try:
            cache_files = list(self.data_dir.glob("*_*.json"))
            if not cache_files:
                return None
            
            # Pega o arquivo mais recente
            latest_file = max(cache_files, key=lambda f: f.stat().st_mtime)
            return datetime.fromtimestamp(latest_file.stat().st_mtime)
            
        except Exception as e:
            logger.error(f"Erro ao obter última atualização: {e}")
            return None

def main():
    """Função principal para teste"""
    manager = TrendsManager()
    trends = manager.collect_all_trends()
    
    print(f"📊 Coletadas tendências de {len(trends)} fontes")
    for platform, platform_trends in trends.items():
        if platform != 'fallback_active' and isinstance(platform_trends, list):
            print(f"  {platform}: {len(platform_trends)} tendências")

if __name__ == "__main__":
    main()


    def get_all_trends_flat(self):
        """Retorna todas as tendências em uma lista plana"""
        trends_dict = self.collect_all_trends()
        flat_trends = []
        
        for platform, trends in trends_dict.items():
            if isinstance(trends, list):
                for trend in trends:
                    trend['platform'] = platform
                    flat_trends.append(trend)
        
        return flat_trends

