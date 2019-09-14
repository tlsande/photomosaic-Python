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


def processImages(locations, num):
    start = time.time()
    for i in range(0, len(locations)):
        if locations[i].endswith(('.png', '.jpg', '.gif')):
            img = Image.open(locations[i])
            img = img.resize((64, 64))
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
            averages.append((int(row[1]), int(row[2]), int(row[3])))
        # for i in range(len(locations)):
        #     print(i)
        return locations, averages

# def distance(color1, color2):
#     return np.linalg.norm(color1 - color2)
#
# # Basic search for now, might add option for top n cloest as to no reuse images too much
# def closestColor(pix):
#     locations, averages = loadCache()
#     min = None
#     closestLocation = ""
#     for i in range(len(locations)):
#         if distance(pix, averages[i] < min) or min is None:
#             min = distance(pix, averages[i])
#             closestLocation = locations[i]
#             print(min)
#             print(closestLocation)


if __name__ == '__main__':
    locations = getAllPaths(sys.argv[1])

    numThreads = multiprocessing.cpu_count()

    splitLocations = np.array_split(locations, numThreads)

    if not os.path.exists(imageProcessed):
        os.mkdir(imageProcessed)

    num = 0
    p = []
    for i in range(numThreads):
        print(i)
        p.append(multiprocessing.Process(target=processImages, args=(splitLocations[i], num)))
        num += len(splitLocations[i])
        p[i].start()
    for i in range(numThreads):
        p[i].join()

    writeCache(imageProcessed)
    newLocations, average = loadCache()

    # img = Image.open("images/source/test/test1.png")
    # # closestColor(img.getpixel((500, 500)))
    # p1 = average[20]
    # p2 = img.getpixel((500,500))
    # print(distance(p1, p2))
