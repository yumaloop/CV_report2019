import numpy as np 
import cv2

# constant
NUM_SECTOR = 9
FLT_EPSILON = 1e-07


def func1(dx, dy, boundary_x, boundary_y, height, width, numChannels):
    r = np.zeros((int(height), int(width)), np.float32)
    alfa = np.zeros((int(height), int(width), 2), np.int)

    for j in range(1, height-1):
        for i in range(1, width-1):
            c = 0
            x = dx[j, i, c]
            y = dy[j, i, c]
            r[j, i] = np.sqrt(x**2 + y**2)

            for ch in range(1, numChannels):
                tx = dx[j, i, ch]
                ty = dy[j, i, ch]
                magnitude = np.sqrt(tx * tx + ty * ty)
                if(magnitude > r[j, i]):
                    r[j, i] = magnitude
                    c = ch
                    x = tx
                    y = ty

            mmax = boundary_x[0] * x + boundary_y[0] * y
            maxi = 0

            for kk in range(0, NUM_SECTOR):
                dotProd = boundary_x[kk]*x + boundary_y[kk]*y
                if(dotProd > mmax):
                    mmax = dotProd
                    maxi = kk
                elif(-dotProd > mmax):
                    mmax = -dotProd
                    maxi = kk + NUM_SECTOR

            alfa[j, i, 0] = maxi % NUM_SECTOR
            alfa[j, i, 1] = maxi
    return r, alfa

def func2(dx, dy, boundary_x, boundary_y, r, alfa, nearest, w, k, height, width, sizeX, sizeY, p, stringSize):
    mapp = np.zeros(int(sizeX * sizeY * p), np.float32)
    for i in range(int(sizeY)):
        for j in range(int(sizeX)):
            for ii in range(int(k)):
                for jj in range(int(k)):

                    if ((i * k + ii > 0) and (i * k + ii < height - 1) and (j * k + jj > 0) and (j * k + jj < width  - 1)):
                        mapp[int(i * stringSize + j * p + alfa[int(k * i + ii), int(j * k + jj), 0]             ) ] += r[int(k * i + ii), int(j * k + jj)] * w[ii, 0] * w[jj, 0]
                        mapp[int(i * stringSize + j * p + alfa[int(k * i + ii), int(j * k + jj), 1] + NUM_SECTOR) ] += r[int(k * i + ii), int(j * k + jj)] * w[ii, 0] * w[jj, 0]

                        if((i + nearest[ii] >= 0) and (i + nearest[ii] <= sizeY - 1)):
                            mapp[int((i + nearest[ii]) * stringSize + j * p + alfa[int(k * i + ii), int(j * k + jj), 0]              ) ] += r[int(k * i + ii), int(j * k + jj)] * w[ii, 1] * w[jj, 0]
                            mapp[int((i + nearest[ii]) * stringSize + j * p + alfa[int(k * i + ii), int(j * k + jj), 1] + NUM_SECTOR ) ] += r[int(k * i + ii), int(j * k + jj)] * w[ii, 1] * w[jj, 0]
                        if((j + nearest[jj] >= 0) and (j + nearest[jj] <= sizeX - 1)):
                            mapp[int(i * stringSize + (j + nearest[jj]) * p + alfa[int(k * i + ii), int(j * k + jj), 0]              ) ] += r[int(k * i + ii), int(j * k + jj)] * w[ii, 0] * w[jj, 1]
                            mapp[int(i * stringSize + (j + nearest[jj]) * p + alfa[int(k * i + ii), int(j * k + jj), 1] + NUM_SECTOR ) ] += r[int(k * i + ii), int(j * k + jj)] * w[ii, 0] * w[jj, 1]
                        if((i + nearest[ii] >= 0) and (i + nearest[ii] <= sizeY - 1) and (j + nearest[jj] >= 0) and (j + nearest[jj] <= sizeX - 1)):
                            mapp[int((i + nearest[ii]) * stringSize + (j + nearest[jj]) * p + alfa[int(k * i + ii), int(j * k + jj), 0]              ) ] += r[int(k * i + ii), int(j * k + jj)] * w[ii, 1] * w[jj, 1]
                            mapp[int((i + nearest[ii]) * stringSize + (j + nearest[jj]) * p + alfa[int(k * i + ii), int(j * k + jj), 1] + NUM_SECTOR ) ] += r[int(k * i + ii), int(j * k + jj)] * w[ii, 1] * w[jj, 1]
    return mapp

def func3(partOfNorm, mappmap, sizeX, sizeY, p, xp, pp):
    newData = np.zeros(int(sizeY * sizeX * pp), np.float32)
    for i in range(1, int(sizeY+1)):
        for j in range(1, int(sizeX+1)):
            pos1 = i * (sizeX+2) * xp + j * xp
            pos2 = (i-1) * sizeX * pp + (j-1) * pp

            valOfNorm = np.sqrt(partOfNorm[int(  i      * (sizeX + 2) + (j    ) )]  +
                                partOfNorm[int(  i      * (sizeX + 2) + (j + 1) )]  +
                                partOfNorm[int( (i + 1) * (sizeX + 2) + (j    ) )]  +
                                partOfNorm[int( (i + 1) * (sizeX + 2) + (j + 1) )]) + FLT_EPSILON
            newData[int(pos2):int(pos2+p)]       = mappmap[int(pos1):int(pos1+p)] / valOfNorm
            newData[int(pos2+4*p):int(pos2+6*p)] = mappmap[int(pos1+p):int(pos1+3*p)] / valOfNorm

            valOfNorm = np.sqrt(partOfNorm[int(  i      * (sizeX + 2) + (j    ) )]  +
                                partOfNorm[int(  i      * (sizeX + 2) + (j + 1) )]  +
                                partOfNorm[int( (i - 1) * (sizeX + 2) + (j    ) )]  +
                                partOfNorm[int( (i - 1) * (sizeX + 2) + (j + 1) )]) + FLT_EPSILON
            newData[int(pos2+p):int(pos2+2*p)]   = mappmap[int(pos1):int(pos1+p)] / valOfNorm
            newData[int(pos2+6*p):int(pos2+8*p)] = mappmap[int(pos1+p):int(pos1+3*p)] / valOfNorm

            valOfNorm = np.sqrt(partOfNorm[int(  i      * (sizeX + 2) +  j      )]  +
                                partOfNorm[int(  i      * (sizeX + 2) + (j - 1) )]  +
                                partOfNorm[int( (i + 1) * (sizeX + 2) +  j      )]  +
                                partOfNorm[int( (i + 1) * (sizeX + 2) + (j - 1) )]) + FLT_EPSILON
            newData[int(pos2+2*p):int(pos2+3*p)]  = mappmap[int(pos1):int(pos1+p)] / valOfNorm
            newData[int(pos2+8*p):int(pos2+10*p)] = mappmap[int(pos1+p):int(pos1+3*p)] / valOfNorm

            valOfNorm = np.sqrt(partOfNorm[int(  i      * (sizeX + 2) +  j      )]  +
                                partOfNorm[int(  i      * (sizeX + 2) + (j - 1) )]  +
                                partOfNorm[int( (i - 1) * (sizeX + 2) +  j      )]  +
                                partOfNorm[int( (i - 1) * (sizeX + 2) + (j - 1) )]) + FLT_EPSILON
            newData[int(pos2+3*p):int(pos2+4*p)]   = mappmap[int(pos1):int(pos1+p)] / valOfNorm
            newData[int(pos2+10*p):int(pos2+12*p)] = mappmap[int(pos1+p):int(pos1+3*p)] / valOfNorm
    return newData

def func4(mappmap, p, sizeX, sizeY, pp, yp, xp, nx, ny):
    newData = np.zeros(int(sizeX * sizeY * pp), np.float32)
    for i in range(int(sizeY)):
        for j in range(int(sizeX)):
            pos1 = (i * sizeX + j) * p
            pos2 = (i * sizeX + j) * pp
            for jj in range(int(2 * xp)):  # 2*9
                newData[int(pos2 + jj)] = np.sum(mappmap[int(pos1 + yp * xp + jj):int(pos1 + 3 * yp * xp + jj):int(2 * xp)]) * ny
            for jj in range(int(xp)):  # 9
                newData[int(pos2 + 2 * xp + jj)] = np.sum(mappmap[int(pos1 + jj):int(pos1 + jj + yp * xp):int(xp)]) * ny
            for ii in range(int(yp)):  # 4
                newData[int(pos2 + 3 * xp + ii)] = np.sum(mappmap[int(pos1 + yp * xp + ii * xp * 2):int(pos1 + yp * xp + ii * xp * 2 + 2 * xp)]) * nx
    return newData



def getFeatureMaps(image, k, mapp):
    kernel = np.array([[-1., 0., 1.]], np.float32)
    height = image.shape[0]
    width = image.shape[1]
    assert(image.ndim==3 and image.shape[2])
    numChannels = 3 #(1 if image.ndim==2 else image.shape[2])

    sizeX = int(width / k)
    sizeY = int(height / k)
    px = 3 * NUM_SECTOR
    p = px
    stringSize = sizeX * p

    mapp['sizeX'] = sizeX
    mapp['sizeY'] = sizeY
    mapp['numFeatures'] = p
    mapp['map'] = np.zeros(int(mapp['sizeX'] * mapp['sizeY'] * mapp['numFeatures']), np.float32)

    dx = cv2.filter2D(np.float32(image), -1, kernel)   # np.float32(...) is necessary
    dy = cv2.filter2D(np.float32(image), -1, kernel.T)

    arg_vector = np.arange(NUM_SECTOR+1).astype(np.float32) * np.pi / NUM_SECTOR
    boundary_x = np.cos(arg_vector) 
    boundary_y = np.sin(arg_vector)

    ### 200x speedup
    r, alfa = func1(dx, dy, boundary_x, boundary_y, height, width, numChannels)
    ### ~0.001s

    nearest = np.ones((k), np.int)
    nearest[0:int(k/2)] = -1

    w = np.zeros((k, 2), np.float32)
    a_x = np.concatenate((k/2 - np.arange(k/2) - 0.5, np.arange(k/2,k) - k/2 + 0.5)).astype(np.float32)
    b_x = np.concatenate((k/2 + np.arange(k/2) + 0.5, -np.arange(k/2,k) + k/2 - 0.5 + k)).astype(np.float32)
    w[:, 0] = 1.0 / a_x * ((a_x*b_x) / (a_x+b_x))
    w[:, 1] = 1.0 / b_x * ((a_x*b_x) / (a_x+b_x))

    ### 500x speedup
    mapp['map'] = func2(dx, dy, boundary_x, boundary_y, r, alfa, nearest, w, k, height, width, sizeX, sizeY, p, stringSize)
    ### ~0.001s

    return mapp


def normalizeAndTruncate(mapp, alfa):
    sizeX = int(mapp['sizeX'])
    sizeY = int(mapp['sizeY'])
    p  = NUM_SECTOR
    xp = NUM_SECTOR * 3
    pp = NUM_SECTOR * 12

    ### 50x speedup
    # idx = np.arange(0, int(sizeX * sizeY * mapp['numFeatures']), int(mapp['numFeatures'])).reshape(int(sizeX * sizeY), 1) + np.arange(p)
    idx = np.arange(0, int(sizeX * sizeY * mapp['numFeatures']), int(mapp['numFeatures'])) + np.arange(int(sizeX * sizeY))
    partOfNorm = np.sum(mapp['map'][idx] ** 2, axis=1) ### ~0.0002s  mapp['map'].shape = sizeX * sizeY * (3 * NUM_SECTOR)

    sizeX, sizeY = sizeX - 2, sizeY - 2
    
    ### 30x speedup
    newData = func3(partOfNorm, mapp['map'], sizeX, sizeY, p, xp, pp)
    ###

    # truncation
    newData[newData > alfa] = alfa

    mapp['numFeatures'] = pp
    mapp['sizeX'] = sizeX
    mapp['sizeY'] = sizeY
    mapp['map'] = newData

    return mapp


def PCAFeatureMaps(mapp):
    sizeX = mapp['sizeX']
    sizeY = mapp['sizeY']

    p = mapp['numFeatures']
    pp = NUM_SECTOR * 3 + 4
    yp = 4
    xp = NUM_SECTOR

    nx = 1.0 / np.sqrt(xp*2)
    ny = 1.0 / np.sqrt(yp)
    ### 190x speedup
    newData = func4(mapp['map'], p, sizeX, sizeY, pp, yp, xp, nx, ny)
    ###

    mapp['numFeatures'] = pp
    mapp['map'] = newData

    return mapp
