import streamlit as st
import json
import os
import random
import time

# --- CONFIGURAÇÃO ---
SENHA_VERMELHO = "008"  # Mude esta senha!
ARQUIVO_ESTADO = "game_state.json"
# --------------------

def carregar_estado():
    """Lê o estado do jogo do arquivo JSON. Se não existir, cria um novo."""
    if os.path.exists(ARQUIVO_ESTADO):
        with open(ARQUIVO_ESTADO, 'r') as f:
            return json.load(f)
    else:
        # Estado inicial padrão
        return {
            "red": {"rolled": False, "dice": []},
            "blue": {"rolled": False, "dice": []},
            "revealed": False
        }

def salvar_estado(estado):
    """Salva o estado atual do jogo no arquivo JSON."""
    with open(ARQUIVO_ESTADO, 'w') as f:
        json.dump(estado, f, indent=4)

def resetar_jogo():
    """Reseta o jogo, limpando o estado e o arquivo."""
    estado_inicial = {
        "red": {"rolled": False, "dice": []},
        "blue": {"rolled": False, "dice": []},
        "revealed": False
    }
    salvar_estado(estado_inicial)
    # Limpa o estado da sessão para forçar o login novamente
    for key in list(st.session_state.keys()):
        del st.session_state[key]


# --- INTERFACE DO USUÁRIO (UI) ---

st.set_page_config(page_title="Jogo de Dados Secreto", layout="centered")

# Carrega o estado atual do jogo
game_state = carregar_estado()

# Título Principal
st.title("🎲 Jogo de Dados Secreto 🎲")

# --- TELA DE LOGIN ---
if 'team' not in st.session_state:
    st.header("Escolha seu Lado")
    
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Lado Azul 🔵")
        if st.button("Entrar como Azul"):
            st.session_state.team = 'blue'
            st.rerun()

    with col2:
        st.subheader("Lado Vermelho 🔴")
        password = st.text_input("Senha do Anfitrião", type="password")
        if st.button("Entrar como Vermelho"):
            if password == SENHA_VERMELHO:
                st.session_state.team = 'red'
                st.rerun()
            else:
                st.error("Senha incorreta!")

# --- TELA DO JOGO ---
else:
    team_color = "🔴" if st.session_state.team == 'red' else "🔵"
    st.header(f"Você está no Lado {st.session_state.team.capitalize()} {team_color}")
    
    # Botão para atualizar o estado manualmente
    if st.button("🔄 Atualizar Status do Jogo"):
        st.rerun()

    col1, col2 = st.columns(2)
    
    # Lado Vermelho
    with col1:
        st.markdown("<div style='background-color:#8B0000; padding:15px; border-radius:10px; border: 2px solid #FF4136;'>", unsafe_allow_html=True)
        st.subheader("Lado Vermelho 🔴")
        
        # Lógica de rolagem
        if not game_state['red']['rolled']:
            if st.session_state.team == 'red':
                if st.button("Rolar Dados (Vermelho)"):
                    game_state['red']['dice'] = [random.randint(1, 6) for _ in range(5)]
                    game_state['red']['rolled'] = True
                    salvar_estado(game_state)
                    st.rerun()
            else:
                st.info("Aguardando o Lado Vermelho rolar...")
        else:
            st.success("Dados Rolados! Aguardando revelação.")

        # Exibição dos dados
        if game_state['revealed']:
            dados_str = " ".join([f"<span style='font-size: 2em;'>{d}</span>" for d in game_state['red']['dice']])
            st.markdown(f"<div style='background-color:white; color:black; text-align:center; padding: 10px; border-radius:5px;'>{dados_str}</div>", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)
        
    # Lado Azul
    with col2:
        st.markdown("<div style='background-color:#00008B; padding:15px; border-radius:10px; border: 2px solid #0074D9;'>", unsafe_allow_html=True)
        st.subheader("Lado Azul 🔵")
        
        # Lógica de rolagem
        if not game_state['blue']['rolled']:
            if st.session_state.team == 'blue':
                if st.button("Rolar Dados (Azul)"):
                    game_state['blue']['dice'] = [random.randint(1, 6) for _ in range(5)]
                    game_state['blue']['rolled'] = True
                    salvar_estado(game_state)
                    st.rerun()
            else:
                st.info("Aguardando o Lado Azul rolar...")
        else:
            st.success("Dados Rolados! Aguardando revelação.")

        # Exibição dos dados
        if game_state['revealed']:
            dados_str = " ".join([f"<span style='font-size: 2em;'>{d}</span>" for d in game_state['blue']['dice']])
            st.markdown(f"<div style='background-color:white; color:black; text-align:center; padding: 10px; border-radius:5px;'>{dados_str}</div>", unsafe_allow_html=True)
            
        st.markdown("</div>", unsafe_allow_html=True)

    # --- CONTROLES DE ANFITRIÃO (VERMELHO) ---
    if st.session_state.team == 'red':
        st.markdown("---")
        st.subheader("Controles do Anfitrião")
        
        # Botão de Revelar
        ambos_rolaram = game_state['red']['rolled'] and game_state['blue']['rolled']
        if st.button("REVELAR DADOS PARA TODOS", disabled=not ambos_rolaram):
            game_state['revealed'] = True
            salvar_estado(game_state)
            st.rerun()

        # Botão de Resetar
        if st.button("Resetar Jogo para uma Nova Rodada"):
            resetar_jogo()
            st.rerun()
