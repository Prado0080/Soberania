import streamlit as st
import json
import os
import random

# --- CONFIGURAÇÃO ---
SENHA_VERMELHO = "sua-senha-secreta"  # Mude esta senha!
ARQUIVO_ESTADO = "game_state.json"
# --------------------

# Define a estrutura de um jogo novo/resetado
def criar_estado_inicial():
    return {
        "red": {"dice": [], "rolled_once": False, "rerolled": False},
        "blue": {"dice": [], "rolled_once": False, "rerolled": False},
        "revealed_to_all": False
    }

# Carrega o estado do jogo do arquivo ou cria um novo
def carregar_estado():
    if os.path.exists(ARQUIVO_ESTADO):
        with open(ARQUIVO_ESTADO, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return criar_estado_inicial()
    return criar_estado_inicial()

# Salva o estado do jogo no arquivo
def salvar_estado(estado):
    with open(ARQUIVO_ESTADO, 'w') as f:
        json.dump(estado, f, indent=4)

# Renderiza os dados em um formato visual
def exibir_dados(dados):
    dados_html = " ".join([f"<span style='font-size: 2em; display: inline-block; margin: 0 5px;'>{d}</span>" for d in dados])
    st.markdown(f"<div style='background-color:white; color:black; text-align:center; padding: 10px; border-radius:5px;'>{dados_html}</div>", unsafe_allow_html=True)

# --- LÓGICA PRINCIPAL DO APLICATIVO ---

st.set_page_config(page_title="Jogo de Dados Secreto", layout="centered")
st.title("🎲 Jogo de Dados Secreto 🎲")

game_state = carregar_estado()

# --- TELA DE LOGIN ---
if 'team' not in st.session_state:
    st.header("Escolha seu Lado")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Lado Azul 🔵")
        if st.button("Entrar como Azul"):
            st.session_state.team = 'blue'
            st.rerun() # Usado aqui para forçar a transição de tela
    with col2:
        st.subheader("Lado Vermelho 🔴")
        password = st.text_input("Senha do Anfitrião", type="password", key="pwd_input")
        if st.button("Entrar como Vermelho"):
            if password == SENHA_VERMELHO:
                st.session_state.team = 'red'
                st.rerun() # Usado aqui para forçar a transição de tela
            else:
                st.error("Senha incorreta!")

# --- TELA DO JOGO ---
else:
    my_team = st.session_state['team']
    team_color = "🔴" if my_team == 'red' else "🔵"
    st.header(f"Você está no Lado {my_team.capitalize()} {team_color}")
    
    # CORREÇÃO DO BUG: Se o jogo foi resetado (time não rolou), mas a sessão local ainda "vê" os dados, limpa a flag local.
    if st.session_state.get('view_my_dice', False) and not game_state[my_team]['rolled_once']:
        st.session_state.view_my_dice = False

    # Botão para atualizar manualmente a tela, caso necessário
    if st.button("🔄 Atualizar Status do Jogo"):
        pass  # Clicar no botão já causa um rerun natural do Streamlit

    col1, col2 = st.columns(2)

    # --- LÓGICA DO LADO VERMELHO ---
    with col1:
        st.markdown("<div style='background-color:#8B0000; padding:15px; border-radius:10px; border: 2px solid #FF4136; min-height: 350px;'>", unsafe_allow_html=True)
        st.subheader("Lado Vermelho 🔴")
        
        red_state = game_state['red']

        # 1. Botão de rolar dados
        if not red_state['rolled_once']:
            if my_team == 'red':
                if st.button("Rolar Dados (Vermelho)"):
                    red_state['dice'] = [random.randint(1, 6) for _ in range(5)]
                    red_state['rolled_once'] = True
                    salvar_estado(game_state)
                    st.rerun()
            else:
                st.info("Aguardando o Lado Vermelho rolar...")
        else:
            st.success("Dados Rolados!")
            
            # 2. Botão de ver os próprios dados
            if my_team == 'red' and not st.session_state.get('view_my_dice'):
                if st.button("Ver meus dados 🔴"):
                    st.session_state.view_my_dice = True
                    st.rerun()

        # 3. Exibição dos dados e opção de re-rolagem
        should_display = game_state['revealed_to_all'] or (my_team == 'red' and st.session_state.get('view_my_dice'))
        if red_state['rolled_once'] and should_display:
            exibir_dados(red_state['dice'])
            
            if my_team == 'red' and not red_state['rerolled']:
                st.markdown("---")
                options_map = {f"Dado #{i+1} (valor: {d})": i for i, d in enumerate(red_state['dice'])}
                dice_to_reroll = st.multiselect("Escolha até 2 dados para rolar novamente:", options_map.keys(), max_selections=2, key="reroll_red")
                if st.button("Rolar selecionados (Vermelho)"):
                    indices = [options_map[label] for label in dice_to_reroll]
                    for i in indices:
                        red_state['dice'][i] = random.randint(1, 6)
                    red_state['rerolled'] = True
                    salvar_estado(game_state)
                    st.rerun()
            elif red_state['rerolled']:
                 st.info("Re-rolagem já utilizada.")

        st.markdown("</div>", unsafe_allow_html=True)

    # --- LÓGICA DO LADO AZUL ---
    with col2:
        st.markdown("<div style='background-color:#00008B; padding:15px; border-radius:10px; border: 2px solid #0074D9; min-height: 350px;'>", unsafe_allow_html=True)
        st.subheader("Lado Azul 🔵")

        blue_state = game_state['blue']
        
        # 1. Botão de rolar dados
        if not blue_state['rolled_once']:
            if my_team == 'blue':
                if st.button("Rolar Dados (Azul)"):
                    blue_state['dice'] = [random.randint(1, 6) for _ in range(5)]
                    blue_state['rolled_once'] = True
                    salvar_estado(game_state)
                    st.rerun()
            else:
                st.info("Aguardando o Lado Azul rolar...")
        else:
            st.success("Dados Rolados!")

            # 2. Botão de ver os próprios dados
            if my_team == 'blue' and not st.session_state.get('view_my_dice'):
                if st.button("Ver meus dados 🔵"):
                    st.session_state.view_my_dice = True
                    st.rerun()

        # 3. Exibição dos dados e opção de re-rolagem
        should_display = game_state['revealed_to_all'] or (my_team == 'blue' and st.session_state.get('view_my_dice'))
        if blue_state['rolled_once'] and should_display:
            exibir_dados(blue_state['dice'])

            if my_team == 'blue' and not blue_state['rerolled']:
                st.markdown("---")
                options_map = {f"Dado #{i+1} (valor: {d})": i for i, d in enumerate(blue_state['dice'])}
                dice_to_reroll = st.multiselect("Escolha até 2 dados para rolar novamente:", options_map.keys(), max_selections=2, key="reroll_blue")
                if st.button("Rolar selecionados (Azul)"):
                    indices = [options_map[label] for label in dice_to_reroll]
                    for i in indices:
                        blue_state['dice'][i] = random.randint(1, 6)
                    blue_state['rerolled'] = True
                    salvar_estado(game_state)
                    st.rerun()
            elif blue_state['rerolled']:
                st.info("Re-rolagem já utilizada.")

        st.markdown("</div>", unsafe_allow_html=True)

    # --- CONTROLES DO ANFITRIÃO ---
    if my_team == 'red':
        st.markdown("---")
        st.subheader("Controles do Anfitrião")
        
        ambos_rolaram = game_state['red']['rolled_once'] and game_state['blue']['rolled_once']
        if st.button("REVELAR DADOS PARA TODOS", disabled=not ambos_rolaram or game_state['revealed_to_all']):
            game_state['revealed_to_all'] = True
            salvar_estado(game_state)
            st.rerun()

        if st.button("Resetar Jogo para uma Nova Rodada"):
            novo_estado = criar_estado_inicial()
            salvar_estado(novo_estado)
            # Limpa a sessão do anfitrião para mandá-lo para a tela de login
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
