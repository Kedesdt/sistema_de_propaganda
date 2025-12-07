"""
Forçar locale e encoding ANTES de importar psycopg2
"""
import sys
import os

print("=" * 60)
print("TESTE COM LOCALE FORÇADO")
print("=" * 60)

# 1. Forçar encoding do Python
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# 2. Variáveis de ambiente
os.environ['PYTHONIOENCODING'] = 'utf-8'
os.environ['PGCLIENTENCODING'] = 'UTF8'
os.environ['LC_ALL'] = 'C'
os.environ['LANG'] = 'C'

print("\n1. Encoding do Python:")
print(f"   sys.getdefaultencoding(): {sys.getdefaultencoding()}")
print(f"   sys.getfilesystemencoding(): {sys.getfilesystemencoding()}")
print(f"   PYTHONIOENCODING: {os.getenv('PYTHONIOENCODING')}")
print(f"   PGCLIENTENCODING: {os.getenv('PGCLIENTENCODING')}")

print("\n2. Testando conexão:")
try:
    # Limpar módulos do psycopg2 do cache
    for mod in list(sys.modules.keys()):
        if 'psycopg2' in mod:
            del sys.modules[mod]
    
    import psycopg2
    
    conn = psycopg2.connect(
        host="127.0.0.1",
        port=5432,
        database="propaganda_db",
        user="admin",
        password="bd99d0060e"
    )
    print("   ✅ Conexão OK!")
    cursor = conn.cursor()
    cursor.execute("SELECT version();")
    version = cursor.fetchone()
    print(f"   PostgreSQL: {version[0]}")
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"   ❌ Erro: {e}")
    
    # Verificar onde o erro acontece
    import traceback
    tb = traceback.format_exc()
    print("\n   Stack trace completo:")
    print(tb)
    
    # Tentar identificar o arquivo problemático
    print("\n   Buscando arquivo com encoding problemático:")
    import psycopg2
    psycopg2_path = psycopg2.__file__
    print(f"   psycopg2 localizado em: {psycopg2_path}")

print("\n" + "=" * 60)