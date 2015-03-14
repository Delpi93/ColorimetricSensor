import cv
import numpy as np

def channel_processing(channel):
    cv.AdaptiveThreshold(channel, channel, 255, adaptive_method=cv.CV_ADAPTIVE_THRESH_MEAN_C, thresholdType=cv.CV_THRESH_BINARY, blockSize=255, param1=25)
    cv.Dilate(channel, channel, None, 1)
    cv.Erode(channel, channel, None, 1)

def get_circles(storage, output):
    circles = np.asarray(storage)
    roi = []
    
    for circle in circles:
        Radius, x, y = int(circle[0][2]), int(circle[0][0]), int(circle[0][1])
        # con relaciones trigonometricas sacamos el cuadrado inscrito en el circulo suponemos que el angulo es de 45 grados
        b = int(Radius * 0.7071)
        xb1 = x - b
        xb2 = x + b
        yb1 = y - b
        yb2 = y + b


        cut = output[yb1:yb2, xb1:xb2]        
        roi.append(cut)

        cv.ShowImage("pic{:>05}".format(circle),cut)
    
    return roi

def moda(roi):
  
    
    aux = 0
    cont = 0
    moda = -1
    roi.sort(cmp=None, key=None, reverse=False)
    
    for i in range(0,len(roi)-1):
        if (roi[i] == roi[i+1]):
            cont = cont + 1
            if cont >= aux:
                aux = cont
                moda = roi[i]
        else:
            cont=0
 
    return moda
    
def modafinal (roi):
    r,g,b= dividir(roi)
    vr = vectorizar(r)
    vv = vectorizar(g)
    va = vectorizar(b)
    m_r = moda(vr)
    m_v = moda(vv)
    m_a = moda(va)  

    vaux = [m_r,m_v,m_a]
    return vaux    

def dividir (roi):

    rojo = cv.CreateImage((roi.width,roi.height), cv.IPL_DEPTH_8U, 1)
    verde = cv.CreateImage((roi.width,roi.height), cv.IPL_DEPTH_8U, 1)
    azul= cv.CreateImage((roi.width,roi.height), cv.IPL_DEPTH_8U, 1)
    cv.Split(roi,rojo,verde,azul,None)
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
        R = rgb_cord[0] 
        G = rgb_cord[1] 
        B = rgb_cord[2] 
        Cmax = max(R,G,B)
        Cmin = min(R,G,B)
        Delta = Cmax - Cmin
        #Calculo de H
        if Delta == 0 :
            H = 0
        if Cmax == R:
            H = 60 * (((float(G) - float(B)) / float(Delta)) % 6)
        if Cmax == G:
            H = 60 * (((float(B) - float(R)) / float(Delta)) + 2)
        if Cmax == B:
            H = 60 * (((float(R) - float(G)) / float(Delta)) + 4)

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
        



output = cv.LoadImage('sensor4.jpg')
orig = cv.LoadImage('sensor4.jpg')

# Creamos los canales r g b
rrr=cv.CreateImage((orig.width,orig.height), cv.IPL_DEPTH_8U, 1)
ggg=cv.CreateImage((orig.width,orig.height), cv.IPL_DEPTH_8U, 1)
bbb=cv.CreateImage((orig.width,orig.height), cv.IPL_DEPTH_8U, 1)
processed = cv.CreateImage((orig.width,orig.height), cv.IPL_DEPTH_8U, 1)


storage = cv.CreateMat(orig.width, 1, cv.CV_32FC3)

#dividimos la imagen en canales
cv.Split(orig,bbb,ggg,rrr,None)
#procesamos cada canal por separado
channel_processing(rrr)
channel_processing(ggg)
channel_processing(bbb)
#volvemos a combinarlos
cv.And(rrr, ggg, rrr)
cv.And(rrr, bbb, processed)

#Obtenemos las fronteras
cv.Canny(processed, processed, 5, 70, 3)
#Suavizamos
cv.Smooth(processed, processed, cv.CV_GAUSSIAN, 7, 7)

#find circles 
#escaner-1, escaner-2 ----> radiomax=115
#escaner-3, escaner-4 ----> radiomax=135
#3,4 ---------------------> radiomax=301
#1,2 ---------------------> radiomax=150
#sensor6.jpg--------------> radiomax=130
#para blanco 2 -----------> radiomax=250 (el param1 del umbral es 15)
#para morado -----------> radiomax= 135   (el param1 del umbral es 25)
#para sensor2 -----------> radiomax= 200   (el param1 del umbral es 25)
#para sensor2 -----------> radiomax= 220  (el param1 del umbral es 25)

radiomax=220
cv.HoughCircles(processed, storage, cv.CV_HOUGH_GRADIENT, 2, 32, 100, radiomax)


rois = get_circles(storage, output)

moda_rojo=[]
moda_verde = []
moda_azul = []
circulo_rgb = []

for roi in rois:
    aux = modafinal(roi)    
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
#print circulo_hsv

cv.ShowImage('asdf',output)
    
cv.WaitKey(0)