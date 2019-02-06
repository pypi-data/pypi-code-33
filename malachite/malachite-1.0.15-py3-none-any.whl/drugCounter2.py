from collections import Counter
import csv
import mechanize
from bs4 import BeautifulSoup as BS
import requests
import urllib

master = []
totalCanc = []
totalDrugs = []

def dcount2(path_in, numof, list_of_files, name, path_out, category, toppDict):
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

            array = []
            j=0
            while j<num_lines:
                b = symbolslist.split('\n')[j]
                array.append(b)
                j+=1



            tempDrugList = []
            for i in range(0, len(array)):
                if toppDict[cat] in array[i]:
                    # print("ARRAY[i]: "+array[i])
                    tempDrugList.append(array[i].split('\t')[2])

            # Remove duplicates in list of drugs
            tempDrugList = set(tempDrugList)
            tempDrugList = list(tempDrugList)
            # print("CHECK",len(tempDrugList))
            # print("CHECK",len(tempDrugList))
            tempDrugList1 = []
            # print("TEMPDRUGLIST:", tempDrugList)
            sep = ' ['
            sep2 = '; '
            for word in tempDrugList:
                # print("WORD:", word)
                if '[' in word:
                    # print("TRUE")
                    rest = word.split(sep,1)[0]
                    # print("Rest:", rest)
                    tempDrugList1.append(str(rest))
                elif ';' in word:
                    # print("TRUE")
                    rest = word.split(sep2,1)[0]
                    # print("Rest:", rest)
                    tempDrugList1.append(str(rest))
                else:
                    tempDrugList1.append(word)
            tempDrugList = tempDrugList1

            # print("TEMPDRUGLIST1:", tempDrugList1)
            # print("TEMPDRUGLIST:", tempDrugList)
            # number of drugs
            count = len(tempDrugList)
            # print(len(tempDrugList))
            # print("CHECK",len(tempDrugList))
            totalTemp.extend(tempDrugList)

            # print("CHECK",len(tempDrugList))
            # print("CHECK",len(totalTemp))

            totalTemp = [str(x).lower() for x in tempDrugList]

            # print("CHECK",len(tempDrugList))
            # print("CHECK",len(totalTemp))
            totalTemp = set(totalTemp)
            totalTemp = list(totalTemp)
            # print("CHECK",len(totalTemp))
            master.extend(totalTemp)
            # print("CHECK",len(master))

            # titleCount is a list of patient and corresponding number of drugs
            titleCount = []
            titleCount.append([title, count])

            # writes to csv as Patient, #number of drugs
            # fd = open('individidualcount.csv','a')
            # for row in titleCount:
            #     fd.write(str(row) + "\n")



            # Checks to see if cancer.gov request is working
            # r = requests.post("https://www.cancer.gov/about-cancer/treatment/drugs")
            # print(r.status_code, r.reason)
            # print(r.content)

            # print(master)
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
            # q = [e for e in masterNew if e in cancgovNew]
            q = list(set(q))
            # print(len(q))

            totalCanc.extend(q)
            # print(len(q))
            # print(len(totalCanc))
            # print(totalCanc)
            totalDrugs.extend(masterNew)
            # print(masterNew)

            # if "gemcitabine" in masterNew:
            #     print("TRUE")
            # else:
            #     print("FALSE")
            # if "gemcitabine hydrochloride" in cancgovNew:
            #     print("TRUE")
            # else:
            #     print("FALSE")
            # if "gemcitabine" in q:
            #     print("TRUE")
            # else:
            #     print("FALSE")
            # print(len(masterNew))
            # print(len(cancgovNew))
            # print(len(q))

            # z = z+1
            # file = open("/Users/Gershkowitz/Desktop/HowTo/Phase2/Results/LuadTotal"+str(z),"w")
            # file.write("Cancer Drugs:")
            # file.write("\n")
            # file.write("\n")
            # file.write(str(q))
            # file.write("\n")
            # file.write("\n")

            # file.write("All Drugs:")
            # file.write("\n")
            # file.write("\n")
            # file.write(str(masterNew))


        # Converts to tuple with drug/number of occurences
        canc1 = Counter(totalCanc)
        # Sorts into most common first
        canc2 = canc1.most_common()

        mast1 = Counter(totalDrugs)
        # Sorts into most common first
        mast2 = mast1.most_common()
        # print("Cancer Drugs:"+str(canc2))
        # print("Total Drugs:"+str(mast2))
        #
        # file = open(str(path_out) +str(cat)+ "--" +name +"Total.txt","w")
        # print(str(str(path_out) +str(cat)+ "--" +name +"Total.txt"))
        # file.write("Cancer Drugs:")
        # file.write("\n")
        # file.write("\n")
        # file.write(str(canc2))
        # file.write("\n")
        # file.write("\n")
        #
        # file.write("All Drugs:")
        # file.write("\n")
        # file.write("\n")
        # file.write(str(mast2))

        if cat == "Drug":
            file = open(str(path_out) +str(cat)+ "--" +name +"Total.txt","w")
            file.write("Cancer Drugs:")
            file.write("\n")
            file.write("\n")
            file.write(str(canc2))
            file.write("\n")
            file.write("\n")

            file.write("All Drugs:")
            file.write("\n")
            file.write("\n")
            file.write(str(mast2))
        else:
            file = open(str(path_out) +str(cat)+ "--" +name +"Total.txt","w")
            file.write(str(cat) +": ")
            file.write("\n")
            file.write("\n")
            file.write(str(mast2))
            file.write("\n")
            file.write("\n")

        # with open('drugslistpre.csv','wb') as out:
        #     csv_out=csv.writer(out)
        #     csv_out.writerow([master])
        #
        # with open('drugslistpost.csv','wb') as out:
        #     csv_out=csv.writer(out)
        #     csv_out.writerow([q])
