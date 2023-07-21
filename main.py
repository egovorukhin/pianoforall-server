#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import time
import codecs
import http.server
import signal
import socketserver
import email.message
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import json

IP = os.environ['APP_IP']
PORT = int(os.environ['APP_PORT'])
APP_DIR = os.path.dirname(os.environ['APP_PATH'])

# IP = 'localhost'
# PORT = 8081
# APP_DIR = os.path.dirname('./www')

msg = email.message.Message()


def send_mail(subject, content):
    port = 25  # For starttls
    smtp_server = "mail.netangels.ru"
    sender_email = "info@sevchel74.ru"
    receiver_email = "info@sevchel74.ru,severnyy.chelovek74@mail.ru"
    #receiver_email = "info@sevchel74.ru,yegor.govorukhin@mail.ru"
    password = "26CawKxUiPgfPDVV"

    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = sender_email
    message["To"] = receiver_email
    message.attach(MIMEText(content, "plain"))

    server = smtplib.SMTP(smtp_server, port)
    try:
        server.starttls()
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message.as_string())
    except Exception as e:
        print(e)
    finally:
        server.quit()


class MyHandler(http.server.BaseHTTPRequestHandler):
    def do_HEAD(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        try:
            index_path = os.path.join(APP_DIR, 'www/index.html')
            with codecs.open(index_path, 'r', encoding='utf-8') as f:
                content = f.read()
                self.wfile.write(content.encode('utf-8'))
        except IOError:
            self.wfile.write(b'index.html not found!\n')

    def do_POST(self):
        name, subject, mail, text, content = '', '', '', '', ''
        if self.path == "/mail":

            content = self.rfile.read(int(self.headers['Content-Length']))
            print(content)
            self.data = json.loads(content)

            self.send_header("Content-type", "text/html")
            self.end_headers()

            try:
                if "name" in self.data:
                    name = self.data["name"]
                if "subject" in self.data:
                    subject = self.data["subject"]
                if "email" in self.data:
                    mail = self.data["email"]
                if "text" in self.data:
                    text = self.data["text"]
                # send_mail("Сайт 'СЧ': " + subject,
                #          "%s\r\n\r\nСообщение отправлено с сайта от %s (email: %s)" % (text, name, mail))
                self.send_response(200)
                self.wfile.write(b'OK')
            except IOError:
                self.send_response(412)
                self.wfile.write(b'Error send mail\n')


class SigException(Exception):
    pass


if __name__ == '__main__':
    def sig_handler(signum, frame):
        raise SigException("Termination by signal %s" % signum)


    signal.signal(signal.SIGTERM, sig_handler)

    socketserver.TCPServer.allow_reuse_address = True
    httpd = socketserver.TCPServer((IP, PORT), MyHandler)

    print(time.asctime(), "Server Starts - %s:%s" % (IP, PORT))
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    except SigException as err:
        print('Handling exception on catching signal:', err)

    httpd.server_close()
    print(time.asctime(), "Server Stops - %s:%s" % (IP, PORT))
