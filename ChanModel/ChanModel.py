from typing import TypedDict, Union, List, Optional, Dict

class ChanProcessConfig(TypedDict, total=False):
    # 中枢相关配置
    zs_combine: bool  # 是否进行中枢合并，默认为 True
    zs_combine_mode: str  # 中枢合并模式，取值：zs（两中枢区间有重叠才合并，默认）、peak（两中枢有K线重叠就合并）
    one_bi_zs: bool  # 是否需要计算只有一笔的中枢（分析趋势时会用到），默认为 False
    zs_algo: str  # 中枢算法，取值：normal（段内中枢，默认）、over_seg（跨段中枢）、auto（自动）

    # 笔相关配置
    bi_algo: str  # 笔算法，取值：normal（按缠论笔定义来算，默认）、fx（顶底分形即成笔）
    bi_strict: bool  # 是否只用严格笔(bi_algo=normal时有效)，默认为 True
    gap_as_kl: bool  # 缺口是否处理成一根K线，默认为 True
    bi_end_is_peak: bool  # 笔的尾部是否是整笔中最低/最高，默认为 True
    bi_fx_check: str  # 检查笔顶底分形是否成立的方法，取值：strict（默认）、totally、loss、half
    bi_allow_sub_peak: bool  # 是否允许次高点成笔，默认为 True

    # 线段相关配置
    seg_algo: str  # 线段计算方法，取值：chan（利用特征序列来计算，默认）、1+1（都业华版本 1+1 终结算法）、break（线段破坏定义来计算线段）
    left_seg_method: str  # 剩余那些不能归入确定线段的笔如何处理成段，取值：all（收集至最后一个方向正确的笔，成为一段）、peak（默认，如果有个靠谱的新的极值，那么分成两段）

    # 指标相关配置
    mean_metrics: List[int]  # 均线计算周期（用于生成特征及绘图时使用），默认为空[]，例子：[5,20]
    trend_metrics: List[int]  # 计算上下轨道线周期，即 T 天内最高/低价格（用于生成特征及绘图时使用），默认为空[]
    boll_n: int  # 布林线参数 N，整数，默认为 20（用于生成特征及绘图时使用）
    macd: Dict[str, int]  # MACD配置，默认为 {"fast": 12, "slow": 26, "signal": 9}
    cal_demark: bool  # 是否计算demark指标，默认为 False
    demark: Dict[str, Union[int, bool]]  # 德马克指标配置，默认为 {
    #     'demark_len': 9,
    #     'setup_bias': 4,
    #     'countdown_bias': 2,
    #     'max_countdown': 13,
    #     'tiaokong_st': True,
    #     'setup_cmp2close': True,
    #     'countdown_cmp2close': True,
    # }
    cal_rsi: bool  # 是否计算rsi指标，默认为 False
    rsi_cycle: int  # rsi计算周期，默认为 14
    cal_kdj: bool  # 是否计算kdj指标，默认为 False
    kdj_cycle: int  # kdj计算周期，默认为 9

    # 其他配置
    trigger_step: bool  # 是否回放逐步返回，默认为 False，用于逐步回放绘图时使用
    skip_step: int  # trigger_step 为 True 时有效，指定跳过前面几根K线，默认为 0
    kl_data_check: bool  # 是否需要检验K线数据，检查项包括时间线是否有乱序，大小级别K线是否有缺失；默认为 True
    max_kl_misalgin_cnt: int  # 在次级别找不到K线最大条数，默认为 2（次级别数据有缺失），kl_data_check 为 True 时生效
    max_kl_inconsistent_cnt: int  # 天K线以下（包括）子级别和父级别日期不一致最大允许条数（往往是父级别数据有缺失），默认为 5，kl_data_check 为 True 时生效
    print_warning: bool  # 打印K线不一致的明细，默认为 True
    print_err_time: bool  # 计算发生错误时打印因为什么时间的K线数据导致的，默认为 False
    auto_skip_illegal_sub_lv: bool  # 如果获取次级别数据失败，自动删除该级别（比如指数数据一般不提供分钟线），默认为 False

    # 模型相关配置
    model: Optional[str]  # 模型类，支持接入机器学习模型对买卖点打分，参见下文「模型」，默认为 None
    score_thred: Optional[float]  # 模型开仓平仓分数阈值，model 配置时生效，默认为 None
    cal_feature: bool  # 是否计算特征，默认为 False（加速计算），但是如果开启了 model 或者 cbsp_strategy 会被强制设置成 True

    # 离群点检测相关配置
    od_win_width: int  # 离群点检测窗口，默认为 100
    od_mean_thred: float  # 离群点检测阈值，默认为 3.0
    od_max_zero_cnt: Optional[int]  # 指标为 0 的K线最大值，超过回抛异常，默认为 None，表示不检测
    od_skip_zero: bool  # 自动跳过指标为 0 的指标，（即不把 0 当做指标），默认为 True

    # 买卖点相关配置
    divergence_rate: float  # 1类买卖点背驰比例，即离开中枢的笔的 MACD 指标相对于进入中枢的笔，默认为 0.9
    min_zs_cnt: int  # 1类买卖点至少要经历几个中枢，默认为 1
    bsp1_only_multibi_zs: bool  # min_zs_cnt 计算的中枢至少 3 笔（少于 3 笔是因为开启了 one_bi_zs 参数），默认为 True
    max_bs2_rate: float  # 2类买卖点那一笔回撤最大比例，默认为 0.9999
    bs1_peak: bool  # 1类买卖点位置是否必须是整个中枢最低点，默认为 True
    macd_algo: str  # MACD指标算法（可自定义），取值：peak（红绿柱最高点，默认）、full_area（整根笔对应的MACD的面积）、area（整根笔对应的MACD的面积，只考虑相应红绿柱）、slope（笔斜率）、amp（笔的涨跌幅）、diff（首尾K线对应的MACD柱子高度的差值的绝对值）、amount（笔上所有K线成交额总和）、volumn（笔上所有K线成交量总和）、amount_avg（笔上K线平均成交额）、volumn_avg（笔上K线平均成交量）、turnrate_avg（笔上K线平均换手率）、rsi（笔上RSI值极值）
    bs_type: str  # 关注的买卖点类型，逗号分隔，默认"1,1p,2,2s,3a,3b"
    bsp2_follow_1: bool  # 2类买卖点是否必须跟在1类买卖点后面（用于小转大时1类买卖点因为背驰度不足没生成），默认为 True
    bsp3_follow_1: bool  # 3类买卖点是否必须跟在1类买卖点后面（用于小转大时1类买卖点因为背驰度不足没生成），默认为 True
    bsp3_peak: bool  # 3类买卖点突破笔是不是必须突破中枢里面最高/最低的，默认为 False
    bsp2s_follow_2: bool  # 类2买卖点是否必须跟在2类买卖点后面（2类买卖点可能由于不满足 max_bs2_rate 最大回测比例条件没生成），默认为 False
    max_bsp2s_lv: Optional[int]  # 类2买卖点最大层级（距离2类买卖点的笔的距离/2），默认为None，不做限制
    strict_bsp3: bool  # 3类买卖点对应的中枢必须紧挨着1类买卖点，默认为 False

    # 自定义策略类相关配置
    cbsp_strategy: Optional[str]  # 自定义策略类，默认为 None，框架自带实现类别为 CCustomStrategy/CSegBspStrategy
    strategy_para: Dict  # 需要传递给自定义买卖点的参数，字典，默认为{}
    strict_open: bool  # 严格开仓条件，即如果对一个买卖点当下无法找到合适的买卖时机却已经完成一笔了，就放弃。默认为 True
    use_qjt: bool  # 使用区间套计算买卖点（多级别下才有效），默认为 True
    short_shelling: bool  # 是否做空，默认为 True
    judge_on_close: bool  # 根据K线收盘价来作为开/平仓指标，默认为 True（否则当天K线某一时刻突破了信号阈值即会交易）
    max_sl_rate: Optional[float]  # 最大止损阈值（如果策略计算出来的止损阈值超过此值，会被截断），默认为 None
    max_profit_rate: Optional[float]  # 最大止盈阈值（比如买点买了，卖点还没出现但收益已经超过该值），默认为 None
    only_judge_last: bool  # 只计算最后一跟K线的买卖点类型/买卖点信号，默认为 False。开启后速度非常快，适合用于海量选股时使用，或者每天计算出现交易信号的股票时使用
    cal_cover: bool  # 是否计算平仓，默认为 True；（对做空同样生效）
    cbsp_check_active: bool  # cbsp 开仓是否需要满足交易活跃度指标，默认为 True，既不交易不活跃股票
    print_inactive_reason: bool  # 是否打印股票不活跃原因，默认为 False
    stock_no_active_day: int  # 不活跃股票计算检测最近多少根K线，默认为 30
    stock_no_active_thred: int  # stock_no_active_day 根K线内一字线超过阈值则定义为不活跃；（涨跌停除外），默认为 3
    stock_distinct_price_thred: int  # stock_no_active_day 根K线内股价多样性低于多少则定义为不活跃，默认为 25


class PlotConfig(TypedDict):
    """
    绘图配置字典，用于控制绘图元素的显示。
    """
    plot_kline: bool  # 画K线，默认为 False
    plot_kline_combine: bool  # 画合并K线，默认为 False
    plot_bi: bool  # 画笔，默认为 False
    plot_seg: bool  # 画线段，默认为 False
    plot_eigen: bool  # 画特征序列（一般调试用），默认为 False
    plot_zs: bool  # 画中枢，默认为 False
    plot_segseg: bool  # 画线段分段，默认为 False
    plot_bsp: bool  # 画理论买卖点，默认为 False
    plot_cbsp: bool  # 画自定义策略买卖点位置，默认为 False
    plot_segzs: bool  # 画线段中枢，默认为 False
    plot_segbsp: bool  # 画线段的理论买卖点，默认为 False
    plot_macd: bool  # 画 MACD 图（图片下方额外开一幅图），默认为 False
    plot_channel: bool  # 画上下轨道，默认为 False
    plot_boll: bool  # 画布林线，默认为 False
    plot_mean: bool  # 画均线，默认为 False
    plot_tradeinfo: bool  # 绘制配置的额外信息（在另一根 y 轴上），默认为 False
    plot_marker: bool  # 添加自定义文本标记，默认为 False
    plot_demark: bool  # 绘制Demark指标，默认为 False
    plot_rsi: bool  # 绘制rsi指标，默认为 False
    plot_kdj: bool  # 绘制kdj指标，默认为 False
