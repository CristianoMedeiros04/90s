"""
Tela Raio-X - Engenharia de Copy Viral
Análise de vídeos de sucesso e geração de copies similares
"""
import streamlit as st
import os
import base64
import tempfile
from datetime import datetime
from utils.raiox import (
    validate_video_url, 
    process_video_complete, 
    create_download_content,
    format_duration
)
from modules.cerebro import get_cerebro_context, calcular_completude_perfil, load_cerebro_data

def render_raiox_page():
    """Renderiza a página Raio-X"""
    
    st.title("🧬 Raio-X - Engenharia de Copy Viral")
   
    # Verificação do perfil
    perfil = load_cerebro_data()
    completude = calcular_completude_perfil(perfil)
    
    if completude < 20:
        st.error("❌ **Perfil incompleto!** Preencha pelo menos 20% do seu perfil na tela 'Cérebro' para usar o Raio-X.")
        st.info("💡 O Raio-X precisa do seu contexto para adaptar as copies ao seu nicho e público.")
        return
    
    # Status do perfil
    col1, col2 = st.columns([3, 1])

    with col1:
        # Barra de progresso estilizada com HTML
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
    
    if completude < 50:
        st.markdown("⚠️ Para melhores resultados, complete mais campos do seu perfil na tela 'Cérebro'.")   
   
    
    # Interface principal
    st.subheader("📹 Análise de Vídeo")
    
    # Campo de entrada da URL
    video_url = st.text_input(
        "**Cole aqui o link do vídeo (YouTube, TikTok, Instagram...)**:",
        placeholder="https://www.youtube.com/watch?v=...",
        help="Suportamos YouTube, TikTok, Instagram, Facebook e Twitter"
    )
    
    # Validação em tempo real
    if video_url:
        is_valid, platform_or_error = validate_video_url(video_url)
        if is_valid:
            st.success(f"✅ URL válida - Plataforma: {platform_or_error}")
        else:
            st.error(f"❌ {platform_or_error}")
    
    # Botão de análise
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        analyze_button = st.button(
            "⌕ Analisar Vídeo", 
            type="primary", 
            use_container_width=True,
            disabled=not video_url or not validate_video_url(video_url)[0]
        )
    
    # Processamento do vídeo
    if analyze_button and video_url:
        
        # Container para feedback de progresso
        progress_container = st.container()
        
        with progress_container:
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            def update_progress(message):
                """Callback para atualizar progresso"""
                status_text.text(message)
                
                # Simula progresso baseado na mensagem
                if "Validando" in message:
                    progress_bar.progress(10)
                elif "metadados" in message:
                    progress_bar.progress(25)
                elif "Baixando" in message:
                    progress_bar.progress(40)
                elif "Transcrevendo" in message:
                    progress_bar.progress(60)
                elif "Analisando" in message:
                    progress_bar.progress(80)
                elif "Gerando" in message:
                    progress_bar.progress(90)
                elif "concluído" in message:
                    progress_bar.progress(100)
            
            # Processa o vídeo
            result, error = process_video_complete(video_url, update_progress)
            
            if error:
                st.error(f"❌ {error}")
                return
            
            if not result:
                st.error("❌ Erro desconhecido no processamento")
                return
        
        # Limpa o feedback de progresso
        progress_container.empty()
        
        # Exibe resultados
        st.success("✅ **Análise concluída com sucesso!**")
        
        # Metadados do vídeo
        st.subheader("📊 Informações do Vídeo")
        
        metadata = result['metadata']
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Visualizações", f"{metadata.get('view_count', 0):,}")
        
        with col2:
            st.metric("Curtidas", f"{metadata.get('like_count', 0):,}")
        
        with col3:
            st.metric("Duração", format_duration(metadata.get('duration', 0)))
        
        # Informações detalhadas
        st.markdown(f"**📝 Título:** {metadata.get('title', 'N/A')}")
        st.markdown(f"**👤 Autor:** {metadata.get('uploader', 'N/A')}")
        st.markdown(f"**🌐 Plataforma:** {metadata.get('platform', 'N/A')}")
        
        st.markdown("---")
        
        # Transcrição original (colapsável)
        with st.expander("📜 Transcrição Original", expanded=False):
            st.text_area(
                "Conteúdo transcrito:",
                value=result['transcription'],
                height=200,
                disabled=True
            )
        
        # Análise da estrutura
        st.subheader("🧠 Análise da Estrutura")
        st.markdown(result['structure_analysis'])
        
        st.markdown("---")
        
        # Nova copy gerada
        st.subheader("✍️ Nova Copy Personalizada")
        
        # Área editável para a copy
        new_copy_text = st.text_area(
            "Copy adaptada ao seu perfil:",
            value=result['new_copy'],
            height=400,
            help="Você pode editar a copy antes de baixar"
        )
        
        # Estatísticas da copy
        col1, col2, col3 = st.columns(3)
        
        with col1:
            word_count = len(new_copy_text.split())
            st.metric("Palavras", word_count)
        
        with col2:
            # Estimativa de duração (150 palavras por minuto)
            estimated_duration = int((word_count / 150) * 60)
            st.metric("Duração Est.", f"{estimated_duration}s")
        
        with col3:
            char_count = len(new_copy_text)
            st.metric("Caracteres", char_count)
        
        # Botões de ação
        st.markdown("---")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Botão de download
            download_content = create_download_content(new_copy_text, metadata)
            
            st.download_button(
                label="📥 Baixar Copy",
                data=download_content,
                file_name=f"copy_raiox_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain",
                use_container_width=True
            )
        
        with col2:
            # Botão para copiar
            if st.button("📋 Copiar Copy", use_container_width=True):
                st.code(new_copy_text, language=None)
                st.success("✅ Copy copiada! Use Ctrl+C para copiar do campo acima.")
        
        with col3:
            # Botão para nova análise
            if st.button("🔄 Nova Análise", use_container_width=True):
                st.rerun()
    
    # Informações sobre a ferramenta   
    with open("icons/exclamation.svg", "rb") as f:
        chart_svg = base64.b64encode(f.read()).decode()
    
    st.markdown(f"""
        <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 1.5rem;">
            <img src="data:image/svg+xml;base64,{chart_svg}" width="26" height="26" style="margin-top: 2px;" />
            <h3 style="margin: 0; font-size: 1.6rem; font-weight: 600;">Como funciona o Raio-X</h3>
        </div>
    """, unsafe_allow_html=True)   
    
    st.markdown("""
    **O Raio-X analisa vídeos virais e adapta a estrutura ao seu perfil:**
    
    1. **🔍 Análise:** Baixa e transcreve o vídeo automaticamente
    2. **🧠 Estrutura:** Identifica gatilhos, padrões e elementos de engajamento  
    3. **🎯 Personalização:** Adapta ao seu nicho, público e tom de voz
    4. **✍️ Geração:** Cria copy similar mantendo a estrutura viral
    5. **📥 Download:** Permite baixar e editar o resultado    
    
    """)
    
    # Dicas de uso
    with st.expander("💡 Dicas para melhores resultados"):
        st.markdown("""
        **◉─  Escolha vídeos com bom desempenho:**
        - Muitas visualizações e curtidas
        - Comentários engajados
        - Conteúdo relevante ao seu nicho
        
        **◉─  Complete seu perfil:**
        - Quanto mais completo, melhor a personalização
        - Inclua histórias e experiências pessoais
        - Defina claramente seu público-alvo
        
        **◉─  Edite o resultado:**
        - Ajuste detalhes específicos do seu negócio
        - Adicione CTAs personalizados
        - Adapte exemplos à sua realidade
        """)

# Função para compatibilidade com o sistema de navegação
def show_raiox_page():
    """Função de compatibilidade"""
    render_raiox_page()

