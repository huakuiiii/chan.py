
from abc import ABCMeta, abstractmethod
from typing import Dict, List, Union
from Chan import CChan
from Common.CEnum import KL_TYPE
from Common.ChanException import CChanException
from Plot.PlotMeta import CChanPlotMeta


def reformat_plot_config(plot_config: Dict[str, bool]):
    """
    兼容不填写`plot_`前缀的情况
    """
    def _format(s):
        return s if s.startswith("plot_") else f"plot_{s}"

    return {_format(k): v for k, v in plot_config.items()}


def parse_single_lv_plot_config(plot_config: Union[str, dict, list]) -> Dict[str, bool]:
    """
    返回单一级别的plot_config配置
    """
    if isinstance(plot_config, dict):
        return reformat_plot_config(plot_config)
    elif isinstance(plot_config, str):
        return reformat_plot_config(dict([(k.strip().lower(), True) for k in plot_config.split(",")]))
    elif isinstance(plot_config, list):
        return reformat_plot_config(dict([(k.strip().lower(), True) for k in plot_config]))
    else:
        raise CChanException(
            "plot_config only support list/str/dict", ErrCode.PLOT_ERR)


def parse_plot_config(plot_config: Union[str, dict, list], lv_list: List[KL_TYPE]) -> Dict[KL_TYPE, Dict[str, bool]]:
    """
    支持：
        - 传入字典
        - 传入字符串，逗号分割
        - 传入数组，元素为各个需要画的笔的元素
        - 传入key为各个级别的字典
        - 传入key为各个级别的字符串
        - 传入key为各个级别的数组
    """
    if isinstance(plot_config, dict):
        if all(isinstance(_key, str) for _key in plot_config.keys()):  # 单层字典
            return {lv: parse_single_lv_plot_config(plot_config) for lv in lv_list}
        elif all(isinstance(_key, KL_TYPE) for _key in plot_config.keys()):  # key为KL_TYPE
            for lv in lv_list:
                assert lv in plot_config
            return {lv: parse_single_lv_plot_config(plot_config[lv]) for lv in lv_list}
        else:
            raise CChanException(
                "plot_config if is dict, key must be str/KL_TYPE", ErrCode.PLOT_ERR)
    return {lv: parse_single_lv_plot_config(plot_config) for lv in lv_list}


class AbSctractPlotDriver(metaclass=ABCMeta):
    def __init__(self, chan: CChan, plot_config: Union[str, dict, list] = '', plot_para=None):
        if plot_para is None:
            plot_para = {}
        figure_config: dict = plot_para.get('figure', {})

        self.plot_para = plot_para
        self.plot_config = parse_plot_config(plot_config, chan.lv_list)
        self.plot_metas: List[CChanPlotMeta] = self.getPlotMeta(chan, figure_config)
        self.lv_lst = chan.lv_list[:len(self.plot_metas)]

        # x_range = self.GetRealXrange(figure_config, plot_metas[0])
        plot_macd: Dict[KL_TYPE, bool] = {kl_type: conf.get(
            "plot_macd", False) for kl_type, conf in self.plot_config.items()}

    def draw(self):
        for meta, lv in zip(self.plot_metas, self.lv_lst):
            self.prepare_current_lv(meta)
            self.drawElement(self.plot_config[lv], meta, lv, self.plot_para, None, None)

    def drawElement(self, plot_config: Dict[str, bool], meta: CChanPlotMeta, lv, plot_para, macd_data, x_limits):
        funcLst = dir(self)
        for funcName in plot_config:
            if plot_config.get(funcName) and funcName in funcLst:
                getattr(self, funcName)(meta)

    def getPlotMeta(self, chan: CChan, figure_config) -> List[CChanPlotMeta]:
        plot_metas = [CChanPlotMeta(chan[kl_type]) for kl_type in chan.lv_list]
        if figure_config.get("only_top_lv", False):
            plot_metas = [plot_metas[0]]
        return plot_metas

    @abstractmethod
    def prepare_current_lv(self, meta: CChanPlotMeta):
        pass
    @abstractmethod
    def plot_kline(self, meta: CChanPlotMeta):
        pass

    @abstractmethod
    def plot_kline_combine(self, meta: CChanPlotMeta):
        pass

    @abstractmethod
    def plot_bi(self, meta: CChanPlotMeta):
        pass

    @abstractmethod
    def plot_seg(
        self,
        meta: CChanPlotMeta
    ):
        pass

    @abstractmethod
    def plot_segseg(
        self,
        meta: CChanPlotMeta
    ):
        pass

    @abstractmethod
    def plot_eigen(self, meta: CChanPlotMeta):
        pass

    @abstractmethod
    def plot_zs(self, meta: CChanPlotMeta):
        pass

    @abstractmethod
    def plot_segzs(self, meta: CChanPlotMeta):
        pass

    @abstractmethod
    def plot_macd(self, meta: CChanPlotMeta):
        pass

    @abstractmethod
    def plot_mean(self, meta: CChanPlotMeta):
        pass

    @abstractmethod
    def plot_channel(self, meta: CChanPlotMeta):
        pass

    @abstractmethod
    def plot_boll(self, meta: CChanPlotMeta):
        pass

    def bsp_common_draw(self, bsp_list):
        pass

    @abstractmethod
    def plot_bsp(self, meta: CChanPlotMeta):
        pass

    @abstractmethod
    def plot_segbsp(self, meta: CChanPlotMeta):
        pass

    @abstractmethod
    def plot_marker(self, meta: CChanPlotMeta):
        pass

    @abstractmethod
    def draw_demark_begin_line(self):
        pass

    @abstractmethod
    def plot_rsi(self, meta: CChanPlotMeta):
        pass

    @abstractmethod
    def plot_kdj(
        self,
        meta: CChanPlotMeta
    ):
        pass

    @abstractmethod
    def draw_demark(self, meta: CChanPlotMeta):  # sourcery skip: low-code-quality
        pass

    @abstractmethod
    def show_figure(self):  # sourcery skip: low-code-quality
        pass
