import streamlit as st
import json
import os
import random
import time

# --- CONFIGURAÇÃO ---
SENHA_VERMELHO = "sua-senha-secreta"  # Mude esta senha!
ARQUIVO_ESTADO = "game_state.json"
# --------------------

def carregar_estado():
    """Lê o estado do jogo do arquivo JSON. Se não existir, cria um novo."""
    if os.path.exists(ARQUIVO_ESTADO):
        with open(ARQUIVO_ESTADO, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return criar_estado_inicial() # Arquivo corrompido ou vazio
    else:
        return criar_estado_inicial()

def criar_estado_inicial():
    """Retorna a estrutura de um estado de jogo zerado."""
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
    estado_inicial = criar_estado_inicial()
    salvar_estado(estado_inicial)
    # Limpa o estado da sessão para forçar o login novamente
    for key in list(st.session_state.keys()):
        del st.session_state[key]

# --- FUNÇÃO AUXILIAR PARA EXIBIR DADOS ---
def exibir_dados(dados):
    """Renderiza os dados em um formato bonito."""
    dados_html = " ".join([f"<span style='font-size: 2em; display: inline-block; margin: 0 5px;'>{d}</span>" for d in dados])
    st.markdown(f"<div style='background-color:white; color:black; text-align:center; padding: 10px; border-radius:5px;'>{dados_html}</div>", unsafe_allow_html=True)

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
        password = st.text_input("Senha do Anfitrião", type="password", key="pwd_input")
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
    
    if st.button("🔄 Atualizar Status do Jogo"):
        st.rerun()

    col1, col2 = st.columns(2)
    
    # Lado Vermelho
    with col1:
        st.markdown("<div style='background-color:#8B0000; padding:15px; border-radius:10px; border: 2px solid #FF4136; min-height: 250px;'>", unsafe_allow_html=True)
        st.subheader("Lado Vermelho 🔴")
        
        if not game_state['red']['rolled']:
            if st.session_state.team == 'red':
                if st.button("Rolar Dados (Vermelho)"):
                    game_state['red']['dice'] = [random.randint(1, 6) for _ in range(5)]
                    game_state['red']['rolled'] = True
                    salvar_estado(game_state)
                    st.rerun()
            else:
                st.info("Aguardando o Lado Vermelho rolar...")
        else: # Se já rolou
            st.success("Dados Rolados!")
            # NOVO: Botão para o jogador ver seus próprios dados
            if st.session_state.team == 'red' and not st.session_state.get('view_my_dice', False):
                if st.button("Ver meus dados 🔴"):
                    st.session_state.view_my_dice = True
                    st.rerun()

        # ATUALIZADO: Lógica de exibição dos dados
        if game_state['revealed']:
            exibir_dados(game_state['red']['dice'])
        elif st.session_state.get('team') == 'red' and st.session_state.get('view_my_dice', False):
            exibir_dados(game_state['red']['dice'])

        st.markdown("</div>", unsafe_allow_html=True)
        
    # Lado Azul
    with col2:
        st.markdown("<div style='background-color:#00008B; padding:15px; border-radius:10px; border: 2px solid #0074D9; min-height: 250px;'>", unsafe_allow_html=True)
        st.subheader("Lado Azul 🔵")
        
        if not game_state['blue']['rolled']:
            if st.session_state.team == 'blue':
                if st.button("Rolar Dados (Azul)"):
                    game_state['blue']['dice'] = [random.randint(1, 6) for _ in range(5)]
                    game_state['blue']['rolled'] = True
                    salvar_estado(game_state)
                    st.rerun()
            else:
                st.info("Aguardando o Lado Azul rolar...")
        else: # Se já rolou
            st.success("Dados Rolados!")
            # NOVO: Botão para o jogador ver seus próprios dados
            if st.session_state.team == 'blue' and not st.session_state.get('view_my_dice', False):
                if st.button("Ver meus dados 🔵"):
                    st.session_state.view_my_dice = True
                    st.rerun()

        # ATUALIZADO: Lógica de exibição dos dados
        if game_state['revealed']:
            exibir_dados(game_state['blue']['dice'])
        elif st.session_state.get('team') == 'blue' and st.session_state.get('view_my_dice', False):
            exibir_dados(game_state['blue']['dice'])
            
        st.markdown("</div>", unsafe_allow_html=True)

    # --- CONTROLES DE ANFITRIÃO (VERMELHO) ---
    if st.session_state.team == 'red':
        st.markdown("---")
        st.subheader("Controles do Anfitrião")
        
        ambos_rolaram = game_state['red']['rolled'] and game_state['blue']['rolled']
        if st.button("REVELAR DADOS PARA TODOS", disabled=not ambos_rolaram or game_state['revealed']):
            game_state['revealed'] = True
            salvar_estado(game_state)
            st.rerun()

        if st.button("Resetar Jogo para uma Nova Rodada"):
            resetar_jogo()
            st.rerun()
