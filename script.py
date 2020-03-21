try:
    # Python 3.x
    from urllib.request import urlopen
except ImportError:
    # Python 2.x
    from urllib import urlopen

from bs4 import BeautifulSoup
import datetime
import csv


def month_to_num(month):
    month_dict = {
        'Jan': 1,
        'Feb': 2,
        'Mar': 3,
        'Apr': 4,
        'May': 5,
        'Jun': 6,
        'Jul': 7,
        'Aug': 8,
        'Sep': 9,
        'Oct': 10,
        'Nov': 11,
        'Dec': 12
    }
    return month_dict[month]


def format_date(date):
    split_date = date.split(" ", 1)
    year = int(split_date[0])
    just_dates = split_date[1].split("to")
    month_day = just_dates[0].split("-")
    month = month_to_num(month_day[0].strip())
    day = month_day[1].strip()
    new_date = datetime.date(year=year, month=month, day=int(day))
    return new_date


def parse_row(row):
    date = row[0].text.strip()
    prices = [price.text for price in row[1:]]
    return (date, prices)


def load_html_data_from_url(url, history):
    u = urlopen(url)
    try:
        html = u.read().decode('utf-8')
    finally:
        u.close()
    soup = BeautifulSoup(html, features="html.parser")
    dates = soup.find('table', {"summary": "Henry Hub Natural Gas Spot Price (Dollars per Million Btu)"}).find_all('tr')
    dates = [date.extract() for date in dates if len(date.get_text(strip=True)) != 0]
    if history == 'daily':
        loaded_html = dates[1:]
    else:
        loaded_html = dates[1:-3]
    return loaded_html


def save_daily_csv(url):
    html_data = load_html_data_from_url(url, "daily")
    with open('price_daily.csv', newline='', mode='w') as price_daily:
        fieldnames = ['Dates', 'Prices']
        writer = csv.DictWriter(price_daily, fieldnames=fieldnames)
        writer.writeheader()
        for row in html_data:
            row_data = parse_row(row.find_all('td'))
            date = format_date(row_data[0])
            prices = row_data[1]
            for i in range(0, len(prices)):
                nexr_day = date + datetime.timedelta(days=i)
                price_writer = csv.writer(price_daily, delimiter=',')
                price_writer.writerow([nexr_day, prices[i]])


def save_monthly_csv(url):
    html_data = load_html_data_from_url(url, "monthly")
    with open('price_monthly.csv', newline='', mode='w') as price_monthly:
        fieldnames = ['Dates', 'Prices']
        writer = csv.DictWriter(price_monthly, fieldnames=fieldnames)
        writer.writeheader()
        for row in html_data:
            row_data = parse_row(row.find_all('td'))
            year = int(row_data[0])
            prices = row_data[1]
            for i in range(1, len(prices)+1):
                date = datetime.date(year, i, 1)
                price_writer = csv.writer(price_monthly, delimiter=',')
                price_writer.writerow([date, prices[i-1]])


def extract_data(url, history="daily"):
    if history == "daily":
        save_daily_csv(url)
    else:
        save_monthly_csv(url)


if __name__ == "__main__":
    extract_data('https://www.eia.gov/dnav/ng/hist/rngwhhdD.htm', history="daily")
