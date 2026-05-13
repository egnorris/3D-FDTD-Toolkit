import numpy as np
import matplotlib.pyplot as plt
import pandas as pd


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
    structureLength = []
    structureCenter = []
    l, w = np.shape(imageArray)
    for i in range(1,l-1):
        # structures cannot touch the edges
        for k in range(1,w-1):
            s=[imageArray[i,k-1], imageArray[i,k], imageArray[i,k+1]]
            flag = stateAnalysis(s)
            if flag == 0:
                length = 1
                structureLength.append(length)
                structureCenter.append((k,i))
            elif flag == 1:
                length = 1
                x0 = k
            elif flag == 2:
                length += 1
            elif flag == 3:
                length += 1
                x1 = k
                x = int(round((x1 + x0)/2))
                structureLength.append(length)
                structureCenter.append((x,i))
    return pd.DataFrame({"Center":structureCenter, "Length": structureLength})


imageArray = np.random.randint(0,2, (5, 10))
imageArray[:, 0] = 0
imageArray[:, -1] = 0
imageArray[0, :] = 0
imageArray[-1, :] = 0

plt.imshow(imageArray, cmap='binary')
plt.savefig("io/imageArray.png")
structures= getStructures(imageArray)
print(structures)
        
