"""
Craft Demo for Intuit

Author
    James Hamilton

Github repo
    https://github.com/JamesHamiltonDev/craftDemo


Program to calculate current hardware utilization by departments and applications
in preparation for a migration to AWS cloud.  This program also includes a financial forecast
for the next 3 years.

"""

import pandas
#import git
import urllib.request
from pathlib import Path
import time
import numpy

## Function to pull an Excel file from the master branch of GitHub repository.
## A continues while loop was created to verify file download before moving to the next function.
## Sleep method added to not bombard Github with requests.
##
def pullExcelFromGithub():
    url = ('https://raw.githubusercontent.com/JamesHamiltonDev/craftDemo/master/hardware.xlsx')
    pathToExcelFile = Path('hardware.xlsx')
    fileNotFound = True
    while fileNotFound is True:
         print("Downloading file . . .")
         time.sleep(2)
         try:
             if pathToExcelFile.is_file():
                 fileNotFound = False
                 print('File downloaded')
                 return fileNotFound
             else:
                 urllib.request.urlretrieve(url, filename='hardware.xlsx')
         except:
             pass


def sanitizeDataframe(hardwareData):
    unsanitized = hardwareData
    sanitize = unsanitized.apply(lambda x: x.astype(str).str.lower().str.strip())
    sanitize.columns = map(str.upper, sanitize.columns)
    sanitize = sanitize.astype(object).replace('nan', 'None')
    sanitize = sanitize.loc[sanitize['LOGICAL STATUS'] == "operational"]
    sanitize['CPU CORES'] = sanitize['CPU CORES'].astype(int)
    sanitize['RAM (MB)'] = sanitize['RAM (MB)'].astype(int)
    return sanitize


def readExcelIntoDataframe():
    waitingForDownload = pullExcelFromGithub()
    if waitingForDownload is False:
        hardwareExcelToDataframe = pandas.read_excel(open('hardware.xlsx', 'rb'))
        sanitizedData = sanitizeDataframe(hardwareExcelToDataframe)
        resourcesByDepartment(sanitizedData)
        resourcesByApplication(sanitizedData)
        resourcesByDataCenter(sanitizedData)
        mergeAWSonHardwareDF(sanitizedData)
    else:
        print('Download failed')


def resourcesByDepartment(departmentResources):
    resourcesBeingUsedByDepartment = departmentResources
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


def readAWScsv():
    awsCSV = pandas.read_csv('amazonEC2prices.csv')
    return awsCSV


def sliceSplitSanitizeCSV():
    awsCSVdataframe = readAWScsv()
    awsCSVdataframe = awsCSVdataframe.apply(lambda x: x.astype(str).str.lower().str.strip())
    awsCSVdataframe['RAM (GiB)'] = awsCSVdataframe['RAM (GiB)'].str.replace(' gib', '')
    awsCSVdataframe[["cpu", "RAM (GiB)"]] = awsCSVdataframe[["cpu", "RAM (GiB)"]].astype(int)
    awsCSVdataframe["RAM (MB)"] = awsCSVdataframe["RAM (GiB)"].apply(lambda x: (x * 8589934592) / 8000000).astype(int)
    awsCSVdataframe["hourly cost"] = awsCSVdataframe["hourly cost"].str.replace('$', '').str.split(' ').str.get(0).astype(float)
    awsCSVdataframe["gregorian year cost"] = awsCSVdataframe["hourly cost"].apply(lambda x: x * 8760).astype(float)
    awsCSVdataframe["leap year cost"] = awsCSVdataframe["hourly cost"].apply(lambda x: x * 8784).astype(float)
    awsCSVdataframe.columns = map(str.upper, awsCSVdataframe.columns)
    return awsCSVdataframe


def mergeAWSonHardwareDF(hardwareDF):
    saniHardwareDF = pandas.DataFrame(hardwareDF)
    print(saniHardwareDF)

if __name__ == '__main__':
    readExcelIntoDataframe()
