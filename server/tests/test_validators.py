"""
Testes para os validators customizados
"""
import pytest
from wtforms import Form, StringField, FloatField, IntegerField
from wtforms.validators import DataRequired
from utils.validators import (
    CPF_CNPJ, TelefoneBR, Latitude, Longitude, PositiveNumber,
    validate_cpf, validate_cnpj
)


class DummyForm(Form):
    """Formulário dummy para testes"""
    pass


def test_validate_cpf_valido():
    """Testa validação de CPF válido"""
    assert validate_cpf('11144477735') == True
    assert validate_cpf('111.444.777-35') == True  # Com formatação


def test_validate_cpf_invalido():
    """Testa validação de CPF inválido"""
    assert validate_cpf('12345678901') == False  # Dígitos verificadores errados
    assert validate_cpf('11111111111') == False  # Todos dígitos iguais
    assert validate_cpf('123456789') == False    # Tamanho errado


def test_validate_cnpj_valido():
    """Testa validação de CNPJ válido"""
    assert validate_cnpj('11222333000181') == True
    assert validate_cnpj('11.222.333/0001-81') == True  # Com formatação


def test_validate_cnpj_invalido():
    """Testa validação de CNPJ inválido"""
    assert validate_cnpj('12345678901234') == False  # Dígitos verificadores errados
    assert validate_cnpj('11111111111111') == False  # Todos dígitos iguais
    assert validate_cnpj('123456789012') == False    # Tamanho errado


def test_cpf_cnpj_validator_cpf():
    """Testa validator CPF_CNPJ com CPF"""
    class TestForm(Form):
        cpf_cnpj = StringField('CPF/CNPJ', validators=[CPF_CNPJ()])
    
    # CPF válido
    form = TestForm(data={'cpf_cnpj': '11144477735'})
    assert form.validate()
    
    # CPF inválido
    form = TestForm(data={'cpf_cnpj': '12345678901'})
    assert not form.validate()


def test_cpf_cnpj_validator_cnpj():
    """Testa validator CPF_CNPJ com CNPJ"""
    class TestForm(Form):
        cpf_cnpj = StringField('CPF/CNPJ', validators=[CPF_CNPJ()])
    
    # CNPJ válido
    form = TestForm(data={'cpf_cnpj': '11222333000181'})
    assert form.validate()
    
    # CNPJ inválido
    form = TestForm(data={'cpf_cnpj': '12345678901234'})
    assert not form.validate()


def test_telefone_br_validator_valido():
    """Testa validator TelefoneBR com telefones válidos"""
    class TestForm(Form):
        telefone = StringField('Telefone', validators=[TelefoneBR()])
    
    # Celular (11 dígitos)
    form = TestForm(data={'telefone': '11987654321'})
    assert form.validate()
    
    # Celular com formatação
    form = TestForm(data={'telefone': '(11) 98765-4321'})
    assert form.validate()
    
    # Fixo (10 dígitos)
    form = TestForm(data={'telefone': '1133334444'})
    assert form.validate()


def test_telefone_br_validator_invalido():
    """Testa validator TelefoneBR com telefones inválidos"""
    class TestForm(Form):
        telefone = StringField('Telefone', validators=[TelefoneBR()])
    
    # DDD inválido
    form = TestForm(data={'telefone': '01987654321'})
    assert not form.validate()
    
    # Tamanho errado
    form = TestForm(data={'telefone': '119876543'})
    assert not form.validate()
    
    # Celular não começa com 9
    form = TestForm(data={'telefone': '11887654321'})
    assert not form.validate()


def test_latitude_validator_valida():
    """Testa validator Latitude com valores válidos"""
    class TestForm(Form):
        latitude = FloatField('Latitude', validators=[Latitude()])
    
    form = TestForm(data={'latitude': -23.5505})
    assert form.validate()
    
    form = TestForm(data={'latitude': 0})
    assert form.validate()
    
    form = TestForm(data={'latitude': 90})
    assert form.validate()
    
    form = TestForm(data={'latitude': -90})
    assert form.validate()


def test_latitude_validator_invalida():
    """Testa validator Latitude com valores inválidos"""
    class TestForm(Form):
        latitude = FloatField('Latitude', validators=[Latitude()])
    
    form = TestForm(data={'latitude': 91})
    assert not form.validate()
    
    form = TestForm(data={'latitude': -91})
    assert not form.validate()


def test_longitude_validator_valida():
    """Testa validator Longitude com valores válidos"""
    class TestForm(Form):
        longitude = FloatField('Longitude', validators=[Longitude()])
    
    form = TestForm(data={'longitude': -46.6333})
    assert form.validate()
    
    form = TestForm(data={'longitude': 0})
    assert form.validate()
    
    form = TestForm(data={'longitude': 180})
    assert form.validate()
    
    form = TestForm(data={'longitude': -180})
    assert form.validate()


def test_longitude_validator_invalida():
    """Testa validator Longitude com valores inválidos"""
    class TestForm(Form):
        longitude = FloatField('Longitude', validators=[Longitude()])
    
    form = TestForm(data={'longitude': 181})
    assert not form.validate()
    
    form = TestForm(data={'longitude': -181})
    assert not form.validate()


def test_positive_number_validator_valido():
    """Testa validator PositiveNumber com valores válidos"""
    class TestForm(Form):
        numero = FloatField('Número', validators=[PositiveNumber()])
    
    form = TestForm(data={'numero': 1})
    assert form.validate()
    
    form = TestForm(data={'numero': 0.1})
    assert form.validate()
    
    form = TestForm(data={'numero': 1000})
    assert form.validate()


def test_positive_number_validator_invalido():
    """Testa validator PositiveNumber com valores inválidos"""
    class TestForm(Form):
        numero = FloatField('Número', validators=[PositiveNumber()])
    
    form = TestForm(data={'numero': 0})
    assert not form.validate()
    
    form = TestForm(data={'numero': -1})
    assert not form.validate()
    
    form = TestForm(data={'numero': -0.1})
    assert not form.validate()
