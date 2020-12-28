#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime as dt
import pandas as pd
import collections
import os


class CsvTimeLogger:

    time_format = '%Y-%m-%dT%H:%M:%S'

    @staticmethod
    def time_diff(x):
        return dt.datetime.now() - x['start'] if pd.isnull(x['stop']) else x['stop'] - x['start']

    def __init__(self, log_file_name=r'time_log.csv'):
        self._log_file_name = log_file_name
        if not os.path.exists(self._log_file_name):
            with open(self._log_file_name, 'w') as f:
                f.write('start,stop')

    def start_time(self):
        df = pd.read_csv(self._log_file_name)
        df = df.append({'start': dt.datetime.now().strftime(self.time_format), 'stop': ''}, ignore_index=True)
        df.to_csv(self._log_file_name, index=False)

    def stop_time(self):
        df = pd.read_csv(self._log_file_name)
        df.iloc[-1, 1] = dt.datetime.now().strftime(self.time_format)
        df.to_csv(self._log_file_name, index=False)

    def get_worked_time(self, start_time):
        df = pd.read_csv(self._log_file_name, parse_dates=[0, 1])
        selected_df = df.loc[df.start > start_time.strftime(self.time_format)]
        if selected_df.empty:
            return dt.timedelta()
        times = selected_df.apply(self.time_diff, axis=1)
        return times.sum()

    def get_worked_time_today(self):
        return self.get_worked_time(dt.date.today())

    @staticmethod
    def predicted_end_of_day(worked_time_today):
        return dt.datetime.now() + dt.timedelta(hours=8) - worked_time_today

    def is_working_now(self):
        df = pd.read_csv(self._log_file_name, parse_dates=[0, 1])
        return pd.isnull(df['stop'].iloc[-1])

    def get_time_per_day(self, include_today=False):
        df = pd.read_csv(self._log_file_name, parse_dates=[0, 1])
        df['times'] = df.apply(self.time_diff, axis=1)
        # group by date and sum times for each date
        df_aggregated = df.groupby(lambda x: df['start'].loc[x].date()).sum()
        if not include_today and dt.date.today() in df_aggregated.index:
            df_aggregated.drop(dt.date.today(), inplace=True)
        return df_aggregated['times'].to_dict(collections.OrderedDict)

    def get_extra_hours_statistics(self, include_today=False):
        df = pd.read_csv(self._log_file_name, parse_dates=[0, 1])
        df['times'] = df.apply(self.time_diff, axis=1)
        # group by date and sum times for each date
        df_dates = df.groupby(lambda x: df['start'].loc[x].date()).sum()
        if not include_today and dt.date.today() in df_dates.index:
            df_dates.drop(dt.date.today(), inplace=True)
        return df_dates.apply(lambda x: x['times'] - dt.timedelta(hours=8), axis=1)

    def get_statistics(self, include_today=False, n_days=10):
        ds = self.get_extra_hours_statistics(include_today)
        total_extra_hours = ds.sum()
        time_dict = ds[-n_days:].to_dict(collections.OrderedDict)
        time_dict['Extra hours'] = total_extra_hours
        return time_dict

    def get_extra_hours(self):
        return self.get_extra_hours_statistics().sum()
