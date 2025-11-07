from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import FloatField, PasswordField, SubmitField, StringField, IntegerField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, EqualTo
from utils.validators import CPF_CNPJ, TelefoneBR, Latitude, Longitude, PositiveNumber

class LoginForm(FlaskForm):
    password = PasswordField('Senha', validators=[DataRequired()])
    submit = SubmitField('Entrar')

class ClienteLoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    senha = PasswordField('Senha', validators=[DataRequired()])
    submit = SubmitField('Entrar')

class ClienteRegisterForm(FlaskForm):
    nome = StringField('Nome/Razão Social', validators=[
        DataRequired(),
        Length(min=3, max=100, message='Nome deve ter entre 3 e 100 caracteres')
    ])
    email = StringField('Email', validators=[
        DataRequired(),
        Email(message='Email inválido')
    ])
    senha = PasswordField('Senha', validators=[
        DataRequired(),
        Length(min=6, message='Senha deve ter no mínimo 6 caracteres')
    ])
    confirmar_senha = PasswordField('Confirmar Senha', validators=[
        DataRequired(),
        EqualTo('senha', message='As senhas não coincidem')
    ])
    cpf_cnpj = StringField('CPF/CNPJ', validators=[
        DataRequired(),
        CPF_CNPJ()
    ])
    telefone = StringField('Telefone', validators=[
        DataRequired(),
        TelefoneBR()
    ])
    endereco = TextAreaField('Endereço', validators=[
        DataRequired(),
        Length(min=10, max=200, message='Endereço deve ter entre 10 e 200 caracteres')
    ])
    submit = SubmitField('Cadastrar')

class UploadVideoForm(FlaskForm):
    video = FileField('Vídeo', validators=[
        FileRequired(),
        FileAllowed(['mp4', 'avi', 'mov', 'mkv', 'webm'], 'Somente arquivos de vídeo!')
    ])
    latitude = FloatField('Latitude', validators=[
        DataRequired(),
        Latitude()
    ])
    longitude = FloatField('Longitude', validators=[
        DataRequired(),
        Longitude()
    ])
    radius_km = FloatField('Raio (km)', validators=[
        DataRequired(),
        PositiveNumber()
    ])
    submit = SubmitField('Upload')

class ClienteUploadVideoForm(FlaskForm):
    video = FileField('Vídeo', validators=[
        FileRequired(),
        FileAllowed(['mp4', 'avi', 'mov', 'mkv', 'webm'], 'Somente arquivos de vídeo!')
    ])
    latitude = FloatField('Latitude', validators=[
        DataRequired(),
        Latitude()
    ])
    longitude = FloatField('Longitude', validators=[
        DataRequired(),
        Longitude()
    ])
    radius_km = FloatField('Raio (km)', validators=[
        DataRequired(),
        PositiveNumber()
    ])
    submit = SubmitField('Enviar para Aprovação')

class AdicionarCreditosForm(FlaskForm):
    creditos = IntegerField('Quantidade de Créditos', validators=[
        DataRequired(),
        PositiveNumber()
    ])
    submit = SubmitField('Adicionar Créditos')
