from datetime import timedelta

import evalscripts as eva
import os
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
# Para ver cuántas fotos hay en un intervalo de fechas:
"""
curl -X POST "services.sentinel-hub.com/api/v1/catalog/search" \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJ3dE9hV1o2aFJJeUowbGlsYXctcWd4NzlUdm1hX3ZKZlNuMW1WNm5HX0tVIn0.eyJleHAiOjE3MTcxNDg0NjEsImlhdCI6MTcxNzE0NDg2MSwianRpIjoiOWNlZTlmNTYtOWRkYi00Yjk3LWI1MTYtNjFlYTc1Mzk3NDdjIiwiaXNzIjoiaHR0cHM6Ly9zZXJ2aWNlcy5zZW50aW5lbC1odWIuY29tL2F1dGgvcmVhbG1zL21haW4iLCJzdWIiOiI4ZTY1ODMxMS01Yjg1LTRmYzAtOWFjYi1jMmZjNjZkODVkMDMiLCJ0eXAiOiJCZWFyZXIiLCJhenAiOiI3MWZkZDIzNS0wMjkyLTQ0ZTAtYWQ1MC1iYWNiZWE4N2NhNTkiLCJzY29wZSI6ImVtYWlsIHByb2ZpbGUiLCJjbGllbnRIb3N0IjoiODguMjEuMjAuOTkiLCJjbGllbnRJZCI6IjcxZmRkMjM1LTAyOTItNDRlMC1hZDUwLWJhY2JlYTg3Y2E1OSIsImVtYWlsX3ZlcmlmaWVkIjpmYWxzZSwicHJlZmVycmVkX3VzZXJuYW1lIjoic2VydmljZS1hY2NvdW50LTcxZmRkMjM1LTAyOTItNDRlMC1hZDUwLWJhY2JlYTg3Y2E1OSIsImNsaWVudEFkZHJlc3MiOiI4OC4yMS4yMC45OSIsImFjY291bnQiOiI2MTc2NTM4NS1jYzNhLTQ3NTAtOTNlNS0wMjExMGJjYjEyOTkifQ.OlsRMYvI3O1Gz4RfgwBvy88TX4GLFrwa00W1TZlg6yfhBBaAEVFfTv872qznOSkK0cgqurGC6C_nJey9jj9kUhLXfgKwXO1cNiuWPm_SrlPx6vUfybFpykbYj1S72ZKQgOijEiPuopPiMPokAKdUUDSmHCnF4TSuSu6v6Kkgp-qkarl390tjywHp7Tp5rkSBKuFqJ5yOjHq43I4sxJlE7jthHkV1-5inqGHEmazgWh1FJLTrEFIjnIETsf8NnBp0v3ODJL2DYdbSVpivYRc6v6cVOTCswXLEbx_42CptsqIzHyYUpFcykpPxA10OagYb77AZE6xkxjS08cE6s5hR2g" \
     -d '{
           "bbox": [-0.889549, 37.621846, -0.681152, 37.828226],
           "datetime": "2015-01-01T00:00:00Z/2024-05-25T00:00:00Z",
           "collections": ["sentinel-2-l1c"],
           "limit": 50,
           "distinct": "date"
         }'
"""
# request -> string que indica el tipo de evalscript a utilizar en la petición a Sentinel
# date -> fecha de la toma de datos. Se le suman siete días para abarcar una semana de toma de imágenes, evitando así
# que que haya peticiones sin respuesta
# config -> configuración de la petición
# bbox -> área de la toma de fotos
# size -> tamaño de la foto
def request(request, date, config, bbox, size):
    print("En request.py")
    start = date;
    end = date + timedelta(days=10)
    if request == "truecolor":
       return  SentinelHubRequest(
            #data_folder="truecolor-all-images",
            data_folder="truecolor",
            evalscript=eva.evalscript_true_color,
            input_data=[
                SentinelHubRequest.input_data(
                    data_collection=DataCollection.SENTINEL2_L2A,
                    time_interval=(start, start),
                )
            ],
            responses=[SentinelHubRequest.output_response("default", MimeType.PNG)],
            bbox=bbox,
            size=size,
            config=config,
        )
    elif request == "allbands":
        return SentinelHubRequest(
            data_folder="allbands",
            evalscript=eva.evalscript_all_bands,
            input_data=[
                SentinelHubRequest.input_data(
                    data_collection=DataCollection.SENTINEL2_L2A,
                    time_interval=(start, start),
                )
            ],
            responses=[SentinelHubRequest.output_response("default", MimeType.TIFF)],
            bbox=bbox,
            size=size,
            config=config,
        )
    elif request == "mago":
        print("Pidiendo a mago")
        return SentinelHubRequest(
            data_folder="MAGO-Cyano",
            evalscript=eva.evalscript_MAGO,
            input_data=[
                SentinelHubRequest.input_data(
                    data_collection=DataCollection.SENTINEL2_L2A,
                    time_interval=(start, start),
                    mosaicking_order=MosaickingOrder.LEAST_CC,
                )
            ],
            responses=[SentinelHubRequest.output_response("default", MimeType.TIFF)],
            bbox=bbox,
            size=size,
            config=config,
        )
    elif request == "ulises":
        return SentinelHubRequest(
            data_folder="ulises",
            evalscript=eva.evalscript_ulises,
            #warnings = "YES",
            input_data=[
                SentinelHubRequest.input_data(
                    data_collection=DataCollection.SENTINEL2_L2A,
                    time_interval=(start, start),
                    mosaicking_order=MosaickingOrder.LEAST_CC,
                )
            ],
            responses=[SentinelHubRequest.output_response("default", MimeType.TIFF)],
            bbox=bbox,
            size=size,
            config=config,
        )
    elif request == "video_ulises":
        return SentinelHubRequest(
            data_folder="video_ulises",
            evalscript=eva.evalscript_ulises,
            #warnings = "YES",
            input_data=[
                SentinelHubRequest.input_data(
                    data_collection=DataCollection.SENTINEL2_L2A,
                    time_interval=(start, end),
                    mosaicking_order=MosaickingOrder.LEAST_CC,
                )
            ],
            responses=[SentinelHubRequest.output_response("default", MimeType.TIFF)],
            bbox=bbox,
            size=size,
            config=config,
        )
    elif request == "video_mago":
        return SentinelHubRequest(
            data_folder="video_MAGO",
            evalscript=eva.evalscript_MAGO,
            input_data=[
                SentinelHubRequest.input_data(
                    data_collection=DataCollection.SENTINEL2_L2A,
                    time_interval=(start, end),
                    mosaicking_order=MosaickingOrder.LEAST_CC,
                )
            ],
            responses=[SentinelHubRequest.output_response("default", MimeType.TIFF)],
            bbox=bbox,
            size=size,
            config=config,
        )
    elif request == "video_truecolor":
       return  SentinelHubRequest(
            data_folder="video_truecolor",
            evalscript=eva.evalscript_true_color,
            input_data=[
                SentinelHubRequest.input_data(
                    data_collection=DataCollection.SENTINEL2_L1C,
                    time_interval=(start, end),
                )
            ],
            responses=[SentinelHubRequest.output_response("default", MimeType.PNG)],
            bbox=bbox,
            size=size,
            config=config,
        )
    elif request == "wqs":
       return SentinelHubRequest(
           data_folder="WQS",
           evalscript=eva.evalscript_all_bands,
           input_data=[
               SentinelHubRequest.input_data(
                   data_collection=DataCollection.SENTINEL2_L1C,
                   time_interval=(start, end),
                   mosaicking_order=MosaickingOrder.LEAST_CC,
               )
           ],
           responses=[SentinelHubRequest.output_response("default", MimeType.TIFF)],
           bbox=bbox,
           size=size,
           config=config,
       )
    elif request == "slc":
        return SentinelHubRequest(
            data_folder="slc",
            evalscript=eva.evalscript_slc,
            input_data=[
                SentinelHubRequest.input_data(
                    data_collection=DataCollection.SENTINEL2_L1C,
                    time_interval=(start, start),
                )
            ],
            responses=[SentinelHubRequest.output_response("default", MimeType.TIFF)],
            bbox=bbox,
            size=size,
            config=config,
        )