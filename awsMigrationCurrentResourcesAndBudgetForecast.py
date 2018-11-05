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
pandas.set_option('display.max_rows', 2000)
import urllib.request
from pathlib import Path
import time
import os
import git
import calendar



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
    awsCSVdataframe[["cpu"]] = awsCSVdataframe[["cpu"]].apply(lambda x: x.astype(int))
    awsCSVdataframe[["RAM (GiB)"]] = awsCSVdataframe[["RAM (GiB)"]].apply(lambda x: x.astype(str).str.replace(',', ''))
    awsCSVdataframe[["RAM (GiB)"]] = awsCSVdataframe[["RAM (GiB)"]].apply(lambda x: x.astype(float))
    awsCSVdataframe["RAM (MB)"] = awsCSVdataframe["RAM (GiB)"].apply(lambda x: (x * 8589934592) / 8000000).astype(int)
    awsCSVdataframe["hourly cost"] = awsCSVdataframe["hourly cost"].str.replace('$', '').str.split(' ').str.get(0).astype(float)
    awsCSVdataframe["gregorian year cost"] = awsCSVdataframe["hourly cost"].apply(lambda x: x * 8760).astype(float)
    awsCSVdataframe["leap year cost"] = awsCSVdataframe["hourly cost"].apply(lambda x: x * 8784).astype(float)
    awsCSVdataframe['cpu cores'] = awsCSVdataframe['cpu']
    awsCSVdataframe = awsCSVdataframe.drop('cpu', 1)
    awsCSVdataframe.columns = map(str.upper, awsCSVdataframe.columns)
    return awsCSVdataframe


def matchRemaining(remainDC, awsC):
    remainDF = pandas.DataFrame(remainDC)
    remainDF = remainDF.sort_values(['RAM (MB)'])
    remainDF[["CPU CORES"]] = remainDF[["CPU CORES"]].apply(lambda x: x.astype(str).str.replace('1', '2'))
    remainDF[["CPU CORES"]] = remainDF[["CPU CORES"]].apply(lambda x: x.astype(int))
    remainDFtuple = tuple(list(remainDF['RAM (MB)'].drop_duplicates()))
    remainDF = remainDF.sort_values(['RAM (MB)'])
    awsDF = pandas.DataFrame(awsC)
    awsDF = awsDF.sort_values(['RAM (MB)'])
    awsDFtuple = tuple(list(awsDF['RAM (MB)'].drop_duplicates()))
    listRemain = []
    for ramDC in remainDFtuple:
        remainRAM = remainDF.loc[remainDF['RAM (MB)'] == ramDC]
        for ramAWS in awsDFtuple:
            if ramAWS > ramDC:
                awsRam = awsDF.loc[awsDF['RAM (MB)'] == ramAWS]
                mergeRam = pandas.merge(remainRAM, awsRam, on=['CPU CORES'], how='inner',
                                        suffixes=['_DC', '_AWS'])
                listRemain.append(mergeRam)
            else:
                pass
    listRemain = pandas.concat(listRemain, axis=0, ignore_index=True)
    listRemain = listRemain.drop_duplicates(subset=['UID'], keep='first')
    listRemain = listRemain.reset_index(drop=True)
    return(listRemain)


def ramCheckAndMerge(dc, aws):
    ramDCframe = pandas.DataFrame(dc)
    ramAWSframe = pandas.DataFrame(aws)
    saniHardwareUniqueRam = tuple(list(ramDCframe['RAM (MB)'].drop_duplicates()))
    ramAWSframe = ramAWSframe.sort_values(['RAM (MB)'])
    ramDCframe = ramDCframe.sort_values(['RAM (MB)'])
    awsUniqueRam = tuple(list(ramAWSframe['RAM (MB)'].drop_duplicates()))
    listDF = []
    for ramDC in saniHardwareUniqueRam:
        saniRam = ramDCframe.loc[ramDCframe['RAM (MB)'] == ramDC]
        for ramAWS in awsUniqueRam:
            if ramAWS > ramDC:
                awsRam = ramAWSframe.loc[ramAWSframe['RAM (MB)'] == ramAWS]
                mergeRam = pandas.merge(saniRam, awsRam, on=['CPU CORES'], how='inner',
                                           suffixes=['_DC', '_AWS'])
                listDF.append(mergeRam)
            else:
                pass

    listDF = pandas.concat(listDF, axis=0, ignore_index=True)
    listDF = listDF.drop_duplicates(subset=['UID'], keep='first')
    listDF = listDF.reset_index(drop=True)
    remaining = pandas.DataFrame()
    remaining = ramDCframe[(~ramDCframe.UID.isin(listDF.UID))]
    remainDF = matchRemaining(remaining, ramAWSframe)
    frames = [listDF, remainDF]
    concatDF = pandas.concat(frames, axis=0, ignore_index=True)
    concatDF = concatDF.sort_values(['UID'])
    concatDF = concatDF.reset_index(drop=True)
    return concatDF


def mergeAWSonHardware(hardwareDF):
    """ Function receives param from sanitizeDataframe. Drop Windows systems from list since all new systems
    will be RHEL based.
    """
    saniHardwareDF = pandas.DataFrame(hardwareDF)
    awsPriceDF = sliceSplitSanitizeCSV()
    saniHardwareDF = saniHardwareDF.loc[saniHardwareDF['OPERATING SYSTEM'] != "windows"]
    allMatches = ramCheckAndMerge(saniHardwareDF, awsPriceDF)
    getHostingCost(allMatches)


def gYearEngineerTeam(financial, perc, col):
    finDF = pandas.DataFrame(financial)
    colLength = len(finDF.columns)
    if colLength < 22:
        finDF[col] = finDF['GREGORIAN YEAR COST'].apply(lambda x: (x * perc))
        engineerTeams = ['engineering', 'engineering canada']
        engineering = finDF[finDF.DEPARTMENT.isin(engineerTeams)]
        return engineering
    else:
        splitCol = int(col.split(" ", 1)[0])
        splitCol = str(splitCol - 1)
        newCol = (splitCol + " COST")
        finDF[col] = finDF[newCol].apply(lambda x: (x * perc))
        engineerTeams = ['engineering', 'engineering canada']
        engineering = finDF[finDF.DEPARTMENT.isin(engineerTeams)]
        return engineering


def lYearEngineerTeam(fin, p, c):
    splitCol = int(c.split(" ", 1)[0])
    splitCol = str(splitCol - 1)
    newCol = (splitCol + " COST")
    leapPercInc = p + 0.0027
    fin[c] = fin[newCol].apply(lambda x: (x * leapPercInc))
    engineerTeams = ['engineering', 'engineering canada']
    engineering = fin[fin.DEPARTMENT.isin(engineerTeams)]
    return engineering


def salesTeam(sfin, scol):
    sfinDF = pandas.DataFrame(sfin)
    sfinDF = sfinDF.loc[sfinDF['DEPARTMENT'] == "sales"]
    sfinDF["DISCOUNT"] = sfin['GREGORIAN YEAR COST'].apply(lambda x: (x * .80))
    sfinDF[scol] = sfin['GREGORIAN YEAR COST'].apply(lambda x: (x - sfinDF['DISCOUNT']))
    sfinDF = sfinDF.drop(['DISCOUNT'], 1)
    sfinDF['2020 COST'] = 0
    sfinDF['2021 COST'] = 0
    return sfinDF


def remainingTeams(rfin):
    rfinDF = pandas.DataFrame(rfin)
    rTeams = ['engineering', 'engineering canada', 'sales']
    rfinDF = rfinDF[~rfinDF.DEPARTMENT.isin(rTeams)]
    rfinDF['2019 COST'] = rfinDF['GREGORIAN YEAR COST']
    rfinDF['2020 COST'] = rfinDF['LEAP YEAR COST']
    rfinDF['2021 COST'] = rfinDF['GREGORIAN YEAR COST']
    return rfinDF


def getHostingCost(matchesDF):
    hostingDF = pandas.DataFrame(matchesDF)
    year2019 = (calendar.isleap(2019))
    year2020 = (calendar.isleap(2020))
    year2021 = (calendar.isleap(2021))

    efinReport = pandas.DataFrame(hostingDF)
    sfinReport = pandas.DataFrame(hostingDF)
    rfinReport = pandas.DataFrame(hostingDF)
    f2019col = ("2019 COST")
    f2020col = ("2020 COST")
    f2021col = ("2021 COST")
    if year2019 == False:
        engineer2019 = gYearEngineerTeam(efinReport, 1.10, f2019col)
    else:
        engineer2019 = lYearEngineerTeam(efinReport, 1.10, f2019col)
    if year2020 == False:
        engineer2020 = gYearEngineerTeam(efinReport, 1.25, f2020col)
    else:
        engineer2020 = lYearEngineerTeam(efinReport, 1.25, f2020col)
    if year2021 == False:
        engineer2021 = gYearEngineerTeam(efinReport, 1.40, f2021col)
    else:
        engineer2021 = lYearEngineerTeam(efinReport, 1.40, f2021col)
    salesF = salesTeam(sfinReport, f2019col)
    rfinancial = remainingTeams(rfinReport)
    fframes = [engineer2021, salesF, rfinancial]
    concatFinacialReport =pandas.concat(fframes, axis=0, ignore_index=True)
    concatFinacialReport = concatFinacialReport.sort_values(['DEPARTMENT'])
    groupedFinacialReport = concatFinacialReport.groupby(['DEPARTMENT'])[["2019 COST", "2020 COST", "2021 COST"]].sum()
    print(groupedFinacialReport)
    toGitHub()


def toGitHub():
    os.system("git commit")
    #os.system("git request-pull origin/master origindevelopment")



if __name__ == '__main__':

    readExcelIntoDataframe()
