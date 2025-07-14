import streamlit as st
import json
import os
import random
import time

# --- CONFIGURAÇÃO ---
SENHA_VERMELHO = "sua-senha-secreta"  # Mude esta senha!
ARQUIVO_ESTADO = "game_state.json"
# --------------------

def criar_estado_inicial():
    """Retorna a estrutura de um estado de jogo zerado com um novo game_id."""
    return {
        "game_id": time.time(),  # CORREÇÃO: ID único para cada jogo
        "red": {"rolled": False, "rerolled": False, "dice": []},
        "blue": {"rolled": False, "rerolled": False, "dice": []},
        "revealed": False
    }

def carregar_estado():
    """Lê o estado do jogo do arquivo JSON. Se não existir, cria um novo."""
    if os.path.exists(ARQUIVO_ESTADO):
        with open(ARQUIVO_ESTADO, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return criar_estado_inicial()
    else:
        return criar_estado_inicial()

def salvar_estado(estado):
    """Salva o estado atual do jogo no arquivo JSON."""
    with open(ARQUIVO_ESTADO, 'w') as f:
        json.dump(estado, f, indent=4)

def resetar_jogo_local():
    """Limpa a sessão local do usuário."""
    keys_to_keep = ['team'] # Mantém a informação do time
    for key in list(st.session_state.keys()):
        if key not in keys_to_keep:
            del st.session_state[key]
    st.session_state.view_my_dice = False

# --- FUNÇÃO AUXILIAR PARA EXIBIR DADOS ---
def exibir_dados(dados):
    """Renderiza os dados em um formato bonito."""
    dados_html = " ".join([f"<span style='font-size: 2em; display: inline-block; margin: 0 5px;'>{d}</span>" for d in dados])
    st.markdown(f"<div style='background-color:white; color:black; text-align:center; padding: 10px; border-radius:5px;'>{dados_html}</div>", unsafe_allow_html=True)

# --- INTERFACE DO USUÁRIO (UI) ---
st.set_page_config(page_title="Jogo de Dados Secreto", layout="centered")
st.title("🎲 Jogo de Dados Secreto 🎲")

game_state = carregar_estado()

# --- CORREÇÃO DO BUG DE RESET: Verificação de Sincronia ---
# Se o ID do jogo no servidor for diferente do que temos na sessão, o jogo foi resetado.
if st.session_state.get('game_id') != game_state.get('game_id'):
    resetar_jogo_local()
    st.session_state.game_id = game_state.get('game_id')
    st.rerun()

# --- TELA DE LOGIN ---
if 'team' not in st.session_state:
    st.header("Escolha seu Lado")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Lado Azul 🔵")
        if st.button("Entrar como Azul"):
            st.session_state.team = 'blue'
            st.session_state.game_id = game_state.get('game_id')
            st.rerun()
    with col2:
        st.subheader("Lado Vermelho 🔴")
        password = st.text_input("Senha do Anfitrião", type="password", key="pwd_input")
        if st.button("Entrar como Vermelho"):
            if password == SENHA_VERMELHO:
                st.session_state.team = 'red'
                st.session_state.game_id = game_state.get('game_id')
                st.rerun()
            else:
                st.error("Senha incorreta!")

# --- TELA DO JOGO ---
else:
    team_color = "🔴" if st.session_state.team == 'red' else "🔵"
    st.header(f"Você está no Lado {st.session_state.team.capitalize()} {team_color}")
    
    if st.button("🔄 Atualizar Status do Jogo"):
        st.rerun()

    # Define o estado do time atual para facilitar o acesso
    my_team_state = game_state[st.session_state.team]
    
    col1, col2 = st.columns(2)

    for team, team_box in [("red", col1), ("blue", col2)]:
        with team_box:
            team_name = "Vermelho" if team == "red" else "Azul"
            team_emoji = "🔴" if team == "red" else "🔵"
            bg_color = "#8B0000" if team == "red" else "#00008B"
            border_color = "#FF4136" if team == "red" else "#0074D9"
            
            st.markdown(f"<div style='background-color:{bg_color}; padding:15px; border-radius:10px; border: 2px solid {border_color}; min-height: 350px;'>", unsafe_allow_html=True)
            st.subheader(f"Lado {team_name} {team_emoji}")

            current_team_state = game_state[team]
            is_my_turn = st.session_state.team == team

            if not current_team_state['rolled']:
                if is_my_turn:
                    if st.button(f"Rolar Dados ({team_name})", key=f"roll_{team}"):
                        current_team_state['dice'] = [random.randint(1, 6) for _ in range(5)]
                        current_team_state['rolled'] = True
                        salvar_estado(game_state)
                        st.rerun()
                else:
                    st.info(f"Aguardando o Lado {team_name} rolar...")
            else: # Se já rolou
                st.success("Dados Rolados!")
                if is_my_turn and not st.session_state.get('view_my_dice', False):
                    if st.button(f"Ver meus dados {team_emoji}", key=f"view_{team}"):
                        st.session_state.view_my_dice = True
                        st.rerun()

            # Exibir dados e opção de re-rolagem
            should_display_dice = game_state['revealed'] or (is_my_turn and st.session_state.get('view_my_dice'))
            
            if current_team_state['rolled'] and should_display_dice:
                exibir_dados(current_team_state['dice'])

                # NOVA FUNCIONALIDADE: Re-rolar dados
                if is_my_turn and not current_team_state['rerolled']:
                    st.markdown("---")
                    st.write("Escolha até 2 dados para rolar novamente:")
                    
                    options_map = {f"Dado #{i+1} (valor: {d})": i for i, d in enumerate(current_team_state['dice'])}
                    dice_to_reroll_labels = st.multiselect(
                        "Selecione os dados",
                        options=options_map.keys(),
                        max_selections=2,
                        key=f"reroll_select_{team}"
                    )
                    
                    if st.button("Rolar dados selecionados", key=f"reroll_btn_{team}"):
                        indices_to_reroll = [options_map[label] for label in dice_to_reroll_labels]
                        for i in indices_to_reroll:
                            current_team_state['dice'][i] = random.randint(1, 6)
                        
                        current_team_state['rerolled'] = True
                        salvar_estado(game_state)
                        st.rerun()
                elif current_team_state['rerolled']:
                    st.info("Você já rolou os dados novamente.")

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
            novo_estado = criar_estado_inicial()
            salvar_estado(novo_estado)
            st.rerun()
