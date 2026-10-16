import numpy as np
import matplotlib.pyplot as plt
from numba import njit

# parameters
tmax = 100000
visc = 0.01
Lx = 400
Ly = 100
force = 4e-6

tau = 3.0*visc + 0.5
Q = 9

# arrays
f = np.zeros((Ly, Lx, Q))
f_new = np.zeros((Ly, Lx, Q))   # <-- novo buffer

Ux = np.zeros((Ly, Lx))
Uy = np.zeros((Ly, Lx))
Dens = np.ones((Ly, Lx))
Obst = np.ones((Ly, Lx))

Y, X = np.mgrid[0:Ly, 0:Lx]

w = np.array([4.0/9.0, 1.0/9.0, 1.0/9.0, 1.0/9.0, 1.0/9.0,
              1.0/36.0, 1.0/36.0, 1.0/36.0, 1.0/36.0])

ex = np.array([0, 1, 0, -1, 0, 1, -1, -1, 1])
ey = np.array([0, 0, 1, 0, -1, 1, 1, -1, -1])
kinv = np.array([0, 3, 4, 1, 2, 7, 8, 5, 6])

@njit
def feq(k, dens, ux, uy):
    cu = ex[k]*ux + ey[k]*uy
    return w[k]*dens*(1.0 + 3.0*cu + 4.5*cu*cu - 1.5*(ux*ux + uy*uy))

@njit
def init(Ux, Uy, Dens, Obst, f):
    for j in range(Ly):
        for i in range(Lx):
            Ux[j, i] = 0.0
            Uy[j, i] = 0.0
            Dens[j, i] = 1.0
            if ((i - Lx/4)**2 + (j - Ly/2)**2 <= (Ly/8)**2) | (j==0) | (j==Ly-1):
                Obst[j, i] = 1
            else:
                Obst[j, i] = 0
            for k in range(Q):
                f[j, i, k] = feq(k, Dens[j, i], Ux[j, i], Uy[j, i])

@njit
def macro(f, Dens, Ux, Uy):
    for j in range(Ly):
        for i in range(Lx):
            dens = 0.0
            ux = 0.0
            uy = 0.0
            for k in range(Q):
                val = f[j, i, k]
                dens += val
                ux += val * ex[k]
                uy += val * ey[k]
            Dens[j, i] = dens
            Ux[j, i] = ux / dens
            Uy[j, i] = uy / dens

@njit
def collision(f, Dens, Ux, Uy):
    for j in range(Ly):
        for i in range(Lx):
            for k in range(Q):
                eq = feq(k, Dens[j, i], Ux[j, i] + force*tau, Uy[j, i])
                f[j, i, k] += (eq - f[j, i, k]) / tau

@njit
def stream(f, f_new, Obst):
    for j in range(Ly):
        for i in range(Lx):
            for k in range(Q):
                iprev = (i - ex[k]) % Lx
                jprev = (j - ey[k]) % Ly
                if Obst[j, i] == 0:
                    f_new[j, i, k] = f[jprev, iprev, k]
                else:
                    f_new[j, i, k] = f[j, i, kinv[k]]

# main
init(Ux, Uy, Dens, Obst, f)

plt.ion()
fig, ax = plt.subplots()
vmod = np.sqrt(Ux**2 + Uy**2)
im = ax.imshow(vmod, cmap='jet', interpolation="bilinear")
cb = fig.colorbar(im, ax=ax, fraction=0.015, pad=0.04)

for t in range(tmax):
    collision(f, Dens, Ux, Uy)
    stream(f, f_new, Obst)
    f, f_new = f_new, f     # swap 
    macro(f, Dens, Ux, Uy)

    if t % 250 == 0:
        vmod = np.sqrt(Ux**2 + Uy**2)
        vmod = np.ma.masked_where(Obst == 1, vmod)
        im.set_data(vmod)
        vmin = 0.0
        vmax = vmod.max()
        im.set_clim(vmin, vmax) 
        plt.pause(0.001)

    # if t % 5000 == 0:
    #     vmod = np.sqrt(Ux**2 + Uy**2)
    #     vmod = np.ma.masked_where(Obst == 1, vmod)

    #     im=plt.imshow(vmod, interpolation="bilinear", cmap='jet')
    #     plt.streamplot(X, Y, Ux, Uy, density=1.5, color="w", linewidth=1.5)
    #     plt.colorbar(im)
    #     plt.tight_layout()
    #     plt.savefig(f"cylinder-{t}.pdf")
    #     plt.close()