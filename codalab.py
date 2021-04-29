import time
import requests

import requests
from requests import RequestException
from lxml import etree
from bs4 import BeautifulSoup

def methodGet(url, params=None, headers=None, redo=6):
    """
    :param headers:
    :param redo:
    :param proxy:
    :param params:
    :param url:str
    :return: :class:`Response <Response>` object
    :rtype: requests.Response
    It also needs parameters, which can be extended by yourself
    """
    if not headers:
        headers = {}
    proxies = None
    headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 ' \
                            '(KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'
    for i in range(redo):
        try:
            t = requests.get(url, timeout=16, params=params, proxies=proxies, headers=headers)
            state = t.status_code
            # 如果状态码是4开头的，表示请求可能出错了
            # print(state, t.url)
            if state in [400, 403, 500]:
                time.sleep(1)
                continue
            if state == 429:
                time.sleep(0.38)
                continue
            if 399 < state < 500:
                return None
            # 如果 HTTP 请求返回了不成功的状态码， Response.raise_for_status() 会抛出一个 HTTPError 异常。
            t.raise_for_status()
            return t
        # 所有Requests显式抛出的异常都继承自 requests.exceptions.RequestException 。
        except RequestException as e:
            time.sleep(2)
            print(e)
    print(url, redo)
    return None

def main():
    result_set = set()
    with open('results.txt', 'r') as f:
        for line in f:
            line = line.strip().split('\t')
            if len(line)<5:
                continue
            if tuple(line[1:]) not in result_set:
                result_set.add(tuple(line[1:]))
                print(line[1:])
    index = 0
    while True:
        index+=1
        time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        timeStamp = int(time.time())
        if index%100==0:
            print(time_str)  # 1381419600
        url = 'https://competitions.codalab.org/competitions/28029/results/46092?_=' + str(timeStamp)
        req = methodGet(url=url)
        if req is None:
            continue
        html = req.text
        soup = BeautifulSoup(html, "lxml")
        table = soup.find('table', class_='resultsTable dataTable')
        trs = table.find_all('tr')
        for tr in trs[3:6]:
            tds = tr.find_all('td')
            teamname = str(tds[1].p.text).strip()
            entries = str(tds[2].text).strip()
            data_of_last = str(tds[3].text).strip()
            mAP = str(tds[5].text).strip()
            if (teamname, entries, data_of_last, mAP) not in result_set:
                result_set.add((teamname, entries, data_of_last, mAP))

                with open('results.txt', 'a') as f:
                    f.write(time_str + '\t' + teamname + '\t' + entries + '\t' + data_of_last + '\t' + mAP + '\n')
                print(time_str + '\t' + teamname + '\t' + entries + '\t' + data_of_last + '\t'  + mAP +'\n')
        for tr in trs[6:15]:
            tds = tr.find_all('td')
            teamname = str(tds[1].text).strip()
            entries = str(tds[2].text).strip()
            data_of_last = str(tds[3].text).strip()
            mAP = str(tds[5].text).strip()

            if (teamname, entries, data_of_last, mAP) not in result_set:
                result_set.add((teamname, entries, data_of_last, mAP))

                with open('results.txt', 'a') as f:
                    f.write(time_str + '\t' + teamname + '\t' + entries + '\t' + data_of_last + '\t' + mAP +'\n')
                print(time_str + '\t' + teamname + '\t' + entries + '\t' + data_of_last + '\t'  + mAP  +'\n')
if __name__ == '__main__':
    main()
