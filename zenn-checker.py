# -*- coding: utf-8 -*-
import io
import json
import time
import threading
import webbrowser

import requests
import schedule
from pystray import Icon, Menu, MenuItem
from PIL import Image, ImageEnhance
from bs4 import BeautifulSoup as bs

INTERVAL = 600
base_url = 'https://zenn.dev'


class taskTray:
    def __init__(self):
        self.running = False
        self.articles = []
        self.maps = {}

        with requests.get(base_url + '/favicon.ico') as r:
            self.update_icon = Image.open(io.BytesIO(r.content))
            self.normal_icon = ImageEnhance.Brightness(self.update_icon).enhance(0.5).convert('L')

        menu = self.buildMenu()
        self.app = Icon(name='PYTHON.win32.zenn-checker', title='zenn-checker', icon=self.normal_icon, menu=menu)
        self.doCheck()

    def buildMenu(self):
        item = [
            MenuItem('Check', self.doCheck, visible=False, default=True),
            MenuItem('Zenn.dev', self.openPage),
            Menu.SEPARATOR,
        ]
        for title in self.articles:
            item.append(MenuItem(title, self.openPage))
        item.append(Menu.SEPARATOR)
        item.append(MenuItem('Exit', self.stopApp))
        return Menu(*item)

    def openPage(self, _, title):
        self.app.icon = self.normal_icon
        self.app.update_menu()
        webbrowser.open(self.maps.get(str(title)))

    def doCheck(self):
        articles = []
        maps = {'Zenn.dev': base_url}
        with requests.get(base_url + '/articles') as r:
            soup = bs(r.content, 'html.parser')
            data = json.loads(soup.find(id='__NEXT_DATA__').text)['props']['pageProps']['articles'][:10]
            for a in data:
                title = a['title']
                url = base_url + a['path']
                articles.append(title)
                maps[title] = url

        if self.articles != articles:
            self.articles = articles
            self.maps = maps
            self.app.icon = self.update_icon
            self.app.menu = self.buildMenu()
            self.app.update_menu()

    def runSchedule(self):
        schedule.every(INTERVAL).seconds.do(self.doCheck)

        while self.running:
            schedule.run_pending()
            time.sleep(1)

    def stopApp(self):
        self.running = False
        self.app.stop()

    def runApp(self):
        self.running = True

        task_thread = threading.Thread(target=self.runSchedule)
        task_thread.start()

        self.app.run()


if __name__ == '__main__':
    taskTray().runApp()
