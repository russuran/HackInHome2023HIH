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
from werkzeug.utils import secure_filename
import yake
import docx
import re
from pdfminer.high_level import extract_text
import ezodf


def made_text(file_name):
    name_split = file_name.split('/')[-1]
    tip = name_split.split('.')[-1]
    if tip == 'txt':
        return f'{name_split} ' + open(file_name, encoding='utf-8').read()
    if tip in ['docx', 'docm']:
        doc = docx.Document(file_name)
        return f'{name_split} ' + ''.join([p.text for p in doc.paragraphs])
    if tip == 'pdf':
        return f'{name_split} ' + ' '.join(re.findall(r'\b\w+\b', extract_text(file_name)))
    if tip in ('odt', 'ods', 'odg', 'odp'):
        fl = ezodf.opendoc(file_name)
        print(str(fl))
        out = []
        for i in fl.body:
            out.extend(re.findall(r"\b\w+\b", i.plaintext().lower()))
        return f'{name_split} ' + ' '.join(out)
    return 0


def made_keywords(text):
    try:
        nmbr = int(count_words(text) * 0.10)
        extractor_ru = yake.KeywordExtractor(
            lan="ru",
            n=4,
            dedupLim=0.6,
            top=nmbr
        )
        return list(x[0].lower() for x in sorted(tuple(extractor_ru.extract_keywords(text)), key=lambda y: y[1]))
    except Exception as er:
        return ['document']


def count_words(text):
    n = len(re.findall(r'\b\w+\b', text))
    return float(n)


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

        print(idd, typee, name, number, timestamp_added_1, timestamp_added_2, timestamp_accepted_1,
              timestamp_accepted_2, key_words)
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

            key_words_count = {}
            key_words = key_words.split(' ')

            result = cur.fetchall()
        maxx = 0
        for i in range(len(result)):
            res = ''

            try:
                data_to_go = made_keywords(made_text(result[i][7]))
                print(data_to_go)
                for j in data_to_go:
                    res += f' str(j)'
            except Exception as error:
                print(error)

            key_words = res
            for k in range(len(result)):
                for m in key_words:
                    try:
                        key_words_count[result[k][0]] += result[k][6].count(m)
                    except:
                        key_words_count[result[k][0]] = 0
                        key_words_count[result[k][0]] += result[k][6].count(m)
            if sum(key_words_count.values()) > maxx:
                maxx = sum(key_words_count.values())
                flname_to_show = result[i][7]

            with sq.connect("app.db") as con:
                cur = con.cursor()

                cur.execute("SELECT * FROM files WHERE filepath = ?", (flname_to_show, ))

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

        db.session.add(f)
        db.session.commit()
        db.session.refresh(f)

        return redirect(url_for('index'))

    return render_template('checkpoint.html', form=form)
