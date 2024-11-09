import pandas as pd

from Plot.PlotMeta import CChanPlotMeta


class ChanDataProcessor:
    def __init__(self, meta: CChanPlotMeta):
        df = pd.DataFrame(columns=['time'])
        df['time'] = meta.datetick
        self.meta = meta
        self.df = df
    def process_kline_data(self, meta: CChanPlotMeta):
        self.df = self.df.join(pd.DataFrame([klu for klu in meta.klu_iter()]))

    def process(self):
        self.process_kline_data(self.meta)
        return self.df
