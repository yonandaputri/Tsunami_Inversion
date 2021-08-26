# insert module
import numpy as np
np.random.seed(105)
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
PROJ 'TsBOX01' 'TB01'
$
$***********MODEL DESCRIPTION
$
$   Tsunami modelling for synthetic case : rectangular domain
$	Numerical experiment for Tsunami in rectangular domain
$   Case 01 : Initial condition inside
$             cause a tsunami with an initial condition of inverted gaussian profile
$
$***********MODEL INPUT*********************************
$ - setting coordinates
MODE NONST TWOD
$
$ -cgrid:xmin, ymin, direction of domain, length-x, length-y, Nx, Ny
CGRID 0. 0. 0 33250 13200 380 120
$
$ - number of vertical layer and proportion
VERT 1
$
$ ---- inp bottom : xmin, ymin, direction of domain, Nx-1, Ny-1, dx, dy
$ ---- read bottom : factor, filename, rotation, 0, FREE
INPGRID BOTTOM 0. 0. 0. 1 1 33250 13200
READINP BOTTOM -1. '../Bathymetry_FLAT.txt' 4 0 FREE
$
$ ---- initial condition : load from file : initial_gaussian_01.txt
INPGRID WLEV 0. 0. 0. 380 120 87.5 110 EXCEPTION -999
READINP WLEV 1.0 'initial_gaussian_"""+str(case)+""".txt' 4 0 FREE
$
$ ---- input boundary : side, <N,E,S,W>, orientation <ClockWise/CCW>,
$ ---- BTYPE, <weakly refl/linear riemman invariant/radiation>, constant/varying, regular(plane)/spectrum(JONSWAP),
$ ---- wave height, period, direction(commonly from E, CCW) SERIES 'Solitwave.bnd'
$ ---- Saat ini dinonaktifkan
$ BOU SIDE N CCW BTYPE SOMMERFELD
$ BOU SIDE E CCW BTYPE SOMMERFELD
BOU SIDE W CCW BTYPE SOMMERFELD
$ BOU SIDE S CCW BTYPE SOMMERFELD
$
$ ---- SPONGE LAYER % only 1 dx or 185 m (this one could work, altough reflect some)
$ ---- Saat ini dinonaktifkan
$ SPONGE N 185.
$ SPONGE E 185.
$ SPONGE W 185.
$ SPONGE S 185.
$ ---- physical setting : BREAK = breaking activated, NONHYDROSTATIC = nonhydrostatic activated
BREAK
$ NONHYDROSTATIC
$ DISCRET CORRDEP FIRST
$
$************ OUTPUT REQUESTS *************************
$ ---- extract at specific locations :
POINT 'GAUGE' FILE '../BP_input.txt'
TABLE 'GAUGE' HEADER 'DATA_INPUT.txt' TSEC WATL VEL OUTPUT 000000.000 30 SEC
$
POINT 'POIN' FILE '../BP_target.txt'
TABLE 'POIN' HEADER 'DATA_TARGET.txt' TSEC WATL VEL OUTPUT 000000.000 30 SEC
$
$ ---- extract for a whole domain for specific variable (WATL = water level)
$ ---- group : must be 'COMPGRD' index of xmin, index of xmax, index of ymin, index of ymax
$ ---- Saat ini dinonaktifkan
GROUP 'COMPGRD' 1 380 1 120
BLOCK 'COMPGRD' NOHEAD 'BASE01.mat' LAY 3 XP YP BOTL OUTPUT 000000.000 99999 SEC
BLOCK 'COMPGRD' NOHEAD 'MAIN01.mat' LAY 3 WATL OUTPUT 000000.000 30 SEC
BLOCK 'COMPGRD' NOHEAD 'MAIN02.mat' LAY 3 VEL OUTPUT 000000.000 30 SEC
$
TEST 1,0
$ compute from 0 sec with dt = 0.5 sec for 10 min 0 sec (= 600 sec)
COMPUTE 000000.000 0.5 SEC 001000.000
STOP
	"""

number = 100

array_x0 = np.random.uniform(low=6000, high=29000, size=(number,))
array_y0 = np.random.uniform(low=3000, high=9000, size=(number,))
array_a0 = np.random.uniform(low=1, high=1.5, size=(number,))
array_a1 = np.random.uniform(low=1, high=1.5, size=(number,))
array_rx = np.random.uniform(low=800, high=1500, size=(number,))
array_ry = np.random.uniform(low=800, high=1500, size=(number,))
array_r0 = np.random.uniform(low=0, high=30, size=(number,))

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
    Nx = 381  # Number of x-grid
    Ny = 121  # Number of y-grid
    # disesuaikan dengan domain simulasi
    x = np.linspace(0, 33250, num=Nx)
    y = np.linspace(0, 13200, num=Ny)

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

    # plt.figure()
    # plt.pcolor(X, Y, eta)
    # plt.colorbar()
    # plt.show()

    print(case)
    os.mkdir(str(case))
    np.savetxt(str(case)+'/initial_gaussian_'+str(case)+'.txt',
                eta, fmt='%1.2e')

    file_swash = open(str(case)+"/swash_"+str(case)+".sws", "w+")
    file_swash.write(swash_input(str(case)))

case = 0

for i in range(number):
    case += 1

    path = str(case)
    command = 'swashrun -input swash_'+path
    p = subprocess.call(command,cwd=path,shell=True)
