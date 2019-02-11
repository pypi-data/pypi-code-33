from collections import Counter
import csv
import mechanize
from bs4 import BeautifulSoup as BS
import requests
import urllib

master = []
totalCanc = []
totalDrugs = []

def dcount(path_in, numof, list_of_files, name, path_out, category, toppDict):
    # master = []
    # totalCanc = []
    # totalDrugs = []
    for cat in category:
        master = []
        totalCanc = []
        totalDrugs = []
        print("CURRENT CATEGORY: "+str(cat))
        z = 0
        for j in range(0, numof):
            master = []
            totalTemp = []
            title = str(path_in) + str(list_of_files[j])
            print(title)
            symbolfile = open(title)

            symbolslist = symbolfile.read()

            num_lines = sum(1 for line in open(title))
            print("NUMLINES: "+str(num_lines))

            array = []
            j=0
            while j<num_lines:
                b = symbolslist.split('\n')[j]
                array.append(b)
                j+=1
                if j%1000 == 0:
                    print("CurrentLine: "+str(j)+" out of "+str(num_lines))
            tempDrugList = []
            for i in range(0, len(array)):
                if toppDict[cat] in array[i]:
                    tempDrugList.append(array[i].split('\t')[2])
                    # print("ARRAY[i]: "+array[i].split('\t')[2])

            # Remove duplicates in list of drugs
            tempDrugList = set(tempDrugList)
            tempDrugList = list(tempDrugList)

            tempDrugList1 = []

            sep = ' ['
            sep2 = '; '
            for word in tempDrugList:
                if '[' in word:
                    rest = word.split(sep,1)[0]
                    tempDrugList1.append(str(rest))
                elif ';' in word:
                    rest = word.split(sep2,1)[0]
                    tempDrugList1.append(str(rest))
                else:
                    tempDrugList1.append(word)
            tempDrugList = tempDrugList1

            count = len(tempDrugList)

            totalTemp.extend(tempDrugList)

            totalTemp = [str(x).lower() for x in tempDrugList]

            totalTemp = set(totalTemp)
            totalTemp = list(totalTemp)
            master.extend(totalTemp)

            # titleCount is a list of patient and corresponding number of drugs
            titleCount = []
            titleCount.append([title, count])

            # Converts to tuple with drug/number of occurences
            c = Counter(master)
            # Sorts into most common first
            mc = c.most_common()
            # print mc

            cancgov = []
            html = requests.get('https://www.cancer.gov/about-cancer/treatment/drugs')
            soup = BS(html.text, "lxml")
            for d in soup.find_all("ul", {"class": "no-bullets no-description"}):
                for b in d.find_all('li'):
                    element = b.string
                    if ((element) != None):
                        cancgov.append(element.encode('utf-8').strip())
            cancgov = set(cancgov)
            cancgov = list(cancgov)

            cancgovNew = []
            cancgovNew = [str(item).lower() for item in cancgov]

            masterNew = []
            masterNew = [str(x).lower() for x in master]

            # q is list of drugs found in https://www.cancer.gov/about-cancer/treatment/drugs
            # checks to see if is substring of words in the list
            q = []
            for mas in masterNew:
                m = [s for s in cancgovNew if mas in s]
                if not m:
                    pass
                else:
                    q.append(mas)
                m = []

            q = list(set(q))

            totalCanc.extend(q)

            totalDrugs.extend(masterNew)

            z = z+1
            if cat == "Drug":
                file = open(str(path_out) +str(cat)+ "--" +name + str(z),"w")
                file.write("Cancer Drugs:")
                file.write("\n")
                file.write("\n")
                file.write(str(q))
                file.write("\n")
                file.write("\n")

                file.write("All Drugs:")
                file.write("\n")
                file.write("\n")
                file.write(str(masterNew))
            else:
                file = open(str(path_out) +str(cat)+ "--" +name + str(z),"w")
                file.write(str(cat) +": ")
                file.write("\n")
                file.write("\n")
                file.write(str(masterNew))
                file.write("\n")
                file.write("\n")


            # master = []
            # totalCanc = []
            # totalDrugs = []
