import sqlite3

DB_NAME = "evolucao_pessoal.db"


def conectar():
    return sqlite3.connect(DB_NAME)


def criar_tabelas():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS metas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            descricao TEXT,
            area TEXT,
            status TEXT DEFAULT 'Ativa',
            progresso INTEGER DEFAULT 0,
            data_criacao TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tarefas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            descricao TEXT,
            prioridade TEXT,
            prazo TEXT,
            status TEXT DEFAULT 'Pendente',
            meta_id INTEGER,
            data_criacao TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (meta_id) REFERENCES metas(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS habitos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            descricao TEXT,
            frequencia TEXT,
            meta_id INTEGER,
            data_inicio TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (meta_id) REFERENCES metas(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS registro_habitos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            habito_id INTEGER,
            data TEXT,
            FOREIGN KEY (habito_id) REFERENCES habitos(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS compromissos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            data TEXT,
            hora TEXT,
            observacao TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS financas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo TEXT,
            descricao TEXT,
            valor REAL,
            categoria TEXT,
            data TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS avaliacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mes TEXT,
            area TEXT,
            nota INTEGER,
            data_avaliacao TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS conquistas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT,
            descricao TEXT,
            data TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


# --- METAS ---
def adicionar_meta(titulo, descricao, area):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO metas (titulo, descricao, area) VALUES (?, ?, ?)",
        (titulo, descricao, area),
    )
    conn.commit()
    conn.close()


def listar_metas():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM metas ORDER BY status, titulo")
    rows = cursor.fetchall()
    conn.close()
    return rows


def atualizar_progresso_meta(meta_id):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT COUNT(*) FROM tarefas WHERE meta_id = ?",
        (meta_id,),
    )
    total = cursor.fetchone()[0]
    if total == 0:
        conn.close()
        return
    cursor.execute(
        "SELECT COUNT(*) FROM tarefas WHERE meta_id = ? AND status = 'Concluída'",
        (meta_id,),
    )
    concluidas = cursor.fetchone()[0]
    progresso = int((concluidas / total) * 100)
    cursor.execute(
        "UPDATE metas SET progresso = ? WHERE id = ?",
        (progresso, meta_id),
    )
    conn.commit()
    conn.close()


def excluir_meta(id):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM metas WHERE id = ?", (id,))
    conn.commit()
    conn.close()


# --- TAREFAS ---
def adicionar_tarefa(titulo, descricao, prioridade, prazo, meta_id=None):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO tarefas (titulo, descricao, prioridade, prazo, meta_id)
        VALUES (?, ?, ?, ?, ?)
        """,
        (titulo, descricao, prioridade, prazo, meta_id),
    )
    conn.commit()
    conn.close()
    if meta_id:
        atualizar_progresso_meta(meta_id)


def listar_tarefas(status=None):
    conn = conectar()
    cursor = conn.cursor()
    if status:
        cursor.execute(
            "SELECT * FROM tarefas WHERE status = ? ORDER BY prazo",
            (status,),
        )
    else:
        cursor.execute("SELECT * FROM tarefas ORDER BY status, prazo")
    rows = cursor.fetchall()
    conn.close()
    return rows


def concluir_tarefa(id):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE tarefas SET status = 'Concluída' WHERE id = ?",
        (id,),
    )
    cursor.execute("SELECT meta_id FROM tarefas WHERE id = ?", (id,))
    row = cursor.fetchone()
    conn.commit()
    conn.close()
    if row and row[0]:
        atualizar_progresso_meta(row[0])


def excluir_tarefa(id):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT meta_id FROM tarefas WHERE id = ?", (id,))
    row = cursor.fetchone()
    cursor.execute("DELETE FROM tarefas WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    if row and row[0]:
        atualizar_progresso_meta(row[0])


# --- HÁBITOS ---
def adicionar_habito(nome, descricao, frequencia, meta_id=None):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO habitos (nome, descricao, frequencia, meta_id) VALUES (?, ?, ?, ?)",
        (nome, descricao, frequencia, meta_id),
    )
    conn.commit()
    conn.close()


def listar_habitos():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM habitos ORDER BY nome")
    rows = cursor.fetchall()
    conn.close()
    return rows


def registrar_habito(habito_id, data):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO registro_habitos (habito_id, data) VALUES (?, ?)",
        (habito_id, data),
    )
    conn.commit()
    conn.close()


def contar_registros_habito(habito_id):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT COUNT(*) FROM registro_habitos WHERE habito_id = ?",
        (habito_id,),
    )
    total = cursor.fetchone()[0]
    conn.close()
    return total


def excluir_habito(id):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM habitos WHERE id = ?", (id,))
    conn.commit()
    conn.close()


# --- COMPROMISSOS ---
def adicionar_compromisso(titulo, data, hora, observacao):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO compromissos (titulo, data, hora, observacao) VALUES (?, ?, ?, ?)",
        (titulo, data, hora, observacao),
    )
    conn.commit()
    conn.close()


def listar_compromissos(data=None):
    conn = conectar()
    cursor = conn.cursor()
    if data:
        cursor.execute(
            "SELECT * FROM compromissos WHERE data = ? ORDER BY hora",
            (data,),
        )
    else:
        cursor.execute("SELECT * FROM compromissos ORDER BY data, hora")
    rows = cursor.fetchall()
    conn.close()
    return rows


def excluir_compromisso(id):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM compromissos WHERE id = ?", (id,))
    conn.commit()
    conn.close()


# --- FINANÇAS ---
def adicionar_financa(tipo, descricao, valor, categoria, data):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO financas (tipo, descricao, valor, categoria, data)
        VALUES (?, ?, ?, ?, ?)
        """,
        (tipo, descricao, valor, categoria, data),
    )
    conn.commit()
    conn.close()


def listar_financas():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM financas ORDER BY data")
    rows = cursor.fetchall()
    conn.close()
    return rows


def excluir_financa(id):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM financas WHERE id = ?", (id,))
    conn.commit()
    conn.close()


# --- AVALIAÇÕES ---
def salvar_avaliacao(mes, area, nota):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO avaliacoes (mes, area, nota) VALUES (?, ?, ?)",
        (mes, area, nota),
    )
    conn.commit()
    conn.close()


def listar_avaliacoes():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM avaliacoes ORDER BY id")
    rows = cursor.fetchall()
    conn.close()
    return rows


# --- CONQUISTAS ---
def adicionar_conquista(nome, descricao):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO conquistas (nome, descricao) VALUES (?, ?)",
        (nome, descricao),
    )
    conn.commit()
    conn.close()


def listar_conquistas():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM conquistas ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return rows


def verificar_conquistas():
    conquistas = []
    tarefas = listar_tarefas()
    concluidas = [t for t in tarefas if t[5] == "Concluída"]
    habitos = listar_habitos()
    metas = listar_metas()

    if len(concluidas) >= 1:
        conquistas.append(("Primeira tarefa concluída", "Você completou sua primeira tarefa."))
    if len(concluidas) >= 5:
        conquistas.append(("Mão na massa", "Você concluiu 5 tarefas."))
    if len(habitos) >= 1:
        conquistas.append(("Primeiro hábito", "Você criou seu primeiro hábito."))
    if len(metas) >= 1:
        conquistas.append(("Primeira meta", "Você definiu sua primeira meta."))
    if any(m[5] == 100 for m in metas):
        conquistas.append(("Meta concluída", "Você concluiu uma meta!"))

    salvas = listar_conquistas()
    nomes_salvos = [s[1] for s in salvas]
    for nome, descricao in conquistas:
        if nome not in nomes_salvos:
            adicionar_conquista(nome, descricao)
