from vnpy.trader.constant import Direction
from vnpy.trader.object import TradeData, OrderData, TickData
from vnpy.trader.engine import BaseEngine
from vnpy.app.algo_trading import AlgoTemplate
import math


'''
############################################################
作者：张峻铭
新增：需要引入数据库机制，存储实时变化的pos，存储对应标的的设置，持仓等信息
1、引入数据库
2、引入持仓参数
############################################################
'''

class GridAlgo(AlgoTemplate):
    """"""

    display_name = "Grid 网格"

    default_setting = {
        "vt_symbol": "",
        "price": 0.0,
        "step_price": 0.0,
        "step_volume": 0,
        "interval": 10,
    }

    variables = [
        "pos",
        "timer_count",
        "vt_orderid"
    ]

    def __init__(
        self,
        algo_engine: BaseEngine,
        algo_name: str,
        setting: dict
    ):
        """"""
        super().__init__(algo_engine, algo_name, setting)

        # Parameters
        self.vt_symbol = setting["vt_symbol"]
        self.price = setting["price"]
        self.step_price = setting["step_price"]
        self.step_volume = setting["step_volume"]
        self.interval = setting["interval"]

        # Variables
        self.timer_count = 0
        self.vt_orderid = ""
        '''
        #########################################################################
        作者：张峻铭
        新增：获取系统中单个品种的持仓，这里与cta不同，cta是获取的文件仓位，
        所以存在直接的net pos，这里获取的是账号总仓位，所以要自我调节。
        但要注意，这里并没有考虑和cta的融合，既cta按照自己记录的仓位有可能在这里被
        消耗掉，将来进行改进的时候需要在这里加入存储文件
        1、将pos转变为net pos，不考虑冻结掉的仓位，因为那可能是交易员自主挂单
        
        # get_position返回的是holding对象，里面各种属性
        # print(self.get_position(self.vt_symbol).long_pos)
        #########################################################################
        '''
        self.pos = self.get_position(self.vt_symbol).long_pos - self.get_position(self.vt_symbol).short_pos
        self.last_tick = None

        self.subscribe(self.vt_symbol)
        self.put_parameters_event()
        self.put_variables_event()

        # # 测试使用
        # self.on_timer()

    def on_tick(self, tick: TickData):
        """"""
        self.last_tick = tick

    def on_timer(self):
        """"""
        if not self.last_tick:
            return

        self.timer_count += 1
        if self.timer_count < self.interval:
            self.put_variables_event()
            return
        self.timer_count = 0

        if self.vt_orderid:
            self.cancel_all()

        '''
        ############################################################
        作者：张峻铭
        新增：原生代码没有考虑开平仓问题，这里需要修改
        1、先将sell变为short
        2、self.pos为轧差值，可正可负，判断后再处理
        3、对于仓位加绝对值先处理，然后根据pos的正负进行处理
        
        源代码：
        # Calculate target volume to buy and sell
        target_buy_distance = (
            self.price - self.last_tick.ask_price_1) / self.step_price
        target_buy_position = math.floor(
            target_buy_distance) * self.step_volume
        target_buy_volume = target_buy_position - self.pos

        # Calculate target volume to sell
        target_sell_distance = (
            self.price - self.last_tick.bid_price_1) / self.step_price
        target_sell_position = math.ceil(
            target_sell_distance) * self.step_volume
        target_sell_volume = self.pos - target_sell_position


        # Buy when price dropping
        # 首先判断目前仓位
        if target_buy_volume > 0:
            self.vt_orderid = self.buy(
                self.vt_symbol,
                self.last_tick.ask_price_1,
                min(target_buy_volume, self.last_tick.ask_volume_1)
            )
        # Sell when price rising
        elif target_sell_volume > 0:
            self.vt_orderid = self.short(
                self.vt_symbol,
                self.last_tick.bid_price_1,
                min(target_sell_volume, self.last_tick.bid_volume_1)
            )
        ############################################################
        '''
        # Calculate target volume to buy and sell
        target_buy_distance = (
            self.price - self.last_tick.ask_price_1) / self.step_price
        target_buy_position = math.floor(
            target_buy_distance) * self.step_volume
        target_buy_volume = target_buy_position - abs(self.pos)

        # Calculate target volume to sell
        target_sell_distance = (
            self.price - self.last_tick.bid_price_1) / self.step_price
        target_sell_position = math.ceil(
            target_sell_distance) * self.step_volume
        target_sell_volume = abs(self.pos) - target_sell_position

        if(self.pos == 0):
            # 多开，空开
            if target_buy_volume > 0:
                self.vt_orderid = self.buy(
                    self.vt_symbol,
                    self.last_tick.ask_price_1,
                    min(target_buy_volume, self.last_tick.ask_volume_1)
                )
            # Sell when price rising
            elif target_sell_volume > 0:
                self.vt_orderid = self.short(
                    self.vt_symbol,
                    self.last_tick.bid_price_1,
                    min(target_sell_volume, self.last_tick.bid_volume_1)
                )
        elif(self.pos > 0):
            # 多开，空平
            if target_buy_volume > 0:
                self.vt_orderid = self.buy(
                    self.vt_symbol,
                    self.last_tick.ask_price_1,
                    min(target_buy_volume, self.last_tick.ask_volume_1)
                )
            # Sell when price rising
            elif target_sell_volume > 0:
                self.vt_orderid = self.sell(
                    self.vt_symbol,
                    self.last_tick.bid_price_1,
                    min(target_sell_volume, self.last_tick.bid_volume_1)
                )
        elif(self.pos < 0):
            # 多平，空开
            if target_buy_volume > 0:
                self.vt_orderid = self.cover(
                    self.vt_symbol,
                    self.last_tick.ask_price_1,
                    min(target_buy_volume, self.last_tick.ask_volume_1)
                )
            # Sell when price rising
            elif target_sell_volume > 0:
                self.vt_orderid = self.short(
                    self.vt_symbol,
                    self.last_tick.bid_price_1,
                    min(target_sell_volume, self.last_tick.bid_volume_1)
                )

        # Update UI
        self.put_variables_event()

    def on_order(self, order: OrderData):
        """"""
        if not order.is_active():
            self.vt_orderid = ""
            self.put_variables_event()

    def on_trade(self, trade: TradeData):
        """"""
        if trade.direction == Direction.LONG:
            self.pos += trade.volume
        else:
            self.pos -= trade.volume

        self.put_variables_event()
