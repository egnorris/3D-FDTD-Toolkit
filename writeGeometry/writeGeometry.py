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
    structureCenterx = []
    structureCentery = []
    l, w = np.shape(imageArray)
    for i in range(l):
        # structures cannot touch the edges
        for k in range(w):
            if k == 0:
                s=[imageArray[i,k], imageArray[i,k+1]]
                if s == [1,1]:
                    length = 1
                    x0 = k
                elif s == [1,0]:
                    length = 1
                    structureLength.append(length)
                    structureCenterx.append(k)
                    structureCentery.append(i)
            elif k == w-1:
                s=[imageArray[i,k-1], imageArray[i,k]]
                if s == [1,1]:
                    length += 1
                    x1 = k
                    x = (x1 + x0)/2
                    structureLength.append(length)
                    structureCenterx.append(x)
                    structureCentery.append(i)
                if s == [0,1]:
                    length = 1
                    structureLength.append(length)
                    structureCenterx.append(k)
                    structureCentery.append(i)
            else:
                s=[imageArray[i,k-1], imageArray[i,k], imageArray[i,k+1]]
                flag = stateAnalysis(s)
                if flag == 0:
                    length = 1
                    structureLength.append(length)
                    structureCenterx.append(k)
                    structureCentery.append(i)
                elif flag == 1:
                    length = 1
                    x0 = k
                elif flag == 2:
                    length += 1
                elif flag == 3:
                    length += 1
                    x1 = k
                    x = (x1 + x0)/2
                    structureLength.append(length)
                    structureCenterx.append(x)
                    structureCentery.append(i)
    return pd.DataFrame({"x":structureCenterx,"y":structureCentery, "l": structureLength})


imageArray = np.random.randint(0,2, (5, 10))
#remove data from the boundaries of the image
#imageArray[:, 0] = 0
#imageArray[:, -1] = 0
#imageArray[0, :] = 0
#imageArray[-1, :] = 0

structures= getStructures(imageArray)
x = structures["x"].tolist()
y = structures["y"].tolist()
l = structures["l"].tolist()

plt.scatter(x, y, zorder=1)
for i in range(len(l)):
    plt.plot([x[i]-l[i]/2, x[i]+l[i]/2],[y[i],y[i]], c= 'white', zorder=0)


plt.imshow(imageArray, cmap='binary', zorder=-1)
plt.savefig("io/imageStructurePreview.png")



        
