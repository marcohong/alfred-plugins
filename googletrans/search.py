# -*-   coding: utf-8 -*-
'''
由于alfred-workflow 支持Python 2.6 and 2.7，请使用安装python2.7

感谢以下的项目，排名不分先后
    execjs: https://github.com/doloopwhile/PyExecJS
    workflow: https://github.com/deanishe/alfred-workflow
'''
import sys
import time
import urllib
from workflow import Workflow, web
from gen_tk import GenTK

reload(sys)
sys.setdefaultencoding('utf-8')

LANG = {
    'zh': ('zh-CN', 'en'),
    'en': ('en', 'zh-CN')
}

HEADERS = {
    'user-agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36',
    'accept-language': 'zh-CN,zh;q=0.9,en-GB;q=0.8,en;q=0.7,zh-TW;q=0.6',
}


def check_contain_chinese(text):
    for _str in text.decode('utf-8'):
        if u'\u4e00' <= _str <= u'\u9fff':
            return True
    return False


def check_max_len(text):
    if len(text) > 4891:
        return False
    return True


def get_url(text, lang='zh'):
    '''
    :param lang: <str> zh or en
    '''
    sl, tl = LANG.get(lang)
    js = GenTK()
    tk = js.get_tk(text)
    text = urllib.quote(text.encode('utf-8', 'replace'))
    _url = 'https://translate.google.cn/translate_a/single?'\
        'client=t&sl={sl}&tl={tl}&hl=zh-CN&dt=at&dt=bd&dt=ex&dt=ld'\
        '&dt=md&dt=qca&dt=rw&dt=rm&dt=ss&dt=t&ie=UTF-8&oe=UTF-8&ssel'\
        '=5&tsel=5&kc=1&tk={tk}&q={text}'.format(
            sl=sl, tl=tl, tk=tk, text=text)
    return _url


def request_url(url):
    req = web.get(url, headers=HEADERS)
    req.raise_for_status()
    return req.json()


def trans_zh_to_en(text):
    url = get_url(text, 'zh')
    return request_url(url)


def trans_en_to_zh(text):
    url = get_url(text, 'en')
    return request_url(url)


def google_translate(text):
    func = trans_zh_to_en if check_contain_chinese(text) else trans_en_to_zh
    return func(text)


def translate_url(text):
    lang = 'zh-CN'if not check_contain_chinese(text) else 'en'
    text = urllib.quote(text.encode('utf-8', 'replace'))
    url = 'https://translate.google.cn/#auto/{lang}/{text}'.format(
        lang=lang, text=text)
    return url


def process_child(wf, url, datas):
    for data in datas[1]:
        if len(data) >= 2:
            for sub in data[2]:
                subtitle = '{0}: {1}'.format(data[0], ', '.join(sub[1]))
                wf.add_item(title=sub[0], subtitle=subtitle,
                            quicklookurl=url, arg=sub[0],
                            valid=True)


def main(wf):
    if not wf.args:
        wf.add_item(title=u'请输入要翻译的内容',
                    subtitle=u'只支持中文--英文，英文--中文翻译', valid=True)
    else:
        text = wf.args[0].decode('utf-8', 'replace')
        if not check_max_len(text):
            wf.add_item(title=u'翻译内容太长',
                        subtitle=u'翻译内容不能超过4891个字符', valid=True)
        else:
            time.sleep(0.1)
            data = google_translate(text)
            url = translate_url(text)
            if not data:
                wf.add_item(title=text, subtitle=text,
                            quicklookurl=url, arg=text, valid=True)
            else:
                result = data[0][0][0]
                wf.add_item(title=text, subtitle=result,
                            quicklookurl=url, arg=text, valid=True)
                if data[1]:
                    process_child(wf, url, data)

    wf.send_feedback()

if __name__ == '__main__':
    wf = Workflow()
    sys.exit(wf.run(main))
