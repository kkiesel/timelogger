# -*- coding: utf-8 -*-

import datetime as dt
import wx
import wx.grid
import pandas as pd
import subprocess
from csvtimelogger import CsvTimeLogger


def format_timedelta(td):
    out = '-' if td < dt.timedelta() else ''
    return out + '{: 03d}:{:02d} h'.format(*divmod(abs(int(td.total_seconds())) // 60, 60))


def get_color_red_white_blue(v):
    """Return dark red (v=-1), light red (-1<v<0) white (v=0), light blue (0<v<1) and dark blue (v=1)"""
    v = max(min(v, 1), -1)  # constrains v to be in [-1, 1]
    other_colors = int(255 * (1 - abs(v)))
    if v > 0:
        c = wx.Colour(other_colors, other_colors, 255)
    else:
        c = wx.Colour(255, other_colors, other_colors)
    return c


class TimeLoggerFrame(wx.Frame):
    label_template = 'Worked today: {worked_today}\nEnd of Day:   {eod}\nExtra hours:     {extra_hours}'

    def __init__(self, log_file_name, hours_per_day):
        wx.Frame.__init__(self, None, title='WorkTime')
        self.wtl = CsvTimeLogger(log_file_name, hours_per_day)
        self.working_now = self.wtl.is_working_now()
        self.panel = wx.Panel(self)

        self.stat_button = wx.Button(self.panel, wx.ID_ANY, 'Statistics')
        self.Bind(wx.EVT_BUTTON, self.open_statistics, self.stat_button)

        self.edit_button = wx.Button(self.panel, wx.ID_ANY, 'Edit log file')
        self.Bind(wx.EVT_BUTTON, self.edit_log_file, self.edit_button)

        self.start_button = wx.Button(self.panel, wx.ID_ANY, 'Stop' if self.working_now else 'Start')
        self.Bind(wx.EVT_BUTTON, self.press_button, self.start_button)

        self.plot_button = wx.Button(self.panel, wx.ID_ANY, 'Plot')
        self.Bind(wx.EVT_BUTTON, self.get_plot, self.plot_button)

        self.label = wx.StaticText(self.panel, wx.ID_ANY, self.label_template)
        self.update_texts()

        top_sizer = wx.BoxSizer(wx.VERTICAL)
        top_sizer.Add(self.label, 0, wx.ALL | wx.EXPAND, 5)

        buttons_sizer = wx.GridSizer(2)
        buttons_sizer.Add(self.start_button, 0, wx.CENTER)
        buttons_sizer.Add(self.stat_button, 0, wx.LEFT)
        buttons_sizer.Add(self.edit_button, 0, wx.LEFT)
        buttons_sizer.Add(self.plot_button, 0, wx.LEFT)
        top_sizer.Add(buttons_sizer)
        self.panel.SetSizer(top_sizer)
        top_sizer.Fit(self)

        self.timer = wx.Timer(self, -1)
        self.timer.Start(10000)  # all 10 seconds
        self.Bind(wx.EVT_TIMER, self.update_texts, self.timer)

        self.Show()

    def open_statistics(self, event):
        StatisticsFrame(self)

    def edit_log_file(self, event):
        subprocess.call(['notepad', self.wtl.log_file_name])

    def update_texts(self, event=None):
        self.working_now = self.wtl.is_working_now()
        self.start_button.SetLabelText('Stop' if self.working_now else 'Start')
        wtd = self.wtl.get_worked_time_today()
        format_dict = {
            'worked_today': format_timedelta(wtd),
            'eod': self.wtl.predicted_end_of_day(wtd).strftime('%H:%M Uhr'),
            'extra_hours': format_timedelta(self.wtl.get_extra_hours())
        }
        self.label.SetLabelText(self.label_template.format(**format_dict))

    def press_button(self, event):
        if self.working_now:
            self.wtl.stop_time()
        else:
            self.wtl.start_time()
        self.working_now = not self.working_now
        self.update_texts()

    def get_plot(self, event):
        return
        plt.close()
        data = self.wtl.get_extra_hours_statistics()
        data = pd.concat({'day': data, 'cumsum': data.cumsum()}, axis=1)
        data.plot(title='Extra hours')
        plt.xlabel('Date')
        plt.ylabel('Extra hours')
        plt.show()
        plt.legend(['Per Day', 'Cumulative'])
        plt.show()
        data.plot()


class StatisticsFrame(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, title='Statistics')

        wtl = CsvTimeLogger()
        statistics = wtl.get_statistics()
        panel = wx.Panel(self)
        top_sizer = wx.BoxSizer(wx.VERTICAL)

        grid = wx.grid.Grid(self, -1)
        grid.CreateGrid(len(statistics), 2)  # + 1 due to summary row at end
        grid.SetColLabelValue(0, "Day")
        grid.SetColLabelValue(1, "Worked")
        grid.SetRowLabelSize(0)

        for i, (k, v) in enumerate(statistics.items()):
            grid.SetCellValue(i, 1, format_timedelta(v))
            grid.SetCellAlignment(i, 1, wx.ALIGN_RIGHT, wx.ALIGN_CENTER)
            if isinstance(k, dt.date):
                grid.SetCellValue(i, 0, k.strftime('%a %Y-%m-%d'))
                grid.SetCellAlignment(i, 0, wx.ALIGN_RIGHT, wx.ALIGN_CENTER)

                rel_extra_time = v.total_seconds() / dt.timedelta(hours=4).seconds
                grid.SetCellBackgroundColour(i, 1, get_color_red_white_blue(rel_extra_time))
            else:
                grid.SetCellValue(i, 0, k)

        grid.AutoSize()
        top_sizer.Add(grid, 0, wx.CENTER)
        panel.SetSizer(top_sizer)
        top_sizer.Fit(self)
        self.Show()
