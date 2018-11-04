"""
Craft Demo for Intuit
    AWS Migration
        hardware and financial assessment

Author
    James Hamilton

Github repo
    https://github.com/JamesHamiltonDev/craftDemo


Program to calculate current hardware utilization by departments and applications
in preparation for a migration to AWS cloud.  This program also includes a financial forecast
for the next 3 years.

"""

import pandas
pandas.set_option('display.width', 300)
#import git
import urllib.request
from pathlib import Path
import time
import numpy


#


def pullExcelFromGithub():
    """Function to pull an Excel file from the master branch of GitHub repository
    A continues while loop was created to verify file download before moving to the next function
    """
    url = ('https://raw.githubusercontent.com/JamesHamiltonDev/craftDemo/master/hardware.xlsx')
    pathToExcelFile = Path('hardware.xlsx')
    fileNotFound = True
    while fileNotFound is True:
         print("Downloading file . . .")
#
## URL requests to third party site intentionally delayed.  Third party providers have a habit of
## blocking IPs that bombard their servers with requests.
#
         time.sleep(3)
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
    """ Function receives param from readExcelIntoDataFrame.
     This function sanitizes the data and removes any hardware without
     the logical status of operational.  All NaN or nan entries changed to the
     string None.  Group and Site header changed to Department and Data Center
     for parity with instructions.  Added a UID column.
     """
    unsanitized = hardwareData
    unsanitized['UID'] = range(10000, 10000 + len(unsanitized))
    unsanitized[["Department", "Data Center"]] = unsanitized[["Group", "Site"]]
    unsanitized = unsanitized.drop(["Group", "Site"], 1)
    sanitize = unsanitized.apply(lambda x: x.astype(str).str.lower().str.strip())
    sanitize.columns = map(str.upper, sanitize.columns)
    sanitize = sanitize.astype(object).replace('nan', 'None')
    sanitize = sanitize.loc[sanitize['LOGICAL STATUS'] == "operational"]
    sanitize['CPU CORES'] = sanitize['CPU CORES'].astype(int)
    sanitize['RAM (MB)'] = sanitize['RAM (MB)'].astype(int)
    sanitize = sanitize.reset_index(drop=True)

    return sanitize


def readExcelIntoDataframe():
    """ Function calls pullExcelFromGithub function.  Excel is not returned but verification
    of file existence.  SciPY module pandas reads Excel and sends it to sanitzeDataFrame function.
    Returned sanitized dataframe is passed to the functions below to generate the requested output.
     """
    waitingForDownload = pullExcelFromGithub()
    if waitingForDownload is False:
        hardwareExcelToDataframe = pandas.read_excel(open('hardware.xlsx', 'rb'))
        sanitizedData = sanitizeDataframe(hardwareExcelToDataframe)
        resourcesByDepartment(sanitizedData)
        resourcesByApplication(sanitizedData)
        resourcesByDataCenter(sanitizedData)
        mergeAWSonHardware(sanitizedData)
    else:
        print('Download failed')


def resourcesByDepartment(departmentResources):
    """ Function receives param from sanitizeDataframe function.  Data is grouped by DEPARTMENT
    while CPU and RAM are summed for each department.
    """
    resourcesBeingUsedByDepartment = departmentResources
    sumDepartmentResources = resourcesBeingUsedByDepartment.groupby(['DEPARTMENT'])[["CPU CORES", "RAM (MB)"]].sum()
    print(sumDepartmentResources)


def resourcesByApplication(applicationResources):
    """ Function receives param from sanitizeDataframe function.  Department rows are sorted.
    Dataframe is then grouped by Department and Application while CPU and Ram are summed for each application
    being used by the department.
    """
    applicationsDepartment = applicationResources
    applicationsDepartment = applicationsDepartment.sort_values(['DEPARTMENT'])
    appsGroupedByDepartment = applicationsDepartment.groupby(['DEPARTMENT', 'APPLICATION'])[["CPU CORES", "RAM (MB)"]].sum()
    print(appsGroupedByDepartment)


def resourcesByDataCenter(dataCenterResources):
    """ Function receives param from sanitizeDataframe function.  Data Center rows are sorted.
    Dataframe is grouped by Data Center while CPU and RAM are summed for each Data Center.
    """
    resourcesDatacenter = dataCenterResources
    resourcesDatacenterSorted = resourcesDatacenter.sort_values(['DATA CENTER'])
    groupedResourcesBySite = resourcesDatacenterSorted.groupby(['DATA CENTER'])[["CPU CORES", "RAM (MB)"]].sum()
    print(groupedResourcesBySite)


def readAWScsv():
    """ AWS csv read into pandas data frame and returned.
    """
    awsCSV = pandas.read_csv('amazonEC2prices.csv')
    return awsCSV


def sliceSplitSanitizeCSV():
    """ Function calls readAWScsv.  All rows in data frame are turned into strings, lowered, and stripped
    of white space.  The RAM gebibyte notations in the RAM (GiB) rows are removed.  RAM and cpu rows are
    changed to integer datatypes for calculations.  RAM (MB) column is created by converting GiB to MB from
    the RAM (GiB) column.  Removed $ sign and other notations from hourly cost column.  Hourly cost column
    converted to float type.  Gregorian year cost and Leap year cost columns created by calculating number
    of hours a year.
    """
    awsCSVdataframe = readAWScsv()
    awsCSVdataframe = awsCSVdataframe.apply(lambda x: x.astype(str).str.lower().str.strip())
    awsCSVdataframe['RAM (GiB)'] = awsCSVdataframe['RAM (GiB)'].str.replace(' gib', '')
    awsCSVdataframe[["cpu", "RAM (GiB)"]] = awsCSVdataframe[["cpu", "RAM (GiB)"]].astype(int)
    awsCSVdataframe["RAM (MB)"] = awsCSVdataframe["RAM (GiB)"].apply(lambda x: (x * 8589934592) / 8000000).astype(int)
    awsCSVdataframe["hourly cost"] = awsCSVdataframe["hourly cost"].str.replace('$', '').str.split(' ').str.get(0).astype(float)
    awsCSVdataframe["gregorian year cost"] = awsCSVdataframe["hourly cost"].apply(lambda x: x * 8760).astype(float)
    awsCSVdataframe["leap year cost"] = awsCSVdataframe["hourly cost"].apply(lambda x: x * 8784).astype(float)
    awsCSVdataframe['cpu cores'] = awsCSVdataframe['cpu']
    awsCSVdataframe = awsCSVdataframe.drop('cpu', 1)
    awsCSVdataframe.columns = map(str.upper, awsCSVdataframe.columns)
    return awsCSVdataframe


def mergeAWSonHardware(hardwareDF):
    """ Function receives param from sanitizeDataframe. Drop Windows systems from list since all new systems
    will be RHEL based.  """
    saniHardwareDF = pandas.DataFrame(hardwareDF)
    awsPriceDF = sliceSplitSanitizeCSV()
##  create column in aws for container size to match sani
    saniHardwareDF = saniHardwareDF.loc[saniHardwareDF['OPERATING SYSTEM'] != "windows"]

    awsPriceDF["CONTAINER SIZE"] = awsPriceDF["AWS CONTAINER"].str.split('.').str.get(1)
    awsPriceDF = awsPriceDF.replace({'CONTAINER SIZE' : {'micro': 'm', 'small': 's', 'medium': 'm',
                                                            'large': 'l', 'xlarge': 'xl', '2xlarge': '2xl',
                                                            '4xlarge': '4xl', '10xlarge': '10xl',
                                                            '12xlarge': '12xl', '16xlarge': '16xl',
                                                            '24xlarge': '24xl'}})
    saniHardwareDF = saniHardwareDF.sort_values(['RAM (MB)'])
#
#    create unique ID for sani after filter and merge
    mergedf = pandas.merge(saniHardwareDF, awsPriceDF, on=['CONTAINER SIZE', 'CPU CORES'], how='left', suffixes=['_DC', '_AWS'])
    print(saniHardwareDF)
#    print(mergedf)
#    filenameDF = ('testFile.csv')
#    mergedf.to_csv(filenameDF)
#


if __name__ == '__main__':
    readExcelIntoDataframe()
