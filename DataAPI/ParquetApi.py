import os
from datetime import datetime
from typing import Iterable

import pandas as pd
from attr.validators import instance_of

from Common.CEnum import DATA_FIELD, KL_TYPE
from Common.ChanException import CChanException, ErrCode
from Common.CTime import CTime
from Common.func_util import str2float
from KLine.KLine_Unit import CKLine_Unit

from .CommonStockAPI import CCommonStockApi


def create_item_dict(data, column_name):
    for i, name in enumerate(column_name):
        data[i] = parse_time_column(data[name]) if name == DATA_FIELD.FIELD_TIME else str2float(data[name])
    return dict(zip(column_name, data))


def parse_time_column(inp):
    # 20210902113000000
    # 2021-09-13
    dt = pd.to_datetime(inp)
    return CTime.from_datetime(dt)


class ParquetApi(CCommonStockApi):
    def __init__(self, code, k_type=KL_TYPE.K_1M, begin_date=None, end_date=None, autype=None):
        self.headers_exist = True  # 第一行是否是标题，如果是数据，设置为False
        self.columns = [
            DATA_FIELD.FIELD_TIME,
            DATA_FIELD.FIELD_OPEN,
            DATA_FIELD.FIELD_HIGH,
            DATA_FIELD.FIELD_LOW,
            DATA_FIELD.FIELD_CLOSE,
            # DATA_FIELD.FIELD_VOLUME,
            # DATA_FIELD.FIELD_TURNOVER,
            # DATA_FIELD.FIELD_TURNRATE,
        ]  # 每一列字段
        if not begin_date is None:
            begin_date = pd.to_datetime(begin_date) if isinstance(begin_date, str) else begin_date
        if not end_date is None:
            end_date = pd.to_datetime(end_date) if isinstance(end_date, str) else end_date
        self.time_column_idx = self.columns.index(DATA_FIELD.FIELD_TIME)
        super(ParquetApi, self).__init__(code, k_type, begin_date, end_date, autype)

    def get_kl_data(self) -> Iterable[CKLine_Unit]:
        # 这里只有1分钟
        data_path = os.environ['cache_data_path']
        file_path = f"{data_path}/{self.code}.parquet"
        if not os.path.exists(file_path):
            raise CChanException(f"file not exist: {file_path}", ErrCode.SRC_DATA_NOT_FOUND)
        df = pd.read_parquet(file_path)
        df[DATA_FIELD.FIELD_TIME] = df['dt']
        if not set(self.columns).issubset(set(df.columns)):
            raise CChanException(f"file format error: {file_path} columns not enough", ErrCode.SRC_DATA_FORMAT_ERROR)

        for index, row in df.iterrows():
            if len(row) < len(self.columns):
                raise CChanException(f"file format error: {file_path}", ErrCode.SRC_DATA_FORMAT_ERROR)
            if self.begin_date is not None and row[DATA_FIELD.FIELD_TIME] < self.begin_date:
                continue
            if self.end_date is not None and row[DATA_FIELD.FIELD_TIME] > self.end_date:
                continue
            yield CKLine_Unit(create_item_dict(row, self.columns))

    def SetBasciInfo(self):
        pass

    @classmethod
    def do_init(cls):
        pass

    @classmethod
    def do_close(cls):
        pass
