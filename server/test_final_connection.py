"""
Teste final de conexão com todas as correções aplicadas
"""
import os

# Forçar variáveis de ambiente ANTES de importar qualquer biblioteca
os.environ['PYTHONIOENCODING'] = 'utf-8'
os.environ['PGCLIENTENCODING'] = 'UTF8'
os.environ['LC_MESSAGES'] = 'C'
os.environ['LC_ALL'] = 'C'

print("=" * 60)
print("TESTE FINAL DE CONEXÃO")
print("=" * 60)

print("\n1. Variáveis de ambiente configuradas:")
print(f"   PYTHONIOENCODING: {os.getenv('PYTHONIOENCODING')}")
print(f"   PGCLIENTENCODING: {os.getenv('PGCLIENTENCODING')}")
print(f"   LC_MESSAGES: {os.getenv('LC_MESSAGES')}")
print(f"   LC_ALL: {os.getenv('LC_ALL')}")

# Agora importar as bibliotecas
print("\n2. Testando conexão direta com psycopg2:")
try:
    import psycopg2
    
    # Conexão com opções de locale
    conn = psycopg2.connect(
        host="127.0.0.1",
        port=5432,
        database="propaganda_db",
        user="admin",
        password="bd99d0060e",
        options='-c lc_messages=C -c client_encoding=UTF8'
    )
    
    print("   ✅ Conexão OK!")
    
    cursor = conn.cursor()
    cursor.execute("SELECT version();")
    version = cursor.fetchone()
    print(f"   PostgreSQL: {version[0][:50]}...")
    
    cursor.execute("SHOW lc_messages;")
    lc_messages = cursor.fetchone()
    print(f"   lc_messages: {lc_messages[0]}")
    
    cursor.execute("SHOW client_encoding;")
    encoding = cursor.fetchone()
    print(f"   client_encoding: {encoding[0]}")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"   ❌ Erro: {e}")
    import traceback
    traceback.print_exc()

# Testar com SQLAlchemy (como o app usa)
print("\n3. Testando com SQLAlchemy (como no app):")
try:
    from sqlalchemy import create_engine, text
    
    uri = "postgresql://admin:bd99d0060e@127.0.0.1:5432/propaganda_db"
    
    # Criar engine com as mesmas opções do config.py
    engine = create_engine(
        uri,
        connect_args={
            'options': '-c lc_messages=C -c client_encoding=UTF8'
        }
    )
    
    print("   ✅ Engine criado")
    
    with engine.connect() as conn:
        result = conn.execute(text("SELECT version();"))
        version = result.fetchone()
        print(f"   ✅ Conexão OK!")
        print(f"   PostgreSQL: {version[0][:50]}...")
        
        result = conn.execute(text("SHOW lc_messages;"))
        lc_messages = result.fetchone()
        print(f"   lc_messages: {lc_messages[0]}")
        
except Exception as e:
    print(f"   ❌ Erro: {e}")
    import traceback
    traceback.print_exc()

# Testar com Flask app
print("\n4. Testando com Flask app:")
try:
    from app import create_app
    from models import db
    
    app = create_app()
    
    with app.app_context():
        # Testar conexão
        db.session.execute(text("SELECT 1"))
        print("   ✅ Flask app conectado ao PostgreSQL!")
        
        # Verificar configurações
        result = db.session.execute(text("SHOW lc_messages;"))
        lc_messages = result.fetchone()
        print(f"   lc_messages: {lc_messages[0]}")
        
        result = db.session.execute(text("SHOW client_encoding;"))
        encoding = result.fetchone()
        print(f"   client_encoding: {encoding[0]}")
        
except Exception as e:
    print(f"   ❌ Erro: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("TESTE CONCLUÍDO")
print("=" * 60)
print("\n✅ Se todos os testes passaram, o app está pronto!")
print("   Execute: python server/app.py")
print("\n⚠️  Se ainda houver erro, configure pg_hba.conf no PostgreSQL")
print("=" * 60)
