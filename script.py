#!/usr/bin/env python

try:
    # Python 3.x
    from urllib.request import urlopen
except ImportError:
    # Python 2.x
    from urllib import urlopen

import datetime
import csv
import logging
from bs4 import BeautifulSoup


logging.basicConfig(level=logging.INFO, format='%(message)s')
monthly_price_filename = "./data/monthly_natural_gas_prices.csv"
daily_price_filename = "./data/daily_natural_gas_prices.csv"


def month_to_num(month):
    """Returns number value for abbreviated month

    Args:
        month (str): Abbreviated month to get number value
    Returns:
        month_num (int): Month number of abbreviated month
    """
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
    month_num = month_dict[month]
    return month_num


def format_date(date):
    """Formats row string date values to proper date

    Args:
        date (str): String date value
    Returns:
        new_date (datetime.date): New date generated from date string
    """
    split_date = date.split(" ", 1)
    year = int(split_date[0])
    just_dates = split_date[1].split("to")
    month_day = just_dates[0].split("-")
    month = month_to_num(month_day[0].strip())
    day = month_day[1].strip()
    new_date = datetime.date(year=year, month=month, day=int(day))
    return new_date


def parse_row(row):
    """Parse html row tags into readable tuple

    Args:
        row (list): data rows with html tags
    Returns:
        data_rows (tuple): text extracted from hmtl row tags
    """
    date = row[0].text.strip()
    prices = [price.text for price in row[1:]]
    data_rows = (date, prices)
    return data_rows


def load_html_data_from_url(url, history):
    """Load html data from url link

    Args:
        url (str): url to load data from
        history: data history to load (daily or monthly)
    Returns:
        loaded_html (list): extracted html data from url
    """
    try:
        url_data = urlopen(url)
    except Exception:
        logging.info("Unable to open %s for %s gas prices.\nPlease check that "
                     "you have the correct url\n", url, history)
        return
    try:
        html = url_data.read().decode('utf-8')
    finally:
        url_data.close()

    soup = BeautifulSoup(html, features="html.parser")
    summary_text = "Henry Hub Natural Gas Spot Price (Dollars per Million Btu)"
    dates = soup.find('table', {"summary": summary_text}).find_all('tr')
    dates = [date.extract() for date in dates if len(date.get_text(strip=True))
             != 0]
    if history == 'daily':
        loaded_html = dates[1:]
    else:
        loaded_html = dates[1:-3]
    return loaded_html


def save_daily_price_to_csv(url):
    """Save daily price history to csv file

    Args:
        url (str): url to load data from
    Returns:
        None
    """
    logging.info("Starting daily price extraction...")
    try:
        html_data = load_html_data_from_url(url, "daily")
        with open(daily_price_filename, newline='', mode='w') as daily_price:
            fieldnames = ['Dates', 'Prices']
            writer = csv.DictWriter(daily_price, fieldnames=fieldnames)
            writer.writeheader()
            logging.info("Saving to csv...")
            for row in html_data:
                row_data = parse_row(row.find_all('td'))
                date = format_date(row_data[0])
                prices = row_data[1]
                for price_index in range(0, len(prices)):
                    next_day = date + datetime.timedelta(days=price_index)
                    price_writer = csv.writer(daily_price, delimiter=',')
                    price_writer.writerow([next_day, prices[price_index]])
        logging.info("Completed. Data saved to %s", daily_price_filename)
    except Exception:
        logging.error("Cannot save daily data to csv from %s\nYou either "
                      "have the wrong url or the url page structure has"
                      "changed.\n", url)
        return


def save_monthly_price_to_csv(url):
    """Save monthly price history to csv file

    Args:
        url (str): url to load data from
    Returns:
        None
    """
    logging.info("Starting monthly price extraction...")
    try:
        html_data = load_html_data_from_url(url, "monthly")
        with open(monthly_price_filename, newline='', mode='w') as \
                monthly_price:
            fieldnames = ['Dates', 'Prices']
            writer = csv.DictWriter(monthly_price, fieldnames=fieldnames)
            writer.writeheader()
            logging.info("Saving to csv...")
            for row in html_data:
                row_data = parse_row(row.find_all('td'))
                year = int(row_data[0])
                prices = row_data[1]
                for price_index in range(len(prices)):
                    date = datetime.date(year=year, month=price_index + 1,
                                         day=1)
                    price_writer = csv.writer(monthly_price, delimiter=',')
                    price_writer.writerow([date, prices[price_index]])
        logging.info("Completed. Data saved to %s", monthly_price_filename)
    except Exception:
        logging.error("Cannot save monthly data to csv from %s\nYou either "
                      "have the wrong url or the url page structure has "
                      "changed.\n", url)
        return


if __name__ == "__main__":
    save_daily_price_to_csv('https://www.eia.gov/dnav/ng/hist/rngwhhdD.htm')
    save_monthly_price_to_csv('https://www.eia.gov/dnav/ng/hist/rngwhhdm.htm')
