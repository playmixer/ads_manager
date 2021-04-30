from flask import request
from datetime import datetime, timedelta
from src import formats
from typing import List


def time_delta_period(date1: str, date2: str):
    d1 = datetime.strptime(date1, formats.DATE_JS)
    d2 = datetime.strptime(date2, formats.DATE_JS)
    day_list = []
    while d1 <= d2:
        day_list.append(d1)
        d1 = d1 + timedelta(days=1)
    return day_list


class Args:
    def __init__(self):
        self.date1 = request.args.get('date1')
        self.date2 = request.args.get('date2')


class Chart:
    def __init__(self):
        self.args = Args()
        self.dataset = []

    @property
    def labels(self):
        return self.__labels

    @labels.setter
    def labels(self, labels):
        self.__labels = labels

    def get_data(self):
        return {
            'labels': self.labels,
            'datasets': self.dataset
        }

    def add_data(self, val):
        self.dataset.append(val)
