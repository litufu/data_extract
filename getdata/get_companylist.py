# _author : litufu
# date : 2018/4/19
import pandas as pd
import tushare as ts
from sqlalchemy import create_engine
engine = create_engine(r'sqlite:///H:\data_extract\db.sqlite3')

# engine = create_engine('postgresql://postgres:123456abc@localhost:5432/companyvalue')
#create_engine说明：dialect[+driver]://user:password@host/dbname[?key=value..]


def getCompanyList():
    '''
    通过tushare获取上市公司列表，并与数据库中存储的上市公司列表进行比较，如果存在差异，则将未存储的数据存入
    :return:
    '''

    #获取最新的公司列表数据
    df = ts.get_stock_basics()
    df = df.reset_index()  #将index变为columns
    df = df[['code','name','area','industry','timeToMarket']]   #选取和数据库表相同的字段
    df = df[df.timeToMarket!=0]
    df.timeToMarket = pd.to_datetime(df.timeToMarket,format='%Y%m%d',errors='ignore')  #将timeToMarket列变为datetime类型
    #获取已经存储的公司列表数据
    df1 = pd.read_sql('report_data_extract_companylist',engine)  #从数据库中读取列表
    is_saved = df1.code.values      #获取已存储的公司代码列表
    #将未存储的数据存入数据库
    df = df[~df.code.isin(is_saved)]
    if len(df) == 0:
        pass
    else:
        try:
            df.to_sql('report_data_extract_companylist', engine, index=False, if_exists='append')
        except Exception as e:
            print(e)

if __name__ == '__main__':
    getCompanyList()
