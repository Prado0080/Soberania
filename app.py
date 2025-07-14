import streamlit as st
import json
import os
import random

# --- CONFIGURAÇÃO ---
SENHA_VERMELHO = "008"  # Mude esta senha!
ARQUIVO_ESTADO = "game_state.json"
# --------------------

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
        "revealed_bets": False,
        "revealed_banks": False
    }

def carregar_estado():
    if os.path.exists(ARQUIVO_ESTADO):
        with open(ARQUIVO_ESTADO, 'r') as f:
            try:
                estado = json.load(f)
                if 'economy' not in estado.get('red', {}):
                    return criar_estado_inicial()
                return estado
            except (json.JSONDecodeError, KeyError):
                return criar_estado_inicial()
    return criar_estado_inicial()

def salvar_estado(estado):
    with open(ARQUIVO_ESTADO, 'w') as f:
        json.dump(estado, f, indent=4)

def exibir_dados(dados):
    dados_html = " ".join([f"<span style='font-size: 2em; display: inline-block; margin: 0 5px;'>{d}</span>" for d in dados])
    st.markdown(f"<div style='background-color:white; color:black; text-align:center; padding: 10px; border-radius:5px;'>{dados_html}</div>", unsafe_allow_html=True)

# --- LÓGICA PRINCIPAL DO APLICATIVO ---
st.set_page_config(page_title="Soberania", layout="centered")
st.title("🎲 Soberania 🎲")

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

    bets_locked = game_state['red']['economy']['locked'] and game_state['blue']['economy']['locked']
    col1, col2 = st.columns(2)

    # --- LÓGICA DO LADO VERMELHO ---
    with col1:
        st.markdown("<div style='background-color:#8B0000; padding:15px; border-radius:10px; border: 2px solid #FF4136; min-height: 500px;'>", unsafe_allow_html=True)
        st.subheader("Lado Vermelho 🔴")
        red_state = game_state['red']
        is_my_team = my_team == 'red'

        with st.expander("Definir Aposta e Banco", expanded=not red_state['economy']['locked']):
            if not red_state['economy']['locked']:
                if is_my_team:
                    banco = st.number_input("Seu Banco Total", min_value=0, step=10, key="banco_red")
                    aposta = st.number_input("Sua Aposta Inicial", min_value=0, step=10, key="aposta_red")
                    if st.button("Confirmar Valores (Vermelho)"):
                        if aposta > banco:
                            st.warning("A aposta não pode ser maior que o banco!")
                        else:
                            red_state['economy'].update({"banco": banco, "aposta": aposta, "locked": True})
                            salvar_estado(game_state)
                            st.rerun()
                else: st.info("Aguardando definição de valores.")
            else:
                st.success("Valores confirmados!")
                # CORRIGIDO: Só mostra os valores para o jogador do time certo.
                if is_my_team:
                    st.write(f"**Seu Banco:** {red_state['economy']['banco']} 🪙")
                    st.write(f"**Sua Aposta Atual:** {red_state['economy']['aposta']} 🪙")
        st.markdown("---")

        if not red_state['rolled_once']:
            if is_my_team:
                if st.button("Rolar Dados (Vermelho)", disabled=not bets_locked):
                    red_state.update({"dice": [random.randint(1, 6) for _ in range(5)], "rolled_once": True})
                    salvar_estado(game_state)
                    st.rerun()
            else: st.info("Aguardando o Lado Vermelho rolar...")
        else:
            st.success("Dados Rolados!")
            if is_my_team and not st.session_state.get('view_my_dice'):
                if st.button("Ver meus dados 🔴"):
                    st.session_state.view_my_dice = True
                    st.rerun()
        
        pode_dobrar = red_state['economy']['aposta'] * 2 <= red_state['economy']['banco']
        if is_my_team and red_state['economy']['locked'] and not game_state['revealed_to_all']:
            # ATUALIZADO: Botão com novo estilo.
            if st.button("DOBRAR APOSTA 💥", disabled=not pode_dobrar, key="double_red"):
                red_state['economy']['aposta'] *= 2
                salvar_estado(game_state)
                st.rerun()

        should_display_dice = game_state['revealed_to_all'] or (is_my_team and st.session_state.get('view_my_dice'))
        if red_state['rolled_once'] and should_display_dice:
            exibir_dados(red_state['dice'])
            # ATUALIZADO: Lógica de re-rolagem só aparece se os dados ainda não foram revelados para todos.
            if is_my_team and not red_state['rerolled'] and not game_state['revealed_to_all']:
                st.markdown("---")
                options_map = {f"Dado #{i+1} (valor: {d})": i for i, d in enumerate(red_state['dice'])}
                dice_to_reroll = st.multiselect("Escolha até 2 dados para rolar novamente:", options_map.keys(), max_selections=2, key="reroll_red")
                if st.button("Rolar selecionados (Vermelho)"):
                    indices = [options_map[label] for label in dice_to_reroll]
                    for i in indices: red_state['dice'][i] = random.randint(1, 6)
                    red_state['rerolled'] = True
                    salvar_estado(game_state)
                    st.rerun()
            elif red_state['rerolled']: st.info("Re-rolagem já utilizada.")
        
        st.markdown("---")
        if game_state['revealed_bets']: st.info(f"Aposta Revelada: {red_state['economy']['aposta']} 🪙")
        if game_state['revealed_banks']: st.warning(f"Banco Revelado: {red_state['economy']['banco']} 🪙")
        st.markdown("</div>", unsafe_allow_html=True)

    # --- LÓGICA DO LADO AZUL ---
    with col2:
        st.markdown("<div style='background-color:#00008B; padding:15px; border-radius:10px; border: 2px solid #0074D9; min-height: 500px;'>", unsafe_allow_html=True)
        st.subheader("Lado Azul 🔵")
        blue_state = game_state['blue']
        is_my_team = my_team == 'blue'

        with st.expander("Definir Aposta e Banco", expanded=not blue_state['economy']['locked']):
            if not blue_state['economy']['locked']:
                if is_my_team:
                    banco = st.number_input("Seu Banco Total", min_value=0, step=10, key="banco_blue")
                    aposta = st.number_input("Sua Aposta Inicial", min_value=0, step=10, key="aposta_blue")
                    if st.button("Confirmar Valores (Azul)"):
                        if aposta > banco:
                            st.warning("A aposta não pode ser maior que o banco!")
                        else:
                            blue_state['economy'].update({"banco": banco, "aposta": aposta, "locked": True})
                            salvar_estado(game_state)
                            st.rerun()
                else: st.info("Aguardando definição de valores.")
            else:
                st.success("Valores confirmados!")
                # CORRIGIDO: Só mostra os valores para o jogador do time certo.
                if is_my_team:
                    st.write(f"**Seu Banco:** {blue_state['economy']['banco']} 🪙")
                    st.write(f"**Sua Aposta Atual:** {blue_state['economy']['aposta']} 🪙")
        st.markdown("---")

        if not blue_state['rolled_once']:
            if is_my_team:
                if st.button("Rolar Dados (Azul)", disabled=not bets_locked):
                    blue_state.update({"dice": [random.randint(1, 6) for _ in range(5)], "rolled_once": True})
                    salvar_estado(game_state)
                    st.rerun()
            else: st.info("Aguardando o Lado Azul rolar...")
        else:
            st.success("Dados Rolados!")
            if is_my_team and not st.session_state.get('view_my_dice'):
                if st.button("Ver meus dados 🔵"):
                    st.session_state.view_my_dice = True
                    st.rerun()

        pode_dobrar = blue_state['economy']['aposta'] * 2 <= blue_state['economy']['banco']
        if is_my_team and blue_state['economy']['locked'] and not game_state['revealed_to_all']:
            # ATUALIZADO: Botão com novo estilo.
            if st.button("DOBRAR APOSTA 💥", disabled=not pode_dobrar, key="double_blue"):
                blue_state['economy']['aposta'] *= 2
                salvar_estado(game_state)
                st.rerun()
        
        should_display_dice = game_state['revealed_to_all'] or (is_my_team and st.session_state.get('view_my_dice'))
        if blue_state['rolled_once'] and should_display_dice:
            exibir_dados(blue_state['dice'])
            # ATUALIZADO: Lógica de re-rolagem só aparece se os dados ainda não foram revelados para todos.
            if is_my_team and not blue_state['rerolled'] and not game_state['revealed_to_all']:
                st.markdown("---")
                options_map = {f"Dado #{i+1} (valor: {d})": i for i, d in enumerate(blue_state['dice'])}
                dice_to_reroll = st.multiselect("Escolha até 2 dados para rolar novamente:", options_map.keys(), max_selections=2, key="reroll_blue")
                if st.button("Rolar selecionados (Azul)"):
                    indices = [options_map[label] for label in dice_to_reroll]
                    for i in indices: blue_state['dice'][i] = random.randint(1, 6)
                    blue_state['rerolled'] = True
                    salvar_estado(game_state)
                    st.rerun()
            elif blue_state['rerolled']: st.info("Re-rolagem já utilizada.")

        st.markdown("---")
        if game_state['revealed_bets']: st.info(f"Aposta Revelada: {blue_state['economy']['aposta']} 🪙")
        if game_state['revealed_banks']: st.warning(f"Banco Revelado: {blue_state['economy']['banco']} 🪙")
        st.markdown("</div>", unsafe_allow_html=True)

    # --- CONTROLES DO ANFITRIÃO ---
    if my_team == 'red':
        st.markdown("---")
        st.subheader("Controles do Anfitrião")
        col_a, col_b, col_c, col_d = st.columns(4)
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
        with col_c:
            ambos_rolaram = game_state['red']['rolled_once'] and game_state['blue']['rolled_once']
            if st.button("REVELAR DADOS", disabled=not ambos_rolaram or game_state['revealed_to_all']):
                game_state['revealed_to_all'] = True
                salvar_estado(game_state)
                st.rerun()
        with col_d:
            if st.button("Resetar Jogo"):
                novo_estado = criar_estado_inicial()
                salvar_estado(novo_estado)
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()
