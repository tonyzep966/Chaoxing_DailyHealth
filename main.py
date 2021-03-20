import base64
import json
import re
import time

import pymysql
import requests


class Health:
    def __init__(self, username="", password="", student_id="", name=""):
        self._session = requests.session()
        self._form_data = {}
        self._headers = {}
        self._body = {}
        self._cookie = ""
        self._uid = ""
        self._username = username
        self._password = password
        self._student_id = student_id
        self._name = name

    def _login(self):
        login_url = "https://passport2.chaoxing.com/fanyalogin"
        with open('login_headers.json', 'r', encoding='utf-8') as f:
            content = f.read()
        login_headers = json.loads(content)
        with open('login_body.json', 'r', encoding='utf-8') as f:
            content = f.read()
        password = self._password
        bytes_password = password.encode("utf-8")
        str_password = bytes.decode(base64.b64encode(bytes_password))

        # Get Major User Cookie
        login_body = json.loads(content)
        login_body["uname"] = self._username
        login_body["password"] = str_password
        resp = self._session.post(url=login_url, headers=login_headers, data=login_body)
        self._uid = resp.cookies.get_dict()["_uid"]
        pattern = re.compile(r'[{}"]')
        cookie = json.dumps(resp.cookies.get_dict())
        cookie = pattern.sub("", cookie).replace(": ", "=").replace(",", ";")
        self._cookie = cookie
        print(self._name)

    # Get "oa_xxx" series cookie
    def _get_oa(self):
        get_url = ""  # TODO: get_url you need to change
        with open('get_oa_header.json', 'r', encoding='utf-8') as f:
            content = f.read()
        get_headers = json.loads(content)
        get_headers["Cookie"] = self._cookie
        resp = self._session.post(url=get_url, headers=get_headers)
        # print(resp.cookies.get_dict())
        pattern = re.compile(r'[{}"]')
        cookie = json.dumps(resp.cookies.get_dict())
        cookie = pattern.sub("", cookie).replace(": ", "=").replace(",", ";")
        self._cookie += ";" + cookie

    # Get check code, which you will need to post form
    def _get_check_code(self):
        get_url = ""  # TODO: get_url you need to change. This is the url of page where actual form at
        with open('get_checkcode_headers.json', 'r', encoding='utf-8') as f:
            content = f.read()
        get_headers = json.loads(content)
        get_headers["Cookie"] = self._cookie
        resp = self._session.get(url=get_url, headers=get_headers)
        check_code = re.findall(r"checkCode.*'(.*)'", resp.text)
        return check_code

    def _post_form(self):
        post_url = "https://office.chaoxing.com/data/apps/forms/fore/user/save?lookuid=" + self._uid
        with open('post_headers.json', 'r', encoding='utf-8') as f:
            headers_content = f.read()
        post_headers = json.loads(headers_content)
        post_headers["Cookie"] = self._cookie
        # print(self._cookie)
        with open('form.json', 'r', encoding='utf-8') as f:
            form_content = f.read()
        form_content = form_content.replace("\n", "").replace(" ", "")
        with open('post_body.json', 'r', encoding='utf-8') as f:
            body_content = f.read()
        post_body = json.loads(body_content)
        post_body["checkCode"] = self._get_check_code()
        form_json = json.loads(form_content)
        form_json[1]["fields"][0]["values"][0]["val"] = time.strftime("%Y-%m-%d")
        # print(form_json[2]["fields"][0]["values"][0]["val"])  # student_id
        # print(form_json[3]["fields"][0]["values"][0]["val"])  # name
        # print(form_json[8]["fields"][0]["values"][0]["val"])  # username, which is phone number
        # print(form_json[19]["fields"][0]["values"][0]["val"])  # location
        form_json[2]["fields"][0]["values"][0]["val"] = self._student_id
        form_json[3]["fields"][0]["values"][0]["val"] = self._name
        form_json[8]["fields"][0]["values"][0]["val"] = self._username
        form_json[19]["fields"][0]["values"][0]["val"] = ""
        form_content = json.dumps(form_json)
        # print(post_headers["Cookie"])
        post_body["formData"] = form_content
        # print(post_body)
        resp = self._session.post(url=post_url, headers=post_headers, data=post_body)
        print(resp.text)

    def control(self):
        self._login()
        self._get_oa()
        self._post_form()
        # self._get_check_code()


if __name__ == '__main__':
    conn = pymysql.connect(
        host="localhost",
        user="root",
        password="",  # TODO: Your MySQL Password
        port=3306,
        database="",  # TODO: MySQL Database
        charset="utf8"
    )
    cursor = conn.cursor()
    cursor.execute("select * from health_user")
    result = cursor.fetchall()
    for rs in result:
        health = Health(username=rs[0], password=rs[1], student_id=rs[2], name=rs[3])
        health.control()
        time.sleep(2)

    cursor.close()
    conn.close()
