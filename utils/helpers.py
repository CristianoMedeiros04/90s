"""
Funções auxiliares para o aplicativo de geração de roteiros
"""
import os
import json
import streamlit as st
from datetime import datetime
from docx import Document


def carregar_perfil():
    """Carrega o perfil do usuário do arquivo JSON"""
    try:
        if os.path.exists("data/perfil.json"):
            with open("data/perfil.json", "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception as e:
        st.error(f"Erro ao carregar perfil: {e}")
    return {}


def salvar_perfil(perfil):
    """Salva o perfil do usuário no arquivo JSON"""
    try:
        os.makedirs("data", exist_ok=True)
        with open("data/perfil.json", "w", encoding="utf-8") as f:
            json.dump(perfil, f, ensure_ascii=False, indent=2)
    except Exception as e:
        st.error(f"Erro ao salvar perfil: {e}")


def carregar_historico():
    """Carrega o histórico de roteiros do arquivo JSON"""
    try:
        if os.path.exists("data/historico.json"):
            with open("data/historico.json", "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception as e:
        st.error(f"Erro ao carregar histórico: {e}")
    return []


def salvar_historico(historico):
    """Salva o histórico de roteiros no arquivo JSON"""
    try:
        os.makedirs("data", exist_ok=True)
        with open("data/historico.json", "w", encoding="utf-8") as f:
            json.dump(historico, f, ensure_ascii=False, indent=2)
    except Exception as e:
        st.error(f"Erro ao salvar histórico: {e}")


def calcular_completude_perfil(perfil):
    """Calcula a porcentagem de completude do perfil"""
    if not perfil:
        return 0
    
    total_campos = 37  # Total de campos do perfil conforme especificação
    campos_preenchidos = sum(1 for valor in perfil.values() if valor and str(valor).strip())
    return int((campos_preenchidos / total_campos) * 100) if total_campos > 0 else 0


def extrair_texto_arquivo(arquivo):
    """Extrai texto de arquivos DOCX ou TXT"""
    try:
        if arquivo.type == "application/pdf":
            st.warning("⚠️ Arquivos PDF não são suportados no momento. Use arquivos DOCX ou TXT.")
            return ""
        elif arquivo.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            doc = Document(arquivo)
            texto = "\n".join([para.text for para in doc.paragraphs])
            return texto
        elif arquivo.type == "text/plain":
            return arquivo.getvalue().decode('utf-8')
        else:
            return ""
    except Exception as e:
        st.error(f"Erro ao extrair texto do arquivo: {e}")
        return ""


def aplicar_filtros_historico(historico, filtro_texto, filtro_formato, filtro_data):
    """Aplica filtros ao histórico de roteiros"""
    
    resultado = historico.copy()
    
    # Filtro por texto
    if filtro_texto:
        filtro_texto = filtro_texto.lower()
        resultado = [
            r for r in resultado 
            if filtro_texto in r.get('titulo', '').lower() or 
               filtro_texto in r.get('conteudo', '').lower()
        ]
    
    # Filtro por formato
    if filtro_formato and filtro_formato != "Todos":
        resultado = [
            r for r in resultado 
            if r.get('formato', 'Não especificado') == filtro_formato
        ]
    
    # Filtro por data
    if filtro_data:
        data_str = str(filtro_data)
        resultado = [
            r for r in resultado 
            if r.get('data', '').startswith(data_str)
        ]
    
    return resultado


def salvar_alteracoes_roteiro(roteiro_original, novo_titulo, novo_conteudo, historico_completo):
    """Salva as alterações feitas em um roteiro"""
    
    # Encontra o roteiro no histórico completo
    for i, roteiro in enumerate(historico_completo):
        if roteiro.get('id') == roteiro_original.get('id'):
            # Atualiza os dados
            historico_completo[i]['titulo'] = novo_titulo
            historico_completo[i]['conteudo'] = novo_conteudo
            historico_completo[i]['data_atualizacao'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            break
    
    # Atualiza o estado da sessão
    st.session_state["historico"] = historico_completo
    
    # Salva em arquivo
    salvar_historico(historico_completo)


def excluir_roteiro(roteiro_para_excluir, historico_completo):
    """Exclui um roteiro do histórico"""
    
    # Remove o roteiro do histórico
    historico_atualizado = [
        roteiro for roteiro in historico_completo 
        if roteiro.get('id') != roteiro_para_excluir.get('id')
    ]
    
    # Atualiza o estado da sessão
    st.session_state["historico"] = historico_atualizado
    
    # Salva em arquivo
    salvar_historico(historico_atualizado)
    
    # Limpa a confirmação
    if "confirmar_exclusao" in st.session_state:
        del st.session_state["confirmar_exclusao"]



def salvar_roteiro(roteiro_data):
    """
    Salva um novo roteiro no histórico
    
    Args:
        roteiro_data: Dict com dados do roteiro
        
    Returns:
        bool: True se salvou com sucesso, False caso contrário
    """
    try:
        # Carrega histórico atual
        historico = carregar_historico()
        
        # Adiciona ID único se não existir
        if 'id' not in roteiro_data:
            roteiro_data['id'] = f"roteiro_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Adiciona data de criação se não existir
        if 'data' not in roteiro_data:
            roteiro_data['data'] = datetime.now().isoformat()
        
        # Adiciona ao histórico
        historico.append(roteiro_data)
        
        # Salva histórico atualizado
        salvar_historico(historico)
        
        # Atualiza estado da sessão
        st.session_state["historico"] = historico
        
        return True
        
    except Exception as e:
        st.error(f"Erro ao salvar roteiro: {str(e)}")
        return False

