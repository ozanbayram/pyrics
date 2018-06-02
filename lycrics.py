from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import sys
import requests
from bs4 import BeautifulSoup
import sqlite3

class Lyrics(QTabWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("PYRICS")
        self.resize(600, 500)
        self.setWindowIcon(QIcon('img/icon.png'))

        self.tab1 = QWidget()
        self.tab2 = QWidget()

        self.addTab(self.tab1, "Tab 1")
        self.addTab(self.tab2, "Tab 2")

        self.tab1UI()
        self.tab2UI()

        self.login()
        self.db()
        self.updateFav()

    def tab1UI(self):
        self.SearchButon = QPushButton(self)
        self.SearchButon.setText("Search")

        self.FavButon = QPushButton(self)
        self.FavButon.setText("Add a new Favorite")
        self.FavButon.setIcon(QIcon("img/star+.png"))
        self.listwidget = QListWidget(self)

        self.LineEdit = QLineEdit(self)

        self.TextEdit = QTextEdit(self)

        self.ErrorMessage = QAction(self)
        self.ErrorMessage.setText("Uyarı")
        self.ErrorMessage.triggered.connect(self.errorMessageShow)

        self.InfoMessage = QAction(self)
        self.InfoMessage.setText("Bilgi")
        self.InfoMessage.triggered.connect(self.infoMessageShow)

        layout = QGridLayout(self)

        layout.addWidget(self.LineEdit, 0, 0)
        layout.addWidget(self.SearchButon, 1, 0)
        layout.addWidget(self.FavButon, 2, 0)
        layout.addWidget(self.listwidget, 3, 0)
        layout.addWidget(self.TextEdit, 0, 1, 4, 1)

        self.setTabText(0, "Search")
        self.setTabIcon(0, QIcon("img/search.png"))
        self.tab1.setLayout(layout)

        self.SearchButon.clicked.connect(self.printTitle)
        self.listwidget.itemDoubleClicked.connect(self.printLycris)
        self.FavButon.clicked.connect(self.addFav)

    def tab2UI(self):
        self.TextFav = QTextEdit(self)

        self.ListFav = QListWidget(self)

        self.DeleteButon = QPushButton(self)
        self.DeleteButon.setText("Delete")
        self.DeleteButon.setIcon(QIcon("img/star-.png"))

        layout2 = QGridLayout(self)
        layout2.addWidget(self.DeleteButon, 0, 0)
        layout2.addWidget(self.ListFav, 1, 0, 2, 2)
        layout2.addWidget(self.TextFav, 0, 2, 3, 2)

        self.tab2.setLayout(layout2)
        self.setTabText(1, "My Favorite")
        self.setTabIcon(1, QIcon("img/star.png"))

        self.ListFav.doubleClicked.connect(self.printFavLyrics)
        self.DeleteButon.clicked.connect(self.deleteFav)
    def login(self):
        self.base_url = 'https://api.genius.com'
        self.headers = {'Authorization': 'Bearer ' + 'YOUR CLIENT ACCESSS TOKEN'}
        self.search_url = self.base_url + '/search'

    def printTitle(self):
        self.listwidget.clear()
        self.titles = []
        data = {'q': self.LineEdit.text()}
        response = requests.get(self.search_url, data=data, headers=self.headers)
        json = response.json()
        self.hits = json['response']['hits']
        for hit in self.hits:
            result = hit["result"]["full_title"]
            self.titles.append(result)
        self.listwidget.addItems(self.titles)

    def getTitle(self):
        self.title = self.hits[self.getIndex()]["result"]["full_title"]
        return self.title

    def getIndex(self):
        self.index = self.listwidget.currentRow()
        return self.index

    def getUrl(self):
        self.url = self.hits[self.getIndex()]["result"]["url"]
        return  self.url

    def printLycris(self):
        self.TextEdit.setText(self.getLycris(self.getUrl()))

    def getLycris(self, url):
        page = requests.get(url)
        html = BeautifulSoup(page.content, 'html.parser')
        lyrics = html.find('div', class_='lyrics').text
        return lyrics

    def errorMessageShow(self):
        QMessageBox.warning(self, "Uyarı", "Lütfen  sıra seçin")

    def infoMessageShow(self):
        QMessageBox.information(self, "Başlık", "Başarı ile eklendi")

    def addFav(self):
        if self.getIndex() == -1 :
            self.errorMessageShow()
        else :
            title = self.getTitle()
            url = self.getUrl()
            self.im.execute("""INSERT INTO  favorite(title, url) VALUES(?,?)""",(title,url))
            self.db.commit()
            self.infoMessageShow()
            self.updateFav()

    def updateFav(self):
        self.ListFav.clear()
        self.im.execute("""SELECT title FROM favorite """)
        for i in self.im.fetchall():
            self.ListFav.addItems(i)

    def printFavLyrics(self):
        self.favTitle = self.ListFav.currentItem().text()
        self.im.execute("""SELECT * FROM favorite WHERE title = ? """, (self.favTitle,))
        url = self.im.fetchone()[1]
        self.TextFav.setText(self.getLycris(url))

    def db(self):
        self.db = sqlite3.connect("favorite.db")
        self.im = self.db.cursor()
        self.im.execute("""CREATE TABLE IF NOT EXISTS favorite (title, url)""")

    def deleteFav(self):
        self.favTitle = self.ListFav.currentItem().text()
        self.im.execute("""DELETE FROM favorite WHERE title = ? """, (self.favTitle,))
        self.db.commit()
        self.updateFav()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Lyrics()
    window.show()
    app.exec_()
