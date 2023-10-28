# -*- coding: utf-8 -*-
from flask import render_template, flash, redirect, url_for
from app import app
from app import db
from app.forms import LoginForm, FileForm
from flask_login import *
from flask_login import current_user, login_user
from app.models import User, Files
from app import login
import sqlite3


@app.route('/')
@app.route('/index')
def index():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    return render_template('main.html')


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.is_submitted() and form.validate():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user)
        return redirect(url_for('index'))
    return render_template('lgn.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/add_user')
def add_user():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    return render_template('main.html', permission=current_user.permissions)


@app.route('/add_file', methods=['GET', 'POST'])
def add_file():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    form = FileForm()
    if form.is_submitted() and form.validate():

        f = Files(type=form.type.data,
                  name=form.name.data,
                  number=form.number.data,
                  timestamp_added=form.timestamp_added.data,
                  timestamp_added_accepted=form.timestamp_accepted.data,)
        db.session.add(f)  # добавляем в бд
        db.session.commit()  # сохраняем изменения
        db.session.refresh(f)  # обновляем состояние объекта

        return redirect(url_for('index'))

    return render_template('checkpoint.html', form=form)

