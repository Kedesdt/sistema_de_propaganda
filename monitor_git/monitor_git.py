import subprocess
import time
import sys

REPO_PATH = "."
BRANCH_NAME = "main"
CHECK_INTERVAL = 60  # segundos

# Se True, não executamos o `git pull`, apenas simulamos a ação.
DRY_RUN = False


def get_remote_commit():
    result = subprocess.run(
        ["git", "ls-remote", "origin", BRANCH_NAME],
        cwd=REPO_PATH,
        stdout=subprocess.PIPE,
        text=True,
    )
    return result.stdout.split()[0] if result.stdout else None


def get_local_commit():
    result = subprocess.run(
        ["git", "rev-parse", BRANCH_NAME],
        cwd=REPO_PATH,
        stdout=subprocess.PIPE,
        text=True,
    )
    return result.stdout.strip()


def pull_changes(dry_run=False):
    """Executa 'git pull' a menos que dry_run seja True, nesse caso apenas loga a ação.

    Parâmetros:
    - dry_run: bool — se True, não executa o pull de fato.
    """
    if dry_run:
        print(f"[DRY-RUN] Simulando: git pull origin {BRANCH_NAME} (cwd={REPO_PATH})")
        return

    subprocess.run(["git", "pull", "origin", BRANCH_NAME], cwd=REPO_PATH)


def monitor_branch():
    print(f"Monitorando a branch '{BRANCH_NAME}'...")

    while True:
        time.sleep(CHECK_INTERVAL)
        current_remote_commit = get_remote_commit()
        local_commit = get_local_commit()

        if current_remote_commit and current_remote_commit != local_commit:
            print("Atualização detectada! Executando git pull...")
            pull_changes(dry_run=DRY_RUN)


if __name__ == "__main__":

    # Opções simples via argv: aceitamos --dry ou --dry-run em qualquer posição.
    if any(arg in ("--dry", "--dry-run", "-n") for arg in sys.argv[1:]):
        DRY_RUN = True

    # Argumentos posicionais — mantidos para compatibilidade (branch, repo_path, interval)
    # Ex.: python monitor_git.py main . 60 --dry
    positional = [a for a in sys.argv[1:] if a not in ("--dry", "--dry-run", "-n")]
    if len(positional) > 0:
        BRANCH_NAME = positional[0]
    if len(positional) > 1:
        REPO_PATH = positional[1]
    if len(positional) > 2:
        try:
            CHECK_INTERVAL = int(positional[2])
        except ValueError:
            print(
                f"Valor inválido para CHECK_INTERVAL: {positional[2]}. Usando padrão {CHECK_INTERVAL}."
            )

    print(
        f"Config: branch={BRANCH_NAME}, repo={REPO_PATH}, interval={CHECK_INTERVAL}, dry_run={DRY_RUN}"
    )
    monitor_branch()
