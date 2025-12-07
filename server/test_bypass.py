"""
Teste com bypass completo de arquivos de configuração
"""

import os
import sys

# ANTES de qualquer import, limpar TODAS as variáveis PostgreSQL
pg_vars = [
    "PGAPPNAME",
    "PGCLIENTENCODING",
    "PGCONNECT_TIMEOUT",
    "PGDATABASE",
    "PGDATESTYLE",
    "PGGSSLIB",
    "PGHOST",
    "PGHOSTADDR",
    "PGKRBSRVNAME",
    "PGLOCALEDIR",
    "PGOPTIONS",
    "PGPASSFILE",
    "PGPASSWORD",
    "PGPORT",
    "PGSERVICE",
    "PGSERVICEFILE",
    "PGSSL",
    "PGSSLCERT",
    "PGSSLCOMPRESSION",
    "PGSSLCRL",
    "PGSSLKEY",
    "PGSSLMODE",
    "PGSSLROOTCERT",
    "PGSYSCONFDIR",
    "PGTARGETSESSIONATTRS",
    "PGTZ",
    "PGUSER",
    "PGGEQO",
]

for var in pg_vars:
    if var in os.environ:
        del os.environ[var]

# Definir apenas o necessário
os.environ["PGCLIENTENCODING"] = "UTF8"
os.environ["LC_ALL"] = "C"
os.environ["LANG"] = "C"
os.environ["LANGUAGE"] = "en_US:en"

# Forçar Python para UTF-8
if sys.platform == "win32":
    import codecs

    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer, "strict")
    sys.stderr = codecs.getwriter("utf-8")(sys.stderr.buffer, "strict")

print("=" * 60)
print("TESTE COM BYPASS TOTAL")
print("=" * 60)

print("\n1. Testando com psycopg2 (conexão direta sem arquivos config):")
try:
    import psycopg2

    # Conexão totalmente explícita - sem usar URI
    conn = psycopg2.connect(
        host="172.21.209.118",
        port=5432,
        dbname="propaganda_db",  # Usar 'dbname' ao invés de 'database'
        user="admin",
        password="bd99d0060e",
        connect_timeout=10,
        client_encoding="UTF8",
        application_name="flask_test",
    )

    print("   ✅ CONEXÃO FUNCIONOU!")

    cursor = conn.cursor()
    cursor.execute("SELECT version();")
    version = cursor.fetchone()
    print(f"   PostgreSQL: {version[0][:80]}...")

    cursor.execute("SHOW client_encoding;")
    encoding = cursor.fetchone()
    print(f"   Client encoding: {encoding[0]}")

    cursor.execute("SHOW lc_messages;")
    lc = cursor.fetchone()
    print(f"   LC_MESSAGES: {lc[0]}")

    cursor.close()
    conn.close()

    print("\n   🎉 SUCESSO! O problema NÃO é o PostgreSQL!")
    print("   O problema é como o psycopg2 lê a URI ou arquivos locais.")

except Exception as e:
    print(f"   ❌ ERRO: {e}")
    print("\n   Se der erro de encoding aqui, o problema é:")
    print("   - Instalação do psycopg2 está corrompida")
    print("   - Ou há arquivo de sistema do Windows com encoding errado")
    import traceback

    traceback.print_exc()

print("\n2. Testando com SQLAlchemy usando parâmetros explícitos:")
try:
    from sqlalchemy import create_engine, text
    from sqlalchemy.engine.url import URL

    # Criar URL do SQLAlchemy de forma explícita
    db_url = URL.create(
        drivername="postgresql",
        username="admin",
        password="bd99d0060e",
        host="172.21.209.118",
        port=5432,
        database="propaganda_db",
    )

    print(f"   URL criada: {db_url}")

    engine = create_engine(
        db_url,
        connect_args={
            "connect_timeout": 10,
            "client_encoding": "UTF8",
            "application_name": "flask_test",
        },
        pool_pre_ping=True,
    )

    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        print("   ✅ SQLAlchemy FUNCIONOU!")

        result = conn.execute(text("SELECT version();"))
        version = result.fetchone()
        print(f"   PostgreSQL: {version[0][:80]}...")

    print("\n   🎉 SUCESSO COM SQLALCHEMY!")
    print("   Use URL.create() ao invés de string URI no config.py")

except Exception as e:
    print(f"   ❌ ERRO SQLAlchemy: {e}")
    import traceback

    traceback.print_exc()

print("\n" + "=" * 60)
print("CONCLUSÃO")
print("=" * 60)
print("Se os testes acima funcionaram, atualize o config.py para usar")
print("URL.create() ao invés de string URI.")
print("=" * 60)
