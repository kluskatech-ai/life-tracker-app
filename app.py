import streamlit as st
import pandas as pd
import database as db
from datetime import date, datetime

db.criar_tabelas()

st.set_page_config(
    page_title="Evolução Pessoal",
    page_icon="🎯",
    layout="wide",
)

areas_vida = [
    "Saúde",
    "Família",
    "Relacionamento",
    "Finanças",
    "Carreira",
    "Desenvolvimento Pessoal",
    "Espiritualidade",
    "Diversão e Lazer",
    "Contribuição Social",
    "Ambiente e Organização",
]

menu = st.sidebar.radio(
    "Navegação",
    ["Hoje", "Tarefas", "Hábitos", "Metas", "Agenda", "Finanças", "Evolução"],
)

db.verificar_conquistas()


# --- helpers de ação para evitar erro removeChild ---
def acao_tarefa(tarefa_id, tipo):
    st.session_state["acao_tarefa"] = {"id": tarefa_id, "tipo": tipo}


def processar_acao_tarefa():
    if "acao_tarefa" in st.session_state:
        acao = st.session_state["acao_tarefa"]
        if acao["tipo"] == "concluir":
            db.concluir_tarefa(acao["id"])
            st.toast("Tarefa concluída!", icon="✅")
        elif acao["tipo"] == "excluir":
            db.excluir_tarefa(acao["id"])
            st.toast("Tarefa removida!", icon="🗑️")
        del st.session_state["acao_tarefa"]
        st.rerun()


def acao_habito(habito_id):
    st.session_state["acao_habito"] = habito_id


def processar_acao_habito():
    if "acao_habito" in st.session_state:
        db.registrar_habito(st.session_state["acao_habito"], date.today().isoformat())
        st.toast("Hábito registrado!", icon="🔥")
        del st.session_state["acao_habito"]
        st.rerun()


def acao_generica(chave, funcao, mensagem, icone):
    if chave in st.session_state:
        funcao(st.session_state[chave])
        st.toast(mensagem, icon=icone)
        del st.session_state[chave]
        st.rerun()


# ====================
# TELA HOJE
# ====================
if menu == "Hoje":
    st.title("📍 Hoje")
    st.markdown("O que importa agora, o que já avancei e qual é o próximo passo.")

    pendentes = db.listar_tarefas("Pendente")
    habitos = db.listar_habitos()
    metas = db.listar_metas()
    hoje_str = date.today().isoformat()
    compromissos_hoje = db.listar_compromissos(hoje_str)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Tarefas pendentes", len(pendentes))
    col2.metric("Hábitos ativos", len(habitos))
    col3.metric("Metas ativas", len([m for m in metas if m[4] == "Ativa"]))
    col4.metric("Compromissos hoje", len(compromissos_hoje))

    st.subheader("Compromissos de hoje")
    if compromissos_hoje:
        for c in compromissos_hoje:
            st.write(f"**{c[3]}** — {c[1]} | {c[4] or ''}")
    else:
        st.info("Nenhum compromisso para hoje.")

    st.subheader("Próximas tarefas")
    if pendentes:
        for t in pendentes[:5]:
            st.write(f"- **{t[1]}** | {t[3]} | até {t[4]}")
    else:
        st.info("Nenhuma tarefa pendente.")

    conquistas = db.listar_conquistas()
    if conquistas:
        st.subheader("🏆 Conquistas recentes")
        for c in conquistas[:3]:
            st.success(f"**{c[1]}**: {c[2]}")


# ====================
# TELA TAREFAS
# ====================
elif menu == "Tarefas":
    st.title("✅ Tarefas")
    processar_acao_tarefa()

    with st.form("nova_tarefa", clear_on_submit=True):
        st.subheader("Nova tarefa")
        titulo = st.text_input("Título *")
        descricao = st.text_area("Descrição")
        prioridade = st.selectbox("Prioridade", ["Alta", "Média", "Baixa"])
        prazo = st.date_input("Prazo", value=date.today())

        metas = db.listar_metas()
        opcoes_meta = {"Nenhuma": None}
        for m in metas:
            opcoes_meta[f"{m[1]}"] = m[0]

        meta_nome = st.selectbox("Vincular à meta", list(opcoes_meta.keys()))
        enviar = st.form_submit_button("Adicionar tarefa")

        if enviar and titulo:
            db.adicionar_tarefa(
                titulo,
                descricao,
                prioridade,
                prazo.isoformat(),
                opcoes_meta[meta_nome],
            )
            st.success("Tarefa adicionada!")
            st.rerun()

    st.divider()

    st.subheader("Tarefas pendentes")
    tarefas = db.listar_tarefas("Pendente")
    if tarefas:
        for t in tarefas:
            col1, col2, col3 = st.columns([4, 1, 1])
            with col1:
                st.write(f"**{t[1]}** | {t[3]} | até {t[4]}")
            with col2:
                st.button(
                    "Concluir",
                    key=f"ok_{t[0]}",
                    on_click=acao_tarefa,
                    args=(t[0], "concluir"),
                )
            with col3:
                st.button(
                    "Excluir",
                    key=f"del_{t[0]}",
                    on_click=acao_tarefa,
                    args=(t[0], "excluir"),
                )
    else:
        st.info("Nenhuma tarefa pendente.")

    st.subheader("Tarefas concluídas")
    concluidas = db.listar_tarefas("Concluída")
    if concluidas:
        for t in concluidas:
            st.write(f"~~{t[1]}~~ ✅")
    else:
        st.info("Nenhuma tarefa concluída ainda.")


# ====================
# TELA HÁBITOS
# ====================
elif menu == "Hábitos":
    st.title("🔁 Hábitos")
    acao_generica(
        "acao_habito",
        lambda x: db.registrar_habito(x, date.today().isoformat()),
        "Hábito registrado!",
        "🔥",
    )

    with st.form("novo_habito", clear_on_submit=True):
        st.subheader("Novo hábito")
        nome = st.text_input("Nome do hábito *")
        descricao = st.text_area("Descrição")
        frequencia = st.selectbox(
            "Frequência", ["Diário", "Semanal", "Seg a Sex", "Fins de semana"]
        )

        metas = db.listar_metas()
        opcoes_meta = {"Nenhuma": None}
        for m in metas:
            opcoes_meta[f"{m[1]}"] = m[0]

        meta_nome = st.selectbox("Vincular à meta", list(opcoes_meta.keys()))
        enviar = st.form_submit_button("Criar hábito")

        if enviar and nome:
            db.adicionar_habito(nome, descricao, frequencia, opcoes_meta[meta_nome])
            st.success("Hábito criado!")
            st.rerun()

    st.divider()

    habitos = db.listar_habitos()
    metas_dict = {m[0]: m[1] for m in db.listar_metas()}

    if habitos:
        st.subheader("Meus hábitos")
        for h in habitos:
            total = db.contar_registros_habito(h[0])
            meta_texto = ""
            if h[4] and h[4] in metas_dict:
                meta_texto = f" | meta: {metas_dict[h[4]]}"

            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.write(f"**{h[1]}** | {h[3]} | registros: {total}{meta_texto}")
            with col2:
                st.button(
                    "Registrei hoje",
                    key=f"hab_{h[0]}",
                    on_click=acao_habito,
                    args=(h[0],),
                )
            with col3:
                if st.button("Excluir", key=f"del_hab_{h[0]}"):
                    db.excluir_habito(h[0])
                    st.rerun()
    else:
        st.info("Nenhum hábito cadastrado.")


# ====================
# TELA METAS
# ====================
elif menu == "Metas":
    st.title("🎯 Metas")

    with st.form("nova_meta", clear_on_submit=True):
        st.subheader("Nova meta")
        titulo = st.text_input("Título da meta *")
        descricao = st.text_area("Descrição")
        area = st.selectbox("Área da vida", areas_vida)
        enviar = st.form_submit_button("Criar meta")

        if enviar and titulo:
            db.adicionar_meta(titulo, descricao, area)
            st.success("Meta criada!")
            st.rerun()

    st.divider()

    metas = db.listar_metas()
    if metas:
        st.subheader("Metas ativas")
        for m in metas:
            col1, col2 = st.columns([4, 1])
            with col1:
                st.write(f"**{m[1]}** | {m[3]} | Progresso: {m[5]}%")
                st.progress(m[5] / 100)
            with col2:
                if st.button("Excluir", key=f"del_meta_{m[0]}"):
                    db.excluir_meta(m[0])
                    st.rerun()
    else:
        st.info("Nenhuma meta cadastrada.")


# ====================
# TELA AGENDA
# ====================
elif menu == "Agenda":
    st.title("📅 Agenda")

    with st.form("novo_compromisso", clear_on_submit=True):
        st.subheader("Novo compromisso")
        titulo = st.text_input("Título *")
        data = st.date_input("Data", value=date.today())
        hora = st.time_input("Hora", value=datetime.strptime("09:00", "%H:%M").time())
        observacao = st.text_area("Observação")
        enviar = st.form_submit_button("Adicionar compromisso")

        if enviar and titulo:
            db.adicionar_compromisso(
                titulo,
                data.isoformat(),
                hora.strftime("%H:%M"),
                observacao,
            )
            st.success("Compromisso adicionado!")
            st.rerun()

    st.divider()

    st.subheader("Próximos compromissos")
    compromissos = db.listar_compromissos()
    if compromissos:
        for c in compromissos:
            col1, col2 = st.columns([5, 1])
            with col1:
                st.write(f"**{c[2]}** às **{c[3]}** — {c[1]} | {c[4] or ''}")
            with col2:
                if st.button("Excluir", key=f"del_comp_{c[0]}"):
                    db.excluir_compromisso(c[0])
                    st.rerun()
    else:
        st.info("Nenhum compromisso cadastrado.")


# ====================
# TELA FINANÇAS
# ====================
elif menu == "Finanças":
    st.title("💰 Finanças")

    with st.form("nova_financa", clear_on_submit=True):
        st.subheader("Novo lançamento")
        tipo = st.selectbox("Tipo", ["Receita", "Despesa"])
        descricao = st.text_input("Descrição *")
        valor = st.number_input("Valor *", min_value=0.0, format="%.2f")
        categoria = st.selectbox(
            "Categoria",
            ["Salário", "Investimentos", "Alimentação", "Transporte", "Moradia", "Saúde", "Lazer", "Outros"],
        )
        data = st.date_input("Data", value=date.today())
        enviar = st.form_submit_button("Adicionar lançamento")

        if enviar and descricao and valor > 0:
            db.adicionar_financa(
                tipo,
                descricao,
                valor,
                categoria,
                data.isoformat(),
            )
            st.success("Lançamento adicionado!")
            st.rerun()

    st.divider()

    financas = db.listar_financas()
    if financas:
        st.subheader("Lançamentos")
        for f in financas:
            sinal = "+" if f[1] == "Receita" else "-"
            col1, col2 = st.columns([5, 1])
            with col1:
                st.write(f"**{f[5]}** | {sinal} R$ {f[3]:,.2f} | {f[2]} ({f[4]})")
            with col2:
                if st.button("Excluir", key=f"del_fin_{f[0]}"):
                    db.excluir_financa(f[0])
                    st.rerun()

        df = pd.DataFrame(
            financas, columns=["ID", "Tipo", "Descrição", "Valor", "Categoria", "Data"]
        )
        receitas = df[df["Tipo"] == "Receita"]["Valor"].sum()
        despesas = df[df["Tipo"] == "Despesa"]["Valor"].sum()
        saldo = receitas - despesas

        st.divider()
        col1, col2, col3 = st.columns(3)
        col1.metric("Receitas", f"R$ {receitas:,.2f}")
        col2.metric("Despesas", f"R$ {despesas:,.2f}")
        col3.metric("Saldo", f"R$ {saldo:,.2f}")
    else:
        st.info("Nenhum lançamento cadastrado.")


# ====================
# TELA EVOLUÇÃO
# ====================
elif menu == "Evolução":
    st.title("📊 Mapa de Evolução")
    st.markdown("Avalie suas 10 áreas da vida de 0 a 10.")

    with st.form("formulario_avaliacao"):
        nome_mes = st.text_input(
            "Mês de referência", value=date.today().strftime("%m/%Y")
        )
        notas = {}
        col1, col2 = st.columns(2)
        for i, area in enumerate(areas_vida):
            with col1 if i % 2 == 0 else col2:
                notas[area] = st.slider(area, 0, 10, 5)
        enviar = st.form_submit_button("Salvar avaliação")

    if enviar:
        media_geral = sum(notas.values()) / len(notas)
        for area, nota in notas.items():
            db.salvar_avaliacao(nome_mes, area, nota)
        st.success(f"Avaliação de {nome_mes} salva com sucesso!")
        st.metric("Média Geral", f"{media_geral:.2f}")

    avaliacoes = db.listar_avaliacoes()
    if avaliacoes:
        st.subheader("📊 Histórico de Avaliações")
        df = pd.DataFrame(
            avaliacoes, columns=["ID", "Mês", "Área", "Nota", "Data"]
        )
        st.dataframe(df, width="stretch")

        st.subheader("📈 Última Avaliação por Área")
        ultimo_mes = df["Mês"].iloc[-1]
        ultima = df[df["Mês"] == ultimo_mes].set_index("Área")["Nota"]
        st.bar_chart(ultima)
