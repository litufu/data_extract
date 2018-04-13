# _author : litufu
# date : 2018/4/12
from nose.tools import *
from utils.parsehtml_new import *
from bs4.element import Tag
import pandas as pd
from sqlalchemy import create_engine
engine = create_engine('sqlite:///tempParseHtml.db')
#
def test_file_to_database():
    filepath = r'H:\data_extract\report\shenzhen\1204618902.html'
    file = HtmlFile(filepath)
    file.to_database()
#
# def test_parse_dir_structure():
#     filepath = r'H:\data_extract\report\shenzhen\1204618902.html'
#     file = HtmlFile(filepath)
#     file.parse_dir_structure()