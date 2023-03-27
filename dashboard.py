import mysql.connector
import pandas as pd
import numpy as np
import streamlit as st
import folium
from streamlit_folium import st_folium
import geopandas as gpd
import plotly.graph_objects as go
import plotly.express as px
from PIL import Image
import warnings
warnings.filterwarnings('ignore')

@st.cache_resource
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

def filter_sentiment_positif_tiap_provinsi(df):
    location_unique = df['location'].unique()
    new_df = pd.DataFrame()
    for location in location_unique:
        location_sentiment = df[(df['location'] == location) & (df['Sentiment'] == '1')]
        highest_jumlah = location_sentiment.loc[location_sentiment['jumlah'].idxmax()]  # Filter for the highest 'jumlah' value
        new_df = new_df.append(highest_jumlah)
    new_df = new_df.sort_values(by='jumlah', ascending=False).reset_index(drop=True)
    return new_df

def display_map(df_jkt):
    map_indo = folium.Map(location=[-2.5489, 118.0149], tiles='cartodbdark_matter', zoom_start=4) 

    # choropleth = folium.Choropleth(
    #     geo_data=df_jkt,
    #     data=df_jkt,
    #     columns=['Tokoh', 'jumlah'],
    #     key_on='feature.properties.Tokoh',
    #     fill_color=['red, blue', 'yellow'],
    #     fill_opacity=0.7,
    #     line_opacity=0.2,
    #     highlight=True
    # )
    # choropleth.geojson.add_to(map_indo)
    # choropleth.geojson.add_child(
    #     folium.features.GeoJsonTooltip(['Tokoh', 'jumlah','location'], labels=False)
    # )
    #Loop through each row in the dataframe

    # selectbox=selectbox
    # df_jkt = df_jkt.query("nama_kategori in @selectbox")
    # for _, r in df_jkt.iterrows():
        
    #     # Without simplifying the representation of each borough,
    #     # the map might not be displayed
    #     sim_geo = gpd.GeoSeries(r['geometry']).simplify(tolerance=0.001)
    #     geo_j = sim_geo.to_json()
    #     geo_j = folium.GeoJson(data=geo_j)
    #     #folium.Popup(r['nama_kategori']).add_to(geo_j)
    #     folium.Popup(r['Tokoh']).add_to(geo_j)
    #     # folium.Marker(icon = folium.Icon(color='red'))
    #     geo_j.add_to(map_indo)
    
    # for _, r in df_jkt.iterrows():

    #     # Without simplifying the representation of each borough,
    #     # the map might not be displayed
    #     sim_geo = gpd.GeoSeries(r['geometry']).simplify(tolerance=0.001)
    #     geo_j = sim_geo.to_json()

    #     # Define the style function

    #     # Create the GeoJson layer with style function and popup
    #     geo_j = folium.GeoJson(data=geo_j)
    #     folium.Popup(r['Tokoh']).add_to(geo_j)
        
    #     # Add the GeoJson layer to the map
    #     geo_j.add_to(map_indo)
        
    style_function = lambda x: {
    "fillColor": "#ff0000" if x["properties"]["Tokoh"] == "Ganjar Pranowo" else
                 "#0000ff" if x["properties"]["Tokoh"] == "Anies Baswedan" else
                 "#ffff00",
    "fill":True,
    "fill_opacity":0.7,
    "line_opacity":0.2,
    "color": False          
    }
    color=folium.GeoJson(df_jkt, style_function=style_function)
    folium.Popup(df_jkt['Tokoh']).add_to(color)
    color.add_to(map_indo)

    #selectbox=st.write(selectbox)
    st_map=st_folium(map_indo, width=700, height=450)
    return st_map


def plot_tokoh_sentiment(df, tokoh):
    # Mengelompokkan berdasarkan tokoh dan sentiment, kemudian menghitung jumlah
    result = df.groupby(['Tokoh', 'Sentiment'])['jumlah'].sum().reset_index()
    
    # Mengubah label sentimen
    result['Sentiment'] = result['Sentiment'].apply(lambda x: 'Netral' if x == '-1' else 'Negatif' if x == '0' else 'Positif')
    
    # Membuat barchart untuk tokoh yang dimaksud
    df_tokoh = result[result['Tokoh'] == tokoh]
    fig = go.Figure(
        data=[go.Bar(
            x=df_tokoh['Sentiment'],
            y=df_tokoh['jumlah'],
            marker=dict(color=['red' if s == 'Negatif' else 'gray' if s == 'Netral' else 'green' for s in df_tokoh['Sentiment']])
        )],
        layout=go.Layout(title='Jumlah Sentiment keseluruhan Provinsi')
    )
    
    
    # Menambahkan anotasi di atas bar
    for i, row in df_tokoh.iterrows():
        fig.add_annotation(
            x=row['Sentiment'],
            y=row['jumlah'],
            text=str(row['jumlah']),
            font=dict(color='white'),
            showarrow=False
        )
    fig.update_layout(width=300, height=450)
    
    st.plotly_chart(fig)
    
def create_line_chart(df, tokoh):
    # Filter data berdasarkan tokoh yang dipilih
    df_tokoh = df[df['Tokoh'] == tokoh]
    
    # Mengubah label sentimen
    df_tokoh['Sentiment'] = df_tokoh['Sentiment'].apply(lambda x: 'Netral' if x == '-1' else 'Negatif' if x == '0' else 'Positif')
    
    # Membuat line chart dengan Plotly
    fig = px.line(df_tokoh, x='date', y='jumlah', color='Sentiment', 
                  title='History Jumlah Sentiment Keseluruhan Provinsi', labels={'Sentiment': 'Sentiment Score'})
    
    # Menampilkan legend
    fig.update_traces(mode='lines+markers')
    
    # Mengatur ukuran figure
    fig.update_layout(width=450, height=450)
    
    # Menampilkan chart
    st.plotly_chart(fig)

def main():
    #TITLE
    APP_TITLE = "Klasifikasi Opini publik di Twitter terhadap bakal calon Presiden Indonesia Tahun 2024 secara Real Time"
    st.set_page_config(APP_TITLE)
    st.title(APP_TITLE)
    #READ MYSQSL DATA
    query = "SELECT * FROM hasil_scraping"
    #READ DATA
    data_df = read_mysql_table(query)
    # # data_df.to_csv("data.csv", index=False)
    #   data_df = pd.read_csv("data.csv")
    geo_df = gpd.read_file('indonesia-prov.geojson')
    #mengganti value Status
    replacement_mapping_dict = {
        "DI. ACEH" : "ACEH",
        "NUSATENGGARA BARAT" : "NUSA TENGGARA BARAT",
        "DAERAH ISTIMEWA YOGYAKARTA" : "DI YOGYAKARTA",
        "BANGKA BELITUNG" : "KEPULAUAN BANGKA BELITUNG"
    }
    geo_df["Propinsi"] = geo_df["Propinsi"].replace(replacement_mapping_dict)
    geo_df.rename(columns={'Propinsi': 'location'}, inplace=True)
    
    #MERGE
    merged_gdf = geo_df.merge(data_df, on='location')
    merged_gdf = gpd.GeoDataFrame(merged_gdf, geometry='geometry')
    #Data Preprocessing Barchart
    count_sentiment_tokoh_loc = merged_gdf.groupby(['location' ,'Sentiment', 'Tokoh'])['location'].count().reset_index(name="jumlah")
    merge2=geo_df.merge(count_sentiment_tokoh_loc, on='location')
    merge2 = merge2[['location', 'Tokoh', 'Sentiment', 'jumlah']]
    fil=filter_sentiment_positif_tiap_provinsi(merge2)
    fil = geo_df.merge(fil, on='location')
    fil = gpd.GeoDataFrame(fil, geometry='geometry')
    fil = fil[['location', 'Tokoh', 'Sentiment', 'jumlah', 'geometry']]
    
    #Data Preprocessing Line Chart
    #count_sentiment_tokoh_byDate_and_location = merged_gdf.groupby(['date' ,'location' ,'Sentiment', 'Tokoh'])['date'].count().reset_index(name="jumlah")
    #data_filter_linechart_with_location=count_sentiment_tokoh_byDate_and_location[['date', 'location', 'Tokoh', 'Sentiment', 'jumlah']]
    count_sentiment_tokoh_byDate = merged_gdf.groupby(['date','Sentiment', 'Tokoh'])['date'].count().reset_index(name="jumlah")
    data_filter_linechart_byDate=count_sentiment_tokoh_byDate[['date', 'Tokoh', 'Sentiment', 'jumlah']]
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
    #st.write(merged_gdf)
    #display_map(gdf)
    st.markdown(f'<h3 style="color: gray;border-radius:50%;" >sumber: www.twitter.com</h3>',unsafe_allow_html=True)
    st.metric(label="Akurasi", value='75 %')
    # Using "with" notation
    with st.container():
         ganjar, anies, prabowo = st.columns(3)
         with ganjar:
            st.subheader("Ganjar Pranowo")
            image = Image.open('images/ganjar.png')
            width = 100
            height = 100
            resized_image = image.resize((width, height))
            st.image(resized_image)
             
         with anies:
            st.subheader("Anies Baswedan")
            image = Image.open('images/anies.png')
            width = 100
            height = 100
            resized_image = image.resize((width, height))
            st.image(resized_image)
             
         with prabowo:
            st.subheader("Prabowo Subianto")
            image = Image.open('images/prabowo.png')
            width = 100
            height = 100
            resized_image = image.resize((width, height))
            st.image(resized_image)
    with st.container():
        st.subheader("Jumlah Sentiment Positif terbanyak tiap Provinsi")
        display_map(fil)
    with st.container():
        st.subheader("Ganjar Pranowo")
        barchart, linechart= st.columns(2)
        with barchart:
            plot_tokoh_sentiment(count_sentiment_tokoh_loc, 'Ganjar Pranowo')
        with linechart:
            create_line_chart(data_filter_linechart_byDate, 'Ganjar Pranowo')
    
    with st.container():
        st.subheader('Anies Baswedan')
        barchart, linechart= st.columns(2)
        with barchart:
            plot_tokoh_sentiment(count_sentiment_tokoh_loc, 'Anies Baswedan')
        with linechart:
            create_line_chart(data_filter_linechart_byDate, 'Anies Baswedan')
    
    with st.container():
        st.subheader('Prabowo Subianto')
        barchart, linechart= st.columns(2)
        with barchart:
            plot_tokoh_sentiment(count_sentiment_tokoh_loc, 'Prabowo Subianto')
        with linechart:
            create_line_chart(data_filter_linechart_byDate, 'Prabowo Subianto')
    # st.write(data_df)
    
if __name__ == "__main__":
    main()
    
    
    