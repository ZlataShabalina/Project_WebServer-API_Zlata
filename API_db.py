from flask import Flask, render_template
from threading import Thread
from PyQt5 import QtWidgets
from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QPixmap
from main import Ui_MainWindow
import requests
import bs4
import sys
from urllib import request
import sqlite3


class mywindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(mywindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.list = []
        self.prog = []
        self.news = []
        self.n = 0
        self.len = 0
        self.ui.setupUi(self)
        self.url = 'http://europaplustv.com/api/v1.0/api.php?r='  # основная ссылка для API
        self.ui.search.hide()
        self.ui.btn.hide()
        self.ui.web.hide()
        self.ui.next.hide()
        self.ui.back.hide()
        self.ui.home.hide()
        self.ui.p1.hide()
        self.ui.p1.name = '1'
        self.ui.p2.hide()
        self.ui.p2.name = '2'
        self.ui.p3.hide()
        self.ui.p3.name = '3'
        self.ui.p4.hide()
        self.ui.p4.name = '4'
        self.ui.p5.hide()
        self.ui.p5.name = '5'
        self.ui.descrip.hide()
        self.ui.prg_name.hide()
        self.ui.news.name = 'news'
        self.ui.prg.name = 'prg'
        self.ui.artists.name = 'artists'
        self.artists = False
        self.ui.news.toggled.connect(self.onClicked)
        self.ui.prg.toggled.connect(self.onClicked)
        self.ui.artists.toggled.connect(self.onClicked)
        # подключаем/создаем базу
        self.conn = sqlite3.connect("base.db")
        self.cursor = self.conn.cursor()
        self.createbd()

    def center(self):  # окно появится в центре экрана
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def createbd(self):
        # удаляем таблицу с разделами программ для перезаписи
        self.cursor.execute("DROP TABLE IF EXISTS type;")
        # Создание таблицы для рубрик
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS type(
           id INT PRIMARY KEY,
           name TEXT,
           description TEXT);
                       """)
        self.conn.commit()

        # создаем таблицу для программ
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS prog(
           id INT PRIMARY KEY,
           title TEXT,
           link TEXT,
           type INT);
                       """)
        self.conn.commit()

        # Создание таблицы для новостей
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS news(
                   id INT PRIMARY KEY,
                   title TEXT,
                   link TEXT,
                   UNIQUE(id));
                               """)
        self.conn.commit()

        # Создание таблицы для артистов
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS artists(
                           id INT PRIMARY KEY,
                           name TEXT,
                           link TEXT);
                                       """)
        self.conn.commit()

    def onClicked(self):
        check = self.sender()
        if check.isChecked():
            if check.name == 'prg':
                self.prg()
            if check.name == 'news':
                self.onnews()
            if check.name == 'artists':
                self.onartist()

    def onnews(self):
        self.n = 0
        self.ui.search.hide()
        self.ui.btn.hide()
        self.ui.web.show()
        self.ui.next.show()
        self.ui.back.show()
        self.ui.home.show()
        self.ui.prg_name.show()
        self.ui.p1.hide()
        self.ui.p2.hide()
        self.ui.p3.hide()
        self.ui.p4.hide()
        self.ui.p5.hide()
        self.ui.im.hide()
        self.ui.descrip.hide()
        self.news = self.get_news()

        self.ui.web.setUrl(QUrl(self.news[self.n][2]))
        self.ui.prg_name.setText(self.news[self.n][1])
        self.ui.prg_name.setStyleSheet("font: 87 10pt 'Arial Black'; color: rgb(255, 0, 0);")
        self.ui.prg_name.move(140, 100)
        self.ui.back.clicked.connect(self.back_n)
        self.ui.next.clicked.connect(self.next_n)
        self.ui.home.clicked.connect(self.home_n)

    def onartist(self):
        self.n = 0
        self.ui.web.hide()
        self.ui.search.show()
        self.ui.btn.show()
        self.ui.next.show()
        self.ui.back.show()
        self.ui.home.show()
        self.ui.prg_name.hide()
        self.ui.p1.hide()
        self.ui.p2.hide()
        self.ui.p3.hide()
        self.ui.p4.hide()
        self.ui.p5.hide()
        self.ui.im.hide()
        self.ui.descrip.hide()
        try:
            self.cursor.execute("SELECT * FROM artists;")
            self.artists = self.cursor.fetchall()
            self.len = len(self.artists) - 1
            self.ui.web.setUrl(QUrl(self.artists[0][2]))
        except:
            self.artists = False

        self.ui.btn.clicked.connect(self.get_artid)
        self.ui.back.clicked.connect(self.back_a)
        self.ui.next.clicked.connect(self.next_a)
        self.ui.home.clicked.connect(self.home_a)

    def get_artid(self):
        text = self.ui.search.toPlainText()
        if text != '':
            try:
                req_id = API.url + f'search/get&model=artists&tbls=artists&msg={text}'
                data = requests.post(req_id).json()['data']['items']
                id = data[0]['id']
                name = data[0]['name']
                url = API.url + f'content/get&model=artists&id={id}'
                art = (id, name, url)
                self.cursor.execute("INSERT OR IGNORE INTO artists VALUES(?, ?, ?);", art)
                self.conn.commit()
                self.cursor.execute("SELECT * FROM artists;")
                self.artists = self.cursor.fetchall()
                self.len = len(self.artists) - 1
                n = 0
                for i in self.artists:
                    if name in i:
                        self.n = n
                        break
                    else:
                        self.n = self.len
                    n += 1
                self.ui.web.setUrl(QUrl(self.artists[self.n][2]))
                self.ui.web.show()
            except:
                pass

    def prg(self):
        self.ui.search.hide()
        self.ui.btn.hide()
        self.ui.web.hide()
        self.ui.p1.isChecked()
        self.ui.im.show()
        self.list = self.get_lst()
        self.prog = self.get_prg(str(self.list[0][0]))
        self.n = 0
        self.len = len(self.prog) - 1
        self.image()
        self.ui.next.show()
        self.ui.back.show()
        self.ui.home.show()
        self.ui.p1.show()
        self.ui.p1.setText(self.list[0][1])
        self.ui.p2.show()
        self.ui.p2.setText(self.list[1][1])
        self.ui.p3.show()
        self.ui.p3.setText(self.list[2][1])
        self.ui.p4.show()
        self.ui.p4.setText(self.list[3][1])
        self.ui.p5.show()
        self.ui.p5.setText(self.list[4][1])
        self.ui.descrip.show()
        self.ui.descrip.setText(self.list[0][2])
        self.ui.descrip.setReadOnly(True)
        self.ui.prg_name.show()
        self.ui.prg_name.setText(self.prog[0][1])
        self.ui.prg_name.setStyleSheet("font: 87 10pt 'Arial Black'; color: rgb(255, 0, 0);")
        self.ui.prg_name.move(280, 100)
        self.ui.p1.toggled.connect(self.onprg)
        self.ui.p2.toggled.connect(self.onprg)
        self.ui.p3.toggled.connect(self.onprg)
        self.ui.p4.toggled.connect(self.onprg)
        self.ui.p5.toggled.connect(self.onprg)
        self.ui.back.clicked.connect(self.back_p)
        self.ui.next.clicked.connect(self.next_p)
        self.ui.home.clicked.connect(self.home_p)

    def onprg(self):
        check = self.sender()
        if check.isChecked():
            if check.name == '1':
                self.n = 0
                self.prog = self.get_prg(self.list[0][0])
                self.ui.descrip.setText(self.list[0][2])
                self.ui.prg_name.setText(self.prog[self.n][1])
                self.ui.prg_name.setStyleSheet("font: 87 10pt 'Arial Black'; color: rgb(255, 0, 0);")
                self.image()
            elif check.name == '2':
                self.n = 0
                self.prog = self.get_prg(self.list[1][0])
                self.ui.descrip.setText(self.list[1][2])
                self.ui.prg_name.setText(self.prog[self.n][1])
                self.ui.prg_name.setStyleSheet("font: 87 10pt 'Arial Black'; color: rgb(255, 0, 0);")
                self.image()
            elif check.name == '3':
                self.n = 0
                self.prog = self.get_prg(self.list[2][0])
                self.ui.descrip.setText(self.list[2][2])
                self.ui.prg_name.setText(self.prog[self.n][1])
                self.ui.prg_name.setStyleSheet("font: 87 10pt 'Arial Black'; color: rgb(255, 0, 0);")
                self.image()
            elif check.name == '4':
                self.n = 0
                self.prog = self.get_prg(self.list[3][0])
                self.ui.descrip.setText(self.list[3][2])
                self.ui.prg_name.setText(self.prog[self.n][1])
                self.ui.prg_name.setStyleSheet("font: 87 10pt 'Arial Black'; color: rgb(255, 0, 0);")
                self.image()
            elif check.name == '5':
                self.n = 0
                self.prog = self.get_prg(self.list[4][0])
                self.ui.descrip.setText(self.list[4][2])
                self.ui.prg_name.setText(self.prog[self.n][1])
                self.ui.prg_name.setStyleSheet("font: 87 10pt 'Arial Black'; color: rgb(255, 0, 0);")
                self.image()

    def image(self):
        data = request.urlopen(self.prog[self.n][2]).read()
        self.pix1 = QPixmap()
        self.pix1.loadFromData(data)
        self.ui.im.setPixmap(self.pix1)
        self.ui.im.setScaledContents(True)

    def home_p(self):
        self.n = 0
        self.ui.prg_name.setText(self.prog[self.n][1])
        self.ui.prg_name.setStyleSheet("font: 87 10pt 'Arial Black'; color: rgb(255, 0, 0);")
        self.image()

    def back_p(self):
        self.n -= 1
        if self.n < 0:
            self.n = self.len
        self.ui.prg_name.setText(self.prog[self.n][1])
        self.ui.prg_name.setStyleSheet("font: 87 10pt 'Arial Black'; color: rgb(255, 0, 0);")
        self.image()

    def next_p(self):
        self.n += 1
        if self.n > self.len:
            self.n = 0
        self.ui.prg_name.setText(self.prog[self.n][1])
        self.ui.prg_name.setStyleSheet("font: 87 10pt 'Arial Black'; color: rgb(255, 0, 0);")
        self.image()

    def home_n(self):
        self.n = 0
        site = self.news[self.n][2]
        c = request.urlopen(site).read()
        with open('templates/page_n.html', 'w+', encoding="cp1251") as f:
            f.write(str(c))
        f.close()

        self.ui.web.setUrl(QUrl('http://127.0.0.1:5000/'))
        self.ui.prg_name.setText(self.news[self.n][1])
        self.ui.prg_name.setStyleSheet("font: 87 10pt 'Arial Black'; color: rgb(255, 0, 0);")




    def back_n(self):
        self.n -= 1
        if self.n < 0:
            self.n = self.len
        site = self.news[self.n][2]
        c = request.urlopen(site).read()
        with open('templates/page_n.html', 'w+', encoding="cp1251") as f:
            f.write(str(c))
        f.close()
        self.ui.web.setUrl(QUrl('http://127.0.0.1:5000/'))
        self.ui.prg_name.setText(self.news[self.n][1])
        self.ui.prg_name.setStyleSheet("font: 87 10pt 'Arial Black'; color: rgb(255, 0, 0);")

    def next_n(self):
        self.n += 1
        if self.n > self.len:
            self.n = 0

        site = self.news[self.n][2]
        c = request.urlopen(site).read()
        with open('templates/page_n.html', 'w+', encoding="cp1251") as f:
            f.write(str(c))
        f.close()
        self.ui.web.setUrl(QUrl('http://127.0.0.1:5000/'))
        self.ui.prg_name.setText(self.news[self.n][1])
        self.ui.prg_name.setStyleSheet("font: 87 10pt 'Arial Black'; color: rgb(255, 0, 0);")

    def back_a(self):
        if self.artists != False:
            self.n -= 1
            if self.n < 0:
                self.n = self.len
            site = self.artists[self.n][2]
            c = request.urlopen(site).read()
            with open('templates/page_n.html', 'w+', encoding="cp1251") as f:
                f.write(str(c))
            f.close()

            self.ui.web.setUrl(QUrl('http://127.0.0.1:5000/'))


    def next_a(self):
        if self.artists != False:
            self.n += 1
            if self.n > self.len:
                self.n = 0
            site = self.artists[self.n][2]
            c = request.urlopen(site).read()
            with open('templates/page_n.html', 'w+', encoding="cp1251") as f:
                f.write(str(c))
            f.close()
            self.ui.web.setUrl(QUrl('http://127.0.0.1:5000/'))

    def home_a(self):
        if self.artists != False:
            self.n = 0
            site = self.artists[self.n][2]
            c = request.urlopen(site).read()
            with open('templates/page_n.html', 'w+', encoding="cp1251") as f:
                f.write(str(c))
            f.close()

            self.ui.web.setUrl(QUrl('http://127.0.0.1:5000/'))

    def get_lst(self):  # запрашиваем список разделов видео с сайта europaplustv.com
        req = API.url + 'cliptype/get&'
        answer = requests.post(req).json()['data']  # получаем данные
        programms = []
        for i in answer:
            # исключаем лишние разделы
            if i['id'] != 111 and i['id'] != 1 and i['id'] != 71 and i['id'] != 2 and i['id'] != 141:
                try:
                    des = bs4.BeautifulSoup(i['description'], "html.parser").text
                except:
                    des = ''
                dic = (i['id'], i['name'], des)
                programms.append(dic)
            # записываем информацию о разделах с программами
        self.cursor.executemany("INSERT OR IGNORE INTO type VALUES (?,?,?)", programms)
        self.cursor.execute("SELECT * FROM type;")
        getlst = self.cursor.fetchall()
        return getlst

    def get_prg(self, id):  # запрашиваем содержание раздела нужной программы
        req = API.url + 'clip/findallbytypeid&type_id=' + str(id)
        answer = requests.post(req).json()['data']['clips']['items']
        list = []
        for i in answer:
            dic = (i['id'], i['performer'], i['path_poster'], id)
            list.append(dic)
        # записываем выпуски программ в базу
        self.cursor.executemany("INSERT OR IGNORE INTO prog VALUES(?, ?, ?, ?);", list)
        self.conn.commit()
        # получаем из базы полное содержимое выпусков программы нужного раздела
        self.cursor.execute(f"SELECT * FROM prog WHERE type = {id};")
        prog = self.cursor.fetchall()
        self.len = len(prog) - 1
        return prog

    def get_news(self):  # запрашиваем ID последних 20 новостей с сайта europaplustv.com и сохраняем в базу
        req_id = API.url + 'news/get&model=news&search_data[limit][start]=0&search_data[limit][count]=20'
        data = requests.post(req_id).json()['data']['items']
        news = []
        # сайт europaplustv через API отдает новости в виде html.
        # Поэтому сразу формируем ссылки на API запрос на страницы с новостями
        for i in data:
            new = (i['id'], i['title'], f"{API.url}content/get&model=news&id={str(i['id'])}")
            news.append(new)
        # записываем информацию о новых новостях в базу
        self.cursor.executemany("INSERT OR IGNORE INTO news VALUES(?, ?, ?);", news)
        self.conn.commit()
        # получаем из базы полный список новостей
        self.cursor.execute("SELECT * FROM news;")
        news = self.cursor.fetchall()
        self.len = len(news) - 1
        return news




if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    API = mywindow()
    API.show()
    app_ = Flask(__name__)


    @app_.route('/')
    @app_.route('/index')
    def index():
        return render_template('page_n.html')


    kwargs = {'host': '127.0.0.1', 'port': 5000, 'threaded': True, 'use_reloader': False, 'debug': True}

    flaskThread = Thread(target=app_.run, daemon=True, kwargs=kwargs).start()


    app.exec_()
