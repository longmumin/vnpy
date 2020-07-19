1、vnpy.trader.converter 中的 OffsetConverter是用来记录持仓的，当想维护一个不同于账户的持仓时，可以创建一个self.offset_converter，用于
更新自己维护的持仓，所有的持仓（holding），委托（oder request），成交（trade）都可以通过offset_converter进行更新
这个新的模块替换了之前容易出错的每个cta策略的持仓设计
