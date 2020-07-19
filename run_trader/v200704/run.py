'''
#########################################################################
作者：张峻铭
新增：
1、独立运行文件，使用命令行模式
#########################################################################
'''

from logging import INFO
from time import sleep
import sys
sys.path.append('D:\\Project\\Python\\vnpy')
try:
    sys.setdefaultencoding('utf8')
except AttributeError:
    pass

from vnpy.event import EventEngine

from vnpy.trader.engine import MainEngine
from vnpy.trader.ui import MainWindow, create_qapp
from vnpy.trader.setting import SETTINGS
from vnpy.trader.utility import load_json

from vnpy.gateway.rohon import RohonGateway
from vnpy.app.algo_trading import AlgoTradingApp
from vnpy.app.risk_manager import RiskManagerApp


SETTINGS["log.level"] = INFO
SETTINGS["log.console"] = True

def main():

    SETTINGS["log.file"] = True

    qapp = create_qapp()

    event_engine = EventEngine()
    main_engine = MainEngine(event_engine)

    # main_engine.write_log(u'<主引擎>创建成功')

    main_engine.add_gateway(RohonGateway)

    main_engine.add_app(AlgoTradingApp)
    main_engine.add_app(RiskManagerApp)

    # main_engine.write_log(u'<应用>启动成功')
    #
    # ctp_setting = load_json('connect_rohon.json')
    # main_engine.connect(ctp_setting, "ROHON")
    # main_engine.write_log(u'<<< 连接CTP接口 >>>')

    # sleep(30)

    main_window = MainWindow(main_engine, event_engine)
    main_window.showMaximized()

    qapp.exec()


if __name__ == '__main__':
    main()