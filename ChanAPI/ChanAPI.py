from typing import TypedDict, List, Dict

from typing_extensions import ParamSpecArgs

from Chan import CChan
from ChanModel import ChanProcessConfig
from Common.CEnum import DATA_SRC, KL_TYPE
from KLine.KLine_List import CKLine_List
from Plot.PlotMeta import CChanPlotMeta


class RealTimeParams(TypedDict, total=False):
    code: str
    lv_list: List[str]
    config: ChanProcessConfig


class StaticParams(TypedDict, total=False):
    code: str
    begin_time: str
    end_time: str
    data_src: DATA_SRC
    lv_list: List[KL_TYPE]
    config: ChanProcessConfig


# return: Dict[KL_TYPE, DataFrame]
def chan_static_data(params: StaticParams):
    chan = CChan(
        code=params.get("code"),
        lv_list=params.get("lv_list"),
        config=params.get("config"),
        begin_time=params.get("begin_time"),
        end_time=params.get("end_time"),
        data_src=params.get("data_src"),
    )
    # TODO: 转换成DataFrame
    metas: Dict[KL_TYPE, CChanPlotMeta] = {kl_type: CChanPlotMeta(chan[kl_type]) for kl_type in chan.lv_list}
    return metas


def chan_real_time_update(params: RealTimeParams):
    chan = CChan(
        code=params.get("code"),
        lv_list=params.get("lv_list"),
        config=params.get("config")
    )
    # TODO: 转换成DataFrame
    chan.trigger_load()
    return chan.kl_datas
