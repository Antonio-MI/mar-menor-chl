#!/bin/bash

GRAPH_XML="snap_graph.xml"
TEMPLATE_PARAMS="snap_graph.properties"
INPUT_DIR="/home/antonio/Documentos/CienciasMarinas/Nitrates/Code/Copernicus/SAFE_downloads"
OUTPUT_DIR="/home/antonio/Documentos/CienciasMarinas/Nitrates/Code/Copernicus/SAFE_downloads/processed"
GPT="/home/antonio/esa-snap/bin/gpt"
OUTPUT_FORMAT="tif"

# Para filtrar por fechas

FILTER_DATES=(
    20160809 20160908 20161028 20170630 20180220 20180307 20180516 20180620 20180710 20180829
    20181003 20181107 20190312 20190625 20190710 20190730 20190814 20190918 20190928 20191003
    20191127 20200220 20200311 20201221 20210105 20210420 20210520 20210614 20210813 20210912
    20211111 20211126 20211201 20220224 20220714 20220729 20220803 20220907 20220927 20230110
    20230301 20230316 20230420 20230525 20240320

)



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
    elif [[ "$net" == "C2X-Nets" ]]; then
        suffix="C2XNets"
    else
        suffix="C2RCCNets"
    fi

    output_file="$OUTPUT_DIR/${base_name}_${suffix}_10m.${OUTPUT_FORMAT}"

    # Crear archivo de parámetros específico
    param_file="/tmp/params_${datecode}.params"
    sed "s|inputFile=.*|inputFile=$input_file|; s|outputFile=.*|outputFile=$output_file|" "$TEMPLATE_PARAMS" > "$param_file"

    # Ejecutar gpt
    echo "Procesando $filename → $output_file"
    "$GPT" "$GRAPH_XML" -p "$param_file"
done

