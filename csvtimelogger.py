#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime as dt
import pandas as pd
import collections
import os


class CsvTimeLogger:

    _time_format = '%Y-%m-%dT%H:%M:%S'
    _df = None

    @staticmethod
    def time_diff(x):
        return dt.datetime.now() - x['start'] if pd.isnull(x['stop']) else x['stop'] - x['start']

    def update(self):
        self._df = pd.read_csv(self._log_file_name, parse_dates=[0, 1])

    def update_csv(self):
        self._df.to_csv(self._log_file_name, index=False)

    def __init__(self, log_file_name=r'time_log.csv', hours_per_day=8):
        self._log_file_name = log_file_name
        self._hours_per_day = hours_per_day
        if not os.path.exists(self._log_file_name):
            with open(self._log_file_name, 'w') as f:
                f.write('start,stop')

    def start_time(self):
        self.update()
        self._df = self._df.append({'start': dt.datetime.now().strftime(self._time_format), 'stop': ''}, ignore_index=True)
        self.update_csv()

    def stop_time(self):
        self.update()
        if self._df.empty:
            self.start_time()
        else:
            self._df.iloc[-1, 1] = dt.datetime.now().strftime(self._time_format)
        self.update_csv()

    def get_worked_time(self, start_time):
        self.update()
        if self._df.empty:
            return dt.timedelta()
        selected_df = self._df.loc[self._df.start > start_time.strftime(self._time_format)]
        if selected_df.empty:
            return dt.timedelta()
        times = selected_df.apply(self.time_diff, axis=1)
        return times.sum()

    def get_worked_time_today(self):
        return self.get_worked_time(dt.date.today())

    def predicted_end_of_day(self, worked_time_today):
        return dt.datetime.now() + dt.timedelta(hours=self._hours_per_day) - worked_time_today

    def is_working_now(self):
        self.update()
        return not self._df.empty and pd.isnull(self._df['stop'].iloc[-1])

    def get_time_per_day(self, include_today=False):
        self.update()
        if self._df.empty:
            return {}
        self._df['times'] = self._df.apply(self.time_diff, axis=1)
        # group by date and sum times for each date
        df_aggregated = self._df.groupby(lambda x: self._df['start'].loc[x].date()).sum()
        if not include_today and dt.date.today() in df_aggregated.index:
            df_aggregated.drop(dt.date.today(), inplace=True)
        return df_aggregated['times'].to_dict(collections.OrderedDict)

    def get_extra_hours_statistics(self, include_today=False):
        df = pd.read_csv(self._log_file_name, parse_dates=[0, 1])
        if df.empty:
            return df
        df['times'] = df.apply(self.time_diff, axis=1)
        # group by date and sum times for each date
        df_dates = df.groupby(lambda x: df['start'].loc[x].date()).sum()
        if not include_today and dt.date.today() in df_dates.index:
            df_dates.drop(dt.date.today(), inplace=True)
        return df_dates.apply(lambda x: x['times'] - dt.timedelta(hours=self._hours_per_day), axis=1)

    def get_statistics(self, include_today=False, n_days=10):
        ds = self.get_extra_hours_statistics(include_today)
        if ds is None:
            return {'Extra hours': dt.timedelta()}
        total_extra_hours = ds.sum()
        time_dict = ds[-n_days:].to_dict(collections.OrderedDict)
        time_dict['Extra hours'] = total_extra_hours
        return time_dict

    def get_extra_hours(self):
        statistics = self.get_extra_hours_statistics()
        if statistics.empty:
            return dt.timedelta()
        else:
            return statistics.sum()
