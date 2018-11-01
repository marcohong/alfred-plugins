# -*-   coding: utf-8 -*-
'''
由于alfred-workflow 支持Python 2.6 and 2.7，请使用安装python2.7

感谢以下的项目，排名不分先后
    ip2region: https://github.com/lionsoul2014/ip2region
    workflow: https://github.com/deanishe/alfred-workflow
'''
import os
import sys
import socket
from workflow import Workflow
from ip2Region import Ip2Region


ROOT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__)))


def init_db():
    file_path = os.path.join(ROOT_PATH, 'ip2region.db')
    return Ip2Region(file_path)


def get_local_ip():
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.connect(('8.8.8.8', 80))
        ip = sock.getsockname()[0]
    except:
        ip = '127.0.0.1'
    finally:
        sock.close()
    return ip


def main(wf):
    if wf.args and Ip2Region.isip(wf.args[0]):
        region = init_db()
        data = region.binarySearch(wf.args[0])
        if data:
            region = data['region'].decode('utf-8')
            wf.add_item(title=wf.args[0],
                        subtitle=region, arg=region, valid=True)
        else:
            wf.add_item(
                title=wf.args[0], subtitle=u'Ip地址格式不正确', valid=True)
    else:
        ipaddr = get_local_ip()
        wf.add_item(title=u'本机地址: %s' % ipaddr, arg=ipaddr, valid=True)
    wf.send_feedback()


if __name__ == '__main__':
    wf = Workflow()
    sys.exit(wf.run(main))
