# _author : litufu
# date : 2018/5/16
import re
from utils.mytools import remove_per_from_df,remove_space_from_df

def recognize_instucti(indexno,indexcontent,indexnos):
    df = None
    instructi = []
    unit = '元'
    pattern0 = re.compile('^.*?单位：(.*?)$')
    if indexno in indexnos:
        for content in indexcontent:
            for classify, item in content.items():
                if classify == 'c' and len(item) > 0:
                    for tables in item:
                        for table in tables:
                            df = remove_per_from_df(remove_space_from_df(table))
                            instructi.append(df.to_string())
                elif classify == 't' and len(item) > 0:
                    if pattern0.match(item):
                        unit = pattern0.match(item).groups()[0]
                    else:
                        ret = re.sub('.*?.适用.不适用', '', item)
                        if ret != '':
                            instructi.append(ret)
                else:
                    pass
    else:
        pass

    return df, unit, ''.join(instructi)

def save_instructi(instructi,modelname,stk_cd_id,acc_per,filedname):
    if len(instructi) > 0:
        if modelname.objects.filter(stk_cd_id=stk_cd_id, acc_per=acc_per):
            obj = modelname.objects.get(stk_cd_id=stk_cd_id, acc_per=acc_per)
            setattr(obj,filedname,instructi)
            obj.save()
        else:
            obj = modelname.objects.create(
                stk_cd_id=stk_cd_id,
                acc_per=acc_per,
            )
            setattr(obj, filedname, instructi)
            obj.save()
    else:
        pass