from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import FloatField, PasswordField, SubmitField, StringField, IntegerField, BooleanField
from wtforms.validators import DataRequired, NumberRange, Email, Length, EqualTo

class LoginForm(FlaskForm):
    password = PasswordField('Senha', validators=[DataRequired()])
    submit = SubmitField('Entrar')

class ClienteLoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    senha = PasswordField('Senha', validators=[DataRequired()])
    submit = SubmitField('Entrar')

class ClienteRegisterForm(FlaskForm):
    nome = StringField('Nome Completo', validators=[DataRequired(), Length(min=3, max=255)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    telefone = StringField('Telefone', validators=[Length(max=50)])
    cpf_cnpj = StringField('CPF/CNPJ', validators=[Length(max=20)])
    senha = PasswordField('Senha', validators=[DataRequired(), Length(min=6)])
    confirmar_senha = PasswordField('Confirmar Senha', validators=[DataRequired(), EqualTo('senha', message='As senhas devem ser iguais')])
    submit = SubmitField('Cadastrar')

class UploadVideoForm(FlaskForm):
    video = FileField('Vídeo', validators=[
        FileRequired(),
        FileAllowed(['mp4', 'avi', 'mov', 'mkv', 'webm'], 'Somente arquivos de vídeo!')
    ])
    latitude = FloatField('Latitude', validators=[
        DataRequired(),
        NumberRange(min=-90, max=90, message='Latitude deve estar entre -90 e 90')
    ])
    longitude = FloatField('Longitude', validators=[
        DataRequired(),
        NumberRange(min=-180, max=180, message='Longitude deve estar entre -180 e 180')
    ])
    radius_km = FloatField('Raio (km)', validators=[
        DataRequired(),
        NumberRange(min=0.1, max=10000, message='Raio deve ser maior que 0')
    ])
    submit = SubmitField('Upload')

class ClienteUploadVideoForm(FlaskForm):
    video = FileField('Vídeo', validators=[
        FileRequired(),
        FileAllowed(['mp4', 'avi', 'mov', 'mkv', 'webm'], 'Somente arquivos de vídeo!')
    ])
    latitude = FloatField('Latitude', validators=[
        DataRequired(),
        NumberRange(min=-90, max=90, message='Latitude deve estar entre -90 e 90')
    ])
    longitude = FloatField('Longitude', validators=[
        DataRequired(),
        NumberRange(min=-180, max=180, message='Longitude deve estar entre -180 e 180')
    ])
    radius_km = FloatField('Raio (km)', validators=[
        DataRequired(),
        NumberRange(min=0.1, max=10000, message='Raio deve ser maior que 0')
    ])
    submit = SubmitField('Enviar para Aprovação')

class AdicionarCreditosForm(FlaskForm):
    creditos = IntegerField('Quantidade de Créditos', validators=[
        DataRequired(),
        NumberRange(min=1, message='Deve adicionar pelo menos 1 crédito')
    ])
    submit = SubmitField('Adicionar Créditos')
