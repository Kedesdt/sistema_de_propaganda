from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import FloatField, PasswordField, SubmitField
from wtforms.validators import DataRequired, NumberRange

class LoginForm(FlaskForm):
    password = PasswordField('Senha', validators=[DataRequired()])
    submit = SubmitField('Entrar')

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
