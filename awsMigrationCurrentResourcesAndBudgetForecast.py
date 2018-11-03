import pandas
#import git
import urllib.request
from pathlib import Path
import time

def pullExcelFromGithub():
    url = ('https://raw.githubusercontent.com/JamesHamiltonDev/craftDemo/master/hardware.xlsx')
    pathToExcelFile = Path('ExcelTest.xlsx')
    fileNotFound = True
    while fileNotFound is True:
         print("Downloading file . . .")
         time.sleep(5)
         try:
             if pathToExcelFile.is_file():
                 fileNotFound = False
                 print('File downloaded')
                 return fileNotFound
             else:
                 excelFileFromGithub = urllib.request.urlretrieve(url, filename='ExcelTest.xlsx')
         except:
             pass

def sanitizeDataframe(hardwareDataframe):
    unsanitizedDataframe = hardwareDataframe
#    print(unsanitizedDataframe)
    sanitizeDataframe = unsanitizedDataframe.where((pandas.notnull(unsanitizedDataframe)), None)
    sanitizeDataframe.columns = map(str.upper, sanitizeDataframe.columns)
#    sanitizeDataframe = sanitizeDataframe
#    sanitizeDataframe = unsanitizedDataframe.apply(lambda x: x.astype(str).str.lower().str.strip().str.replace(' ', ''))

#    sanitizeDataframe.columns = map(str.upper, sanitizeDataframe.columns)
#    upperHeaders = lowercaseDataframe.
    print(sanitizeDataframe)



def readExcelIntoDataframe():
    waitingForDownload = pullExcelFromGithub()
    hardwareExcelToDataframe = pandas.read_excel(open('ExcelTest.xlsx', 'rb'))
#    print(hardwareExcelToDataframe)
    sanitizedData = sanitizeDataframe(hardwareExcelToDataframe)


#    successfullDownload = Path('ExcelTest.xlsx')
#    if waitingForDownload is False:
#        print('Parsing excel into dataframe')
#        hardwareExcel = pandas.read_excel('ExcelTest.xlsx')
#        print(hardwareExcel)
#    else:
#        while waitingForDownload is not False:
#            print("waiting . . .")
#            try:
#                if successfullDownload.is_file():
#                    print('Parsing excel into dataframe')
#                    hardwareExcel = pandas.read_excel('ExcelTest.xlsx')
#                    print(hardwareExcel)
#            except:
#                pass


if __name__ == '__main__':
    readExcelIntoDataframe()
