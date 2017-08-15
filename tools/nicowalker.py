# -*- coding:utf-8 -*-

import argparse
import json
from os import path
import requests
import pickle
import netrc

working_dir = path.dirname(path.abspath(__file__))
cookie_path = "{0}/{1}".format(working_dir, "cookie.json")


class NicoWalker(object):
    command_name = "Default Command"

    def __init__(self):
        self.parser = argparse.ArgumentParser(description=self.command_name)
        self.parser.add_argument('-u', '--username',
                                 dest='mail',
                                 default=None,
                                 help='username')
        self.parser.add_argument('-p', '--password',
                                 dest='passwd',
                                 default=None,
                                 help='password')
        self.mail = None
        self.password = None
        self.args = None
        self.session = None

    def set_parser(self, args=None):
        if args is None:
            args = self.parser.parse_args()
        self.args = args
        mail = args.mail
        password = args.passwd

        # ユーザー名とパスワードをnetrcから取得
        if mail is None or password is None:
            # mail, password = login_nicovideo.get_login_info()
            auth = netrc.netrc()
            mail, _, password = auth.authenticators("nicovideo")

        # ログインしてセッションを取得
        self.mail = mail
        self.password = password
        self.login()

    def login(self, force=False):
        url = "https://secure.nicovideo.jp/secure/login"
        params = {
            'mail': self.mail,
            'password': self.password,
            'next_url': '',
            'site': "niconico"
        }
        self.session = requests.Session()
        # セッションが保存されていた場合、それを使う
        if path.exists(cookie_path) and not force:
            self.load_cookies()
            # ログインできていたらリターン
            if self.is_logged_in():
                return
        self.session.post(url, data=params)
        if self.is_logged_in():
            # クッキーを保存
            self.save_cookies()

    def load_cookies(self):
        with open(cookie_path, "rb") as f:
            cookies = requests.utils.cookiejar_from_dict(pickle.load(f))
            self.session.cookies = cookies

    def save_cookies(self):
        with open(cookie_path, "wb") as f:
            pickle.dump(requests.utils.dict_from_cookiejar(self.session.cookies), f)

    # とりあえずマイリストにアクセスしてログイン状態を確認
    # TODO もうちょっとカジュアルな確認方法を探す
    def is_logged_in(self):
        url = 'http://www.nicovideo.jp/api/deflist/list'
        res = self.session.get(url)
        res_json = json.loads(res.text)
        if res_json["status"] == "fail":
            return False
        else:
            return True
