import datetime
import pandas as pd
from itertools import groupby
from bokeh.plotting import figure, save, output_file
from bokeh.models import ColumnDataSource, Range1d
from bs4 import BeautifulSoup
from dateutil.tz import tzlocal
import random
import os


def unpack_lists(lists_in_list: list) -> list:
    unpacked_list = []
    for elem in lists_in_list:
        if type(elem[0]) is str:
            unpacked_list.append(elem)
        else:
            unpacked_list.extend(elem)
    return unpacked_list


def partition_proc(event: list) -> list:
    """ Функция дробления многодневных процессов и их сортировки по времени начала процесса"""

    def check_date_equality (begin, end) -> bool:
        """ Функция проверки, совпадает ли день начала с днем конца процесса"""
        if begin.day == end.day and begin.month == end.month:
            return True
        return False

    colors = ['#1f77b4', '#aec7e8', '#ff7f0e', '#ffbb78',
              '#2ca02c', '#98df8a', '#d62728', '#ff9896',
              '#9467bd', '#c5b0d5', '#8c564b', '#c49c94',
              '#e377c2', '#f7b6d2', '#bcbd22', '#dbdb8d',
              '#17becf', '#2ca02c', '#a55194', '#637939']
    event_title = event[0]
    begin_event = min(event[1:]).astimezone(tzlocal()).replace(tzinfo=None)
    end_event = max(event[1:]).astimezone(tzlocal()).replace(tzinfo=None)
    color = random.choice(colors)

    if not check_date_equality(begin_event, end_event):
        point = begin_event
        temp_list = []
        time_end = datetime.time(23, 59)        # Все суточные процессы заканиваются в полночь

        while not check_date_equality(point, end_event):
            """ Цикл будет крутиться и на каждом цикле отрезать от процесса сутки, пока
            последние сутки не сравняются с датой окончания процесса"""
            part = datetime.datetime.combine(point.date(), time_end)
            temp_list.append([
                event_title,
                point,
                part,
                color
            ])

            point = part + datetime.timedelta(minutes=2)
        temp_list.append([event_title, point, end_event, color])  # Добавление временного промежутка последних суток
        return temp_list
    return [event_title, begin_event, end_event, color]


def valid_process(process: list) -> bool:
    for elem in process:
        if elem is None:
            return False
    return True


def main(process_list) -> list:
    valid_process_list = []
    for process in process_list:
        process = list(process)
        if valid_process(process):
            valid_process_list.append(partition_proc(process))

    process_list = unpack_lists(valid_process_list)
    return sorted(process_list, key=lambda x: x[1])


def diagram_drow_in_file(day_proc: list, url: str):
    # Рисует диаграмму Ганта и сохраняет ее в файл

    DF = pd.DataFrame(columns=['Process', 'Start', 'End', 'Color'])
    diagram_title = str(day_proc[0][1].date().strftime('%d.%m.%Y'))
    for i, data in enumerate(day_proc[::-1]):
        DF.loc[i] = data
    G = figure(
        title=diagram_title,
        x_axis_type='datetime',
        width=300,
        height=120,
        y_range=DF.Process.tolist(),
        x_range=Range1d(
            DF.Start.min() - datetime.timedelta(hours=1),
            DF.End.max() + datetime.timedelta(hours=1))
    )
    DF['ID'] = DF.index + 0.75
    DF['ID1'] = DF.index + 0.25
    CDS = ColumnDataSource(DF)
    G.quad(
        left='Start',
        right='End',
        bottom='ID',
        top='ID1',
        color='Color',
        source=CDS,
        line_width=3,
        )
    output_file(url)
    save(G)


def parsing_file(url) -> str:
    with open(url) as html:
        soup = BeautifulSoup(html, 'html.parser')
    return str(soup.body.find_all(['div', 'script']))[1:-1]


def start_gantt(original_list):
    url = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'gantt.html')
    diagrams = ''
    correct_process_list = main(original_list)
    correct_process_list = [
        list(elem) for _, elem in groupby(
            correct_process_list,
            lambda x: x[1].day
        )
    ]

    for day_proc in correct_process_list:
        diagram_drow_in_file(day_proc, url)

        diagrams += parsing_file(url)
    return diagrams


if __name__ == '__main__':
    diagrams_list = start_gantt(process_list)
