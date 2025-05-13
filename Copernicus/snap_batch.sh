#!/bin/bash

GRAPH_XML="snap_graph.xml"
TEMPLATE_PARAMS="snap_graph.properties"
INPUT_DIR="/home/antonio/Documentos/CienciasMarinas/Nitrates/Code/Copernicus/SAFE_downloads"
OUTPUT_DIR="/home/antonio/Documentos/CienciasMarinas/Nitrates/Code/Copernicus/SAFE_downloads/export_dim"
GPT="/home/antonio/esa-snap/bin/gpt"
OUTPUT_FORMAT="dim"

# Para filtrar por fechas

FILTER_DATES=(
  20180511 20180516 20180710 
)
#20180809 20180814 20181003 20190220 20190625 20190710
#   20200220 20200225 20200520 20200813 20201221 20210105 20210614 20210714 20210803
#   20210813 20211111 20211201 20220224 20220624 20220803 20220907 20230110 20230120
#   20230301 20230420 20230525 20230719 20230907 20230927 20231116 20240424 20240529
#   20240618 20240703 20240718

if [[ "${#FILTER_DATES[@]}" -gt 0 ]]; then
    echo "Procesando las fechas: ${FILTER_DATES[*]}"
else
    echo "Procesando todos los archivos disponibles"
fi


for input_file in "$INPUT_DIR"/*.SAFE.zip; do
    # Extraer identificadores del nombre
    filename=$(basename "$input_file")
    datecode=$(echo "$filename" | cut -d'_' -f3 | cut -c1-8)
    base_name="${filename%%.SAFE.zip}"

    # Filtrar si se especificaron fechas
    if [[ "${#FILTER_DATES[@]}" -gt 0 && ! " ${FILTER_DATES[*]} " =~ " $datecode " ]]; then
        echo "Saltando $filename (fecha $datecode no en filtro)"
        continue
    fi

    # Leer el tipo de red desde la plantilla
    net=$(grep "^netSet=" "$TEMPLATE_PARAMS" | cut -d= -f2 | tr -d '[:space:]')
    if [[ "$net" == "C2X-COMPLEX-Nets" ]]; then
        suffix="C2XComplexNets"
    else
        suffix="C2XNets"
    fi

    output_file="$OUTPUT_DIR/${base_name}_${suffix}_10m.${OUTPUT_FORMAT}"

    # Crear archivo de parámetros específico
    param_file="/tmp/params_${datecode}.params"
    sed "s|inputFile=.*|inputFile=$input_file|; s|outputFile=.*|outputFile=$output_file|" "$TEMPLATE_PARAMS" > "$param_file"

    # Ejecutar gpt
    echo "Procesando $filename → $output_file"
    "$GPT" "$GRAPH_XML" -p "$param_file"
done

