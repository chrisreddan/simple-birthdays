import os

from datetime import datetime
import smtplib
import psycopg2
from psycopg2.extras import RealDictCursor

hostname = os.environ.get("DB_HOSTNAME")
user = os.environ.get("DB_USER")
password = os.environ.get("DB_PASSWORD")
dbname = os.environ.get("DB_NAME")

conn = psycopg2.connect(host=hostname, user=user, password=password, dbname=dbname)
cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
cur.execute("SELECT url, port, email, password FROM email_properties where app_name = 'simple-birthdays'")
email_properties = cur.fetchone()

email_url = email_properties['url']
email_login = email_properties['email']
email_port = email_properties['port']
email_password = email_properties['password']

cur.execute("SELECT name, birthday, email, is_active FROM people")
people = cur.fetchall()

email_receivers = []
for person in people:
    if person["email"] is not None and person["is_active"]:
        email_receivers.append(person["email"])

should_run = False
email_body = 'Subject: Happy Birthday!\n'
email_body += 'CC: '+",".join(email_receivers)+'\n'

for person in people:
    name = person["name"]
    birthday = str(person["birthday"])
    birthday_date = datetime.strptime(birthday, "%Y-%m-%d")

    if birthday_date.month == datetime.now().month and birthday_date.day == datetime.now().day:
        should_run = True
        age = datetime.now().year - birthday_date.year
        email_body += f"{name} was born on {birthday} and is {age} years old today. Happy birthday!\n\n"

email_body += "-- This email was automatically sent by a script because this person has a terrible memory -- "

if should_run:
    with smtplib.SMTP_SSL(email_url, email_port) as server:
        server.login(email_login, email_password)
        test = server.sendmail(email_login, email_receivers, email_body)
