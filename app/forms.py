from flask_wtf import FlaskForm
from wtforms import StringField, FileField, SelectField, PasswordField, BooleanField, SubmitField, IntegerField
from wtforms.validators import DataRequired, Optional
from wtforms.fields.html5 import DateField


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Войти')


class AddUser(FlaskForm):
    username = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    checkbox1 = BooleanField('Чтение')
    checkbox2 = BooleanField('Запись')
    submit = SubmitField('Добавить')


class SearchFile(FlaskForm):
    id = StringField('№')
    dropdown_list = [('Все', 'Все'),
                     ('ГОСТ', 'ГОСТ'),
                     ('РД', 'РД'),
                     ('Указ', 'Указ'),
                     ('Постановление правительства', 'Постановление правительства'),
                     ('СТО', 'СТО'),
                     ('МИ', 'МИ'),
                     ('РИ', 'РИ'),
                     ('Приказ', 'Приказ'),
                     ('Распоряжение', 'Распоряжение'),
                     ('Уведомление', 'Уведомление'),
                     ('Договор', 'Договор')]

    type = SelectField('Выберите тип', coerce=str, choices=dropdown_list, default=1)
    name = StringField('Название')
    number = StringField('Номер')
    timestamp_added_1 = DateField('Дата выхода от', format='%Y-%m-%d', validators=[Optional()])
    timestamp_added_2 = DateField('Дата выхода до', format='%Y-%m-%d', validators=[Optional()])
    timestamp_accepted_1 = DateField('Дата ввода в действие от', format='%Y-%m-%d', validators=[Optional()])
    timestamp_accepted_2 = DateField('Дата ввода в действие до', format='%Y-%m-%d', validators=[Optional()])

    key_words = StringField('Ключевые слова (через пробел)')

    submit = SubmitField('Поиск')


class FileForm(FlaskForm):
    dropdown_list = [('ГОСТ', 'ГОСТ'),
                     ('РД', 'РД'),
                     ('Указ', 'Указ'),
                     ('Постановление правительства', 'Постановление правительства'),
                     ('СТО', 'СТО'),
                     ('МИ', 'МИ'),
                     ('РИ', 'РИ'),
                     ('Приказ', 'Приказ'),
                     ('Распоряжение', 'Распоряжение'),
                     ('Уведомление', 'Уведомление'),
                     ('Договор', 'Договор')]

    type = SelectField('Выберите тип', coerce=str, choices=dropdown_list, default=1)
    name = StringField('Название', validators=[DataRequired()])
    number = StringField('Номер', validators=[DataRequired()])
    timestamp_added = DateField('Дата выхода', format='%Y-%m-%d')
    timestamp_accepted = DateField('Дата ввода в действие', format='%Y-%m-%d')
    filepath = FileField('Прикрепите файл')
    key_words = StringField('Ключевые слова (через пробел)', validators=[DataRequired()])

    submit = SubmitField('Применить')
