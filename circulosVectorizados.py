import cv
import numpy as np


def channel_processing(channel):
    pass
    cv.AdaptiveThreshold(channel, channel, 255, adaptive_method=cv.CV_ADAPTIVE_THRESH_MEAN_C, thresholdType=cv.CV_THRESH_BINARY, blockSize=255, param1=25)
    #mop up the dirt
    cv.Dilate(channel, channel, None, 1)
    cv.Erode(channel, channel, None, 1)

def draw_circles(storage, output):
    circles = np.asarray(storage)
    cuadrados = []
    
    for circle in circles:
        Radius, x, y = int(circle[0][2]), int(circle[0][0]), int(circle[0][1])
        x1 = x - Radius
        x2 = x + Radius
        y1 = y - Radius
        y2 = y + Radius

        cuadrado = output[y1:y2, x1:x2]        
        cuadrados.append(cuadrado)
       
        #cv.Circle(output, (x, y), 1, cv.CV_RGB(0, 255, 0), -1, 8, 0)
        #cv.Circle(output, (x, y), Radius, cv.CV_RGB(255, 0, 0), 3, 8, 0)

        #para recortar los circulos

        cv.ShowImage("pic{:>05}".format(circle),cuadrado)
    
    return cuadrados

def moda(cuadrados):
  
    
    aux = 0
    cont = 0
    moda = -1
    cuadrados.sort(cmp=None, key=None, reverse=False)
    
    for i in range(0,len(cuadrados)-1):
        if (cuadrados[i] == cuadrados[i+1]):
            cont = cont + 1
            if cont >= aux:
                aux = cont
                moda = cuadrados[i]
        else:
            cont=0
 
    return moda
    
def modafinal (cuadrado):
    r,g,b= dividir(cuadrado)
    vr = vectorizar(r)
    vv = vectorizar(g)
    va = vectorizar(b)
    m_r = moda(vr)
    m_v = moda(vv)
    m_a = moda(va)  

    vaux = [m_r,m_v,m_a]
    return vaux    

def dividir (imagen):

    rojo = cv.CreateImage((imagen.width,imagen.height), cv.IPL_DEPTH_8U, 1)
    verde = cv.CreateImage((imagen.width,imagen.height), cv.IPL_DEPTH_8U, 1)
    azul= cv.CreateImage((imagen.width,imagen.height), cv.IPL_DEPTH_8U, 1)
    cv.Split(imagen,rojo,verde,azul,None)
    Ir = np.asarray(rojo[:,:])
    Iv = np.asarray(verde[:,:])
    Ia = np.asarray(azul[:,:])   
    return Ir,Iv,Ia

def vectorizar (vector):
    
    v = []
    for i in xrange(0,len(vector[0])-1):
        for j in xrange(0,len(vector[0])-1):        
            aux = vector[i][j]
            v.append(aux)
    return v

def conv_HSV (valores_rgb):
    
    valores_hsv = []
    for rgb_cord in valores_rgb:
        R_norm = rgb_cord[0] 
        G_norm = rgb_cord[1] 
        B_norm = rgb_cord[2] 
        Cmax = max(R_norm,G_norm,B_norm)
        Cmin = min(R_norm,G_norm,B_norm)
        Delta = Cmax - Cmin
        #Calculo de H
        if Delta == 0 :
            H = 0
        if Cmax == R_norm:
            H = 60 * (((float(G_norm) - float(B_norm)) / float(Delta)) % 6)
        if Cmax == G_norm:
            H = 60 * (((float(B_norm) - float(R_norm)) / float(Delta)) + 2)
        if Cmax == B_norm:
            H = 60 * (((float(R_norm) - float(G_norm)) / float(Delta)) + 4)

        #Calculo de S
        if Cmax == 0:
            S = 0
        else:
            S = (float(Delta) / float(Cmax))*100

        #Calculo de V
        V = float(Cmax)*100/255

        coordenadas = [H,S,V]
        valores_hsv.append(coordenadas)

    return valores_hsv
        



output = cv.LoadImage('sensor2.jpg')
orig = cv.LoadImage('sensor2.jpg')

# create tmp images
rrr=cv.CreateImage((orig.width,orig.height), cv.IPL_DEPTH_8U, 1)
ggg=cv.CreateImage((orig.width,orig.height), cv.IPL_DEPTH_8U, 1)
bbb=cv.CreateImage((orig.width,orig.height), cv.IPL_DEPTH_8U, 1)
processed = cv.CreateImage((orig.width,orig.height), cv.IPL_DEPTH_8U, 1)


storage = cv.CreateMat(orig.width, 1, cv.CV_32FC3)


#split image into RGB components
cv.Split(orig,rrr,ggg,bbb,None)
#process each componentsolar flare
channel_processing(rrr)
channel_processing(ggg)
channel_processing(bbb)
#combine images using logical 'And' to avoid saturation
cv.And(rrr, ggg, rrr)
cv.And(rrr, bbb, processed)
#cv.ShowImage('before canny', processed)


#use canny, as HoughCircles seems to prefer ring like circles to filled ones.
cv.Canny(processed, processed, 5, 70, 3)
#smooth to reduce noise a bit more
cv.Smooth(processed, processed, cv.CV_GAUSSIAN, 7, 7)
cv.ShowImage('processed', processed)

#find circles 
#escaner-1, escaner-2 ----> radiomax=115
#escaner-3, escaner-4 ----> radiomax=135
#3,4 ---------------------> radiomax=301
#1,2 ---------------------> radiomax=150
#sensor6.jpg--------------> radiomax=130
#para blanco 2 -----------> radiomax=250 (el param1 del umbral es 15)
#para morado -----------> radiomax= 135   (el param1 del umbral es 25)
#para sensor2 -----------> radiomax= 200   (el param1 del umbral es 25)

radiomax=200
cv.HoughCircles(processed, storage, cv.CV_HOUGH_GRADIENT, 2, 32, 100, radiomax)


cuadrados = draw_circles(storage, output)

# for x in xrange(0,len(cuadrados)):
moda_rojo=[]
moda_verde = []
moda_azul = []
circulo_rgb = []

for cuadrado in cuadrados:
    aux = modafinal(cuadrado)    
    moda_rojo.append(aux[2])
    moda_verde.append(aux[1])
    moda_azul.append(aux[0])
    v = [aux[2],aux[1],aux[0]]
    circulo_rgb.append(v)


#Obtenemos las coordenadas HSV
#H va en grados
#S va en %
#V va en %
circulo_hsv = conv_HSV(circulo_rgb)
print circulo_rgb
print circulo_hsv



cv.ShowImage('asdf',output)
    





    
     




cv.WaitKey(0)