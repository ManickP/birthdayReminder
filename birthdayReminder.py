import datetime
import requests
import os

fileName = "ImportantDates.txt"
daysToAlert = 14
poURL = "https://api.pushover.net/1/messages.json"


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
    with open(fileName, "r", encoding='utf-8') as inputFile:
        content = inputFile.readlines()
        for row in content:
            cleanedData.append(row.rstrip())
        return cleanedData


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


def eventToSend(birthdayList):
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
        if dateFromList == tomorrow:
            alertList.append(f'Tomorrow --> {name}, {event} on {date}')
        elif dateFromList == currDate:
            alertList.append(f'Today --> {name}, {event} on {date}')
        # Every sat check event for next 2 weeks
        elif currDate.weekday() == 5 and dateFromList > currDate and dateFromList <= endDate:
            alertList.append(
                f'Upcoming in next {daysToAlert} days --> {name}, {event} on {date}')
    return alertList


def messageStr(alertList):
    message = "\n".join(alertList)
    return message


def notification(message):
    token = os.environ.get("BR_TOKEN")
    user = os.environ.get("PO_USER")
    data = {"token": token,
            "user": user,
            "title": "Event Remider",
            "message": message}
    r = requests.post(poURL, json=data)


cleanedData = filereader(fileName)  # Reads the input txt file
# Transform to a list of format yyyy-mm-dd,event,name
birthdayList = transformData(cleanedData)
# Picks the event for the current month
alertList = eventToSend(birthdayList)
if len(alertList) > 0:
    message = messageStr(alertList)
    print(message)
    notification(message)
