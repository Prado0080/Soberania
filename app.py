import streamlit as st
import json
import os
import random

# --- CONFIGURAÇÃO ---
SENHA_VERMELHO = "sua-senha-secreta"  # Mude esta senha!
ARQUIVO_ESTADO = "game_state.json"
# --------------------

# ATUALIZADO: Define a estrutura de um jogo novo, incluindo a economia
def criar_estado_inicial():
    return {
        "red": {
            "dice": [], "rolled_once": False, "rerolled": False,
            "economy": {"banco": 0, "aposta": 0, "locked": False}
        },
        "blue": {
            "dice": [], "rolled_once": False, "rerolled": False,
            "economy": {"banco": 0, "aposta": 0, "locked": False}
        },
        "revealed_to_all": False,
        "revealed_bets": False,  # NOVO: Flag para revelar apostas
        "revealed_banks": False  # NOVO: Flag para revelar bancos
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
    my_team = st.session_state['team']
    team_color = "🔴" if my_team == 'red' else "🔵"
    st.header(f"Você está no Lado {my_team.capitalize()} {team_color}")
    
    if st.session_state.get('view_my_dice', False) and not game_state[my_team]['rolled_once']:
        st.session_state.view_my_dice = False

    if st.button("🔄 Atualizar Status do Jogo"):
        pass

    # Verifica se ambos os times confirmaram seus valores de aposta
    bets_locked = game_state['red']['economy']['locked'] and game_state['blue']['economy']['locked']

    col1, col2 = st.columns(2)

    # --- LÓGICA DO LADO VERMELHO ---
    with col1:
        st.markdown("<div style='background-color:#8B0000; padding:15px; border-radius:10px; border: 2px solid #FF4136; min-height: 500px;'>", unsafe_allow_html=True)
        st.subheader("Lado Vermelho 🔴")
        
        red_state = game_state['red']
        is_my_turn = my_team == 'red'

        # --- FASE DE APOSTAS ---
        with st.expander("Definir Aposta e Banco", expanded=not red_state['economy']['locked']):
            if not red_state['economy']['locked']:
                if is_my_turn:
                    banco = st.number_input("Seu Banco Total", min_value=0, step=10, key="banco_red")
                    aposta = st.number_input("Sua Aposta Inicial", min_value=0, step=10, key="aposta_red")
                    if st.button("Confirmar Valores (Vermelho)"):
                        if aposta > banco:
                            st.warning("A aposta não pode ser maior que o banco!")
                        else:
                            red_state['economy']['banco'] = banco
                            red_state['economy']['aposta'] = aposta
                            red_state['economy']['locked'] = True
                            salvar_estado(game_state)
                            st.rerun()
                else:
                    st.info("Aguardando o Lado Vermelho definir seus valores.")
            else:
                st.success("Valores confirmados!")
                st.write(f"**Seu Banco:** {red_state['economy']['banco']} 🪙")
                st.write(f"**Sua Aposta Atual:** {red_state['economy']['aposta']} 🪙")

        st.markdown("---")
        
        # --- FASE DE ROLAGEM DE DADOS ---
        if not red_state['rolled_once']:
            if is_my_turn:
                if st.button("Rolar Dados (Vermelho)", disabled=not bets_locked):
                    red_state['dice'] = [random.randint(1, 6) for _ in range(5)]
                    red_state['rolled_once'] = True
                    salvar_estado(game_state)
                    st.rerun()
            else:
                st.info("Aguardando o Lado Vermelho rolar...")
        else:
            st.success("Dados Rolados!")
            if is_my_turn and not st.session_state.get('view_my_dice'):
                if st.button("Ver meus dados 🔴"):
                    st.session_state.view_my_dice = True
                    st.rerun()

        # Botão de dobrar a aposta
        pode_dobrar = red_state['economy']['aposta'] * 2 <= red_state['economy']['banco']
        if is_my_turn and red_state['economy']['locked'] and not game_state['revealed_to_all']:
            if st.button("Dobrar Aposta ⏫", disabled=not pode_dobrar):
                red_state['economy']['aposta'] *= 2
                salvar_estado(game_state)
                st.rerun()

        # Exibição dos dados e re-rolagem
        should_display_dice = game_state['revealed_to_all'] or (is_my_turn and st.session_state.get('view_my_dice'))
        if red_state['rolled_once'] and should_display_dice:
            exibir_dados(red_state['dice'])
            # ... (código de re-rolagem continua aqui, sem alterações) ...
        
        st.markdown("---")
        # --- EXIBIÇÃO PÚBLICA DA ECONOMIA ---
        if game_state['revealed_bets']:
            st.info(f"Aposta Revelada: {red_state['economy']['aposta']} 🪙")
        if game_state['revealed_banks']:
            st.warning(f"Banco Revelado: {red_state['economy']['banco']} 🪙")
        
        st.markdown("</div>", unsafe_allow_html=True)

    # --- LÓGICA DO LADO AZUL ---
    with col2:
        st.markdown("<div style='background-color:#00008B; padding:15px; border-radius:10px; border: 2px solid #0074D9; min-height: 500px;'>", unsafe_allow_html=True)
        st.subheader("Lado Azul 🔵")
        
        blue_state = game_state['blue']
        is_my_turn = my_team == 'blue'

        # --- FASE DE APOSTAS ---
        with st.expander("Definir Aposta e Banco", expanded=not blue_state['economy']['locked']):
            if not blue_state['economy']['locked']:
                if is_my_turn:
                    banco = st.number_input("Seu Banco Total", min_value=0, step=10, key="banco_blue")
                    aposta = st.number_input("Sua Aposta Inicial", min_value=0, step=10, key="aposta_blue")
                    if st.button("Confirmar Valores (Azul)"):
                        if aposta > banco:
                            st.warning("A aposta não pode ser maior que o banco!")
                        else:
                            blue_state['economy']['banco'] = banco
                            blue_state['economy']['aposta'] = aposta
                            blue_state['economy']['locked'] = True
                            salvar_estado(game_state)
                            st.rerun()
                else:
                    st.info("Aguardando o Lado Azul definir seus valores.")
            else:
                st.success("Valores confirmados!")
                st.write(f"**Seu Banco:** {blue_state['economy']['banco']} 🪙")
                st.write(f"**Sua Aposta Atual:** {blue_state['economy']['aposta']} 🪙")
        
        st.markdown("---")

        # --- FASE DE ROLAGEM DE DADOS ---
        if not blue_state['rolled_once']:
            if is_my_turn:
                if st.button("Rolar Dados (Azul)", disabled=not bets_locked):
                    blue_state['dice'] = [random.randint(1, 6) for _ in range(5)]
                    blue_state['rolled_once'] = True
                    salvar_estado(game_state)
                    st.rerun()
            else:
                st.info("Aguardando o Lado Azul rolar...")
        else:
            st.success("Dados Rolados!")
            if is_my_turn and not st.session_state.get('view_my_dice'):
                if st.button("Ver meus dados 🔵"):
                    st.session_state.view_my_dice = True
                    st.rerun()

        # Botão de dobrar a aposta
        pode_dobrar = blue_state['economy']['aposta'] * 2 <= blue_state['economy']['banco']
        if is_my_turn and blue_state['economy']['locked'] and not game_state['revealed_to_all']:
            if st.button("Dobrar Aposta ⏫", disabled=not pode_dobrar):
                blue_state['economy']['aposta'] *= 2
                salvar_estado(game_state)
                st.rerun()

        # Exibição dos dados e re-rolagem
        should_display_dice = game_state['revealed_to_all'] or (is_my_turn and st.session_state.get('view_my_dice'))
        if blue_state['rolled_once'] and should_display_dice:
            exibir_dados(blue_state['dice'])
            # ... (código de re-rolagem aqui, omitido para brevidade, mas deve ser igual ao do Lado Vermelho) ...

        st.markdown("---")
        # --- EXIBIÇÃO PÚBLICA DA ECONOMIA ---
        if game_state['revealed_bets']:
            st.info(f"Aposta Revelada: {blue_state['economy']['aposta']} 🪙")
        if game_state['revealed_banks']:
            st.warning(f"Banco Revelado: {blue_state['economy']['banco']} 🪙")

        st.markdown("</div>", unsafe_allow_html=True)


    # --- CONTROLES DO ANFITRIÃO ---
    if my_team == 'red':
        st.markdown("---")
        st.subheader("Controles do Anfitrião")
        
        # Botões de Revelação Econômica
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            if st.button("Revelar Apostas 💰"):
                game_state['revealed_bets'] = True
                salvar_estado(game_state)
                st.rerun()
        with col_b:
            if st.button("Revelar Bancos 🏦"):
                game_state['revealed_banks'] = True
                salvar_estado(game_state)
                st.rerun()
        
        st.markdown("---")
        
        # Botões de Controle do Jogo
        ambos_rolaram = game_state['red']['rolled_once'] and game_state['blue']['rolled_once']
        if st.button("REVELAR DADOS PARA TODOS", disabled=not ambos_rolaram or game_state['revealed_to_all']):
            game_state['revealed_to_all'] = True
            salvar_estado(game_state)
            st.rerun()

        if st.button("Resetar Jogo para uma Nova Rodada"):
            novo_estado = criar_estado_inicial()
            salvar_estado(novo_estado)
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
