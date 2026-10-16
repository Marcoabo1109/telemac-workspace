#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-
# Reads a tecplot particle .dat file and convert it into a paraview file
#
# A Joly
# 14/11/2014

# In ipython:
# To launch current file: - run ConvertDat2Vtu

# package utilises
import os # pour suivre des chemins dans un repertoire
import numpy as np # pour faire des maths

#%reset

######################################################
### Nom des fichiers
######################################################

tecplotFile = "alg_pos.dat"

######################################################
### Print header
######################################################
print("==========================")
print 'This script converts tecplot result file "%s"' % (tecplotFile)
print 'into a file that can be read by paraview'

# file folder
paraviewFile = tecplotFile.replace('.dat','')

print '\nFor each time step a file will be saved in folder "%s"' % (paraviewFile)
print 'Then load file "%s" in parview to visualize particles moving in time' % (paraviewFile+'.pvd')


######################################################
### Lire le fichier tecplot
######################################################
print("==========================")
print("Reading Tecplot file")
print("==========================")

Root = os.path.join('.')

# Read the time
t = []
with open(os.path.join('.',tecplotFile),'r') as datFile :
    for fline in datFile:
	fline = fline.strip()
	if 'SOLUTIONTIME' in fline :
	  data = fline.split('SOLUTIONTIME=')
	  t.append(float(data[1]))

Nt = len(t)
t = np.array(t,dtype=float)


# Find max number of particles
Np_max = 0


datFile = open(os.path.join('.',tecplotFile),'r')
fline = datFile.readline()
while fline != '' :
    fline = fline.strip()
    Np = 0
    if 'SOLUTIONTIME' in fline :
	data = fline.split(',')
	Np = data[2]
	Np = Np.split('=')
	Np = int(Np[1])
	fline = datFile.readline()
	Np_max = np.max((Np_max,Np))
	#stop
	#fline = datFile.readline()
	#fline = fline.strip()
	#data = fline.split(',')
	#Np = float(data[0])
	#fline = datFile.readline()
    else :
	fline = datFile.readline()
datFile.close()

print 'Number of time steps = %d, Number of particles = %d' % (Nt,Np_max)

######################################################
### Ecrire le fichier paraview
######################################################
print("==========================")
print("Writing Paraview result")
print("==========================")


# Define arrays

info = np.zeros([Np_max],dtype=int)
coord = np.zeros([Np_max,3],dtype=float)

Root_w = os.path.join('.',paraviewFile)

try:
	os.stat(Root_w)
except:
	os.mkdir(Root_w)

print 'Writing vtu particle files to folder "' +  paraviewFile + '"'

# pvd file
pvdFileName = paraviewFile + '.pvd'
pvdFile = open(os.path.join('.',pvdFileName),'w')
pvdFile.write('<?xml version="1.0"?>\n')
pvdFile.write(' <VTKFile type="Collection" version="0.1">\n')
pvdFile.write('  <Collection>\n')

#vtu file
datFile = open(os.path.join('.',tecplotFile),'r')
fline = datFile.readline()
while fline != '' :
    fline = fline.strip()
    Np = 0
    if 'SOLUTIONTIME' in fline :
	data = fline.split(',')
	Np = data[2]
	Np = Np.split('=')
	Np = int(Np[1])
	time = data[3]
	time = time.split('=')
	time = float(time[1])
	#
	it = np.searchsorted(t,time)
	vtuFileName = paraviewFile + '_%04d' % it + '.vtu'
	vtuFile = open(os.path.join(Root_w,vtuFileName),'w')
	print '=> writing file ' + os.path.join(Root_w,vtuFileName)
	vtuFile.write('<?xml version="1.0"?>\n')
	vtuFile.write('<VTKFile type= "UnstructuredGrid"' +
	    ' version= "0.1"  byte_order= "BigEndian">\n')
	vtuFile.write(' <UnstructuredGrid>\n')
	vtuFile.write('  <Piece NumberOfPoints="%d"' % Np +
	    ' NumberOfCells="%d">\n' % Np)
	# Write Id
	#vtuFile.write('   <PointData Scalars="Id" Vectors="Velocity">')
	vtuFile.write('   <PointData Scalars="Id">\n')
	vtuFile.write('    <DataArray type="Int32" Name="Id"' +
	    ' format="ascii">\n')
	for ip in xrange(Np) :
	    fline = datFile.readline()
	    fline = fline.strip()
	    data = fline.split(',')
	    vtuFile.write('%d\t' % (int(data[0])))
	    coord[ip,0] = float(data[1])
	    coord[ip,1] = float(data[2])
	vtuFile.write('\n')
	vtuFile.write('    </DataArray>\n')
	vtuFile.write('   </PointData>\n')
	# Write position
	vtuFile.write('   <Points>\n')
	vtuFile.write('    <DataArray type="Float32" NumberOfComponents="3"' +
	    ' format="ascii">\n')
	#vtuFile.close()
	#stop
	for ip in xrange(Np) :
	    fline = datFile.readline()
	    fline = fline.strip()
	    data = fline.split(',')
	    #vtuFile.write('%f\t%f\t%f\t' % 
		#(float(data[1]),float(data[2]),0))
	    vtuFile.write('%f\t%f\t%f\t' % 
		(coord[ip,0],coord[ip,1],coord[ip,2]))
	vtuFile.write('\n')
	vtuFile.write('    </DataArray>\n')
	vtuFile.write('   </Points>\n')
	vtuFile.write('   <Cells>\n')
	vtuFile.write('    <DataArray type="Int32"' +
	    ' Name="connectivity" format="ascii">\n')
	for ip in xrange(Np) :
	    vtuFile.write('%d\t' % ip)
	vtuFile.write('\n')
	vtuFile.write('    </DataArray>\n')
	vtuFile.write('    <DataArray type="Int32"' +
	    ' Name="offsets" format="ascii">\n')
	for ip in xrange(Np) :
	    vtuFile.write('%d\t' % (ip+1))
	vtuFile.write('\n')
	vtuFile.write('    </DataArray>\n')
	vtuFile.write('    <DataArray type="Int32"' +
	    ' Name="types" format="ascii">\n')
	for ip in xrange(Np) :
	    vtuFile.write('%d\t' % (1))
	vtuFile.write('\n')
	vtuFile.write('    </DataArray>\n')
	vtuFile.write('   </Cells>\n')
	vtuFile.write('  </Piece>\n')
	vtuFile.write(' </UnstructuredGrid>\n')
	vtuFile.write('</VTKFile>\n')
	vtuFile.close()
	#
	pvdFile.write('<DataSet timestep="%f"' % time +
	    ' group="" part="0" file="%s"/>\n' %
	    os.path.join(Root_w,vtuFileName))
	#
	fline = datFile.readline()
    else :
	fline = datFile.readline()
datFile.close()


pvdFile.write('   </Collection>\n')
pvdFile.write('  </VTKFile>\n')
pvdFile.close()
print 'Writing pvd file: "' +  pvdFileName + '"'
