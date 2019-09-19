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


def splitList(list):
    half = len(list) // 2
    return list[:half], list[half:]

# Todo Test converting to pool map instead of manually splitting input array
# Todo Add progress output
def processImages(locations, num, blockSize):
    start = time.time()
    for i in range(0, len(locations)):
        if locations[i].endswith(('.png', '.jpg', '.gif')):
            img = Image.open(locations[i])
            img = img.resize((blockSize, blockSize))
            # img.save(imageProcessed, "test", i + num, ".png")
            # print("test", '{0:04}'.format(i+num), ".png")
            path = imageProcessed + "test" + '{:04d}'.format(i + num) + ".png"
            img.save(path)
    end = time.time()
    print("Runtime: " + str(end - start))

def averageRGB(location):
    img = Image.open(location).convert('RGB')
    # Slower than numpy
    # r = g = b = a = 0
    # start = time.time()
    # for x in range(img.width):
    #     for y in range(img.height):
    #         pixr, pixg, pixb = img.getpixel((x, y))
    #         r += pixr
    #         g += pixg
    #         b += pixb
    #         # a += pixa
    # r = np.round(r / (img.width * img.height))
    # g = np.round(g / (img.width * img.height))
    # b = np.round(b / (img.width * img.height))
    # end = time.time()
    # print("First: ", end - start)
    # print("(", r, ", ", g, ",", b, ")")

    # start = time.time()
    # print(np.round(np.array(img).mean(axis=(0, 1))))
    # end = time.time()
    # print("Second: ", end - start)
    r, g, b, = np.round(np.array(img).mean(axis=(0, 1)))
    r = int(r)
    g = int(g)
    b = int(b)
    # print(r, g, b)
    return r, g, b
    # print(np.round(np.array(img).mean(axis=(0, 1))))
    # return np.round(np.array(img).mean(axis=(0,1)))
    # print(np.rint(np.array(img).mean(axis=(0,1))))
    # return np.rint(np.array(img).mean(axis=(0,1)))
    # return r, g, b

def writeCache(pLocation):
    csvFile = open('cache.csv', 'w')
    writer = csv.writer(csvFile)
    locations = getAllPaths(pLocation)
    # locations = getBasePaths(pLocation)
    for i in locations:
        # print(i)
        # print(averageRGB(i))
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
            # averages.append((int(float(row[1])), int(float(row[2])), int(float(row[3]))))
            # averages.append((int(row[1]), int(row[2]), int(row[3])))
            averages.append(np.array((int(row[1]), int(row[2]), int(row[3]))))
        # for i in range(len(locations)):
        #     print(i)
        return locations, averages

def distance(color1, color2):
    return np.linalg.norm(color1 - color2)

# Todo move loadCache outside of this function. Should only load cache once
# Todo Basic search for now, might add option for top n cloest as to no reuse images too much
def closestColor(pix):
    locations, averages = loadCache()
    # min = None
    min = sys.maxsize
    closestLocation = None
    for i in range(len(locations)):
        # if distance(pix, averages[i]) < min or min is None:
        if distance(pix, averages[i]) < min:
            min = distance(pix, averages[i])
            closestLocation = locations[i]
    return closestLocation

# scaleSize is how much the base image will be scaled down or how much the chunksize of pixel
# to compare to the source image.
# blockSize is how big the source images are
# Todo Add multiprocessing. First test pool map with processImages
def photoMosaicProcess(location, scaleSize, blockSize):
    img = Image.open(location).convert('RGB')
    imgSmall = img.resize((int(img.width / scaleSize), int(img.height / scaleSize)))
    imgBig = imgSmall.resize((int(imgSmall.width * blockSize), int(imgSmall.height * blockSize)))
    start = time.time()
    for x in range(imgSmall.width):
        for y in range(imgSmall.height):
            # USE IMGSMALL YOU DUMB IDIOT
            # print(closestColor(np.array(imgSmall.getpixel((x,y)))))
            curImg = Image.open(closestColor(np.array(imgSmall.getpixel((x,y)))))
            imgBig.paste(curImg, (x * blockSize, y * blockSize))
            # hello = 0
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
        p.append(multiprocessing.Process(target=processImages, args=(splitLocations[i], num, 64)))
        num += len(splitLocations[i])
        p[i].start()
    for i in range(numThreads):
        p[i].join()

    writeCache(imageProcessed)

    # newLocations, average = loadCache()

    photoMosaicProcess(sys.argv[1], blockSize, blockSize)