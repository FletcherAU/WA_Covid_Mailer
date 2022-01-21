# WA Covid Mailer

Sends alerts from [Healthy WA's Covid19 Exposure Locations](https://www.healthywa.wa.gov.au/COVID19locations) to Slack using Block Kit. Credit to https://github.com/kronicd/WA_Covid_Mailer, this fork removed notifications that weren't for Slack and changed the formatting to make use of Slack's Block Kit formatting instead of using text.

## Setup

### Edit the configuration items in wacovidmailer.py

~~~python
### CONFIGURATION ITEMS ###

# Debug mode disables sending of alerts
debug = True

# Database location
db_file = "/path/to/exposures.db"  # will be created on first use

# Slack Alerts
slackAlerts = False
webhook_urls = [
    "https://hooks.slack.com/services/XXXXXXX/XXXXXXX/XXXXXXX",
    "https://hooks.slack.com/services/XXXXXXX/XXXXXXX/XXXXXXX"
]

### END OF CONFIGURATION ITEMS
~~~

### Install your deps

~~~
pip3 install requests lxml sqlite3 pytz
~~~

### Setup your cronjob

~~~
*/15 * * * * /usr/bin/python3 /path/to/wacovidmailer.py > /dev/null 2>&1
~~~

## License

This work is licensed under a
[Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License][cc-by-nc-sa].

[![CC BY-NC-SA 4.0][cc-by-nc-sa-image]][cc-by-nc-sa]

[cc-by-nc-sa]: http://creativecommons.org/licenses/by-nc-sa/4.0/
[cc-by-nc-sa-image]: https://licensebuttons.net/l/by-nc-sa/4.0/88x31.png
[cc-by-nc-sa-shield]: https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey.svg
