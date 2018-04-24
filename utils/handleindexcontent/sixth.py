# _author : litufu
# date : 2018/4/24

from utils.handleIndex import HtmlFile,HtmlPage

filepath = r'H:\data_extract\report\shenzhen\sz_000701_20171231.html'
file = HtmlFile(filepath)
page = HtmlPage(file,30)
print(page.get_page_content())