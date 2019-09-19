from PIL import Image
from os import listdir
from os.path import isfile, join
from os import walk
import os
import time
import numpy as np
import multiprocessing
import sys
import csv
import math

imageProcessed = "images/processed/"
defaultOutputPath = "images/output/"

def getAllPaths(directory):
    directories = []
    for root, dirs, files in walk(directory, topdown=True):
        for name in files:
            directories.append(os.path.join(root, name))
    return directories


def getBasePaths(directory):
    # return [f for f in listdir(directory) if isfile((join(directory, f)))]
    directories = []
    for i in listdir(directory):
        if isfile(join(directory, i)):
            directories.append(join(directory, i))
    return directories

# Todo Test converting to pool map instead of manually splitting input array
# Todo Add progress output
def processImages(locations, num, blockSize):
    start = time.time()
    for i in range(0, len(locations)):
        if locations[i].endswith(('.png', '.jpg', '.gif')):
            img = Image.open(locations[i])
            img = img.resize((blockSize, blockSize))

            path = imageProcessed + "test" + '{:04d}'.format(i + num) + ".png"
            img.save(path)
    end = time.time()
    print("Runtime: " + str(end - start))

def averageRGB(location):
    img = Image.open(location).convert('RGB')

    r, g, b, = np.round(np.array(img).mean(axis=(0, 1)))
    r = int(r)
    g = int(g)
    b = int(b)

    return r, g, b

def writeCache(pLocation):
    csvFile = open('cache.csv', 'w', newline='')
    writer = csv.writer(csvFile)
    locations = getAllPaths(pLocation)
    # locations = getBasePaths(pLocation)
    for i in locations:
        R, G, B = averageRGB(i)
        writer.writerow((i, R, G, B))
    csvFile.close()

def loadCache():
    with open('cache.csv') as csvFile:
        csvReader = csv.reader(csvFile, delimiter=',')
        locations = []
        averages = []
        for row in csvReader:
            locations.append(row[0])
            averages.append((int(row[1]), int(row[2]), int(row[3])))

        return locations, averages

# Todo Basic search for now, might add option for top n cloest as to no reuse images too much
def closestColor(pix, locations, averages):
    min = sys.maxsize
    closestLocation = None
    # start = time.time()
    for i in range(len(locations)):
        dx = pix[0] - averages[i][0]
        dy = pix[1] - averages[i][1]
        dz = pix[2] - averages[i][2]
        temp = math.sqrt(dx*dx + dy*dy + dz*dz)

        if temp < min:
            min = distance(pix, averages[i])
            closestLocation = locations[i]
    return closestLocation

# scaleSize is how much the base image will be scaled down or how much the chunksize of pixel
# to compare to the source image.
# blockSize is how big the source images are
# Todo Add multiprocessing. First test pool map with processImages
def photoMosaicProcess(location, scaleSize, blockSize):
    if not os.path.exists(defaultOutputPath):
        os.mkdir(defaultOutputPath)
    locations, averages = loadCache()
    img = Image.open(location).convert('RGB')
    imgSmall = img.resize((int(img.width / scaleSize), int(img.height / scaleSize)))
    imgBig = imgSmall.resize((int(imgSmall.width * blockSize), int(imgSmall.height * blockSize)))
    start = time.time()
    for x in range(imgSmall.width):
        for y in range(imgSmall.height):
            curImg = Image.open(closestColor(imgSmall.getpixel((x,y)), locations, averages))
            imgBig.paste(curImg, (x * blockSize, y * blockSize))
    end = time.time()
    print("Runtime: ", end - start)
    imgBig.save(defaultOutputPath + "mosaic_" + str(time.time()) + ".png")

    # For checking correct scaling
    # imgSmall.save(defaultOutputPath + "small_" + str(time.time()) + ".png")
    # imgBig.save(defaultOutputPath + "big_" + str(time.time()) + ".png")

if __name__ == '__main__':
    locations = getAllPaths(sys.argv[1])
    blockSize = sys.argv[2]

    numThreads = multiprocessing.cpu_count()

    splitLocations = np.array_split(locations, numThreads)

    if not os.path.exists(imageProcessed):
        os.mkdir(imageProcessed)

    num = 0
    p = []
    for i in range(numThreads):
        print(i)
        p.append(multiprocessing.Process(target=processImages, args=(splitLocations[i], num, int(blockSize))))
        num += len(splitLocations[i])
        p[i].start()
    for i in range(numThreads):
        p[i].join()

    writeCache(imageProcessed)

    photoMosaicProcess(sys.argv[1], blockSize, blockSize)

    # photoMosaicProcess(sys.argv[1], 16, 16)