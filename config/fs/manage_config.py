# _author : litufu
# date : 2018/5/2
import pandas as pd
import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def config_to_json(sheetname,configname):
    '''将excel中的数据转换为json 数据'''
    file = r'H:\data_extract\config\fs\new_data_base_table.xlsx'
    df = pd.read_excel(file, sheetname=sheetname)
    df.to_json(configname,orient='split')


def add_pp_config(item,field,pp_filename):
    '''增加匹配索引'''
    if type(item) is not list:
        item = [item]
    if type(field) is not list:
        field = [field]
    data = {'item':item,'field':field}
    new_df = pd.DataFrame(data)
    df = pd.read_json(pp_filename,orient='split')
    combin_df = pd.concat([df,new_df],join='outer',ignore_index=True)
    combin_df.drop_duplicates(keep='first', inplace=True)
    combin_df.to_json(pp_filename, orient='split')

def del_pp_config(item,pp_filename):
    df = pd.read_json(pp_filename, orient='split')
    df = df[df.item!=item]
    df.to_json(pp_filename, orient='split')

def add_std_config(item,field,cf_filename):
    '''增加标准索引'''
    if type(item) is not list:
        item = [item]
    if type(field) is not list:
        field = [field]
    data = {'item_std':item,'field_std':field}
    new_df = pd.DataFrame(data)
    df = pd.read_json(cf_filename,orient='split')
    combin_df = pd.concat([df,new_df],join='outer',ignore_index=True)
    combin_df.drop_duplicates(keep='first', inplace=True)
    combin_df.to_json(cf_filename, orient='split')

def read_config(filename):
    filepath = os.path.join(BASE_DIR,filename)
    df = pd.read_json(filepath, orient='split')
    return df


# if __name__ == '__main__':
#     # add_pp_config('汇兑收益（损失以“-”号填列）','exchng_gns','lrbpp.json')
#     # add_pp_config('资产处置收益（损失以“-”号填列）','dspsl_of_asts','lrbpp.json')
#
#     del_pp_config('汇兑收益（损失以“－”号填列）','lrbpp.json')
#     del_pp_config('资产处置收益（损失以“-”号填列）','lrbpp.json')
#     df = pd.read_json('lrbpp.json', orient='split')
#     print(df)