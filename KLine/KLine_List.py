import copy
import pandas as pd
from typing import List, Union, overload

from Bi.Bi import CBi
from Bi.BiList import CBiList
from BuySellPoint.BSPointList import CBSPointList
from ChanConfig import CChanConfig
from Common.CEnum import KLINE_DIR, SEG_TYPE
from Common.ChanException import CChanException, ErrCode
from Seg.Seg import CSeg
from Seg.SegConfig import CSegConfig
from Seg.SegListComm import CSegListComm
from ZS.ZSList import CZSList

from .KLine import CKLine
from .KLine_Unit import CKLine_Unit


def get_seglist_instance(seg_config: CSegConfig, lv) -> CSegListComm:
    if seg_config.seg_algo == "chan":
        from Seg.SegListChan import CSegListChan
        return CSegListChan(seg_config, lv)
    elif seg_config.seg_algo == "1+1":
        print(f'Please avoid using seg_algo={seg_config.seg_algo} as it is deprecated and no longer maintained.')
        from Seg.SegListDYH import CSegListDYH
        return CSegListDYH(seg_config, lv)
    elif seg_config.seg_algo == "break":
        print(f'Please avoid using seg_algo={seg_config.seg_algo} as it is deprecated and no longer maintained.')
        from Seg.SegListDef import CSegListDef
        return CSegListDef(seg_config, lv)
    else:
        raise CChanException(f"unsupport seg algoright:{seg_config.seg_algo}", ErrCode.PARA_ERROR)


class CKLine_List:
    def __init__(self, kl_type, conf: CChanConfig):
        self.kl_type = kl_type
        self.config = conf
        self.lst: List[CKLine] = []  # K线列表，可递归  元素KLine类型
        self.bi_list = CBiList(bi_conf=conf.bi_conf)
        self.seg_list: CSegListComm[CBi] = get_seglist_instance(seg_config=conf.seg_conf, lv=SEG_TYPE.BI)
        self.segseg_list: CSegListComm[CSeg[CBi]] = get_seglist_instance(seg_config=conf.seg_conf, lv=SEG_TYPE.SEG)

        self.zs_list = CZSList(zs_config=conf.zs_conf)
        self.segzs_list = CZSList(zs_config=conf.zs_conf)

        self.bs_point_lst = CBSPointList[CBi, CBiList](bs_point_config=conf.bs_point_conf)
        self.seg_bs_point_lst = CBSPointList[CSeg, CSegListComm](bs_point_config=conf.seg_bs_point_conf)

        self.metric_model_lst = conf.GetMetricModel()

        self.step_calculation = self.need_cal_step_by_step()

    def __deepcopy__(self, memo):
        new_obj = CKLine_List(self.kl_type, self.config)
        memo[id(self)] = new_obj
        for klc in self.lst:
            klus_new = []
            for klu in klc.lst:
                new_klu = copy.deepcopy(klu, memo)
                memo[id(klu)] = new_klu
                if klu.pre is not None:
                    new_klu.set_pre_klu(memo[id(klu.pre)])
                klus_new.append(new_klu)

            new_klc = CKLine(klus_new[0], idx=klc.idx, _dir=klc.dir)
            new_klc.set_fx(klc.fx)
            new_klc.kl_type = klc.kl_type
            for idx, klu in enumerate(klus_new):
                klu.set_klc(new_klc)
                if idx != 0:
                    new_klc.add(klu)
            memo[id(klc)] = new_klc
            if new_obj.lst:
                new_obj.lst[-1].set_next(new_klc)
                new_klc.set_pre(new_obj.lst[-1])
            new_obj.lst.append(new_klc)
        new_obj.bi_list = copy.deepcopy(self.bi_list, memo)
        new_obj.seg_list = copy.deepcopy(self.seg_list, memo)
        new_obj.segseg_list = copy.deepcopy(self.segseg_list, memo)
        new_obj.zs_list = copy.deepcopy(self.zs_list, memo)
        new_obj.segzs_list = copy.deepcopy(self.segzs_list, memo)
        new_obj.bs_point_lst = copy.deepcopy(self.bs_point_lst, memo)
        new_obj.metric_model_lst = copy.deepcopy(self.metric_model_lst, memo)
        new_obj.step_calculation = copy.deepcopy(self.step_calculation, memo)
        new_obj.seg_bs_point_lst = copy.deepcopy(self.seg_bs_point_lst, memo)
        return new_obj

    @overload
    def __getitem__(self, index: int) -> CKLine:
        ...

    @overload
    def __getitem__(self, index: slice) -> List[CKLine]:
        ...

    def __getitem__(self, index: Union[slice, int]) -> Union[List[CKLine], CKLine]:
        return self.lst[index]

    def __len__(self):
        return len(self.lst)

    def cal_seg_and_zs(self):
        if not self.step_calculation:
            self.bi_list.try_add_virtual_bi(self.lst[-1])
        cal_seg(self.bi_list, self.seg_list)
        self.zs_list.cal_bi_zs(self.bi_list, self.seg_list)
        update_zs_in_seg(self.bi_list, self.seg_list, self.zs_list)  # 计算seg的zs_lst，以及中枢的bi_in, bi_out

        cal_seg(self.seg_list, self.segseg_list)
        self.segzs_list.cal_bi_zs(self.seg_list, self.segseg_list)
        update_zs_in_seg(self.seg_list, self.segseg_list, self.segzs_list)  # 计算segseg的zs_lst，以及中枢的bi_in, bi_out

        # 计算买卖点
        self.seg_bs_point_lst.cal(self.seg_list, self.segseg_list)  # 线段线段买卖点
        self.bs_point_lst.cal(self.bi_list, self.seg_list)  # 再算笔买卖点

    def need_cal_step_by_step(self):
        return self.config.trigger_step

    def add_single_klu(self, klu: CKLine_Unit):
        klu.set_metric(self.metric_model_lst)
        if len(self.lst) == 0:
            self.lst.append(CKLine(klu, idx=0))
        else:
            _dir = self.lst[-1].try_add(klu)
            if _dir != KLINE_DIR.COMBINE:  # 不需要合并K线
                self.lst.append(CKLine(klu, idx=len(self.lst), _dir=_dir))
                if len(self.lst) >= 3:
                    self.lst[-2].update_fx(self.lst[-3], self.lst[-1])
                if self.bi_list.update_bi(self.lst[-2], self.lst[-1], self.step_calculation) and self.step_calculation:
                    self.cal_seg_and_zs()
            elif self.step_calculation and self.bi_list.try_add_virtual_bi(self.lst[-1],
                                                                           need_del_end=True):  # 这里的必要性参见issue#175
                self.cal_seg_and_zs()

    def klu_iter(self, klc_begin_idx=0):
        for klc in self.lst[klc_begin_idx:]:
            yield from klc.lst

    def to_dataframe_dict(self):
        # Convert lst to DataFrame
        dict = {}
        dict['klu'] = pd.DataFrame([{
            'time': klu.time.to_str(),
            'idx': klu.idx,
            'high': klu.high,
            'low': klu.low,
            'open': klu.open,
            'close': klu.close
        } for klu in self.klu_iter(klc_begin_idx=0)])

        dict['klc'] = pd.DataFrame([{
            'begin_time': klc.time_begin.to_str(),
            'end_time': klc.time_end.to_str(),
            'idx': klc.idx,
            'dir': klc.dir.value,
            'high': klc.high,
            'low': klc.low,
            # 'fx': klc.fx,
        } for klc in self.lst])

        dict['bi'] = pd.DataFrame([{
            'begin_time': bi.get_begin_klu().time.to_str(),
            'end_time': bi.get_end_klu().time.to_str(),
            'dir': bi.dir.value,
            'begin_val': bi.get_begin_val(),
            'end_val': bi.get_end_val(),
            'bi_idx': bi.idx,
            # 'type': bi.type,
            'is_sure': bi.is_sure,
            # 'seg_idx': bi.seg_idx,
            # 'parent_seg': bi.parent_seg.idx if bi.parent_seg else None,
            # 'begin_klc': bi.begin_klc.idx,
            # 'end_klc': bi.end_klc.idx,
            'klu_cnt': bi.get_klu_cnt(),
            'klc_cnt': bi.get_klc_cnt(),
        } for bi in self.bi_list])

        dict['seg'] = pd.DataFrame([{
            'begin_time': seg.get_begin_klu().time.to_str(),
            'end_time': seg.get_end_klu().time.to_str(),
            'begin_val': seg.get_begin_val(),
            'end_val': seg.get_end_val(),
            'dir': seg.dir.value,
            'is_sure': seg.is_sure,
            # 'idx': seg.idx,
            # 'parent_seg': seg.parent_seg.idx if seg.parent_seg else None,
            # 'klu_cnt': seg.get_klu_cnt(),
        } for seg in self.seg_list])

        dict['zs'] = pd.DataFrame([{
            'begin_time': zs.get_begin_klu.time.to_str(),
            'end_time': zs.get_end_klu.time.to_str(),
            'begin_idx': zs.begin.idx,
            'end_idx': zs.end.idx,
            'w': zs.end - zs.begin,
            'h': zs.high - zs.low,
            'dir': zs.bi_out.dir.value,
            'high': zs.peak_high,
            'low': zs.peak_low,
            'is_sure': zs.is_sure,
            'is_onebi_zs': zs.is_one_bi_zs()
        } for zs in self.zs_list])

        dict['seg_seg'] = pd.DataFrame([{
            'begin_time': seg_seg.get_begin_klu().time.to_str(),
            'end_time': seg_seg.get_end_klu().time.to_str(),
            'dir': seg_seg.dir.value,
            'begin_val': seg_seg.get_begin_val(),
            'end_val': seg_seg.get_end_val(),
            'type': seg_seg.type,
            'is_sure': seg_seg.is_sure,
            # 'seg_idx': seg_seg.seg_idx,
            # 'idx': seg_seg.idx,
            # 'parent_seg': seg_seg.parent_seg.idx if seg_seg.parent_seg else None,
            # 'begin_klc': seg_seg.begin_klc.idx,
            # 'end_klc': seg_seg.end_klc.idx,
            # 'klu_cnt': seg_seg.get_klu_cnt(),
            # 'klc_cnt': seg_seg.get_klc_cnt(),
        } for seg_seg in self.segseg_list])

        dict['seg_zs'] = pd.DataFrame([{
            'begin_time': seg_zs.get_begin_klu.time.to_str(),
            'end_time': seg_zs.get_end_klu.time.to_str(),
            'begin_idx': seg_zs.begin.idx,
            'end_idx': seg_zs.end.idx,
            'dir': seg_zs.bi_out.dir.value,
            'high': seg_zs.peak_high,
            'low': seg_zs.peak_low,
            'is_sure': seg_zs.is_sure
        } for seg_zs in self.segzs_list])

        dict['bsp'] = pd.DataFrame([{
            'time': bsp.klu.time.to_str(),
            'idx': bsp.klu.idx,
            'desc': bsp.type2str(),
            'is_buy': bsp.is_buy,
            'is_seg_bsp': bsp.is_segbsp,
            'y': bsp.klu.low if bsp.is_buy else bsp.klu.high
            # 'type': bsp.type,
        } for bsp in self.bs_point_lst])

        return dict


def cal_seg(bi_list, seg_list: CSegListComm):
    seg_list.update(bi_list)

    sure_seg_cnt = 0
    if len(seg_list) == 0:
        for bi in bi_list:
            bi.set_seg_idx(0)
        return
    begin_seg: CSeg = seg_list[-1]
    for seg in seg_list[::-1]:
        if seg.is_sure:
            sure_seg_cnt += 1
        else:
            sure_seg_cnt = 0
        begin_seg = seg
        if sure_seg_cnt > 2:
            break

    cur_seg: CSeg = seg_list[-1]
    for bi in bi_list[::-1]:
        if bi.seg_idx is not None and bi.idx < begin_seg.start_bi.idx:
            break
        if bi.idx > cur_seg.end_bi.idx:
            bi.set_seg_idx(cur_seg.idx + 1)
            continue
        if bi.idx < cur_seg.start_bi.idx:
            assert cur_seg.pre
            cur_seg = cur_seg.pre
        bi.set_seg_idx(cur_seg.idx)


def update_zs_in_seg(bi_list, seg_list, zs_list):
    sure_seg_cnt = 0
    for seg in seg_list[::-1]:
        if seg.ele_inside_is_sure:
            break
        if seg.is_sure:
            sure_seg_cnt += 1
        seg.clear_zs_lst()
        for zs in zs_list[::-1]:
            if zs.end.idx < seg.start_bi.get_begin_klu().idx:
                break
            if zs.is_inside(seg):
                seg.add_zs(zs)
            assert zs.begin_bi.idx > 0
            zs.set_bi_in(bi_list[zs.begin_bi.idx - 1])
            if zs.end_bi.idx + 1 < len(bi_list):
                zs.set_bi_out(bi_list[zs.end_bi.idx + 1])
            zs.set_bi_lst(list(bi_list[zs.begin_bi.idx:zs.end_bi.idx + 1]))

        if sure_seg_cnt > 2:
            if not seg.ele_inside_is_sure:
                seg.ele_inside_is_sure = True
