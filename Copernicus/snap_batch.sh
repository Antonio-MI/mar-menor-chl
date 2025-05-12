#!/bin/bash

GRAPH_XML="snap_graph.xml"
TEMPLATE_PARAMS="snap_graph.properties"
INPUT_DIR="/home/antonio/Documentos/CienciasMarinas/Nitrates/Code/Copernicus/SAFE_downloads"
OUTPUT_DIR="/home/antonio/Documentos/CienciasMarinas/Nitrates/Code/Copernicus/SAFE_downloads/processed"

for input_file in "$INPUT_DIR"/*.SAFE.zip; do
    # Extraer identificadores del nombre
    filename=$(basename "$input_file")
    datecode=$(echo "$filename" | cut -d'_' -f3 | cut -c1-8)
    base_name="${filename%%.SAFE.zip}"

    # Leer el tipo de red desde la plantilla
    net=$(grep "^netSet=" "$TEMPLATE_PARAMS" | cut -d= -f2 | tr -d '[:space:]')
    if [[ "$net" == "C2X-COMPLEX-Nets" ]]; then
        suffix="C2XComplexNets"
    else
        suffix="C2XNets"
    fi

    output_file="$OUTPUT_DIR/${base_name}_${suffix}_10m.tif"

    # Crear archivo de parámetros específico
    param_file="/tmp/params_${datecode}.params"
    sed "s|inputFile=.*|inputFile=$input_file|; s|outputFile=.*|outputFile=$output_file|" "$TEMPLATE_PARAMS" > "$param_file"

    # Ejecutar gpt
    echo "Procesando $filename → $output_file"
    /home/antonio/esa-snap/bin/gpt "$GRAPH_XML" -p "$param_file"
done

