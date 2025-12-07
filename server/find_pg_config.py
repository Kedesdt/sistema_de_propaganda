"""
Encontra arquivos de configuração do PostgreSQL
"""

import os
from pathlib import Path

print("=" * 60)
print("BUSCANDO ARQUIVOS DE CONFIGURAÇÃO POSTGRESQL")
print("=" * 60)

# Locais comuns de arquivos do PostgreSQL no Windows
search_paths = [
    Path(os.getenv("APPDATA", "")) / "postgresql",
    Path(os.getenv("USERPROFILE", "")) / ".postgresql",
    Path(os.getenv("PROGRAMFILES", "")) / "PostgreSQL",
    Path(os.getenv("PROGRAMFILES(X86)", "")) / "PostgreSQL",
    Path("C:/") / "Program Files" / "PostgreSQL",
    Path.home(),
]

config_files = [
    "pgpass.conf",
    "pg_service.conf",
    "postgresql.conf",
    ".pgpass",
    ".pg_service.conf",
]

print("\n1. Procurando arquivos de configuração:")
found_files = []

for search_path in search_paths:
    if not search_path.exists():
        continue

    print(f"\n   Buscando em: {search_path}")

    for config_file in config_files:
        file_path = search_path / config_file
        if file_path.exists():
            print(f"   ✅ Encontrado: {file_path}")
            found_files.append(file_path)

            # Verificar encoding
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    print(f"      UTF-8: OK ({len(content)} chars)")
            except UnicodeDecodeError as e:
                print(f"      ❌ UTF-8: ERRO - {e}")

                # Tentar ler com outros encodings
                for enc in ["latin-1", "cp1252", "iso-8859-1"]:
                    try:
                        with open(file_path, "r", encoding=enc) as f:
                            content = f.read()
                            print(f"      ✅ {enc}: OK - ESTE É O PROBLEMA!")
                            print(f"      Conteúdo:")
                            for line in content.split("\n")[:10]:
                                print(f"         {repr(line)}")
                            break
                    except:
                        continue

# Verificar variável PGSYSCONFDIR
print("\n2. Variável PGSYSCONFDIR:")
pgsysconfdir = os.getenv("PGSYSCONFDIR")
if pgsysconfdir:
    print(f"   {pgsysconfdir}")
    sys_path = Path(pgsysconfdir)
    if sys_path.exists():
        for config_file in config_files:
            file_path = sys_path / config_file
            if file_path.exists():
                print(f"   ✅ Encontrado: {file_path}")
                found_files.append(file_path)
else:
    print("   (não definida)")

# Verificar instalação do PostgreSQL
print("\n3. Procurando instalação do PostgreSQL:")
for drive in ["C:", "D:"]:
    pg_paths = [
        Path(drive) / "PostgreSQL",
        Path(drive) / "Program Files" / "PostgreSQL",
        Path(drive) / "Program Files (x86)" / "PostgreSQL",
    ]

    for pg_path in pg_paths:
        if pg_path.exists():
            print(f"   ✅ {pg_path}")
            # Procurar data dir
            for subdir in pg_path.rglob("data"):
                conf_file = subdir / "postgresql.conf"
                if conf_file.exists():
                    print(f"      Config: {conf_file}")

print("\n4. Solução:")
if found_files:
    print("   Arquivos encontrados com encoding problemático:")
    for f in found_files:
        print(f"   - {f}")
    print("\n   AÇÃO: Converta esses arquivos para UTF-8 ou delete-os")
    print("   Comando para backup:")
    for f in found_files:
        print(f"   move {f} {f}.backup")
else:
    print("   Nenhum arquivo de configuração encontrado")
    print("   O problema pode estar no próprio PostgreSQL")

print("\n" + "=" * 60)
