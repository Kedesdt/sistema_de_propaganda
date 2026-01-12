from flask import Blueprint, redirect

contato_bp = Blueprint("contato", __name__, url_prefix="/contato")


@contato_bp.route("/", methods=["GET"])
def contato():
    return redirect(
        "https://wa.me/5511974922987?text=Ol%C3%A1%2C%20gostaria%20de%20mais%20informa%C3%A7%C3%B5es%20sobre%20os%20servi%C3%A7os%20de%20propaganda."
    )
