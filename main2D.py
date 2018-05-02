# -*- coding: utf-8 -*-

import numpy as np
import math
import scipy.constants
import time
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from PIL import Image

# ==== Preamble ===============================================================
c0   = scipy.constants.speed_of_light
mu0  = scipy.constants.mu_0
eps0 = scipy.constants.epsilon_0
imp0 = math.sqrt(mu0 / eps0)
filename = "perita.png"
epsrel_pera = 2.8

L         = 10.0
dx        = 0.05
dy        = 0.05
finalTime = 1.5*L/c0
cfl       = .99
omega     = 1e8

totalFieldBox_lim = np.array((L*1./4., L*3./4.))
totalFieldBox_len = totalFieldBox_lim[1] - totalFieldBox_lim[0]

delay  = 8e-9
spread = 2e-9


# Box limits
xini = 40
xfin = 160
yini = 20
yfin = 180 

def gaussianFunction(x, x0, spread):
    # Cast function to a numpy array
    x = x*np.ones(1, dtype=float)
    gaussian = np.zeros(x.size, dtype=float)
    for i in range(x.size):
        gaussian[i] = np.exp( - np.power(x[i] - x0, 2) /
                                  (2.0 * np.power(spread, 2)) )
    return gaussian

def gaussian(x, tiempo, omega, c0, desfase=0):
    # Cast function to a numpy array
    x = x*np.ones(1, dtype=float)
    gaussian = np.exp(
            - np.power(-x/c0 + tiempo - desfase, 2) /
            (2.0 * np.power(spread, 2)) )
#    gaussian = np.zeros(x.size, dtype=float)
#    for i in range(x.size):
#        gaussian[i] = np.exp(
#                - np.power(-x/c0 + tiempo - desfase, 2) /
#                (2.0 * np.power(spread, 2)) )
    return gaussian

def planewave(x, tiempo, omega, c0, desfase=0):
    y = np.sin((omega/c0)*x - omega*tiempo + desfase)
    return y


# ==== Inputs / Pre-processing ================================================ 
# ---- Problem definition -----------------------------------------------------


# Ilumination properties
delay  = 5e-9
spread = 2e-9


gridEXX = np.linspace(0,      L,        num=L/dx+1, endpoint=True)
gridEXY = np.linspace(dy/2.0, L-dy/2.0, num=L/dy,   endpoint=True)
gridEYX = np.linspace(dx/2.0, L-dx/2.0, num=L/dx,   endpoint=True)
gridEYY = np.linspace(0,      L,        num=L/dy+1, endpoint=True)
gridHZX = np.linspace(dx/2.0, L-dx/2.0, num=L/dx,   endpoint=True)
gridHZY = np.linspace(dy/2.0, L-dy/2.0, num=L/dy,   endpoint=True)

# ---- Materials --------------------------------------------------------------

# ---- Boundary conditions ----------------------------------------------------
 
# ---- Sources ----------------------------------------------------------------

 
# ---- Output requests --------------------------------------------------------
samplingPeriod = 0.0
 
# ==== Processing =============================================================
# ---- Solver initialization --------------------------------------------------
dt = cfl * dx / c0 / math.sqrt(2)
numberOfTimeSteps = int( finalTime / dt )

if samplingPeriod == 0.0:
    samplingPeriod = dt 
nSamples  = int( math.floor(finalTime/samplingPeriod) )
probeH    = np.zeros((gridHZX.size, gridHZY.size, nSamples))
probeTime = np.zeros(nSamples) 

exOld = np.zeros((gridEXX.size, gridEXY.size), dtype=float)
exNew = np.zeros((gridEXX.size, gridEXY.size), dtype=float)
eyOld = np.zeros((gridEYX.size, gridEYY.size), dtype=float)
eyNew = np.zeros((gridEYX.size, gridEYY.size), dtype=float)
hzOld = np.zeros((gridHZX.size, gridHZY.size), dtype=float)
hzNew = np.zeros((gridHZX.size, gridHZY.size), dtype=float)

if 'initialH' in locals():
    hzOld = initialH

# Determines recursion coefficients
gridEXX = np.linspace(0,      L,        num=L/dx+1, endpoint=True)
gridEXY = np.linspace(dy/2.0, L-dy/2.0, num=L/dy,   endpoint=True)
gridEYX = np.linspace(dx/2.0, L-dx/2.0, num=L/dx,   endpoint=True)
gridEYY = np.linspace(0,      L,        num=L/dy+1, endpoint=True)
gridHZX = np.linspace(dx/2.0, L-dx/2.0, num=L/dx,   endpoint=True)
gridHZY = np.linspace(dy/2.0, L-dy/2.0, num=L/dy,   endpoint=True)

cExcom = dt / eps0 / dx
cEycom = dt / eps0 / dy
cHxcom = dt / mu0  / dx
cHycom = dt / mu0  / dy

cEx = np.ones((int(L/dx + 1), int(L/dy)))*cExcom
cEy = np.ones((int(L/dx), int(L/dy +1) ))*cEycom
cHx = np.ones((int(L/dx), int(L/dy)))*cHxcom
cHy = np.ones((int(L/dx), int(L/dy)))*cHycom

# Abre y convierte la imagen a blanco y negro
im = Image.open(filename).convert('1', dither=Image.NONE)
# Cambia el tamaño
im = im.resize([yfin - yini + 1, xfin - xini + 1], Image.ANTIALIAS)
# Pasa a array de numpy
figure_array = np.logical_not(np.array(im))

# Update permitivities
(cEx[xini:xfin + 1, yini:yfin + 1])[figure_array] = cExcom/epsrel_pera
(cEy[xini:xfin + 1, yini:yfin + 1])[figure_array] = cEycom/epsrel_pera


# ---- Time integration -------------------------------------------------------
print('--- Processing starts---')
tic = time.time();

t = 0.0
for n in range(numberOfTimeSteps):
    # --- Updates E field --- (diferencias regresivas)
    for i in range(1, gridEXX.size-1):
        for j in range(0, gridEXY.size):
            exNew[i][j] = exOld[i][j] + cEy[i][j] * (hzOld[i][j] - hzOld[i  ][j-1])
  
    for i in range(0, gridEYX.size):
        for j in range(1, gridEYY.size-1):
            eyNew[i][j] = eyOld[i][j] - cEx[i][j] * (hzOld[i][j] - hzOld[i-1][j  ])
  
  
    for j in range(yini, yfin+1):           
        eyNew[xini][j] += gaussian(xini*dx, dt*n, omega, c0, desfase=delay)
        if n*dt >= (xfin-xini)*dx/c0:
            eyNew[xfin][j] -= gaussian(xfin*dx, dt*n, omega, c0, desfase=delay)
    for i in range(xini, xfin+1):           
        if n*dt >= (i-xini)*dx/c0:
            # Engañamos a la 1a dentro para que parezca que la onda sigue a la izq.
            exNew[i][yini] = exOld[i][yini] + cEy[i][j] * (hzOld[i][yini] - (hzOld[i  ][yini-1] + gaussian((i+1)*dx, dt*n, omega, c0, desfase=delay)/imp0))
            # (sim.) Cambiamos a dif. progresivas y engañamos a la ultima dentro para que parezca que la onda sigue a la dcha.
            #exNew[i][yfin] = exOld[i][yfin] + cEy * ((hzOld[i][yfin+1] + gaussian((i-1)*dx, dt*n, omega, c0, desfase=delay)/imp0) - hzOld[i  ][yfin] )
            # Engañamos a la primera fuera para que ignore la onda a la izq.
            exNew[i][yfin+1] = exOld[i][yfin+1] + cEy[i][j] * (hzOld[i][yfin+1] - (hzOld[i  ][yfin+1-1] - gaussian((i+1)*dx, dt*n, omega, c0, desfase=delay)/imp0))
            # (sim.) Cambiamos a dif. progesivas y engañamos a la ultima fuera para que ignore la onda a la dcha.
            #exNew[i][yini-1] = exOld[i][yini-1] + cEy * ((hzOld[i][yini] - gaussian((i-1)*dx, dt*n, omega, c0, desfase=delay)/imp0) - hzOld[i  ][yini-1] )
            

    # E field boundary conditions
    
    # PEC
    exNew[ :][ 0] = 0.0;
    exNew[ :][-1] = 0.0;
    eyNew[ 0][ :] = 0.0;
    eyNew[-1][ :] = 0.0;  

    # --- Updates H field --- (dif. progeresivas)
    for i in range(gridHZX.size-1):
        for j in range(gridHZX.size-1):
            hzNew[i][j] = hzOld[i][j] - cHx[i][j] * (eyNew[i+1][j  ] - eyNew[i][j]) +\
                                        cHy[i][j] * (exNew[i  ][j+1] - exNew[i][j])
        
    for j in range(yini, yfin+1):                 
        hzNew[xini-1][j] +=gaussian(xini*dx, dt*n, omega, c0, desfase=delay)/imp0
        if n*dt >= (xfin-xini)*dx/c0:
            hzNew[xfin-1][j] -= gaussian(xfin*dx, dt*n, omega, c0, desfase=delay)/imp0

    # TODO ESTO PARA NADA
#    for i in range(xini, xfin+1):           
#        if n*dt >= (i-xini)*dx/c0:
            # (sim.) Cambiamos a regresivas en la 1a dentro y engañamos para que crea que hay onda a la izq.
            #hzNew[i][yini] = (hzOld[i][yini] - cHx * ( eyNew[i][yini ] -  (eyNew[i-1][yini] + gaussian((i-1)*dx, dt*n, omega, c0, desfase=delay))) +\
            #        cHy * (exNew[i  ][yini] - exNew[i][yini-1]))
            # Engañamos a la ultima dentro para que crea que hay onda a la dcha.
#            hzNew[i][yfin] = (hzOld[i][yfin] - cHx * ((eyNew[i+1][yfin  ] + gaussian((i+1)*dx, dt*n, omega, c0, desfase=delay)) - eyNew[i][yfin]) +\
#                    cHy * (exNew[i  ][yfin+1] - exNew[i][yfin]))
            # Engañamos a la ultima fuera para piense que a la dcha no hay onda
#            hzNew[i][yini-1] = (hzOld[i][yini-1] - cHx * ((eyNew[i+1][yini-1 ] + gaussian((i+1)*dx, dt*n, omega, c0, desfase=delay)) - eyNew[i][yini-1]) +\
#                    cHy * (exNew[i  ][yini] - exNew[i][yini-1]))
            # (sim.) Cambiar a regresivas y engañar a la primera fuera para que piense que a su izq no hay onda
            #hzNew[i][yfin+1] = (hzOld[i][yfin+1] - cHx * ( eyNew[i][yfin+1 ] -  (eyNew[i-1][yfin+1] - gaussian((i-1)*dx, dt*n, omega, c0, desfase=delay))) +\
            #        cHy * (exNew[i  ][yfin+1] - exNew[i][yfin]))


      
    # --- Updates output requests ---
    probeH[:,:,n] = hzNew[:,:]
    probeTime[n] = t
    
    # --- Updates fields and time 
    exOld[:] = exNew[:]
    eyOld[:] = eyNew[:]
    hzOld[:] = hzNew[:]
    t += dt
    print ("Time step: %d of %d" % (n, numberOfTimeSteps-1))

tictoc = time.time() - tic;
print('--- Processing finished ---')
print("CPU Time: %f [s]" % tictoc)

# ==== Post-processing ========================================================

# --- Creates animation ---
fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)
#ax = plt.axes(xlim=(gridE[0], gridE[-1]), ylim=(-1.1, 1.1))
ax.set_xlabel('Y coordinate [m]')
ax.set_ylabel('X coordinate [m]')
line = plt.imshow(probeH[:,:,0], animated=True, vmin=-1e-3, vmax=1e-3)
timeText = ax.text(0.02, 0.95, '', transform=ax.transAxes)

def init():
    line.set_array(probeH[:,:,0])
    timeText.set_text('')
    return line, timeText

def animate(i):
    line.set_array(probeH[:,:,i])
    
    # Trampa para visualizar la onda teorica
    #auxprobeH = probeH[:,:,i]
    #auxprobeH[:,yini-8] = gaussian(gridHX, dt*i, omega, c0, desfase=delay)/imp0
    #auxprobeH[:,yini-7] = auxprobeH[:,yini-8]
    #auxprobeH[:,yini-6] = auxprobeH[:,yini-8]
    #line.set_array(auxprobeH[:,:])

    line.set_array(probeH[:,:,i])
    timeText.set_text('Time = %2.1f [ns]' % (probeTime[i]*1e9))
    return line, timeText

anim = animation.FuncAnimation(fig, animate, init_func=init,
                               frames=nSamples, interval=50, blit=True)

plt.show()

print('=== Program finished ===')
