"""
Página Temas Quentes - Análise REAL de conteúdo web
Agora com web crawler completo e transcrição de vídeos
"""
import streamlit as st
from services.web_crawler import crawl_multiple_sites, extract_single_page_deep
from services.ai_agents_real import analisar_conteudo_com_ia, gerar_relatorio_consolidado
from modules.cerebro import get_cerebro_context
from datetime import datetime
import base64
import json


def render_stalker_page():
    """Renderiza a página Stalker (antiga Temas Quentes)"""
    
    ## === TÍTULO PRINCIPAL === ##
    with open("icons/incognito.svg", "rb") as f:
        svg_base64 = base64.b64encode(f.read()).decode()
    
    st.markdown(f""" 
        <div style="display: flex; align-items: center; gap: 18px; margin-bottom: 1.5rem;">
            <img src="data:image/svg+xml;base64,{svg_base64}" width="48" height="48" style="margin-top: 4px;" />
            <h2 style="margin: 0; font-size: 2.8rem; font-weight: 700;">Stalker</h2>
        </div>
    """, unsafe_allow_html=True)   
    

    # Configuração da análise
    st.subheader("🔗 Links para Análise")
    
    # Campos para URLs
    urls = []
    for i in range(5):
        url = st.text_input(
            f"Link {i+1}:",
            placeholder="https://exemplo.com/artigo",
            key=f"url_{i}",
            help=f"Cole aqui o {i+1}º link para análise"
        )
        if url.strip():
            urls.append(url.strip())
    
    if not urls:
        st.info("👆 Cole pelo menos 1 link para começar a análise")
        return
    
    # Modo de análise
    st.subheader("⚙️ Configuração da Análise")
    
    col1, col2 = st.columns(2)
    
    with col1:
        modo_analise = st.radio(
            "Modo de análise:",
            ["Análise Rápida", "Análise Completa"],
            help="Rápida: apenas a página. Completa: vasculha o site inteiro"
        )
    
    with col2:
        if modo_analise == "Análise Rápida":
            st.info("""
            **Análise Rápida:**
            - Extrai conteúdo da página específica
            - Transcreve vídeos encontrados
            - Análise com IA personalizada
            - ⏱️ Mais rápido
            """)
        else:
            st.info("""
            **Análise Completa:**
            - Vasculha até 5 páginas por site
            - Mapeia links internos
            - Transcreve múltiplos vídeos
            - Relatório abrangente
            - ⏱️ Mais demorado, mais completo
            """)
    
    # Verificar contexto do Cérebro
    cerebro_context = get_cerebro_context()
    if "Perfil não configurado" in cerebro_context:
        st.markdown ("⚠️ Configure seu perfil na tela **Cérebro** para obter análises mais personalizadas!")
    else:
        st.markdown ("✅ Análise será personalizada com base no seu perfil do Cérebro")
    
    # Botão para iniciar análise
    if st.button("🚀 Iniciar Análise de Temas Quentes", type="primary"):
        
        st.markdown("---")
        st.subheader("🔄 Processamento em Andamento")
        
        try:
            if modo_analise == "Análise Rápida":
                # Análise rápida - uma página por vez
                all_analyses = []
                
                for i, url in enumerate(urls):
                    st.markdown(f"### 📄 Analisando Link {i+1}: {url}")
                    
                    # Extrair conteúdo
                    report = extract_single_page_deep(url)
                    
                    if report.get('statistics', {}).get('successful_pages', 0) > 0:
                        # Analisar com IA
                        st.markdown ("Analisando conteúdo...")
                        analysis = analisar_conteudo_com_ia(
                            conteudo=report['all_content'] + report.get('video_content', ''),
                            url=url
                        )
                        
                        if analysis:
                            all_analyses.append(analysis)
                            st.success(f"✅ Link {i+1} analisado com sucesso!")
                            
                            # Mostrar prévia da análise
                            with st.expander(f"🗎 Prévia da Análise - Link {i+1}"):
                                st.markdown(analysis[:500] + "...")
                        else:
                            st.error(f"❌ Erro na análise do Link {i+1}")
                    else:
                        st.error(f"❌ Erro ao extrair conteúdo do Link {i+1}")
                
            else:
                # Análise completa - crawler completo
                st.markdown ("🕷️ Iniciando Pesquisa completa...")
                
                report = crawl_multiple_sites(urls, max_pages_per_site=5)
                
                if report['statistics']['successful_pages'] > 0:
                    # Analisar conteúdo consolidado
                    st.info("◉ Analisando todo o conteúdo coletado com IA...")
                    
                    full_content = report['all_content'] + report.get('video_content', '')
                    analysis = analisar_conteudo_com_ia(
                        conteudo=full_content,
                        url="Múltiplos sites analisados"
                    )
                    
                    if analysis:
                        all_analyses = [analysis]
                        st.success("✅ Análise completa concluída!")
                    else:
                        st.error("❌ Erro na análise com IA")
                        return
                else:
                    st.error("❌ Nenhum conteúdo foi extraído com sucesso")
                    return
            
            # Gerar relatório consolidado
            if all_analyses:
                st.markdown("◉ Gerando relatório consolidado...")
                
                relatorio_final = gerar_relatorio_consolidado(all_analyses)
                
                if relatorio_final:
                    # Exibir resultado final
                    display_analysis_results(relatorio_final, urls, modo_analise, report if modo_analise == "Análise Completa" else None)
                else:
                    st.error("❌ Erro ao gerar relatório consolidado")
            else:
                st.error("❌ Nenhuma análise foi concluída com sucesso")
                
        except Exception as e:
            st.error(f"❌ Erro inesperado durante a análise: {str(e)}")


def display_analysis_results(relatorio, urls, modo_analise, crawler_report=None):
    """Exibe os resultados da análise"""
    
    st.markdown("---")
    st.subheader("📊 Relatório de Temas Quentes")
    
    # Informações da análise
    st.markdown("ℹ️ **Informações da Análise**")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.write(f"**🔗 Links analisados:** {len(urls)}")
    
    with col2:
        st.write(f"**⚙️ Modo:** {modo_analise}")
    
    with col3:
        st.write(f"**📅 Data:** {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    
    # Estatísticas do crawler (se análise completa)
    if crawler_report and modo_analise == "Análise Completa":
        st.markdown("📈 **Estatísticas do Crawling**")
        
        stats = crawler_report['statistics']
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Páginas Processadas", stats['successful_pages'])
        
        with col2:
            st.metric("Total de Palavras", f"{stats['total_words']:,}")
        
        with col3:
            st.metric("Vídeos Encontrados", stats['total_videos'])
        
        with col4:
            st.metric("Vídeos Transcritos", stats['transcribed_videos'])
    
    # Relatório principal
    st.markdown("---")
    st.subheader("🗎 Relatório Consolidado")
    
    # Campo editável para o relatório
    relatorio_editado = st.text_area(
        "Relatório (editável):",
        value=relatorio,
        height=600,
        key="relatorio_temas_quentes"
    )
    
    # Links analisados
    st.markdown("---")
    st.subheader("🔗 Links Analisados")
    
    for i, url in enumerate(urls):
        st.write(f"{i+1}. {url}")
    
    # Páginas mais relevantes (se análise completa)
    if crawler_report and crawler_report.get('top_pages'):
        st.markdown("---")
        st.subheader("⭐ Páginas Mais Relevantes")
        
        for i, page in enumerate(crawler_report['top_pages'][:3]):
            with st.expander(f"📄 {i+1}. {page['title']} ({page['word_count']} palavras)"):
                st.write(f"**URL:** {page['url']}")
                st.write(f"**Conteúdo:** {page['content'][:300]}...")
    
    # Vídeos transcritos (se houver)
    if crawler_report and crawler_report.get('video_transcriptions'):
        st.markdown("---")
        st.subheader("🎥 Vídeos Transcritos")
        
        for i, video in enumerate(crawler_report['video_transcriptions']):
            with st.expander(f"📹 {i+1}. {video['video_title']} ({video['word_count']} palavras)"):
                st.write(f"**URL do vídeo:** {video['video_url']}")
                st.write(f"**Página origem:** {video['page_title']}")
                st.text_area(
                    "Transcrição:",
                    value=video['transcription'][:500] + "...",
                    height=100,
                    disabled=True,
                    key=f"transcricao_{i}"
                )
    
    # Botões de ação
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.download_button(
            "⬇️ Baixar Relatório",
            data=relatorio_editado,
            file_name=f"temas_quentes_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
            mime="text/plain"
        )
    
    with col2:
        if st.button("🗎 Copiar Relatório"):
            st.code(relatorio_editado, language="text")
            st.info("🗎 Relatório exibido acima para cópia manual.")
    
    with col3:
        if st.button("↻ Nova Análise"):
            st.rerun()
    
    # Dicas para usar os insights
    st.markdown("---")
    st.subheader("💡 Como Usar os Insights")
    
    st.markdown("""
    **◉ Para Criação de Conteúdo:**
    - Use as tendências identificadas para criar posts relevantes
    - Adapte os insights para seu público-alvo
    - Crie reacts sobre os vídeos transcritos
    
    **◉ Para Estratégia:**
    - Monitore concorrentes e influenciadores
    - Identifique gaps de conteúdo no mercado
    - Planeje campanhas baseadas em dados reais
    
    **◉ Para Engajamento:**
    - Use os temas quentes em suas postagens
    - Participe de conversas relevantes
    - Crie conteúdo oportuno e atual
    """)


# Função principal para compatibilidade
def show_temas_quentes_page():
    """Função principal da página Temas Quentes"""
    render_temas_quentes_page()

