# -*- coding: utf-8 -*-
from flask import render_template, flash, redirect, url_for
from app import app
from app import db
from app.forms import LoginForm, FileForm, SearchFile, AddUser
from flask_login import *
from flask_login import current_user, login_user
from app.models import User, Files
from app import login
import os
import sqlite3 as sq
from flask import request


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    with sq.connect("app.db") as con:
        cur = con.cursor()

        cur.execute('SELECT * FROM files')

        result = cur.fetchall()

    form = SearchFile()
    if form.is_submitted() and form.validate():
        idd = form.id.data
        typee = form.type.data
        name = form.name.data
        number = form.number.data
        timestamp_added_1 = form.timestamp_added_1.data
        timestamp_added_2 = form.timestamp_added_2.data
        timestamp_accepted_1 = form.timestamp_accepted_1.data
        timestamp_accepted_2 = form.timestamp_accepted_2.data
        key_words = form.key_words.data

        print(idd, typee, name, number, timestamp_added_1, timestamp_added_2, timestamp_accepted_1, timestamp_accepted_2, key_words)
        # самый жёсткий хард-кодинг тут, 6:37;
        work_string = "SELECT * FROM files WHERE "
        args = []
        if idd != '':
            work_string += "id = ? AND "
            args.append(idd)

        if typee != 'Все':
            work_string += "type = ? AND "
            args.append(typee)

        if number != '':
            work_string += "number = ? AND "
            args.append(number)

        if timestamp_added_1 != None and timestamp_added_2 == None:
            work_string += "timestamp_added = ? AND "
            args.append(timestamp_added_1)

        if timestamp_added_2 != None and timestamp_added_1 == None:
            work_string += "timestamp_added = ? AND "
            args.append(timestamp_added_2)

        if timestamp_added_1 != None and timestamp_added_2 != None:
            work_string += "timestamp_added BETWEEN ? AND ? AND "
            args.append(timestamp_added_1)
            args.append(timestamp_added_2)

        if timestamp_accepted_1 != None and timestamp_accepted_2 == None:
            work_string += "timestamp_added = ? AND "
            args.append(timestamp_accepted_1)

        if timestamp_accepted_2 != None and timestamp_accepted_1 == None:
            work_string += "timestamp_added = ? AND "
            args.append(timestamp_accepted_2)

        if timestamp_accepted_1 != None and timestamp_accepted_2 != None:
            work_string += "timestamp_added_accepted BETWEEN ? AND ? AND "
            args.append(timestamp_accepted_1)
            args.append(timestamp_accepted_2)

        work_string = work_string[:-5]
        print(work_string)
        # о боже какой ужас

        with sq.connect("app.db") as con:
            cur = con.cursor()

            cur.execute(work_string, args)

            result = cur.fetchall()

        return render_template('main.html', form=form, data=result)

    return render_template('main.html', data=result, form=form)


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
    form = AddUser()
    if form.is_submitted() and form.validate():

        return redirect(url_for('index'))

    return render_template('user.html', form=form)


@app.route('/add_file', methods=['GET', 'POST'])
def add_file():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    form = FileForm()
    if form.is_submitted() and form.validate():
        fl = request.files['filepath']
        fl.save(fl.filename)
        f = Files(type=form.type.data,
                  name=form.name.data,
                  number=form.number.data,
                  timestamp_added=form.timestamp_added.data,
                  timestamp_added_accepted=form.timestamp_accepted.data,
                  filepath=fl.filename,
                  key_words=form.key_words.data)
        db.session.add(f)  # добавляем в бд
        db.session.commit()  # сохраняем изменения
        db.session.refresh(f)  # обновляем состояние объекта

        return redirect(url_for('index'))

    return render_template('checkpoint.html', form=form)

