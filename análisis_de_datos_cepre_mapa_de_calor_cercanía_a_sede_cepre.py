# -*- coding: utf-8 -*-
"""ANÁLISIS DE DATOS - CEPRE - MAPA DE CALOR CERCANÍA A SEDE CEPRE.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1nGJ2zmpvXzpfIVfA07tSdRQK5x0QNYgf
"""

# INSTALAMOS LIBRERÍAS NECESARIAS
!pip install geopandas folium

# CARGA DE DATASET Y LIBRERÍAS, ADICIONAL PARA EL ANÁLISIS, SE CARGA EL DATASET QUE CONTIENE COORDENADAS DE TODOS LOS DISTRITOS DEL PERÚ
import pandas as pd
from geopy.distance import geodesic

df1 = pd.read_csv('/content/sample_data/Datos_abiertos_cepre.csv')
df2 = pd.read_csv('/content/sample_data/distritos.csv')

# AGREGAR COLUMNA 'COLEGIO_INFO' PARA TENER EN UNA SOLA COLUMNA EL VALOR DE CADA ORIGEN DE COLEGIO
df1['COLEGIO_INFO'] = df1[['COLEGIO_DEPA', 'COLEGIO_PROV', 'COLEGIO_DIST']].astype(str).agg('-'.join, axis=1)
df1['COLEGIO_INFO']

# REASIGNAMOS EL NOMBRE DE LA COLUMNA 'IDHASH' POR EL DE 'ALUMNOS' Y VALIDAMOS LA INFORMACIÓN DEL DF CON LA ACTUALIZACIÓN
df1.rename(columns={'IDHASH': 'ALUMNOS'}, inplace=True)
df1.info()

# REEAMPLAZAR "Distrito X" por "Distrito Y", SE CORRIJEN LOS DATOS PARA TENER UN MATCH CON EL DATASET DE LA CEPRE
df2.loc[df2['NOMBDIST'] == 'ANCO_HUALLO', 'NOMBDIST'] = 'ANCO-HUALLO'
df2.loc[df2['NOMBDIST'] == 'SAN FRANCISCO DE ASIS DE YARUSYACAN', 'NOMBDIST'] = 'SAN FCO.DE ASIS DE YARUSYACAN'
df2.loc[df2['NOMBDIST'] == 'NASCA', 'NOMBDIST'] = 'NAZCA'
df2.loc[df2['NOMBPROV'] == 'NASCA', 'NOMBPROV'] = 'NAZCA'
df2.loc[df2['NOMBDIST'] == 'ALLAUCA', 'NOMBDIST'] = 'AYAUCA'
df2.loc[df2['NOMBDIST'] == 'CORONEL GREGORIO ALBARRACIN LANCHIPA', 'NOMBDIST'] = 'CORONEL GREGORIO ALBARRACIN LANCHIP'

# AGREGAR COLUMNA 'COLEGIO_INFO' PARA TENER EN UNA SOLA COLUMNA EL VALOR DE CADA ORIGEN DE COLEGIO, UTILIZAMOS EL DATO DE COLEGIO, DEBIDO A QUE ES EL MÁS CONFIABLE DE ACUERDO AL ANÁLISIS REALIZADO POR DISTRIBUCIÓN GEOGRÁFICA
df2['COLEGIO_INFO'] = df2[['NOMBDEP', 'NOMBPROV', 'NOMBDIST']].astype(str).agg('-'.join, axis=1)
df2['COLEGIO_INFO']

# SEPARAR COLUMNA 'Geo Point' EN 'LATITUD' y 'LONGITUD'
df2[['LATITUD', 'LONGITUD']] = df2['Geo Point'].str.strip().str.split('|', expand=True)

df2

# REALIZAMOS EL MERGE DE LOS DF BASADOS EN LA COLUMA 'COLEGIO_INFO'
df_merged = pd.merge(df1, df2, on='COLEGIO_INFO', how='left')

df_merged.info()

# SE VALIDA QUE NO SE TIENE NINGÚN REGISTRO CON DATA NaN QUE GENERE INCOSISTENCIA
nan_rows = df_merged[df_merged['NOMBDEP'].isnull()]
unique_colegio_dist = nan_rows['NOMBDEP'].unique()
unique_colegio_dist

# SE ASUME COMO PUNTO DE REFERENCIA LA SEDE DE CEPRE UNI EN AVENIDA JAVIER PRADO - MAGDALENA
punto_referencia = (-12.093290, -77.061559)

# CALCULAR LA DISTANCIA DESDE CADA DISTRITO AL PUNTO DE REFERENCIA
df_merged['DISTANCIA'] = df_merged.apply(lambda row: geodesic((row['LATITUD'], row['LONGITUD']), punto_referencia).kilometers, axis=1)
df_merged['DISTANCIA']

# VERIFIAMOS LA INFORMACIÓN PROCESADA
df_merged[['LATITUD', 'LONGITUD']].describe()

# GENERAMOS UNA MUESTRA DE LA DATA MERGEADA PARA VALIDAR EL PROCESAMIENTO
df_merged.head()

# GENERACIÓN DE MAPA DE CALOR

import folium
from folium.plugins import HeatMap

# MAPA DE CALOR CONSIDERANDO MATRICULADOS EN CEPRE-UNI

# CREAR MAPA CENTRADO EN PERÚ
mapa = folium.Map(location=[-12.0464, -77.0428], zoom_start=6)  # Lima, Perú

# Crear la capa de mapa de calor con los distritos y su cercanía al punto de referencia, usamos 1/distancia para que valores menores indiquen más cercanía
heat_data = [[row['LATITUD'], row['LONGITUD'], 1/row['DISTANCIA']] for index, row in df_merged.iterrows()]

HeatMap(heat_data, radius=20, blur=10, max_zoom=1).add_to(mapa)

# Mostrar el mapa
mapa

# Mostrar manualmente el punto de referencia en el mapa para validar su posicionamiento adecuado

# Usando coordenadas de Lima, Perú como punto de referencia
mapa2 = folium.Map(location=[-12.0464, -77.0428], zoom_start=6)  # Lima, Perú


# punto_referencia = (-12.093290, -77.061559)
folium.Marker(location=[-12.093290, -77.061559], popup="Punto de Referencia").add_to(mapa2)

# Agregar capa de mapa de calor (heatmap)
HeatMap(heat_data, radius=15, blur=10).add_to(mapa2)

# Mostrar el mapa
mapa2

# MAPA DE CALOR CONSIDERANDO INGRESANTES CEPRE-UNI (DIRECTO)

# CREAR MAPA CENTRADO EN PERÚ
mapa3 = folium.Map(location=[-12.0464, -77.0428], zoom_start=6)  # Lima, Perú

# Crear la capa de mapa de calor con los distritos y su cercanía al punto de referencia
heat_data3 = [[row['LATITUD'], row['LONGITUD'], 1/row['DISTANCIA']] for index, row in df_merged[(df_merged['INGRESO']=='SI') & (df_merged['MODO_INGRESO']=='DIRECTO')].iterrows()]

# Añadir el mapa de calor al mapa
HeatMap(heat_data3, radius=20, blur=10, max_zoom=1).add_to(mapa3)

# Mostrar el mapa
mapa3

from sklearn.preprocessing import MinMaxScaler

# MAPA DE CALOR CONSIDERANDO MATRICULADOS, CON VARIACIÓN DEL RADIO DE LAS PUNTOS DE MARCACIÓN E INTENSIDAD PROPORCIONAL A LA DISTANCIA

# COORDENADAS DE REFERENCIA
latitud_referencia = -12.0464  # Lima, Perú
longitud_referencia = -77.0428

# CREAR MAPA CENTRADO EN PERÚ
mapa4 = folium.Map(location=[latitud_referencia, longitud_referencia], zoom_start=6)


# Agrupar por latitud y longitud, contar las repeticiones y calcular la distancia promedio
df_grouped = df_merged.groupby(['LATITUD', 'LONGITUD']).agg(
    DISTANCIA=('DISTANCIA', 'mean'),
    REPETICIONES=('LATITUD', 'size')  # Contamos las repeticiones
).reset_index()

# Crear la intensidad como el inverso de la distancia promedio
df_grouped['INTENSIDAD'] = 1 / df_grouped['DISTANCIA']

# Normalizar la intensidad entre 5 y 20
scaler = MinMaxScaler(feature_range=(5, 10))
df_grouped['RADIO'] = scaler.fit_transform(df_grouped[['REPETICIONES']])

# Preparar los datos para el HeatMap con intensidad y radio variable
heat_data4 = [[row['LATITUD'], row['LONGITUD'], row['INTENSIDAD']] for index, row in df_grouped.iterrows()]

# Añadir la capa de mapa de calor con radio variable
for index, row in df_grouped.iterrows():
    HeatMap([[row['LATITUD'], row['LONGITUD'], row['INTENSIDAD']]], radius=row['RADIO'], blur=20, max_zoom=1).add_to(mapa4)

# Mostrar el mapa
mapa4