from typing import Dict
import pandas as pd

from Chan import CChan
from Common.CEnum import KL_TYPE


def get_chan_dict(chan: CChan):
    metas: Dict[KL_TYPE, Dict[str, pd.DataFrame]] = {}
    for kl_type in chan.lv_list:
        cdt: Dict[str, pd.DataFrame] = chan[kl_type].to_dataframe_dict()
        metas[kl_type] = cdt
    return metas