"""
Validadores customizados para formulários
"""

import re
from wtforms.validators import ValidationError


def validate_cpf(cpf):
    """
    Valida CPF brasileiro

    Args:
        cpf: str (apenas números)

    Returns:
        bool
    """
    # Remove caracteres não numéricos
    cpf = re.sub(r"[^0-9]", "", cpf)

    # Verifica se tem 11 dígitos
    if len(cpf) != 11:
        return False

    # Verifica se todos os dígitos são iguais
    if cpf == cpf[0] * 11:
        return False

    # Validação do primeiro dígito verificador
    soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
    resto = soma % 11
    digito1 = 0 if resto < 2 else 11 - resto

    if int(cpf[9]) != digito1:
        return False

    # Validação do segundo dígito verificador
    soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
    resto = soma % 11
    digito2 = 0 if resto < 2 else 11 - resto

    if int(cpf[10]) != digito2:
        return False

    return True


def validate_cnpj(cnpj):
    """
    Valida CNPJ brasileiro

    Args:
        cnpj: str (apenas números)

    Returns:
        bool
    """
    # Remove caracteres não numéricos
    cnpj = re.sub(r"[^0-9]", "", cnpj)

    # Verifica se tem 14 dígitos
    if len(cnpj) != 14:
        return False

    # Verifica se todos os dígitos são iguais
    if cnpj == cnpj[0] * 14:
        return False

    # Validação do primeiro dígito verificador
    peso = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    soma = sum(int(cnpj[i]) * peso[i] for i in range(12))
    resto = soma % 11
    digito1 = 0 if resto < 2 else 11 - resto

    if int(cnpj[12]) != digito1:
        return False

    # Validação do segundo dígito verificador
    peso = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    soma = sum(int(cnpj[i]) * peso[i] for i in range(13))
    resto = soma % 11
    digito2 = 0 if resto < 2 else 11 - resto

    if int(cnpj[13]) != digito2:
        return False

    return True


class CPF_CNPJ:
    """Validator para CPF ou CNPJ"""

    def __init__(self, message=None):
        if not message:
            message = "CPF ou CNPJ inválido"
        self.message = message

    def __call__(self, form, field):
        cpf_cnpj = re.sub(r"[^0-9]", "", field.data or "")

        if len(cpf_cnpj) == 11:
            if not validate_cpf(cpf_cnpj):
                raise ValidationError(self.message)
        elif len(cpf_cnpj) == 14:
            if not validate_cnpj(cpf_cnpj):
                raise ValidationError(self.message)
        else:
            raise ValidationError("CPF deve ter 11 dígitos ou CNPJ 14 dígitos")


class TelefoneBR:
    """Validator para telefone brasileiro"""

    def __init__(self, message=None):
        if not message:
            message = "Telefone inválido. Use formato: (11) 98765-4321"
        self.message = message

    def __call__(self, form, field):
        telefone = re.sub(r"[^0-9]", "", field.data or "")

        # Aceita 10 dígitos (fixo) ou 11 dígitos (celular)
        if len(telefone) not in [10, 11]:
            raise ValidationError(self.message)

        # Verifica DDD (11 a 99)
        ddd = int(telefone[:2])
        if ddd < 11 or ddd > 99:
            raise ValidationError("DDD inválido")

        # Se for celular (11 dígitos), verifica se começa com 9
        if len(telefone) == 11 and telefone[2] != "9":
            raise ValidationError("Celular deve começar com 9")


class Latitude:
    """Validator para latitude"""

    def __init__(self, message=None):
        if not message:
            message = "Latitude deve estar entre -90 e 90"
        self.message = message

    def __call__(self, form, field):
        try:
            lat = float(field.data)
            if not (-90 <= lat <= 90):
                raise ValidationError(self.message)
        except (TypeError, ValueError):
            raise ValidationError("Latitude inválida")


class Longitude:
    """Validator para longitude"""

    def __init__(self, message=None):
        if not message:
            message = "Longitude deve estar entre -180 e 180"
        self.message = message

    def __call__(self, form, field):
        try:
            lon = float(field.data)
            if not (-180 <= lon <= 180):
                raise ValidationError(self.message)
        except (TypeError, ValueError):
            raise ValidationError("Longitude inválida")


class PositiveNumber:
    """Validator para números positivos"""

    def __init__(self, message=None):
        if not message:
            message = "Valor deve ser maior que zero"
        self.message = message

    def __call__(self, form, field):
        try:
            value = float(field.data)
            if value <= 0:
                raise ValidationError(self.message)
        except (TypeError, ValueError):
            raise ValidationError("Valor numérico inválido")
