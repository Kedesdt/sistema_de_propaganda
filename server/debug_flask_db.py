"""
Debug: Verifica qual URI o Flask está usando
"""

import os
from dotenv import load_dotenv

load_dotenv()

print("=" * 60)
print("DEBUG - CONFIGURAÇÃO DO BANCO")
print("=" * 60)

print("\n1. Variáveis de ambiente:")
print(f"   DATABASE_URI no .env: {os.getenv('DATABASE_URI')}")
print(f"   ADMIN_PASSWORD: {os.getenv('ADMIN_PASSWORD')}")

print("\n2. Testando conexão direta com a URI do .env:")
uri = os.getenv("DATABASE_URI")
print(f"   URI: {uri}")

try:
    import psycopg2
    from urllib.parse import urlparse

    # Parsear a URI
    parsed = urlparse(uri)
    print(f"\n   Parseado:")
    print(f"   - Host: {parsed.hostname}")
    print(f"   - Port: {parsed.port}")
    print(f"   - Database: {parsed.path[1:]}")
    print(f"   - User: {parsed.username}")
    print(f"   - Password: {parsed.password}")

    # Tentar conectar
    print(f"\n3. Tentando conectar...")
    conn = psycopg2.connect(
        host=parsed.hostname,
        port=parsed.port or 5432,
        database=parsed.path[1:],
        user=parsed.username,
        password=parsed.password,
        options="-c lc_messages=C -c client_encoding=UTF8",
    )

    print("   ✅ CONEXÃO OK!")

    cursor = conn.cursor()
    cursor.execute("SELECT version();")
    version = cursor.fetchone()
    print(f"   PostgreSQL: {version[0][:80]}...")

    cursor.execute("SELECT current_database();")
    db = cursor.fetchone()
    print(f"   Database conectado: {db[0]}")

    cursor.close()
    conn.close()

except Exception as e:
    print(f"   ❌ ERRO: {e}")
    import traceback

    traceback.print_exc()

print("\n4. Testando com SQLAlchemy (como o Flask usa):")
try:
    from sqlalchemy import create_engine, text

    engine = create_engine(
        uri, connect_args={"options": "-c lc_messages=C -c client_encoding=UTF8"}
    )

    with engine.connect() as conn:
        result = conn.execute(text("SELECT version();"))
        version = result.fetchone()
        print(f"   ✅ SQLAlchemy CONEXÃO OK!")
        print(f"   PostgreSQL: {version[0][:80]}...")

        result = conn.execute(text("SELECT current_database();"))
        db = result.fetchone()
        print(f"   Database: {db[0]}")

except Exception as e:
    print(f"   ❌ ERRO SQLAlchemy: {e}")
    import traceback

    traceback.print_exc()

print("\n5. Testando com Config do Flask:")
try:
    from config import Config

    print(f"   URI do Config: {Config.SQLALCHEMY_DATABASE_URI}")
    print(f"   Engine options: {Config.SQLALCHEMY_ENGINE_OPTIONS}")

    from sqlalchemy import create_engine, text

    engine = create_engine(
        Config.SQLALCHEMY_DATABASE_URI, **Config.SQLALCHEMY_ENGINE_OPTIONS
    )

    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        print(f"   ✅ Config do Flask FUNCIONA!")

except Exception as e:
    print(f"   ❌ ERRO com Config: {e}")
    import traceback

    traceback.print_exc()

print("\n" + "=" * 60)
print("DIAGNÓSTICO COMPLETO")
print("=" * 60)
