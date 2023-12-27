# birthdayReminder

## Program Info

A python program to remind of upcoming events e.g. bday and anniversary by reading from input file and sending alerts via API call.

---

## How the code works

1. Birthday are read from input text file of format

   Feb
   1 - Jack and Jill wedding day

2. File is read and converted to List of format ["date","event name","name"]

3. Everyday the code runs to check if an event is upcoming tomorrow or today and every Sat sends event upcoming for the next 2 weeks

4. Once the event to sent alert are captured the Pushover API is called to send notifications.

---
