import pandas as pd
import numpy as np
import matplotlib.pylab as plt

printflag = False

#coursesDF = pd.read_csv('courses_new.csv')
#studentsDF = pd.read_csv('studentsWithCpi.csv')

coursesDF = pd.read_csv('courses.csv')
studentsDF = pd.read_csv('students.csv')

courseCount = len(coursesDF.index)
studentCount = len(studentsDF.index)

def makeArray(studentCount, studentDF, courseCount, courseDF, bias, w1, w2, w3):#, w4, w5):
    Array = np.zeros((studentCount, courseCount), dtype=np.int64) + bias
    for i in np.arange(0,courseCount):
        for j in np.arange(0,studentCount):
            if coursesDF['CourseCode'][i] == studentsDF['Choice1'][j]:
                Array[j][i] = w1
            elif coursesDF['CourseCode'][i] == studentsDF['Choice2'][j]:
                Array[j][i] = w2
            elif coursesDF['CourseCode'][i] == studentsDF['Choice3'][j]:
                Array[j][i] = w3
            #elif coursesDF['CourseCode'][i] == studentsDF['Choice4'][j]:
                #Array[j][i] = w4
            #elif coursesDF['CourseCode'][i] == studentsDF['Choice5'][j]:
                #Array[j][i] = w5
    return Array

SvCArray = makeArray(studentCount, studentsDF, courseCount, coursesDF, 10, 1, 2, 3)#, 4, 5)
SvCMatrix = np.mat(SvCArray)

cpiArray = studentsDF['CPI']

times = np.array(coursesDF['CourseNeeds'])

def calcChoiceCost(anAllotment, SvC_array):
    cost1 = (np.sum(anAllotment*SvCarray3))
    return cost1

def squeezeAllotment(anAllotment, times, studentCount, courseCount):
    allotment = np.zeros((studentCount, courseCount))
    start = 0
    for i in range(courseCount):
        stop = start + times[i]
        allotment[:,i] = (np.sum(anAllotment[:,start:stop], 1)).ravel()
        start = stop
    allotment = np.array(allotment, dtype=np.int64)
    return allotment

SvCarray2 = makeArray(studentCount, studentsDF, courseCount, coursesDF, 0, 1, 2, 3)#, 4, 5)

def calculateVariance(cpiArray, allotment, courseCount):
    cpiRepeated = (np.array([cpiArray, ]*courseCount)).transpose()
    SvC_cpi = allotment * cpiRepeated
    b = np.ma.masked_where(SvC_cpi == 0, SvC_cpi)
    #a = np.array(np.ma.mean(b, 0), dtype=np.float)
    a = np.array(np.nanmean(b, 0), dtype=np.float)
    #print b
    variance = np.var(a)
    return variance

x_0 = squeezeAllotment(np.eye(studentCount), times, studentCount, courseCount)

SvCarray3 = makeArray(studentCount, studentsDF, courseCount, coursesDF, 10, 1, 2, 3)#, 4, 5)

def allottedCourseGrade(studentCount, courseCount, studentsDF, anAllotment, SvCarray3):
    allotmentMatrix = anAllotment * SvCarray3
    temp = np.zeros((studentCount, 1))
    for i in range(studentCount):
        for j in range(courseCount):
            if(allotmentMatrix[i,j] != 0):
                if(allotmentMatrix[i,j] == 10):
                    temp[i] = 0;
                    break
                else:
                    temp[i] = studentsDF.loc[i][str("Grade"+str(allotmentMatrix[i,j]))]
                    break

    return sum(temp)

def calculateUtilityFunction(anAllotment, C1, C2, C3, SvCarray2, SvCarray3, courseCount):
    choiceSum = calcChoiceCost(anAllotment, SvCarray2)
    cost1 = C1*choiceSum
    cost2 = C2*allottedCourseGrade(studentCount, courseCount, studentsDF, anAllotment, SvCarray3)
    var = calculateVariance(cpiArray, anAllotment, courseCount)
    cost3 = C3/var
    totalUtility = cost1 + cost2 + cost3
    return totalUtility

beta = 10*np.log10(1+studentCount)
C1 = -1.0
C2 = 1
C3 = 1

#print calculateUtilityFunction(x_0, C1, C2, C3, SvCarray2, SvCarray3, courseCount)

np.random.seed(2**13 - 1)

nIters = 100

utility = np.zeros((nIters,1))

for i in range(nIters):
	print i
	def swapRows(anAllotment):
	    swapId1 = np.random.randint(0,studentCount-1)
	    #print swapId1
	    swapId2 = np.random.randint(0,studentCount-1)
	    #print swapId2
	    if printflag:
			print swapId1
			print swapId2
			print x_0[swapId1,:]
			print x_0[swapId2,:]
	    temp2 = anAllotment.copy()
	    tempVar = temp2[swapId1,:].copy()
	    temp2[swapId1,:] = temp2[swapId2,:]
	    temp2[swapId2,:] = tempVar
	    return temp2
	
	newAllotment = swapRows(x_0)
	
	u1 = calculateUtilityFunction(newAllotment, C1, C2, C3, SvCarray2, SvCarray3, courseCount)
	u2 = calculateUtilityFunction(x_0, C1, C2, C3, SvCarray2, SvCarray3, courseCount)
	utility[i] = u1;
	if printflag:
		print u1, u2
	if u1 >= u2:
	    x_0 = newAllotment
	else:
		beta = 10*np.log10(1+i)
		probVar = np.exp(beta*(u1 - u2))
		randNum = np.random.uniform()
		#if(swapId1 == 6 | swapId2 == 6):
			#print probVar
		if randNum < probVar:
			x_0 = newAllotment
		else:
			x_0 = x_0
	if printflag:
		print x_0

print calculateUtilityFunction(x_0, C1, C2, C3, SvCarray2, SvCarray3, courseCount)
print x_0

c = np.zeros((studentCount, 2))
a, b = np.where(x_0 == 1)
c[:,0] = a
c[:,1] = b

def calcGoodness(anAllotment, SvCarray, courseCount, cpiArray):
    a = anAllotment*SvCarray
    b = np.ma.masked_where(a == 0, a)
    choiceGoodness = np.array(np.nanmean(b, 1), dtype=np.float)
    # meanChoiceGoodness = np.mean(choiceGoodness)
    #
    cpiRepeated = (np.array([cpiArray, ]*courseCount)).transpose()
    SvC_cpi = anAllotment * cpiRepeated
    b = np.ma.masked_where(SvC_cpi == 0, SvC_cpi)
    cpiGoodness = np.array(np.nanmean(b, 0), dtype=np.float)
    return choiceGoodness, cpiGoodness

print calcGoodness(x_0, SvCarray3, courseCount, cpiArray)

#plt.plot(utility)
#plt.show()
