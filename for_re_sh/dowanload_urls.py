import re
import os
import tqdm
import pandas as pd
import requests
import grequests
import datetime
import json
from pathlib import Path
import warnings

# 显示所有列
pd.set_option('display.max_columns', None)
# 显示所有行
pd.set_option('display.max_rows', None)
# 设置value的显示长度为100，默认为50
pd.set_option('max_colwidth', 100)

warnings.filterwarnings("ignore")

code_name_pairs = dict(pd.read_excel("../上海证券公司代码.xlsx", converters={"Stkcd": str}).values)


class SH(object):
    def __init__(self, cookies):
        """
        :param cookies:  您的cookies
        """
        self.cookies = cookies

    def date_ranges(self):
        begin = datetime.datetime(1990, 11, 26)
        now = datetime.datetime.today()
        interv = datetime.timedelta(days=900)
        dates = []
        date = begin
        while True:
            if (date < now) & (date + interv < now):
                date = date + interv
                dates.append(date.strftime('%Y-%m-%d'))
            else:
                dates.append(now.strftime('%Y-%m-%d'))
                break
        return [(d1, d2) for d1, d2 in zip(dates, dates[1:])]

    def companys(self):
        """
        上证所有上市公司名录，公司名及股票代码
        :return: 返回DataFrame
        """
        names = []
        codes = []
        for code, name in code_name_pairs.items():
            names.append(name)
            codes.append(code)
        data = {'name': names, 'code': codes}
        df = pd.DataFrame(data)
        return df

    def disclosure(self, code):
        """
        获得该公司的股票代码、报告类型、年份、定期报告披露日期、定期报告pdf下载链接，返回DataFrame。
        :param code:  股票代码
        :return: 返回DataFrame
        """
        print('正在获取{}定期报告披露信息'.format(code))

        datas = []

        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36',
            'Referer': 'http://www.sse.com.cn/disclosure/listedinfo/regular/'}
        base = 'http://query.sse.com.cn/security/stock/queryCompanyBulletin.do?isPagination=true&productId={code}&securityType=0101%2C120100%2C020100%2C020200%2C120200&reportType2=DQBG&reportType=&beginDate={beginDate}&endDate={endDate}&pageHelp.pageSize=25&pageHelp.pageCount=50&pageHelp.pageNo=1&pageHelp.beginPage=1&pageHelp.cacheSize=1&pageHelp.endPage=5'
        dateranges = self.date_ranges()
        for begin, end in dateranges:
            url = base.format(code=code, beginDate=begin, endDate=end)
            resp = requests.get(url, headers=headers, cookies=self.cookies)
            raw_data = json.loads(resp.text)
            results = raw_data['result']
            for result in results:
                pdf = 'http://www.sse.com.cn' + result['URL']
                # if re.search('\d{6}_\d{4}_[13nz].pdf', pdf):    # 这是源码的正则表达式，我改了
                if re.search('\d{6}_\d+_\w+.pdf', pdf):

                    company = code_name_pairs[str(code)]
                    _type = result['BULLETIN_TYPE']
                    year = result['BULLETIN_YEAR']
                    date = result['SSEDATE']
                    data = [company, code, _type, year, date, pdf]
                    if ("摘要" in _type) or ("补充" in _type) or ("公告" in _type):
                        continue
                    datas.append(data)

        df = pd.DataFrame(datas, columns=['company', 'code', 'type', 'year', 'date', 'pdf'])
        return df

    def pdfurls(self, code):
        """
        仅获取定期报告pdf下载链接
        :param code:  股票代码
        :return: 年报pdf链接
        """
        print('准备获取{}年报文件链接'.format(code))
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36',
            'Referer': 'http://www.sse.com.cn/disclosure/listedinfo/regular/'}
        URLs = []
        base = 'http://query.sse.com.cn/security/stock/queryCompanyBulletin.do?isPagination=true&productId={code}&securityType=0101%2C120100%2C020100%2C020200%2C120200&reportType2=DQBG&reportType=&beginDate={beginDate}&endDate={endDate}&pageHelp.pageSize=25&pageHelp.pageCount=50&pageHelp.pageNo=1&pageHelp.beginPage=1&pageHelp.cacheSize=1&pageHelp.endPage=5'
        dateranges = self.date_ranges()
        for begin, end in dateranges:
            url = base.format(code=code, beginDate=begin, endDate=end)
            resp = requests.get(url, headers=headers, cookies=self.cookies)
            raw_data = json.loads(resp.text)
            results = raw_data['result']
            for result in results:
                _type = result['BULLETIN_TYPE']
                if ("摘要" in _type) or ("补充" in _type) or ("公告" in _type):
                    continue
                URL = 'http://www.sse.com.cn' + result['URL']

                if re.search('\d{6}_\d+_\w+.pdf', URL):
                    URLs.append(URL)
                else:
                    continue
        print('        ', URLs)
        return URLs

    def download(self, code, savepath):
        """
        下载该公司（code）的所有季度报告、半年报、年报pdf文件
        :param code:  上市公司股票代码
        :param savepath:  数据存储所在文件夹的路径，建议使用相对路径
        :return:
        """

        # path = Path(savepath).joinpath(*('disclosure', 'reports', str(code)))
        # Path(path).mkdir(parents=True, exist_ok=True)  # 这两行是我注释掉的

        path = Path(savepath)
        Path(path).mkdir(parents=True, exist_ok=True)

        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36',
            'Referer': 'http://www.sse.com.cn/disclosure/listedinfo/regular/'}

        urls = self.pdfurls(code=code)
        tasks = [grequests.request("GET", url=url, headers=headers, cookies=self.cookies) for url in urls]
        results = grequests.map(tasks)

        for result in results:
            try:
                pdfname = result.url.split('/')[-1]
                pdfpath = path.joinpath(pdfname)

                with open(pdfpath, 'wb') as f:
                    f.write(result.content)
                    print('       已成功下载{}'.format(pdfname))
            except:
                pass


if __name__ == '__main__':
    """
        这是第一步：获取下载链接
    """
    cookies = {
        "Cookie": 'sseMenuSpecial=8311; yfx_c_g_u_id_10000042=_ck22022316204014925274528673892; yfx_f_l_v_t_10000042=f_t_1645604440470__r_t_1645604440470__v_t_1645604440470__r_c_0; VISITED_MENU=%5B%228312%22%5D'}
    sh = SH(cookies)

    save_path = r"./download_urls"
    os.makedirs(save_path, exist_ok=True)

    for com_code, com_name in tqdm.tqdm(code_name_pairs.items()):
        df = sh.disclosure(com_code)
        df = df[df["year"] >= "2009"]

        # 把url所在列名复制一个
        df["url"] = df["pdf"]
        # 获取pdf名称
        pdfs_name = [name.split("/")[-1] for name in df["url"].tolist()]
        df["pdf"] = pdfs_name
        df.sort_values(by=["year", "date"], inplace=True)

        # 去重(有看到pdf名字完全一样的两行，只是在具体日期上有所不同,保留最后一个)
        df.drop_duplicates(["pdf"], keep="last", inplace=True)
        df.reset_index(drop=True, inplace=True)

        # 更改column的顺序
        columns = ["code", "company", "type", "year", "date", "pdf", "url"]
        df = df.reindex(columns=columns)

        df.to_excel(os.path.join(save_path, com_code + "_" + com_name + ".xlsx"))
    print("Done！")
