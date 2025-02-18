#!/usr/bin/env python3
from datetime import datetime, timedelta

from dateutil.parser import parse as parse_date
from pytimeparse import parse as parse_time


def test_parse_date():
    dt = input('Date string: ')
    print(f'     Parsed: {parse_date(dt)}')


def test_parse_time():
    seconds = input('Time string: ')
    td = timedelta(seconds=parse_time(seconds))
    dt = (datetime.now() + td).replace(microsecond=0)
    print(f'    Seconds: {parse_time(seconds)}')
    print(f'  Timedelta: {td}')
    print(f'   Datetime: {dt}')


if __name__ == '__main__':
    while True:
        try:
            test_parse_time()
        except (EOFError, KeyboardInterrupt):
            break
