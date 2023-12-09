import os, time

print(os.getcwd())
print(os.path.abspath("../../.."))

date_year = f'{time.strftime("%Y", time.localtime())}'
date_month = f'{time.strftime("%m-%Y", time.localtime())}'
date_pdf = f'{time.strftime("%Y-%m-%d", time.localtime())}'
name_pdf = f'{date_pdf} Строевая записка отдела ТПСЭД ЦАиТП.pdf'

# link = rf'\\zh-srv-store-1.guin.gov\OTPIS\_!Отчеты\Кто в отпуске для строевки ОТПИС (lapina.g.d@fsin.uis)\{date_year}\{date_month}\{name_pdf}'
link = os.path.abspath(os.path.join("../../../stroevaya_zapiska/", date_year, date_month, name_pdf))
link_dirs = os.path.abspath(os.path.join("../../../stroevaya_zapiska/", date_year, date_month))

print(link)
print(link_dirs)