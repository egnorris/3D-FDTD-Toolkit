import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import argparse
import os
from PIL import Image

def stateAnalysis(s):
        if s == [0,1,0]:
            return 0
        elif s == [0,1,1]:
            return 1
        elif s == [1,1,1]:
            return 2
        elif s == [1,1,0]:
            return 3
        else:
            return 4

def getStructures(imageArray):
    """
    Build a dataframe with coordinates and lengths of structures found in the imageArray input
    """
    structureLength = []
    structureCenterx = []
    structureCentery = []
    l, w = np.shape(imageArray)
    for i in range(l):
        for k in range(w):
            if k == 0:
                #analysis logic for structures at the left boundary
                s=[imageArray[i,k], imageArray[i,k+1]]
                if s == [1,1]:
                    #structure starts at the boundary and continues
                    length = 1
                    x0 = k
                elif s == [1,0]:
                    # single pixel structure at the boundary
                    length = 1
                    structureLength.append(length)
                    structureCenterx.append(k)
                    structureCentery.append(i)
            elif k == w-1:
                #analysis logic for structures at the right boundary
                s=[imageArray[i,k-1], imageArray[i,k]]
                if s == [1,1]:
                    #structure ends at the boundary
                    length += 1
                    x1 = k
                    x = (x1 + x0)/2
                    structureLength.append(length)
                    structureCenterx.append(x)
                    structureCentery.append(i)
                if s == [0,1]:
                    # single pixel structure at the boundary
                    length = 1
                    structureLength.append(length)
                    structureCenterx.append(k)
                    structureCentery.append(i)
            else:
                
                s=[imageArray[i,k-1], imageArray[i,k], imageArray[i,k+1]]
                flag = stateAnalysis(s)
                if flag == 0:
                    # single pixel structure
                    length = 1
                    structureLength.append(length)
                    structureCenterx.append(k)
                    structureCentery.append(i)
                elif flag == 1:
                    # structure starts
                    length = 1
                    x0 = k
                elif flag == 2:
                    # structure continues
                    length += 1
                elif flag == 3:
                    # structure ends
                    length += 1
                    x1 = k
                    x = (x1 + x0)/2
                    structureLength.append(length)
                    structureCenterx.append(x)
                    structureCentery.append(i)
    return pd.DataFrame({"x":structureCenterx,"y":structureCentery, "l": structureLength})


def structurePreview(structures, imageArray, ms=1):
    x = structures["x"].tolist()
    y = structures["y"].tolist()
    l = structures["l"].tolist()
    plt.scatter(x, y, marker='o', zorder=0.5, c='green', s=ms, ec=None)
    for i in range(len(l)):
        plt.scatter([x[i]-l[i]/2],[y[i]], marker='o', c= 'blue', zorder=0, s=ms, ec=None)
        plt.scatter([x[i]+l[i]/2],[y[i]], marker='o', c= 'red', zorder=0, s=ms, ec=None)
    plt.imshow(imageArray, cmap='binary', zorder=-1,)
    plt.tight_layout()
    plt.savefig("io/imageStructurePreview.png", dpi=900)
    plt.close()


def loadImage(fname):
    print('Reading Image')
    img = Image.open(fname)
    print(f"{fname}\n    Format: {img.format}")
    print(f"    Resolution: {img.size}")
    print(f"    Mode: {img.mode}")
    temp = np.asarray(img)
    temp = temp[:,:, :3] < 255
    temp = temp.any(axis=2)
    return temp.astype(int)

def loadArray(fname):
    print('Reading Array')
    return np.random.randint(0,2, (5, 10))

parser = argparse.ArgumentParser(description="write Geometry.json")
parser.add_argument('-imageFile', type=str, required=False, default=None)
parser.add_argument('-arrayFile', type=str, required=False, default=None)
parsedArgs = parser.parse_args().__dict__
if ((parsedArgs['imageFile'] == None) and (parsedArgs['arrayFile'] == None)):
    print("No image or array input file detected, Running demonstration instead.")
    imageArray = np.random.randint(0,2, (5, 10))
    structures= getStructures(imageArray)
    structurePreview(structures, imageArray, ms = 5)

else:
    if (parsedArgs['imageFile'] != None) and (parsedArgs['arrayFile'] == None):
        if os.path.isfile(parsedArgs['imageFile']):
            print(f"Input Image Detected: {parsedArgs['imageFile']}")
            imageArray = loadImage(parsedArgs['imageFile'])
        else:
            raise Exception(f"{parsedArgs['imageFile']} not found!")
            
    elif (parsedArgs['imageFile'] == None) and (parsedArgs['arrayFile'] != None):
        if os.path.isfile(parsedArgs['arrayFile']):
            print(f"Input Array Detected: {parsedArgs['arrayFile']}")
            imageArray = loadArray(parsedArgs['arrayFile'])
        else:
            raise Exception(f"{parsedArgs['arrayFile']} not found!")
    else:
        if os.path.isfile(parsedArgs['imageFile']):
            print(f"Input Array Detected: {parsedArgs['imageFile']}")
            imageArray = loadImage(parsedArgs['imageFile'])
        else:
            print(f"{parsedArgs['imageFile']}: File Not Found!")
            if os.path.isfile(parsedArgs['arrayFile']):
                print(f"Input Array Detected: {parsedArgs['arrayFile']}")
                imageArray = loadArray(parsedArgs['arrayFile'])
            else: 
                raise Exception(f"{parsedArgs['imageFile']} and {parsedArgs['arrayFile']} not found!")

    print(imageArray)
    structures= getStructures(imageArray)
    print(structures)
    structurePreview(structures, imageArray, ms = 0.1)




        
