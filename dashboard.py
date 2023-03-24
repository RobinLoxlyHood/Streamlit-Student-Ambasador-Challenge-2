import pandas as pd
import mysql.connector
import pandas as pd
import numpy as np
import streamlit as st
import folium
from streamlit_folium import st_folium
import geopandas as gpd
import warnings
warnings.filterwarnings('ignore')

def read_mysql_table(query):
    """
    Connects to MySQL database and reads data from specified table.
    
    Args:
    query (str): SQL query to select data from MySQL table
    
    Returns:
    pandas.DataFrame: DataFrame containing data from MySQL table
    """
    # Establish connection to MySQL
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        database="klasifikasi_sentimen"
    )

    # Create DataFrame from MySQL query
    df = pd.read_sql(query, con=mydb)

    # Close the MySQL connection
    mydb.close()

    return df

def filters_lokasi(df_jkt):
    filters_desa_list = ['ALL']+list(df_jkt['location'].unique())
    filters_desa_list.sort()
    filters_desa = st.sidebar.selectbox('Pilih Daerah :', filters_desa_list)
    return filters_desa

def filters_tokoh(df_jkt):
    filters_tokoh_list = ['ALL']+list(df_jkt['Tokoh'].unique())
    filters_tokoh_list.sort()
    filters_tokoh = st.sidebar.selectbox('Pilih Tokoh :', filters_tokoh_list)
    return filters_tokoh

def display_map(df_jkt):
    map_indo = folium.Map(location=[-2.49607,117.89587], tiles='OpenStreetMap', zoom_start=5)

    # choropleth = folium.Choropleth(
    #     geo_data='demografi_jakarta_utara.geojson',
    #     data=df_jkt,
    #     columns=('nama_desa', 'JUMLAH_PEN'),
    #     key_on='feature.properties.nama_desa',
    #     fill_color='YlOrRd',
    #     line_opacity=0.8,
    #     legend_name='nama_desa',
    #     highlight=True
    # )
    # choropleth.geojson.add_to(map)
    #Loop through each row in the dataframe

    # selectbox=selectbox
    # df_jkt = df_jkt.query("nama_kategori in @selectbox")
    for _, r in df_jkt.iterrows():
        
        # Without simplifying the representation of each borough,
        # the map might not be displayed
        sim_geo = gpd.GeoSeries(r['geometry']).simplify(tolerance=0.001)
        geo_j = sim_geo.to_json()
        geo_j = folium.GeoJson(data=geo_j)
        #folium.Popup(r['nama_kategori']).add_to(geo_j)
        folium.Popup(r['location']).add_to(geo_j)
        # folium.Marker(icon = folium.Icon(color='red'))
        geo_j.add_to(map_indo)

    #selectbox=st.write(selectbox)
    st_map=st_folium(map_indo, width=700, height=450)
    return st_map



def main():
    #TITLE
    APP_TITLE = "Visualisasi Klasifikasi Sentimen"
    st.set_page_config(APP_TITLE)
    st.title(APP_TITLE)
    #READ MYSQSL DATA
    query = "SELECT * FROM hasil_scraping"
    
    #READ DATA
    data_df = read_mysql_table(query)
    geo_df = gpd.read_file('indonesia-prov.geojson')
    geo_df.rename(columns={'Propinsi': 'location'}, inplace=True)
    
    #MERGE
    merged_gdf = geo_df.merge(data_df, on='location')
    
    # FILTER  LOKASI
    # lokasi=filters_lokasi(df_jkt=merged_gdf)
    # tokoh =filters_tokoh(df_jkt=lokasi)
    # st.sidebar.title("Filters")
    # with st.sidebar.form(key ='Filters'):
    #     filters_desa_list = ['ALL']+list(merged_gdf['location'].unique())
    #     filters_desa_list.sort()
    #     filters_tokoh = st.sidebar.selectbox('Pilih Daerah :', filters_desa_list)    
    #     select_language = st.radio('Tweet language', ('All', 'English', 'French'))
    #     include_retweets = st.checkbox('Include retweets in data')
    #     num_of_tweets = st.number_input('Maximum number of tweets', 100)
    #     submitted1 = st.form_submit_button(label = 'Search Twitter 🔎')
    display_map(df_jkt=merged_gdf)
    
    
    
    #st.write(merged_gdf)
    
    

if __name__ == "__main__":
    main()
    
    
    