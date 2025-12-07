"""
Testa conexão PostgreSQL com client_encoding
"""

print("=" * 60)
print("TESTE COM CLIENT_ENCODING")
print("=" * 60)

# Teste 1: Com client_encoding
print("\n1. Testando com client_encoding='utf8':")
try:
    import psycopg2
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        database="propaganda_db",
        user="admin",
        password="bd99d0060e",
        client_encoding='utf8'  # Forçar UTF-8
    )
    print("   ✅ Conexão OK com client_encoding")
    cursor = conn.cursor()
    cursor.execute("SELECT version();")
    version = cursor.fetchone()
    print(f"   Versão PostgreSQL: {version[0]}")
    cursor.close()
    conn.close()
except Exception as e:
    print(f"   ❌ Erro: {e}")

# Teste 2: Com options
print("\n2. Testando com options:")
try:
    import psycopg2
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        database="propaganda_db",
        user="admin",
        password="bd99d0060e",
        options='-c client_encoding=UTF8'
    )
    print("   ✅ Conexão OK com options")
    conn.close()
except Exception as e:
    print(f"   ❌ Erro: {e}")

# Teste 3: Verificar variáveis de ambiente
print("\n3. Variáveis de ambiente PostgreSQL:")
import os
pg_vars = [
    'PGCLIENTENCODING', 'PGDATABASE', 'PGHOST', 'PGPORT', 
    'PGUSER', 'PGPASSWORD', 'PGSYSCONFDIR', 'PGSERVICEFILE'
]
for var in pg_vars:
    value = os.getenv(var)
    if value:
        print(f"   {var}={value}")

print("\n" + "=" * 60)
