# starcitizen_tools
Tools used for Star Citizen

## gift_calendar.py

### Purpose
This tool was built for SC ship traders. CIG has this annoying policy where you can only send $1,000 worth of ships/items per day. From what I've gathered, this works on a sliding scale throughout the day. For example, if you gift a $500 ship at 5pm on day 1, then a $250 ship at 10pm on day 1, you will not be able to gift anything more than $250 until 5pm on day 2. 

This gets complicated when you're making lots of sales, so I built a program that ingests your hangar logs and the price of the ship you want to sell, builds a calendar, then tells you the next time that you will be able to sell a ship of that value.

### Here's 