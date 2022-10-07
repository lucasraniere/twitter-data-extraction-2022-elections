from datetime import datetime, timedelta
import re

def convert_timezone(date: str):
    dt = datetime.strptime(date, '%Y%m%d%H%M')
    dt = dt + timedelta(hours=3)
    return datetime.strftime(dt, '%Y%m%d%H%M')


def convert_date(date: str):
    conv_date = ''
    if re.match(r'\d{12}$', date):
        conv_date = date
    elif re.match(r'(\d+-\d+-\d+)$', date):
        conv_date = re.sub(r'-', '', date) + '0000'
    elif re.search(r'(\d+-\d+-\d+\s{1}\d+:\d+$)', date):
        conv_date = re.sub(r'-|:|\s', '', date)
    else:
        conv_date = 'INVALID DATE FORMAT'
    if conv_date != 'INVALID DATE FORMAT':
        conv_date = convert_timezone(conv_date)
    return conv_date


def conv_date_ISO(date: str):
    conv_date = convert_date(date)
    conv_date = conv_date + '00'
    date_time = datetime.strptime(conv_date, '%Y%m%d%H%M%S')
    conv_date = date_time.isoformat('T') + 'Z'
    return conv_date

