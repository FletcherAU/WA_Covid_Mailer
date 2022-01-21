#!/usr/bin/env python3


import requests
import lxml.html
import sqlite3
import json
from pprint import pprint
import smtplib, ssl
import pytz
from datetime import datetime
import os
import shutil
import subprocess
import time


waGovUrl = "https://www.healthywa.wa.gov.au/COVID19locations"
date_time = datetime.now(pytz.timezone("Australia/Perth")).strftime("%d/%m/%Y %H:%M:%S")


### CONFIGURATION ITEMS ###

# Debug mode disables sending of alerts
debug = False

# Database location
db_file = "/home/fletcher/covid/exposures.db"  # will be created on first use

# Slack Alerts
slackAlerts = True
webhook_urls = ["https://hooks.slack.com/services/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"]

### END OF CONFIGURATION ITEMS

if debug:
    db_file = "exposures-debug.db"

def create_connection(db_file):

    conn = None
    try:
        conn = sqlite3.connect(db_file, isolation_level=None)
    except Error as e:
        print(f"something went wrong: {e}")

    # create tables if needed
    query = (
        "SELECT count(name) FROM sqlite_master WHERE type='table' AND name='exposures';"
    )

    result = conn.execute(query)

    if result.fetchone()[0] == 1:
        pass
    else:
        print("creating table...")
        table_create = """ CREATE TABLE IF NOT EXISTS exposures (
                            id integer PRIMARY KEY,
                            datentime text,
                            suburb text,
                            location text,
                            updated text,
                            advice text
                        ); """
        conn.execute(table_create)
        conn.commit()

    return conn


def post_message_to_slack(blocks):

    for webhook_url in webhook_urls:
        slack_data = {"text": "New exposure sites have been added", "blocks": blocks}

        response = requests.post(
            webhook_url,
            data=json.dumps(slack_data),
            headers={"Content-Type": "application/json"},
        )

        if response.status_code != 200:
            raise ValueError(
                "Request to slack returned an error %s, the response is:\n%s"
                % (response.status_code, response.text)
            )

        print("Slack sent")

def getDetails():

    req = requests.get(waGovUrl)

    if req.status_code != 200:
        print(f"Failed to fetch page: {req.reason}")
        raise Exception("reqest_not_ok")

    doc = lxml.html.fromstring(req.content)

    sites_table = doc.xpath('//table[@id="locationTable"]')[0][1]
    rows = sites_table.xpath(".//tr")

    # check for proper header
    header = doc.xpath('//table[@id="locationTable"]')[0][0]
    headerRows = header.xpath(".//th")

    if (headerRows[0].text_content() == 'Exposure date & time' and
    headerRows[1].text_content() == 'Suburb' and
    headerRows[2].text_content() == 'Location' and
    headerRows[3].text_content() == 'Date updated' and
    headerRows[4].text_content() == 'Health advice'):
        pass
    else:
        rows = ""

    if len(rows) < 1:
        print(f"found no data")
        raise Exception("table_parse_fail")

    return rows


def cleanString(location):

    newLoc = ""
    location = location.replace("\xa0", "")
    for line in location.split("\n"):
        newLoc = newLoc + line.lstrip().rstrip() + ", "
    return newLoc.rstrip(", ").replace(", , ", ", ").rstrip("\r\n")

def buildDetails(exposure):
    datentime = cleanString(exposure[1].text_content())
    suburb = cleanString(exposure[2].text_content())
    location = cleanString(exposure[3].text_content())
    updated = cleanString(exposure[4].text_content())
    advice = cleanString(exposure[5].text_content())
    details = {"date":datentime,
               "suburb":suburb,
               "location":location,
               "updated":updated,
               "advice":advice}
    blocks = [{
			"type": "section",
			"fields": [
				{
					"type": "mrkdwn",
					"text": "*Suburb*: "+details["suburb"]
				},
				{
					"type": "mrkdwn",
					"text": "*Location*: "+details["location"]
				},
				{
					"type": "mrkdwn",
					"text": "*Date*: "+details["date"]
				},
				{
					"type": "mrkdwn",
					"text": "*Advice*: "+details["advice"]
				}
			]
		},
		{
			"type": "context",
			"elements": [
				{
					"type": "mrkdwn",
					"text": "Updated "+details["updated"]
				}
			]
		},
		{
			"type": "divider"
		}
	]

    return blocks

def filterExistingExposures(exposure):

    # examine each exposure
    # if it is in the DB already, do nothing
    # if it is not in the DB: add it to our alerts list
    alerts = []
    for exposure in exposures:

        datentime = cleanString(exposure[1].text_content())
        suburb = cleanString(exposure[2].text_content())
        location = cleanString(exposure[3].text_content())
        updated = cleanString(exposure[4].text_content())
        advice = cleanString(exposure[5].text_content())

        query = """SELECT count(id) FROM exposures WHERE
                    datentime = ?
                    AND suburb = ?
                    AND location = ?
                    AND updated = ?
                    AND advice = ?;"""

        args = (datentime, suburb, location, updated, advice)
        result = dbconn.execute(query, args)

        if result.fetchone()[0] > 0:
            pass
            # print('exposure exists')
        else:
            alerts.append(exposure)

    return alerts

# load sqlite3
dbconn = create_connection(db_file)

# backup db incase things go bad
shutil.copy(db_file, f"{db_file}.bak")

# get exposures
try:
    exposures = getDetails()
except:
    exit()

# filter list of exposures to remove known/previously seen exposures
alerts = filterExistingExposures(exposures)

# for each new exposure add it to the DB and add it to a string for comms
slacklist = []

for exposure in alerts:
    slacklist += buildDetails(exposure)

    datentime = cleanString(exposure[1].text_content())
    suburb = cleanString(exposure[2].text_content())
    location = cleanString(exposure[3].text_content())
    updated = cleanString(exposure[4].text_content())
    advice = cleanString(exposure[5].text_content())

    query = f"""INSERT INTO exposures (datentime, suburb, location, updated, advice)
                VALUES (?,?,?,?,?) """

    args = (datentime, suburb, location, updated, advice)
    result = dbconn.execute(query, args)

    if debug:
        print(comms)


# kludge ugh
mailPostSuccess = 200

if not debug:
    if len(slacklist) > 0 and slackAlerts:
        post_message_to_slack(slacklist)

dbconn.commit()
# we don't close as we're using autocommit, this results in greater
# compatability with different versions of sqlite3

if len(comms) > 0 and dreamhostAnounces and mailPostSuccess != 200 and not debug:
    #print(result)
    os.replace(f"{db_file}.bak", db_file)
    sendAdminAlert("Unable to send mail, please investigate")
else:
    os.remove(f"{db_file}.bak")
