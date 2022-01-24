#!/usr/bin/env python
# -*- coding: utf-8 -*-

import wx
from argparse import ArgumentParser
from pathlib import Path

from csvtimelogger import CsvTimeLogger
from gui import TimeLoggerFrame


if __name__ == '__main__':

    parser = ArgumentParser("Record worked time")
    parser.add_argument("--start", action='store_true')
    parser.add_argument("--stop", action='store_true')
    parser.add_argument('--log_file_name', default=Path.home() / 'time_log.csv')
    parser.add_argument('--hours_per_day', default=8, type=int)
    args = parser.parse_args()

    if args.start and args.stop:
        raise NotImplementedError('Either start or stop, you should not do both!')

    if args.stop:
        wtl = CsvTimeLogger(args.log_file_name, args.hours_per_day)
        wtl.stop_time()
    elif args.start:
        wtl = CsvTimeLogger(args.log_file_name, args.hours_per_day)
        wtl.start_time()
    else:
        app = wx.App(False)
        TimeLoggerFrame(args.log_file_name, args.hours_per_day)
        app.MainLoop()
