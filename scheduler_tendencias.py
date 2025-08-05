"""
Sistema de Agendamento de Tendências
Coleta automática diária otimizada para performance
"""
import schedule
import time
import logging
from datetime import datetime
from utils.trends_manager import TrendsManager
import threading
import os

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/scheduler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TrendsScheduler:
    def __init__(self):
        self.trends_manager = TrendsManager()
        self.is_running = False
        
        # Cria diretório de logs se não existir
        os.makedirs('logs', exist_ok=True)
    
    def collect_trends_job(self):
        """Job de coleta de tendências"""
        try:
            logger.info("🚀 Iniciando coleta automática de tendências...")
            start_time = datetime.now()
            
            # Coleta tendências
            trends = self.trends_manager.collect_all_trends()
            
            # Calcula estatísticas
            total_trends = sum(
                len(platform_trends) for key, platform_trends in trends.items()
                if key != 'fallback_active' and isinstance(platform_trends, list)
            )
            
            duration = (datetime.now() - start_time).total_seconds()
            
            logger.info(f"✅ Coleta concluída: {total_trends} tendências em {duration:.1f}s")
            
            # Log detalhado por plataforma
            for platform, platform_trends in trends.items():
                if platform != 'fallback_active' and isinstance(platform_trends, list):
                    logger.info(f"  📱 {platform}: {len(platform_trends)} tendências")
            
        except Exception as e:
            logger.error(f"❌ Erro na coleta automática: {e}")
    
    def start_scheduler(self):
        """Inicia o agendador"""
        if self.is_running:
            logger.warning("Agendador já está rodando")
            return
        
        # Agenda coleta diária às 7h da manhã
        schedule.every().day.at("07:00").do(self.collect_trends_job)
        
        # Agenda coleta a cada 6 horas para manter dados frescos
        schedule.every(6).hours.do(self.collect_trends_job)
        
        self.is_running = True
        logger.info("📅 Agendador iniciado - Coletas às 7h e a cada 6h")
        
        # Executa uma coleta inicial se não há dados recentes
        last_update = self.trends_manager.get_last_update_time()
        if not last_update or (datetime.now() - last_update).total_seconds() > 21600:  # 6 horas
            logger.info("🔄 Executando coleta inicial...")
            self.collect_trends_job()
        
        # Loop principal do agendador
        try:
            while self.is_running:
                schedule.run_pending()
                time.sleep(60)  # Verifica a cada minuto
        except KeyboardInterrupt:
            logger.info("⏹️ Agendador interrompido pelo usuário")
        except Exception as e:
            logger.error(f"❌ Erro no agendador: {e}")
        finally:
            self.is_running = False
    
    def stop_scheduler(self):
        """Para o agendador"""
        self.is_running = False
        schedule.clear()
        logger.info("⏹️ Agendador parado")
    
    def run_in_background(self):
        """Executa o agendador em background"""
        def background_task():
            self.start_scheduler()
        
        thread = threading.Thread(target=background_task, daemon=True)
        thread.start()
        logger.info("🔄 Agendador iniciado em background")
        return thread

def main():
    """Função principal para execução standalone"""
    scheduler = TrendsScheduler()
    
    print("🚀 Iniciando sistema de agendamento de tendências...")
    print("📅 Coletas programadas: 7h da manhã e a cada 6 horas")
    print("⏹️ Pressione Ctrl+C para parar")
    
    try:
        scheduler.start_scheduler()
    except KeyboardInterrupt:
        print("\n⏹️ Parando agendador...")
        scheduler.stop_scheduler()

if __name__ == "__main__":
    main()

