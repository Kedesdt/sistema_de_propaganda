"""
Script de diagnóstico para encontrar o problema de encoding
"""

import os
import sys
from pathlib import Path

print("=" * 60)
print("DIAGNÓSTICO DE ENCODING")
print("=" * 60)

# 1. Verificar encoding do sistema
print(f"\n1. Encoding padrão do sistema: {sys.getdefaultencoding()}")
print(f"   Encoding do filesystem: {sys.getfilesystemencoding()}")

# 2. Ler .env com diferentes encodings
env_file = Path(".env")
print(f"\n2. Arquivo .env existe: {env_file.exists()}")
print(f"   Tamanho: {env_file.stat().st_size if env_file.exists() else 0} bytes")

if env_file.exists():
    print("\n3. Tentando ler com UTF-8:")
    try:
        with open(".env", "r", encoding="utf-8") as f:
            content = f.read()
            print("   ✅ UTF-8: OK")
            print(f"   Conteúdo ({len(content)} chars):")
            for i, line in enumerate(content.split("\n"), 1):
                print(f"   Linha {i}: {repr(line)}")
    except Exception as e:
        print(f"   ❌ Erro UTF-8: {e}")

    print("\n4. Tentando ler com latin-1:")
    try:
        with open(".env", "r", encoding="latin-1") as f:
            content = f.read()
            print("   ✅ Latin-1: OK")
    except Exception as e:
        print(f"   ❌ Erro Latin-1: {e}")

# 3. Testar python-dotenv
print("\n5. Testando python-dotenv:")
try:
    from dotenv import load_dotenv

    load_dotenv(encoding="utf-8")
    db_uri = os.getenv("DATABASE_URI")
    print(f"   ✅ Carregado com sucesso")
    print(f"   DATABASE_URI: {repr(db_uri)}")

    # Verificar cada byte
    if db_uri:
        print(f"\n6. Análise byte a byte da URI:")
        for i, char in enumerate(db_uri):
            byte_val = ord(char)
            print(f"   Pos {i}: '{char}' (ord={byte_val}, hex={hex(byte_val)})")
            if byte_val > 127:
                print(f"   ⚠️ ATENÇÃO: Caractere não-ASCII encontrado!")
except Exception as e:
    print(f"   ❌ Erro ao carregar: {e}")
    import traceback

    traceback.print_exc()

# 4. Testar conexão direta
print("\n7. Testando conexão PostgreSQL direta:")
try:
    import psycopg2

    # Testar com string hardcoded
    test_uri = "postgresql://admin:bd99d0060e@localhost/propaganda_db"
    print(f"   URI de teste: {test_uri}")

    # Parsear URI
    from urllib.parse import urlparse

    parsed = urlparse(test_uri)
    print(f"   Usuario: {parsed.username}")
    print(f"   Senha: {parsed.password}")
    print(f"   Host: {parsed.hostname}")
    print(f"   Porta: {parsed.port}")
    print(f"   Database: {parsed.path[1:]}")

except Exception as e:
    print(f"   ❌ Erro: {e}")
    import traceback

    traceback.print_exc()

print("\n" + "=" * 60)
print("FIM DO DIAGNÓSTICO")
print("=" * 60)
