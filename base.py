from PIL import Image
from os import listdir
from os.path import isfile, join
from os import walk
import os
import time
import numpy as np
import sys

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

def processImages(locations, num):
    start = time.time()
    for i in range(0, len(locations)):
        if locations[i].endswith(('.png', '.jpg', '.gif')):
            img = Image.open(locations[i])
            img = img.resize((64, 64))
            img.save(imageProcessed + "test" + str(i + num) + ".png")
    end = time.time()
    print("Runtime: " + str(end - start))

locations = getAllPaths(sys.argv[1])

if not os.path.exists(imageProcessed):
    os.mkdir(imageProcessed)

processImages(locations, 0)
