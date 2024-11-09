from typing import TypedDict, List, Dict, Union

import pandas as pd

from Chan import CChan
from ChanConfig import CChanConfig
from ChanModel import ChanProcessConfig
from Common.CEnum import DATA_SRC, KL_TYPE
from Plot.PlotMeta import CChanPlotMeta
from Utils.ChanDataProcessor import ChanDataProcessor


class RealTimeParams(TypedDict, total=False):
    code: str
    lv_list: List[str]
    config: ChanProcessConfig


class StaticParams(TypedDict, total=False):
    code: str
    begin_time: str
    end_time: str | None
    data_src: DATA_SRC
    lv_list: List[KL_TYPE]
    config: ChanProcessConfig


class ChanApiReturnType(CChanPlotMeta):
    klu_df: pd.DataFrame


# return: Dict[KL_TYPE, DataFrame]
def chan_static_data(params: StaticParams):
    config = CChanConfig(params.get("config"))
    chan = CChan(
        code=params.get("code"),
        lv_list=params.get("lv_list"),
        config=config,
        begin_time=params.get("begin_time"),
        end_time=params.get("end_time"),
        data_src=params.get("data_src"),
    )
    # TODO: k线数据转换成DataFrame，其他保留
    metas: Dict[KL_TYPE, Dict[str, pd.DataFrame]] = {}
    for kl_type in chan.lv_list:
        cdt: Dict[str, pd.DataFrame] = chan[kl_type].to_dataframe_dict()
        metas[kl_type] = cdt
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
