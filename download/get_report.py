# _author : litufu
# date : 2018/5/20
import os,django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "data_extract.settings")
django.setup()

import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import os
import datetime

from report_data_extract import models

class NotFoundPdfUrlException(Exception):
    def __init__(self, err='没有找到pdf报告url地址'):
        Exception.__init__(self, err)

class GetPdfReport(object):

    def __init__(self,code,ftype,year,path=None):
        '''

                :param stock_str: 股票代码
                :param ftype: 报告类型:zqbg,ndbg,yjdbg,sjdbg
                :return: 报告查询的url地址
                '''
        self.code = code
        self.ftype = ftype
        self.year = str((int(year) + 1)) if self.ftype == 'ndbg' else year
        self.path = path
        self.url = self.get_url()
        self.content = self.get_content()
        self.bs_obj = BeautifulSoup(self.content,'lxml')


    def get_url(self):
        return 'http://vip.stock.finance.sina.com.cn/corp/view/vCB_BulletinGather.php?stock_str={}&ftype={}'.format(self.code,self.ftype)

    def get_content(self):
        return requests.get(self.url).content


    def get_disclosure_date(self):
        #由于公司可能存在披露后修改报告的情况，因此应该存储报告披露日期，以便于修改后更新原报告
        df = pd.read_html(self.content,parse_dates=True)[0]
        df['日期'] = pd.to_datetime(df['日期'])
        df = df.set_index('日期')
        df = df[self.year]
        df = df.sort_index(ascending=False)
        disclosure_date = df.index[0].date()
        return str(disclosure_date)

    def get_pdf_url(self):
        date = self.bs_obj.find(text=self.get_disclosure_date())
        if date is not None:
            name = date.find_parent('td').find_previous_sibling("th")
            if name is not None:
                pdf_name = name.find(text=re.compile('查看PDF公告'))
                if pdf_name is not None:
                    return pdf_name.find_parent('a')['href']
                else:
                    raise NotFoundPdfUrlException
            else:
                raise NotFoundPdfUrlException
        else:
          raise NotFoundPdfUrlException

    def get_code_market(self):
        if self.code.startswith('6'):
            market = 'sh'
        elif self.code.startswith('3'):
            market = 'sz'
        elif self.code.startswith('0'):
            market = 'sz'
        else:
            raise Exception

        return market

    def get_report_date(self):
        '''返回文本形式的报告日期，用于文件命名'''
        year = int(self.year)
        if self.ftype == 'ndbg':
            date = '{}1231'.format(year-1)
        elif self.ftype == 'zqbg':
            date = '{}0630'.format(year)
        elif self.ftype == 'yjdbg':
            date = '{}0331'.format(year)
        elif self.ftype == 'sjdbg':
            date = '{}0930'.format(year)
        else:
            raise Exception
        return date

    def get_report_datetime(self):
        '''返回日期形式的报告日期，用于存储下载记录到数据库'''
        report_date_str = self.get_report_date()
        year = int(report_date_str[:4])
        month = int(report_date_str[4:6])
        day = int(report_date_str[6:])
        report_date = datetime.date(year=year, month=month, day=day)
        return report_date

    def download_report(self):
        if self.is_download_report():
            pass
        else:
            report_date = self.get_report_date()
            market = self.get_code_market()
            file_name = "{}_{}_{}.pdf".format(market,self.code,report_date)
            pdf_url = self.get_pdf_url()
            r = requests.get(pdf_url)
            if self.path == None:
                with open(file_name, "wb") as code:
                    code.write(r.content)
            else:
                file_path = os.path.join(self.path,file_name)
                with open(file_path, "wb") as code:
                    code.write(r.content)
            self.record_download_report()

    def is_download_report(self):
        disclosure_date = self.get_disclosure_date()
        report_date = self.get_report_datetime()
        pdf_url = self.get_pdf_url()
        if models.PdfReportDownloadRecord.objects.filter(stk_cd_id=self.code, acc_per=report_date,
            disclosure_date = disclosure_date,pdf_url = pdf_url ):
            print('股票代码：{}期间{}报告已经存储'.format(self.code,report_date))
            return True
        else:
            return False

    def record_download_report(self):
        disclosure_date = self.get_disclosure_date()
        report_date = self.get_report_datetime()
        pdf_url = self.get_pdf_url()
        if models.PdfReportDownloadRecord.objects.filter(stk_cd_id=self.code, acc_per=report_date):
            obj = models.PdfReportDownloadRecord.objects.get(stk_cd_id=self.code, acc_per=report_date,)
            obj.disclosure_date = disclosure_date
            obj.pdf_url = pdf_url
            obj.save()
        else:
            models.PdfReportDownloadRecord.objects.create(
                stk_cd_id=self.code,
                acc_per=report_date,
                disclosure_date=disclosure_date,
                pdf_url=pdf_url,
            )


if __name__ == '__main__':
    pdf = GetPdfReport('600129','yjdbg','2017',path=r'e:\report')
    url = pdf.download_report()

