# _author : litufu
# date : 2018/4/8

import tabula
from PyPDF2 import PdfFileReader, PdfFileWriter
readFile = 'read.pdf'
writeFile = 'write.pdf'
# 获取一个 PdfFileReader 对象

# 获取 PDF 的页数

filepath = r'C:\Users\28521\Desktop\2016.pdf'
pdfReader = PdfFileReader(open(filepath, 'rb'))
pageCount = pdfReader.getNumPages()
for page in range(1,pageCount+1):
    print(page)
    df = tabula.read_pdf(filepath,encoding='gbk',multiple_tables=True,pages=page)
    print(df)
    is_go_on = input('是否继续')
    if is_go_on == 'y':
        continue
    else:
        break
