
from typing import List, Union
import pandas as pd
from pandas import DataFrame
from Bi import Bi
from Chan import CChan
from Plot.AbSctractPlotDriver import AbSctractPlotDriver
from lightweight_charts import Chart

from Plot.PlotMeta import CBi_meta, CChanPlotMeta


class TradingViewDriver(AbSctractPlotDriver):
    def __init__(self, chan: CChan, plot_config: Union[str, dict, list] = '', plot_para=None):
        self.chart = Chart()
        self.chart.legend(visible=True)
        super(TradingViewDriver, self).__init__(chan, plot_config, plot_para)

    def drawLines(self, type, df: DataFrame):
        line = self.chart.create_line(name=type)
        line.set(df)

    def plot_kline(self, meta: CChanPlotMeta):
        pass

    def plot_kline_combine(self, meta: CChanPlotMeta):
        pass

    def plot_bi(self, meta: CChanPlotMeta):
        bi_list: List[CBi_meta] = meta.bi_list
        datetick = meta.datetick
        biPointDict = {datetick[bi.begin_x]
            : bi.begin_y for idx, bi in enumerate(bi_list)}

        df = pd.DataFrame(columns=['time', 'bi'])
        df['time'] = datetick
        df['bi'] = df['time'].map(biPointDict)
        print(df)
        self.drawLines("bi", df)

    def plot_seg(self, meta: CChanPlotMeta):
        pass

    def plot_segseg(
        self,
        meta: CChanPlotMeta
    ):
        pass

    def plot_eigen(self, meta: CChanPlotMeta):
        pass

    def plot_zs(self, meta: CChanPlotMeta):
        pass

    def plot_segzs(self, meta: CChanPlotMeta):
        pass

    def plot_macd(self, meta: CChanPlotMeta):
        pass

    def plot_mean(self, meta: CChanPlotMeta):
        pass

    def plot_channel(self, meta: CChanPlotMeta):
        pass

    def plot_boll(self, meta: CChanPlotMeta):
        pass

    def bsp_common_draw(self, bsp_list):
        pass

    def plot_bsp(self, meta: CChanPlotMeta):
        pass

    def plot_segbsp(self, meta: CChanPlotMeta):
        pass

    def plot_marker(self, meta: CChanPlotMeta):
        pass

    def draw_demark_begin_line(self):
        pass

    def plot_rsi(self, meta: CChanPlotMeta):
        pass

    def plot_kdj(
        self,
        meta: CChanPlotMeta
    ):
        pass

    def draw_demark(self, meta: CChanPlotMeta):  # sourcery skip: low-code-quality
        pass

    def show_figure(self):
        self.chart.show()
