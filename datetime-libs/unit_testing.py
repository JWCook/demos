from datetime import datetime
from unittest.mock import patch

from time_machine import travel


def now():
    print(datetime.now())


def test_now_stdlib():
    with patch('datetime.datetime.now', datetime('2023-10-28 22:00:00')):
        now()


def test_now_time_machine():
    with travel('2023-10-28 22:00:00'):
        now()


if __name__ == '__main__':
    now()
    test_now_time_machine()
