"""
Decorators para autenticação e autorização
"""

from functools import wraps
from flask import session, redirect, url_for, flash, jsonify
from services import ClienteService


def admin_required(f):
    """
    Decorator que requer autenticação de admin.
    Redireciona para login se não autenticado.
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("admin_logged_in"):
            flash(
                "Você precisa estar logado como admin para acessar esta página.",
                "warning",
            )
            return redirect(url_for("admin.login"))
        return f(*args, **kwargs)

    return decorated_function


def cliente_required(f):
    """
    Decorator que requer autenticação de cliente.
    Redireciona para login se não autenticado ou se o cliente não existe mais no banco.
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        cliente_id = session.get("cliente_id")

        if not cliente_id:
            flash("Você precisa estar logado para acessar esta página.", "warning")
            return redirect(url_for("cliente.login"))

        # Validar se o cliente ainda existe no banco

        cliente = ClienteService.get_cliente_by_id(cliente_id)

        if not cliente:
            # Sessão inválida - limpar e redirecionar
            session.pop("cliente_id", None)
            session.pop("cliente_nome", None)
            flash("Sua sessão expirou ou é inválida. Faça login novamente.", "warning")
            return redirect(url_for("cliente.login"))

        return f(*args, **kwargs)

    return decorated_function


def api_auth_required(f):
    """
    Decorator para rotas de API que requer autenticação.
    Retorna JSON 401 se não autenticado.
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Verificar se é admin ou cliente
        if not session.get("admin_logged_in") and not session.get("cliente_id"):
            return jsonify({"error": "Não autorizado"}), 401
        return f(*args, **kwargs)

    return decorated_function


def admin_or_owner_required(f):
    """
    Decorator que permite acesso se for admin OU dono do recurso.
    Útil para rotas onde o cliente pode acessar seus próprios recursos.
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Admin sempre tem acesso
        if session.get("admin_logged_in"):
            return f(*args, **kwargs)

        # Cliente precisa estar logado
        if not session.get("cliente_id"):
            flash("Você precisa estar logado para acessar esta página.", "warning")
            return redirect(url_for("cliente.login"))

        return f(*args, **kwargs)

    return decorated_function
