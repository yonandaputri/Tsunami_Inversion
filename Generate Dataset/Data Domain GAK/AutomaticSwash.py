# insert module
import numpy as np
np.random.seed(100)
import pandas as pd
import matplotlib.pyplot as plt
import os
from subprocess import call
import subprocess
# function to rotate domain (rotate hump inversely)


def fun_rotation(X, Y, x0, y0, r0):
    Xr = np.cos(r0*np.pi/180)*(X-x0) - np.sin(r0*np.pi/180)*(Y-y0)
    Yr = np.sin(r0*np.pi/180)*(X-x0) + np.cos(r0*np.pi/180)*(Y-y0)
    return(Xr, Yr)


def swash_input(case):
    return """
$*************HEADING***********************************
$
PROJ 'Krakatau0X' 'TK0X'
$
$***********MODEL DESCRIPTION
$ 
$   Tsunami modelling for Krakatau Underwater Landslide
$	Numerical experiment for Tsunami in Sunda Strait 2018
$   Case 01 : An underwater Landslide at SouthWest coast cause a Tsunami 
$ 			  with an initial condition of inverted gaussian profile
$
$***********MODEL INPUT*********************************
$ -setting
SET depmin = 0.1
$
$ -cgrid:xmin, ymin, direction of domain, length-x, length-y, Nx, Ny
CGRID 7400 0 0 181115 160765 490 435
$
$ - number of vertical layer and proportion
VERT 1
$
$ ---- inp bottom : xmin, ymin, direction of domain, Nx-1, Ny-1, dx, dy 
$ ---- read bottom : factor, filename, rotation, 0, FREE
INPGRID BOTTOM 0 0 0. 1019 869 185 185
READINP BOTTOM -1. '../BATNAS_KRAKATAU_LARGE_V01X.txt' 4 0 FREE
$
$ ---- initial condition : commonly zero : initial max = 4 m
INPGRID WLEV 0 0 0. 1019 869 185 185 EXCEPTION -999
READINP WLEV 8.0 'ETA_Gaussian_"""+str(case)+""".txt' 4 0 FREE
$ 
$ ---- SPONGE LAYER % only 1 dx or 185 m (this one could work, altough reflect some)
SPONGE N 370.
SPONGE E 370.
SPONGE W 370.
SPONGE S 370.
$ ---- physical setting : BREAK = breaking activated, NONHYDROSTATIC = nonhydrostatic activated
BREAK
$ NONHYDROSTATIC
$ DISCRET CORRDEP FIRST
$
$************ OUTPUT REQUESTS *************************
$ ---- extract for a whole domain for specific variable (WATL = water level)
$ ---- group : must be 'COMPGRD' index of xmin, index of xmax, index of ymin, index of ymax
$ POINT 'POIN' FILE '../BP.txt'
$ TABLE 'POIN' HEADER 'DATA01.txt' TSEC WATL VEL OUTPUT 000000.000 60 SEC
$
GROUP 'COMPGRD' 1 491 1 436
BLOCK 'COMPGRD' NOHEAD 'BASE01.mat' LAY 3 XP YP BOTL OUTPUT 000000.000 99999 SEC
BLOCK 'COMPGRD' NOHEAD 'MAIN01.mat' LAY 3 WATL OUTPUT 000000.000 60 SEC
BLOCK 'COMPGRD' NOHEAD 'MAIN02.mat' LAY 3 VEL OUTPUT 000000.000 60 SEC
$
TEST 1,0
$ compute from 0 sec with dt = 0.5 sec for 3 min 20 sec (= 200 sec)
COMPUTE 000000.000 0.5 SEC 060000.000
STOP
	"""

bath = pd.read_csv("BATNAS_KRAKATAU_LARGE_V01X.txt", delimiter='\t', header=None)

number = 10
array_x0 = np.random.uniform(low=600, high=620, size=(number,))
array_y0 = np.random.uniform(low=440, high=460, size=(number,))
array_a0 = np.random.uniform(low=1, high=1.5, size=(number,))
array_a1 = np.random.uniform(low=1, high=1.5, size=(number,))
array_rx = np.random.uniform(low=1.5, high=9, size=(number,))
array_ry = np.random.uniform(low=1.5, high=9, size=(number,))
array_r0 = np.random.uniform(low=0, high=45, size=(number,))

case = 0

for i in range(number):
    case += 1

    # casenum = i

    # create initial condition for generating dataset of tsunami inversion :
    x0 = array_x0[i]  # initial hump location - x
    y0 = array_y0[i]  # initial hump location - y

    # initial amplitude of hump cut-off (if necessary 0<a1<a0, a1>=a0 means no cut-off)
    if array_a0[i] > array_a1[i] :
        a0 = array_a0[i]
        a1 = array_a1[i]
    else :
        a0 = array_a1[i]
        a1 = array_a0[i]
    # hump width radius in x - direction (before rotated)
    rx = array_rx[i]
    # hump width radius in y - direction (before rotated)
    ry = array_ry[i]
    r0 = array_r0[i]  # rotation in degree (clockwise)

    # setting domain simulation :
    Nx = 1020  # Number of x-grid
    Ny = 870  # Number of y-grid
    # disesuaikan dengan domain simulasi
    x = np.linspace(0, bath.shape[1], num=Nx)
    y = np.linspace(0, bath.shape[0], num=Ny)

    [X, Y] = np.meshgrid(x, y)
    [Xr, Yr] = fun_rotation(
        X, Y, x0, y0, r0)      # rotate
    # normalized in term of radius
    Rr = np.sqrt((Xr/rx)**2+(Yr/ry)**2)

    # calculate hump and plot (to check) :
    eta = a0*np.exp(-(0.5*Rr)**2)
    # cutting-off
    for ii in range(Nx):
        for jj in range(Ny):
            if eta[jj, ii] > a1:
                eta[jj, ii] = 2*a1-eta[jj, ii]

    print(case)
    os.mkdir(str(case))
    np.savetxt(str(case)+'/ETA_Gaussian_'+str(case)+'.txt',eta, fmt='%1.2e')

    file_swash = open(str(case)+"/Tsm_KRT_c"+str(case)+".sws", "w+")
    file_swash.write(swash_input(str(case)))
    
    # z = np.ma.masked_array(bath.values, bath.values < -5)
    
    # fig = plt.figure(figsize=(20,20))

    # ax = fig.add_subplot(111)

    # # ax.scatter()
    # ax.pcolormesh(X, Y, eta, shading='auto')
    # ax.pcolormesh(z, cmap = "jet", vmin = -3000, vmax = 1000, norm=None)
    
    # plt.show()

case = 0

for i in range(number):

    case += 1

    path = str(case)
    command = 'swashrun Tsm_KRT_c'+path
    p = subprocess.call(command,cwd=path,shell=True)
