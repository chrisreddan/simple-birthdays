import logging
import os
from datetime import datetime

import psycopg2
from psycopg2.extras import RealDictCursor
from sendgrid import SendGridAPIClient, Mail

hostname = os.environ.get("DB_HOSTNAME")
user = os.environ.get("DB_USER")
password = os.environ.get("DB_PASSWORD")
dbname = os.environ.get("DB_NAME")

with psycopg2.connect(host=hostname, user=user, password=password, dbname=dbname) as conn:
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT email_from, sendgrid_api_key FROM email_properties")

    email_properties = cur.fetchone()
    email_from = email_properties['email_from']
    sendgrid_api_key = email_properties['sendgrid_api_key']

    cur.execute("SELECT name, birthday, email, is_active FROM people")
    people = cur.fetchall()

should_run = False
email_to = []
email_body = ""

for person in people:
    if person["email"] is not None and person["is_active"]:
        email_to.append(person["email"])

for person in people:
    name = person["name"]
    birthday = str(person["birthday"])
    birthday_date = datetime.strptime(birthday, "%Y-%m-%d")

    if birthday_date.month == datetime.now().month and birthday_date.day == datetime.now().day:
        should_run = True
        age = datetime.now().year - birthday_date.year
        email_body += f"{name} was born on {birthday} and is {age} years old today. Happy birthday!<br><br>"

email_body += "-- This email was automatically sent by a script because this person has a terrible memory -- "
message = Mail(
    from_email=email_from,
    to_emails=email_to,
    subject='Happy Birthday!',
    html_content=email_body)

if should_run:
    try:
        sendgrid_client = SendGridAPIClient(sendgrid_api_key)
        response = sendgrid_client.send(message)
    except Exception as e:
        logging.error(e.message)
