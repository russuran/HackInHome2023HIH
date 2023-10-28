from flask_wtf import FlaskForm
from wtforms import  StringField, FileField, SelectField, PasswordField, BooleanField, SubmitField, IntegerField
from wtforms.validators import DataRequired
from wtforms.fields.html5 import DateField


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Войти')


class FileForm(FlaskForm):
    dropdown_list = [(1, 'ГОСТ'),
                     (2, 'РД'),
                     (3, 'Указ'),
                     (4, 'Постановление правительства'),
                     (5, 'СТО'),
                     (6, 'МИ'),
                     (7, 'РИ'),
                     (8, 'Приказ'),
                     (9, 'Распоряжение'),
                     (10, 'Уведомление'),
                     (11, 'Договор')]

    type = SelectField('Выберите тип', coerce=int, choices=dropdown_list, default=1)
    name = StringField('Название', validators=[DataRequired()])
    number = StringField('Номер', validators=[DataRequired()])
    timestamp_added = DateField('Дата выхода', format='%Y-%m-%d')
    timestamp_accepted = DateField('Дата ввода в действие', format='%Y-%m-%d')
    file = FileField('Прикрепите файл')
    key_words = StringField('Ключевые слова (через пробел)', validators=[DataRequired()])

    submit = SubmitField('Применить')
