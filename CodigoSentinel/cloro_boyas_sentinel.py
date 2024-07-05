import csv
import os
import numpy as np
import cv2
import tifffile as tiff
import statistics
import math

def media_con_vecinos(matriz, fila, columna):
    filas = len(matriz)
    columnas = len(matriz[0])
    vecinos = []

    # Recorrer las posiciones alrededor del punto (fila, columna)
    for i in range(max(0, fila-1), min(filas, fila+2)):
        for j in range(max(0, columna-1), min(columnas, columna+2)):
            vecinos.append(matriz[i][j])

    # Calcular la media de los valores en vecinos
    return sum(vecinos) / len(vecinos)

def mediana_con_vecinos(matriz, fila, columna):
    filas = len(matriz)
    columnas = len(matriz[0])
    vecinos = []

    # Recorrer las posiciones alrededor del punto (fila, columna)
    for i in range(max(0, fila-1), min(filas, fila+2)):
        for j in range(max(0, columna-1), min(columnas, columna+2)):
            vecinos.append(matriz[i][j])

    # Calcular la media de los valores en vecinos
    return statistics.median(vecinos)

def apply_form(data):
    index = []
    for i in range(0, len(data)):
        for j in range(0, len(data[i])):
            B = data[i][j]
            #result = 194.79 * (data[i][j][4] * (data[i][j][4] / data[i][j][1])) + 0.9061
            #result = 19.866 * math.pow(data[i][j][4] / data[i][j][3], 2.3051)
            #result = math.pow(10, -2.4792 * math.log10(max(data[i][j][2], data[i][j][1]) / data[i][j][2]) - 0.0389)
            #result = 124.94*(B[2] + B[4])/(B[2] + B[3]) - 115.35 # Soria-F1
            #result = 124.94 * (B[2] + B[3]) / (B[2] + B[4]) - 115.35  # INVERTED Soria-F1

            #result = (B[4]-B[5]) / (B[3] - B[5])    # F3 Soria
            result = (B[2] + B[4]) / (B[2] + B[3])  # SIMPLE Soria-F1
            #result = 32.448 * (B[4]/B[3]) - 21.408
            #result = 14.039 + 86.11 * ((B[4] - B[3])/(B[5] + B[3])) + 194.325 * ((B[4] - B[3])/(B[4] + B[3])**2)

            #result = 19.866 * (B[4]/B[3])**2.3051
            #result = math.pow(10, -2.4792 * math.log10(max(B[2], B[1]) / B[2]) - 0.0389)

            #result = B[4]-((0.74-0.705)/(0.74-0.665))*B[3]-(1.0-(0.74-0.705)/(0.74-0.665))*B[5]

            index.append(result)

    return index

def get_points(allbands, fecha):
    #index5 = 194.79 * (samples.B05 * (samples.B05 / samples.B02)) + 0.9061
    result = []
    x = np.array([453, 370, 443, 601, 696, 476, 215, 345, 343, 476, 685, 460])
    y = np.array([87, 373, 372, 450, 500, 668, 633, 748, 915, 969, 997, 806])

    #allbands = allbands[0]
    data = apply_form(allbands)
    data = np.reshape(data, (1167, 891))

    for i in range(0, len(x)):
        #print("En la boya ", i+1, " (", x[i], ",", y[i], ")")
        pixel = data[y[i]][x[i]]
        media = media_con_vecinos(data, y[i], x[i])
        mediana = mediana_con_vecinos(data, y[i], x[i])
        boya = [fecha, pixel, media, mediana]
        result.append(boya)

    return result

def crear_csv(archivo_csv, datos):
    encabezados = ['Fecha', 'Pixel', 'Media', 'Mediana']
    with open(archivo_csv, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(encabezados)
        writer.writerows(datos)

def clorofila_boyas_sentinel(allbands_dir):

    boyas = [[],[],[],[],[],[],[],[],[],[],[],[]]

    # Coge del csv las fechas que tienes que explorar:
    with open('dates-sentinelANDboyas-l2a-cloudless.csv', mode='r') as archivo:
        lector_csv = csv.reader(archivo)

        # Itera sobre cada fila en el archivo CSV
        fila = next(lector_csv)


    for f in fila:
        for archivo in os.listdir(allbands_dir):
            fecha = archivo[:-5]
            if f != fecha:
                continue
            print(fecha)
            img_dir = allbands_dir + archivo
            imagen = tiff.imread(img_dir)
            cloro_boyas = get_points(imagen, fecha)

            for i in range(0, 12):
                boyas[i].append(cloro_boyas[i])


    for i in range(0, 12):
        resultado_csv = 'cloro-csv-l2a-F1-Soria-SIMPLE/' + 'CLORO-E' + str(i+1)
        crear_csv(resultado_csv, boyas[i])


"""x = np.array([453, 370, 443, 601, 696, 476, 215, 345, 343, 476, 685, 460])
y = np.array([91, 373, 372, 450, 500, 668, 633, 748, 915, 969, 997, 806])

foto = cv2.imread('truecolor-dated-l2a/2017-06-30.png')

key = 0
cv2.namedWindow("foto")
while (key != ord('n')):
    key = cv2.waitKey(33)
    for i in range(0, len(x)):
        cv2.circle(foto, (x[i], y[i]), 1, (0, 0, 255), -1)
    cv2.imshow('foto', foto)"""


clorofila_boyas_sentinel('allbands-dated-l2a/')