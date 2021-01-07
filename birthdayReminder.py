import datetime


fileName = "ImportantDates.txt"
daysToAlert = 14


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
        return today
    else:
        return None


def rowSplitterDate(row, input):
    rowSplit = row.split(",")
    date = datetime.datetime.strptime(rowSplit[0], '%Y-%m-%d')
    if input.upper() == "M":
        return date.month
    elif input.upper() == "D":
        return date.day
    elif input.upper() == "F":
        return date
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


def eventCheckerCurrMonth(birthdayList):
    currMonth = today("M")
    currentMonthEventList = []
    for entry in birthdayList:
        monthInList = rowSplitterDate(entry, "M")
        if monthInList == currMonth:
            currentMonthEventList.append(entry)
    return currentMonthEventList


def eventToSend(currentMonthList):
    startDate = today("T")
    endDate = startDate + datetime.timedelta(days=daysToAlert)
    todayList = []
    nextTwoWeekList = []
    for entry in currentMonthList:
        dateFromList = rowSplitterDate(entry, "F")
        date, event, name = entry.split(",")
        date = datetime.datetime.strptime(date, '%Y-%m-%d')
        date = date.strftime('%d-%b')
        if dateFromList == startDate:
            todayList.append(f'{name}, {event} on {date}')
        elif dateFromList > startDate and dateFromList <= endDate:
            nextTwoWeekList.append(f'{name}, {event} on {date}')
    return todayList, nextTwoWeekList


cleanedData = filereader(fileName)  # Reads the input txt file
# Transform to a list of format yyyy-mm-dd,event,name
birthdayList = transformData(cleanedData)
# Picks the event for the current month
currentMonthList = eventCheckerCurrMonth(birthdayList)
#alertList = eventToSend(currentMonthList)
todayList, NextTwoWeekList = eventToSend(currentMonthList)
