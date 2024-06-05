import pandas as pd
import numpy as np


# Función para extraer la fecha más reciente
def extract_recent_date(date_str):
    if isinstance(date_str, str):
        parts = date_str.split('/')
        if len(parts) == 3:
            # Partes de la fecha
            day_range = parts[0].split('-')
            month = parts[1]
            year = parts[2]
            # Crear las dos fechas posibles
            if len(day_range) == 2:
                day1, day2 = day_range[0], day_range[1]
                month, year = month, year
                date1 = pd.to_datetime(f"{day1}/{month}/{year}", format='%d/%m/%Y', errors="coerce")
                date2 = pd.to_datetime(f"{day2}/{month}/{year}", format='%d/%m/%Y', errors="coerce")
                return max(date1, date2)
            else:
                return pd.to_datetime(date_str, format='%d/%m/%Y', errors="coerce")
        else:
            return pd.to_datetime(date_str, format='%d/%m/%Y', errors="coerce")
    return date_str


# Para sustituir los diferentes strings de "Cauce seco", "Agua estancada", etc por 0's
def replace_strings(val):
    if isinstance(val, str):
        return 0
    return val




####################################################

# Código previo

# Extraemos la fecha más reciente en las instancias que tienen dos fechas
# df_caudal['Fecha'] = df_caudal['Fecha'].apply(extract_recent_date)
# df_nitratos['Fecha'] = df_nitratos['Fecha'].apply(extract_recent_date)
# df_fosfatos['Fecha'] = df_fosfatos['Fecha'].apply(extract_recent_date)
# df_conductividad['Fecha'] = df_conductividad['Fecha'].apply(extract_recent_date)
# df_nitratosdiario['Fecha'] = df_nitratosdiario['Fecha'].apply(extract_recent_date)
# df_fosfatosdiario['Fecha'] = df_fosfatosdiario['Fecha'].apply(extract_recent_date)

# Ponemos como 0's todas las observaciones que no tienen un valor

# df_caudal = df_caudal.fillna(0)
# df_caudal = df_caudal.applymap(replace_strings)

# df_nitratos = df_nitratos.fillna(0)
# df_nitratos = df_nitratos.applymap(replace_strings)

# df_fosfatos = df_fosfatos.fillna(0)
# df_fosfatos = df_fosfatos.applymap(replace_strings)

# df_conductividad = df_conductividad.fillna(0)
# df_conductividad = df_conductividad.applymap(replace_strings)

# df_nitratosdiario = df_nitratosdiario.fillna(0)
# df_nitratosdiario = df_nitratosdiario.applymap(replace_strings)

# df_fosfatosdiario = df_fosfatosdiario.fillna(0)
# df_fosfatosdiario = df_fosfatosdiario.applymap(replace_strings)