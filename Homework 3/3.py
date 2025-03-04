import cv2
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from skimage import measure, color

img = cv2.imread("Homework 3/CoffeeBeans.tif")

#Show Image (Q1)
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
plt.figure(1)
plt.subplot(221)
plt.title('Grayscale image')
plt.imshow(gray, cmap = 'gray')

#Threshold Image (Q1)
ret1, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
plt.subplot(222)
plt.title('Thresh')
plt.imshow(thresh, cmap ='gray')

##Foreground/Background seperation (Q2)
#Find openings
kernel = np.ones((3,3), np.uint8)
opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations = 1)
plt.figure(2)
plt.subplot(221)
plt.title('Opening')
plt.imshow(opening, cmap ='gray')

#Find Background
sure_bg = cv2.dilate(opening, kernel, iterations = 1)
plt.subplot(222)
plt.title('background')
plt.imshow(sure_bg, cmap='gray')

#Distance Transform 
dist_transform = cv2.distanceTransform(opening, cv2.DIST_L2, 5)
plt.figure(3)
plt.subplot(231)
plt.title('Dist')
plt.imshow(dist_transform, cmap = 'gray')

#Find Max Distance Transform Value
print(dist_transform.max())

#Pick Distance Transform Value to make Foreground
ret2, sure_fg = cv2.threshold(dist_transform, 0.59*dist_transform.max(), 255, 0)
plt.subplot(232)
plt.title('Dist 0.59')
plt.imshow(sure_fg, cmap = 'gray')

#Find Unknown region by image subtraction
sure_fg = np.uint8(sure_fg)
unknown = cv2.subtract(sure_bg, sure_fg)
plt.subplot(233)
plt.title('Unknown')
plt.imshow(unknown, cmap= 'gray')

#Create Markers using Connected Components
ret3, markers = cv2.connectedComponents(sure_fg)
plt.figure(4)
plt.subplot(221)
plt.title('Connected Components')
plt.imshow(markers, cmap = 'jet')

#Add new value for every new marker
markers = markers + 1

#Set background value to 0, new Connected Components map
markers[unknown == 255] = 0
plt.subplot(222)
plt.title('ConnComp Fixed')
plt.imshow(markers, cmap = 'jet')

#Watershed of markers
markers = cv2.watershed(img, markers)
img[markers == -1] = [0, 255, 255]
img2 = color.label2rgb(markers, bg_label = 0)
plt.figure(5)
plt.title('Watershed')
plt.imshow(img2)

##Find area and count of Coffee Beans (Q3)
props = measure.regionprops_table(markers, gray, properties = ['label', 'area'])

df = pd.DataFrame(props)
#print(df.head())

df = df[df['area'] < 10000 ]
#print(df.head())

df.hist(column = "area", bins = 25)
##Find probability of average value / 2
df.hist(column = "area", bins = 25, density = 'True')
avg = df.mean()

# list of sizes of beans, from data frame generated
listOfBeanSizes = [136, 1105, 899, 969, 1547, 1022, 1382, 1193, 1413, 863, 1083, 1211,
                   12, 982, 1176, 841, 1159, 983, 839, 872, 792, 1235, 795, 1079, 1317,
                   1129, 988, 1043, 998, 723, 858, 993, 1185, 993, 1185, 1267, 1413, 987,
                   1003, 955, 663, 163, 240]

# given a list of bean sizes, prints the number of beans, average bean size, and returns the probability
# that a random bean's size is under half the average size of all beans
def findProbOfAreaUnderHalfMu(listOfSizes):
    sumArea = 0
    numberOfBeans = 0

    # iterates through list, finds total bean "area", number of beans, and average bean size
    for i in listOfSizes:
        sumArea += i
        numberOfBeans += 1
    averageArea = sumArea / numberOfBeans

    # prints number of beans and average bean size
    print("Number of beans: " + str(numberOfBeans))
    print("Average bean size (µ): " + str(averageArea))

    # iterates through list to count beans under half-average
    beansUnderHalfAverageArea = 0
    for i in listOfSizes:
        if i < averageArea / 2:
            beansUnderHalfAverageArea += 1
    # calculates and returns probability
    probability = beansUnderHalfAverageArea / numberOfBeans
    return probability * 100

probability = findProbOfAreaUnderHalfMu(listOfBeanSizes)

print("Probability that bean size is under µ/2: " + str(probability) + "%")