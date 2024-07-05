import csv
import datetime
import os

import matplotlib.pyplot as plt
import numpy as np
import imageio
import request as req
from datetime import  datetime
from datetime import timedelta
import statistics
import json
import shutil
import math
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session


from sentinelhub import (
    CRS,
    BBox,
    DataCollection,
    DownloadRequest,
    MimeType,
    MosaickingOrder,
    SentinelHubDownloadClient,
    SentinelHubRequest,
    bbox_to_dimensions,
    SHConfig
)


import cv2
# Bi1k4S{Bi1k4S{
# ClientID: aaae3095-e322-4e39-b6e5-5a60804612b4
# ClientSecret: Gp7dEKeUjNb4PYmImO0EKkhgOkQSRPIb


# ClientID: 5f393561-3426-4e35-b688-0e90c1f9961c
# ClientSecret: 3o3fKJtaeyukVbMHX3BXRQ07wdPF3QLq

# ClientID: 71fdd235-0292-44e0-ad50-bacbea87ca59
# ClientSecret: QwPaaAVx89lyY8ZiHWbnA9g2ViUbC0MS

# tigre_coords = (-58.619785,-34.449317,-58.538761,-34.393029)
# la_coords = (-0.889549,37.621846,-0.681152,37.828226)
# betsiboka_coords_wgs84 = (46.16, -16.15, 46.51, -15.58)
# lebna_coords = (10.852947,36.726502,10.945816,36.788804)

# Sentinel2 tiene:
#   4 bandas con 10m de resolución
#   6 bandas con 20m de resolución
#   3 bandas con 60m de resolución
#       Usadas para avistamiento de nubes



def move_files(src, dst, dirFotos, date):
    if not os.path.exists(dst):
        os.makedirs(dst)

    for item in os.listdir(src):
        src_path = os.path.join(src, item)
        dst_path = os.path.join(dst, item)

        if os.path.isdir(src_path):
            move_files(src_path, dst_path)
        else:
            shutil.copy2(src_path, dst_path)
        if (item == 'response.tiff' or item == 'response.png'):
            dst_path = dirFotos
            if (item == 'response.tiff'):
                newName = os.path.join(src, date) + '.tiff'
            else:
                newName = os.path.join(src, date) + '.png'
            os.rename(src_path, newName)
            shutil.copy(newName, dst_path)




def imgs_to_video(arrays_imagenes, nombre_video, fps):
    # Obtener el número de frames, altura y ancho de las imágenes
    # num_frames, altura, ancho, _ = arrays_imagenes.shape
    num_frames = len(arrays_imagenes)
    # Definir el objeto VideoWriter
    writer = imageio.get_writer(nombre_video)#, fps)

    # Iterar sobre los arrays de imágenes y escribir cada frame en el video
    for i in range(num_frames):
        frame = arrays_imagenes[i]
        writer.append_data(frame)

    # Cerrar el objeto VideoWriter
    writer.close()

def video_from_sentinel(evalscript, config, bbox, size, firstDay, lastDay):
    # TODO: hacer un bucle que pida imágenes sumando 7 días al rango de fechas para cada petición.
    # Si lo hago con el mosaico de least cloudy adquisitions tendré entre una y dos fotos por semana
    # y con la menor cantidad de nubes posible para poder ver la evolución del mar menor.

    # Array para guardar las imágenes de Sentinel. Primero las pido todas de golpe y después genero el vídeo. Así evito
    # tener al writer esperando a las descargas de red.
    imagenes = []

    # Fecha de inicio de la captura:
    # firstDay = 736178 # Tenemos datos de boyas desde este día, pero Sentinel no tiene imágenes desde ese día

    # Fecha con el offset para poder avanzar las semanas
    dateWithOffset = firstDay;

    # Fecha tope como número
    # todayAsNumber = datetime.now().toordinal()

    while dateWithOffset <= lastDay:
        # Pido la imagen del día que corresponde a Sentinel
        dateWithOffsetAsDate = datetime.fromordinal(dateWithOffset).date()
        imagenes.append(req.request(evalscript, dateWithOffsetAsDate, config, bbox, size).get_data(save_data=True))

        # Pasa una semana
        dateWithOffset += 7


    # TODO: Ahora hay que cambiar el orden de los píxeles, que OpenCV los coge como BGR

    for img in range(0, len(imagenes)):
        for i in range(0, len(imagenes[0][0])):
            for j in range(0, len(imagenes[0][0][0])):
                aux = imagenes[img][0][i][j][0]
                imagenes[img][0][i][j][0] = imagenes[img][0][i][j][2]
                imagenes[img][0][i][j][2] = aux



    # TODO: Bucle para guardar las imágenes en el vídeo
    writer = cv2.VideoWriter('video_salida.mp4', cv2.VideoWriter_fourcc(*'mp4v'), 5, (size[0], size[1]))
    for i in range(0, len(imagenes)):
        # Escribimos el fotograma en el video
        u = np.array(imagenes[i][0])
        writer.write(u)

    # Liberamos el objeto VideoWriter
    writer.release()

def image_from_sentinel(evalscript, config, bbox, size, date):
    req.request(evalscript, date, config, bbox, size).get_data(save_data=True)

    # TODO: 0 = buena imagen
    # TODO: 1 = demasiado nubosa
    # TODO: 2 = no se aprecia bien el parámetro
    status = 0
    return status

def get_points(allbands):
    #index5 = 194.79 * (samples.B05 * (samples.B05 / samples.B02)) + 0.9061
    print("En getPoints")
    x = np.array([453, 370, 443, 601, 696, 476, 215, 345, 343, 476, 685, 460])
    y = np.array([87, 373, 372, 450, 500, 668, 633, 748, 915, 969, 997, 806])
    print(len(allbands))
    allbands = allbands[0]
    print(len(allbands))
    print(allbands[y[0]][x[0]])

    data = apply_form(allbands)
    data = np.reshape(data, (1167, 891))
    print(len(data))
    print(len(data[0]))


    for i in range(0, len(x)):
        print("En la boya ", i+1, " (", x[i], ",", y[i], ")")
        print(data[y[i]][x[i]])
        print("Media ", media_con_vecinos(data, y[i], x[i]))
        print("Mediana ", mediana_con_vecinos(data, y[i], x[i]))


    cv2.namedWindow("foto")
    cv2.namedWindow("foto2")
    key = 0
    foto = cv2.imread('mago.tiff')
    foto2 = cv2.imread('MAGO/2019-08-14--NTU-id5-[2, 6, 6.5, 7, 8, 10, 12]/response.tiff')
    cv2.setMouseCallback('foto', mouse_callback)
    cv2.setMouseCallback('foto2', mouse_callback)
    while (key != ord('n')):
        key = cv2.waitKey(33)
        for i in range(0, len(x)):
            cv2.circle(foto, (x[i], y[i]), 5, (0, 0, 255), -1)
        cv2.imshow('foto', foto)
        cv2.imshow('foto2', foto2)


def apply_form(data):
    index = []
    print("Datalen1 ", len(data))
    print("Datalen2 ", len(data[0]))
    grande = 0
    x = 0
    y = 0
    for i in range(0, len(data)):
        for j in range(0, len(data[i])):
            #result = 194.79 * (data[i][j][4] * (data[i][j][4] / data[i][j][1])) + 0.9061
            #result = 19.866 * math.pow(data[i][j][4] / data[i][j][3], 2.3051)
            #result = math.pow(10, -2.4792 * math.log10(max(data[i][j][2], data[i][j][1]) / data[i][j][2]) - 0.0389)

            result = 124.94*(data[i][j][2] + data[i][j][4])/(data[i][j][2] + data[i][j][3]) - 115.35

            index.append(result)
            if (result > grande):
                grande = result
                x = j
                y = i

    print("GRANDE: ", grande, "(", x, ",", y, ")")

    return index

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

def mouse_callback(event, x, y, flags, params):

    #right-click event value is 2
    if event == cv2.EVENT_LBUTTONDOWN:
        global right_clicks

        print([x, y])

def main():

    config = SHConfig()

    if not config.sh_client_id or not config.sh_client_secret:
        print("Warning! To use Process API, please provide the credentials (OAuth client ID and client secret).")

    client = BackendApplicationClient(client_id=config.sh_client_id)
    oauth = OAuth2Session(client=client)
    token = oauth.fetch_token(
    token_url='https://services.sentinel-hub.com/auth/realms/main/protocol/openid-connect/token', client_secret=config.sh_client_secret, include_client_id=True)
    resp = oauth.get("https://services.sentinel-hub.com/configuration/v1/wms/instances")
    print('\n\n')
    print(resp.content)
    print('\n\n')
    print(token)
    print('\n\n')
    coords = (-0.889549, 37.621846, -0.681152, 37.828226)


    resolution = 20
    bbox = BBox(bbox=coords, crs=CRS.WGS84)
    size = bbox_to_dimensions(bbox, resolution=resolution)
    print(f"Image shape at {resolution} m resolution: {size} pixels")

    firstDay = 736700
    lastDay = 737000

    mode = input("Escriba \"Video\" para hacer un vídeo o \"Imagen\" para obtener una imagen: ")
    mode = "Imagen"

    status = 0
    if (mode == "Video"):
        firstDay = input("Escriba la fecha de inicio (YY-MM-DD): ")
        lastDay = input(("Escriba la fecha final (YY-MM-DD): "))

        firstDay = datetime.strptime(firstDay, '%Y-%m-%d').toordinal()
        lastDay = datetime.strptime(lastDay, '%Y-%m-%d').toordinal()

        video_from_sentinel("video-mago", config, bbox, size, firstDay, lastDay)
    elif (mode == "Imagen"):
        date = input("Escriba la fecha de la foto (YY-MM-DD): ")
        date = datetime.strptime("2015-07-06", '%Y-%m-%d').date()

        with open('dates-sentinelANDboyas-l2a-cloudless.csv', 'r') as f_input:
            csv_reader = csv.reader(f_input)
            for row in csv_reader:
                for date in row:
                    date = datetime.strptime(date, '%Y-%m-%d').date()
                    req.request("allbands", date, config, bbox, size).get_data(save_data=True)

            """        with open('dates-sentinelANDboyas.csv', 'r') as f_input:
            csv_reader = csv.reader(f_input)
            for row in csv_reader:
                for d in row:

                    print(d)"""
        """
        start = datetime.strptime("2015-11-14", '%Y-%m-%d').date()
        end = datetime.strptime("2015-11-14", '%Y-%m-%d').date()
        often = 10
        ran = end.toordinal() - start.toordinal()
        ran = int(ran / often) + 1
        for i in range(0, ran):

            date = start + timedelta(days=i*often)

            print(ran)
            print(i)
            status = req.request("truecolor", date, config, bbox, size).get_data(save_data=True)
            get_points(status)
        """
        src = 'allbands/'
        justImages = 'allbands-dated-l2a/'
        for root, dirs, files in os.walk(src):
            if (root == src):
                continue

            json_path = os.path.join(root, 'request.json')
            with open(json_path, 'r') as json_file:
                data = json.load(json_file)
                time_range = data.get('request', {}).get('payload', {}).get('input', {}).get('data', [{}])[0].get(
                    'dataFilter', {}).get('timeRange', {})
                date_from_str = time_range.get('from')
                date_from_str = date_from_str.split('T')[0]

                newName = os.path.join(src, date_from_str)
                print(files[1])
                print(newName)
                print(root)
                move_files(root, newName, justImages, date_from_str)
                #shutil.rmtree(root)
        for root, dirs, files in os.walk(src):
            if (root == src):
                continue

        if (status != 0):
            # TODO: llamar a utils.py
            a = 0   # Pa que python se calle



if __name__ == '__main__':
    main()