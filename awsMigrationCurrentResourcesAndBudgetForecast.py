import pandas
#import git
import urllib.request
from pathlib import Path
import time
import numpy


def pullExcelFromGithub():
    url = ('https://raw.githubusercontent.com/JamesHamiltonDev/craftDemo/master/hardware.xlsx')
    pathToExcelFile = Path('ExcelTest.xlsx')
    fileNotFound = True
    while fileNotFound is True:
         print("Downloading file . . .")
         time.sleep(3)
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
    sanitizeDataframe = unsanitizedDataframe.apply(lambda x: x.astype(str).str.lower().str.strip())
#    .str.replace(' ', ''))
    sanitizeDataframe.columns = map(str.upper, sanitizeDataframe.columns)
#    sanitizeDataframe = sanitizeDataframe.where((numpy.nan(sanitizeDataframe)), None)
#    sanitizeDataframe = sanitizeDataframe.astype(str).replace('engineeringcanada', 'engineering canada')
    sanitizeDataframe = sanitizeDataframe.astype(object).replace('nan', 'None')
    sanitizeDataframe = sanitizeDataframe.loc[sanitizeDataframe['LOGICAL STATUS'] == "operational"]
    sanitizeDataframe['CPU CORES'] = sanitizeDataframe['CPU CORES'].astype(int)
    sanitizeDataframe['RAM (MB)'] = sanitizeDataframe['RAM (MB)'].astype(int)
    return sanitizeDataframe


def readExcelIntoDataframe():
    waitingForDownload = pullExcelFromGithub()
    if waitingForDownload is False:
        hardwareExcelToDataframe = pandas.read_excel(open('ExcelTest.xlsx', 'rb'))
        sanitizedData = sanitizeDataframe(hardwareExcelToDataframe)
#        listDepartmentsWithHardwareHosted(sanitizedData)
        resourcesByDepartment(sanitizedData)
        resourcesByApplication(sanitizedData)
        resourcesByDataCenter(sanitizedData)
    else:
        print('Download failed')


def listDepartmentsWithHardwareHosted(departmentsHH):
    pass
#    departmentHostingHardware = departmentsHH
#    departmentHostingHardware = departmentHostingHardware.GROUP.unique()
#    arrayDepartmentsToList = list(departmentHostingHardware)
#    print(arrayDepartmentsToList)


def resourcesByDepartment(departmentResources):
    resourcesBeingUsedByDepartment = departmentResources
#    resourcesBeingUsedByDepartment['CPU CORES'] = resourcesBeingUsedByDepartment['CPU CORES'].astype(int)
#    resourcesBeingUsedByDepartment['RAM (MB)'] = resourcesBeingUsedByDepartment['RAM (MB)'].astype(int)
#    resourcesBeingUsedByDepartment = resourcesBeingUsedByDepartment.loc[
#        resourcesBeingUsedByDepartment['LOGICAL STATUS'] == "operational"]
    sumDepartmentResources = resourcesBeingUsedByDepartment.groupby(['GROUP'])[["CPU CORES", "RAM (MB)"]].sum()
    print(sumDepartmentResources)


def resourcesByApplication(applicationResources):
    applicationsDepartment = applicationResources
    applicationsDepartment = applicationsDepartment.sort_values(['GROUP'])
    appsGroupedByDepartment = applicationsDepartment.groupby(['GROUP', 'APPLICATION'])[["CPU CORES", "RAM (MB)"]].sum()
    print(appsGroupedByDepartment)


def resourcesByDataCenter(dataCenterResources):
    resourcesDatacenter = dataCenterResources
    resourcesDatacenterSorted = resourcesDatacenter.sort_values(['SITE'])
    groupedResourcesBySite = resourcesDatacenterSorted.groupby(['SITE'])[["CPU CORES", "RAM (MB)"]].sum()
    print(groupedResourcesBySite)





if __name__ == '__main__':
    readExcelIntoDataframe()
