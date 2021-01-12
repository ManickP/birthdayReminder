import datetime
import requests
import os
import logging

fileName = "ImportantDates.txt"
daysToAlert = 14
poURL = "https://api.pushover.net/1/messages.json"
dateTimeStamp = datetime.datetime.strftime(
    datetime.datetime.now(), '%d_%b_%Y_%H%M%S')

logging.basicConfig(
    filename=f'logs/birthdayReminder_{dateTimeStamp}.log', filemode='w', format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)


def monthNumeric(month):
    month = month.lower()
    try:
        monthNo = datetime.datetime.strptime(month, '%B').month
        return monthNo
    except ValueError:
        error = (f'Error processing the month - {month}')
        return error


def today(input):
    today = datetime.datetime.today()
    if input.upper() == "Y":
        return today.year
    elif input.upper() == "M":
        return today.month
    elif input.upper() == "D":
        return today.day
    elif input.upper() == "T":
        return today.date()
    else:
        return None


def cutOff():
    runTime = datetime.datetime.now()
    currDate = datetime.date.today()
    day, month, year = currDate.day, currDate.month, currDate.year
    cutOffTime = datetime.datetime(
        year, month, day, 12, 0, 0)  # Cut off is noon time
    return runTime, cutOffTime


def rowSplitterDate(row, input):
    rowSplit = row.split(",")
    date = datetime.datetime.strptime(rowSplit[0], '%Y-%m-%d')
    if input.upper() == "M":  # Only Month
        return date.month
    elif input.upper() == "D":  # Only Date
        return date.day
    elif input.upper() == "F":  # Full Date
        return date.date()
    else:
        return date.year


def filereader(fileName):
    cleanedData = []
    try:
        with open(fileName, "r", encoding='utf-8') as inputFile:
            content = inputFile.readlines()
            for row in content:
                cleanedData.append(row.rstrip())
            return cleanedData
    except FileNotFoundError:
        message = f"Could not find file {fileName}"
        logging.warning(message)
        notification("WARN birthdayReminder", message)
        exit()


def eventUpdater(row):
    if "anniversary" in row.lower() or "wedding" in row.lower():
        event = "Anniversary"
    else:
        event = "Birthday"
    return event


def transformData(content):
    birthdayList = []
    for row in content:
        if "-" not in row and len(row) > 0:
            monthNo = monthNumeric(str(row))
        elif "-" in row and len(row) > 0:
            date, person = str(row).split("-", maxsplit=1)
            event = eventUpdater(person)
            year = today("Y")
            birthdate = datetime.date(year, monthNo, int(date))
            birthdayList.append(f'{birthdate},{event},{person.strip()}')
    return birthdayList


def eventToSend(birthdayList, runTime, cutOffTime):
    currDate = today("T")
    tomorrow = currDate + datetime.timedelta(days=1)
    endDate = currDate + datetime.timedelta(days=daysToAlert)
    alertList = []
    for entry in birthdayList:
        dateFromList = rowSplitterDate(entry, "F")
        date, event, name = entry.split(",")
        date = datetime.datetime.strptime(
            date, '%Y-%m-%d')  # Convert string to date
        date = date.strftime('%d-%b')
        if dateFromList == tomorrow and runTime > cutOffTime:
            alertList.append(f'Tomorrow --> {name}, {event} on {date}')
        elif dateFromList == currDate and runTime < cutOffTime:
            alertList.append(f'Today --> {name}, {event} on {date}')
        # Every sat check event for next 2 weeks
        elif currDate.weekday() == 5 and dateFromList > currDate and dateFromList <= endDate and runTime > cutOffTime:
            alertList.append(
                f'Upcoming in next {daysToAlert} days --> {name}, {event} on {date}')
    logging.info(f'The complete alertList is {alertList}')
    return alertList


def messageStr(alertList):
    message = "\n".join(alertList)
    return message


def notification(title, message):
    token = os.environ.get("BR_TOKEN")
    user = os.environ.get("PO_USER")
    data = {"token": token,
            "user": user,
            "title": title,
            "message": message}
    r = requests.post(poURL, json=data)
    logging.info(f'The status code calling {poURL} is {r.status_code}')


logging.info(f'Starting program on {today("T")}')
runTime, cutOffTime = cutOff()  # Cut off time created to support cronjob set
logging.info(f'runTime -> {runTime} cutOffTime -> {cutOffTime}')
cleanedData = filereader(fileName)  # Reads the input txt file
# Transform to a list of format yyyy-mm-dd,event,name
birthdayList = transformData(cleanedData)
# Picks the event for the current month
alertList = eventToSend(birthdayList, runTime, cutOffTime)
if len(alertList) > 0:
    message = messageStr(alertList)
    notification("Event Remider", message)
else:
    logging.info(f"Skipped calling {poURL}")
logging.info(f'Quitting program')
