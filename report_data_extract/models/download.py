# _author : litufu
# date : 2018/5/20

from django.db import models
from .standard import CommonInfo

class PdfReportDownloadRecord(CommonInfo):
    disclosure_date = models.CharField(verbose_name='披露日期', default='', max_length=150)
    pdf_url = models.CharField(verbose_name='pdf下载地址', default='', max_length=300)

    class Meta:
        unique_together = ('stk_cd', 'acc_per')