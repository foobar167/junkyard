import datetime

year = int(input("What year were you born in: "))
month = int(input("What month were you born in (number): "))
day = int(input("What day were you born in: "))

birth_date = datetime.date(year, month, day)  # converts to yy/mm/dd
today = datetime.date.today()  # todays date

days_alive = (today - birth_date).days  # calculates how many days since birth
print(f"You are {days_alive} days old.")  # outputs result
