
from typing import List, Union
import pandas as pd
from pandas import DataFrame
from Chan import CChan
from Common.CEnum import FX_TYPE, KLINE_DIR
from Common.CTime import CTime
from KLine.KLine_Unit import CKLine_Unit
from Plot.AbSctractPlotDriver import AbSctractPlotDriver
from lightweight_charts import Chart

from Plot.PlotMeta import CBS_Point_meta, CBi_meta, CChanPlotMeta, CSeg_meta, CZS_meta


def convert_KLineUnit_klineObj(unit: CKLine_Unit):
    return {"open": unit.open, "close": unit.close, "high": unit.high, "low": unit.low}

def add_zs_text(zs_meta: CZS_meta, fontsize, text_color):
    pass

class TradingViewDriver(AbSctractPlotDriver):
    def __init__(self, chan: CChan, plot_config: Union[str, dict, list] = '', plot_para=None):
        self.chart = Chart()

        self.chart.legend(visible=True)
        rugd = plot_para.get('kl')['rugd']
        up_color = 'rgba(200, 97, 100, 100)' if rugd else 'rgba(39, 157, 130, 100)'
        down_color = 'rgba(39, 157, 130, 100)' if rugd else 'rgba(200, 97, 100, 100)'
        self.chart.candle_style(up_color=up_color, down_color=down_color)
        super(TradingViewDriver, self).__init__(chan, plot_config, plot_para)

        self.draw()
    # 实现父类方法，当前lv开始画图前，准备数据

    def prepare_current_lv(self, meta: CChanPlotMeta):
        df = pd.DataFrame(columns=['time'])
        df['time'] = meta.datetick
        self.df = df

    def common_draw_lines(self, type, df: DataFrame, color='rgba(214, 237, 255, 0.6)', style='solid'):
        line = self.chart.create_line(name=type, color=color, style=style)
        line.set(df)

    def plot_kline(self, meta: CChanPlotMeta):
        klu_lst = [convert_KLineUnit_klineObj(kl) for kl in meta.klu_iter()]
        klineDf = pd.DataFrame(klu_lst)
        self.df = self.df.join(klineDf)
        self.chart.set(self.df)

    def plot_kline_combine(self, meta: CChanPlotMeta):
        pass
        # color_type = {FX_TYPE.TOP: 'red', FX_TYPE.BOTTOM: 'blue',
        #               KLINE_DIR.UP: 'green', KLINE_DIR.DOWN: 'green'}
        # datetick = meta.datetick
        # for klc_meta in meta.klc_list:
        #     self.chart.box(start_time=datetick[klc_meta.begin_idx], end_time=datetick[klc_meta.end_idx], start_value=klc_meta.low, end_value=klc_meta.high, color=color_type[klc_meta.type])

    def plot_bi(self, meta: CChanPlotMeta):
        bi_plot_config = self.plot_para.get('bi', {})
        color = bi_plot_config.get('color') or 'rgba(255, 255, 255, 0.6)'
        bi_list: List[CBi_meta] = meta.bi_list
        datetick = meta.datetick
        biPointDict = {datetick[bi.begin_x]                       : bi.begin_y for idx, bi in enumerate(bi_list)}

        df = self.df
        df['bi'] = df['time'].map(biPointDict)
        self.common_draw_lines("bi", df, color)

    def plot_seg(self, meta: CChanPlotMeta):
        seg_plot_config = self.plot_para.get('seg', {})
        color = seg_plot_config.get('color') or 'rgba(52, 195, 235, 1)'
        seg_list: List[CSeg_meta] = meta.seg_list
        datetick = meta.datetick
        segPointDict = {datetick[seg.begin_x]: seg.begin_y for idx, seg in enumerate(seg_list)}

        df = self.df
        df['seg'] = df['time'].map(segPointDict)
        self.common_draw_lines('seg', df, color)

    def plot_segseg(
        self,
        meta: CChanPlotMeta
    ):
        seg_plot_config = self.plot_para.get('segseg', {})
        color = seg_plot_config.get('color') or 'rgba(219, 131, 15, 1)'
        seg_list: List[CSeg_meta] = meta.segseg_list
        datetick = meta.datetick
        segPointDict = {datetick[seg.begin_x]: seg.begin_y for idx, seg in enumerate(seg_list)}

        df = self.df
        df['segseg'] = df['time'].map(segPointDict)
        self.common_draw_lines('segseg', df, color)

    def plot_eigen(self, meta: CChanPlotMeta):
        pass

    def plot_zs(self, meta: CChanPlotMeta):
        datetick = meta.datetick
        zsList = meta.zs_lst
        zs_plot_config = self.plot_para.get('zs', {})
        draw_one_bi_zs = zs_plot_config.get('draw_one_bi_zs')
        show_text = zs_plot_config.get('show_text')
        fontsize = zs_plot_config.get('fontsize')
        text_color = zs_plot_config.get('text_color')
        for zs_meta in zsList:
            line_style = 'solid' if zs_meta.is_sure else 'dashed'
            if not draw_one_bi_zs and zs_meta.is_onebi_zs:
                continue
            self.chart.box(datetick[zs_meta.begin], zs_meta.low, datetick[zs_meta.end], zs_meta.low + zs_meta.h, style=line_style)
            for sub_zs_meta in zs_meta.sub_zs_lst:
                self.chart.box(datetick[sub_zs_meta.begin], sub_zs_meta.low, datetick[sub_zs_meta.end], sub_zs_meta.low + sub_zs_meta.h, style=line_style)
            # if show_text:
            #     add_zs_text(zs_meta, fontsize, text_color)
            #     for sub_zs_meta in zs_meta.sub_zs_lst:
            #         add_zs_text(sub_zs_meta, fontsize, text_color)

    def plot_segzs(self, meta: CChanPlotMeta):
        datetick = meta.datetick
        for zs_meta in meta.segzs_lst:
            line_style = 'solid' if zs_meta.is_sure else 'dashed'
            self.chart.box(datetick[zs_meta.begin], zs_meta.low, datetick[zs_meta.end], zs_meta.low + zs_meta.h, style=line_style)
            for sub_zs_meta in zs_meta.sub_zs_lst:
                self.chart.box(datetick[sub_zs_meta.begin], sub_zs_meta.low, datetick[sub_zs_meta.end], sub_zs_meta.low + sub_zs_meta.h, style=line_style)

    def plot_macd(self, meta: CChanPlotMeta):
        pass

    def plot_mean(self, meta: CChanPlotMeta):
        pass

    def plot_channel(self, meta: CChanPlotMeta):
        pass

    def plot_boll(self, meta: CChanPlotMeta):
        pass

    def bsp_common_draw(self, datetick, bsp_list: List[CBS_Point_meta],buy_color: str, sell_color: str):
        for bsp in bsp_list:
            color = buy_color if bsp.is_buy else sell_color
            position = 'below' if bsp.is_buy else 'above'
            shape = 'arrow_up' if bsp.is_buy else 'arrow_down'

            self.chart.marker(datetick[bsp.x], text=bsp.desc(), position=position, color=color, shape=shape)

    def plot_bsp(self, meta: CChanPlotMeta):
        datetick = meta.datetick
        self.bsp_common_draw(datetick, meta.bs_point_lst, 'red', 'green')

    def plot_segbsp(self, meta: CChanPlotMeta):
        datetick = meta.datetick
        self.bsp_common_draw(datetick, meta.seg_bsp_lst, 'red', 'green')

    def plot_marker(self, meta: CChanPlotMeta):
        marker_config_dict = self.plot_para.get('marker', {'markers': {}})
        markers = marker_config_dict.get('markers', [])
        default_color = marker_config_dict.get('default_color')
        new_marker = {}
        if len(markers)<=0:
            return
        for klu in meta.klu_iter():
            for date, marker in markers.items():
                date_str = date.to_str() if isinstance(date, CTime) else date
                if klu.include_sub_lv_time(date_str) and klu.time.to_str() != date_str:
                    new_marker[klu.time.to_str()] = marker
        new_marker.update(markers)

        for date, marker in new_marker.items():
            if isinstance(date, CTime):
                date = date.to_str()
            if not (self.df['time'] == date).any():
                continue
            if len(marker) == 2:
                color = default_color
                marker_content, position = marker
            else:
                assert len(marker) == 3
                marker_content, position, color = marker
            assert position in ['up', 'down']
            drawPos = 'above' if position == 'down' else 'below'
            shape = 'arrow_down' if position == 'down' else 'arrow_up'

            self.chart.marker(date, text=marker_content, position=drawPos, color=color, shape=shape)

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
