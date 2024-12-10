import streamlit as st
import geopandas as gpd
import folium
from streamlit_folium import st_folium
import branca.colormap as cm



# Título del dashboard
st.title("Identificación de las áreas más favorables para la recarga de acuíferos")

# Carga de datos
st.sidebar.header("Cargar archivo")
uploaded_file = st.sidebar.file_uploader("Sube un archivo GeoJSON", type=["geojson"])

if uploaded_file:
    # Leer GeoDataFrame
    try:
        gdf = gpd.read_file(uploaded_file)
        st.sidebar.write("Archivo cargado con éxito.")
    except Exception as e:
        st.sidebar.error(f"Error al cargar el archivo: {e}")
        st.stop()
    
    # Mostrar información básica
    st.sidebar.header("Opciones del Mapa")
    st.write("Vista previa de los datos:")
    st.write(gdf.head())
    
    # Selección de columna para color (opcional)
    col_options = ["VALOR","cluster_kmeans"]
    color_column = st.sidebar.selectbox("Selecciona una columna para colorear el mapa", col_options)
    col_options_com = ["VALOR", "LITOLOGIA", "Tipo_de_roca", "Descripcion_suelo", "Descripcion_textura", "Rango_evapotranspiracion", "Rango_precipitacion", "Descripcion_usos_de_suelo", "nombre_zonas_de_recarga", "cluster_kmeans"]

    min_val, max_val = gdf[color_column].min(), gdf[color_column].max()

    if color_column == "VALOR": 
        #Rango de valores para el filtro
        selected_range = st.sidebar.slider(
            f"Selecciona el rango de {color_column}",
            min_value=int(min_val),
            max_value=int(max_val),
            value=(int(min_val), int(max_val)),
        )

    # Filtrar el GeoDataFrame por el rango seleccionado
        filtered_gdf = gdf[(gdf[color_column] >= selected_range[0]) & (gdf[color_column] <= selected_range[1])]
    else:
        filtered_gdf = gdf

    tooltip_columns = st.sidebar.multiselect(
        "Selecciona las columnas para mostrar en el popup", col_options_com, default=[color_column]
    )

    # Crear mapa base
    center = filtered_gdf.geometry.centroid.y.mean(), filtered_gdf.geometry.centroid.x.mean()
    m = folium.Map(location=center, zoom_start=10)

   # Crear colormap
    colormap = cm.LinearColormap(colors=["blue", "green", "yellow", "red"], vmin=min_val, vmax=max_val)
    colormap.caption = f"Escala de {color_column}"

    # Crear tooltip dinámico
    tooltip_text = "<br>".join([f"<b>{col}:</b> {{properties['{col}']}}" for col in tooltip_columns])

    # Añadir GeoDataFrame al mapa con colores dinámicos
    def style_function(feature):
        value = feature["properties"][color_column]
        return {
            "fillColor": colormap(value),
            "color": "black",
            "weight": 1,
            "fillOpacity": 0.8,
        }

    folium.GeoJson(
            filtered_gdf,
            name="Mapa",
            style_function=style_function,
             tooltip=folium.GeoJsonTooltip(
                fields=tooltip_columns,
                aliases=[f"{col}" for col in tooltip_columns],
                localize=True,
                sticky=False,
            ),
    ).add_to(m)

    # Añadir la leyenda
    colormap.add_to(m)

    # Mostrar mapa en Streamlit
    st.subheader("Mapa Interactivo")
    st_folium(m, width=700, height=500)

else:
    st.write("Por favor, sube un archivo GeoJSON para visualizarlo.")
