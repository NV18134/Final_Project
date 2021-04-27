'''
Name: Nathaniel Vil
Date: 2/10/21
Section: HB3
File:
Description:
I pledge that I have completed the programming assignment independently.
I have not copied the code from a student or any source.
I have not given my code to any student.

reading the excel file required


'''

import datetime as dt
import pandas_datareader as pdr
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
import pydeck as pdk

def uniqueList(dataset, dropna=False):
    listing = []
    if not dropna:
        for row in dataset:
            if row not in listing:
                listing.append(row)
        return listing
    else:
        for row in dataset.dropna():
            if row not in listing:
                listing.append(row)
        return listing

def top_count(dict, key, top):
    count_dict = {}
    for value in dict[key]:
        count_dict[value] = dict[key].count(value)
    count_dict = sorted(count_dict.items(), key=lambda x: x[1], reverse=True)
    new_dict = {}
    for item in count_dict[:top]:
        new_dict[item[0]] = item[1]
    return new_dict


def timestamp_datetime_convert(time, ts_to_dt=True):
    if ts_to_dt:
        return pd.Timestamp(time).to_pydatetime()
    else:
        return pd.Timestamp(time)


FILENAME = '/Users/nathanielvil/Downloads/nyc_veh_crash_sample.xlsx'
data = pd.read_excel(FILENAME)
accidents = pd.DataFrame(data)
accidents = accidents.set_index('UNIQUE KEY')

st.sidebar.title('First Query')
consequence = uniqueList(accidents.iloc[:, 11:18].columns)
consequence.insert(0, 'Unspecified')
consequence = st.sidebar.selectbox('Select Consequence: ', consequence)

borough_list = uniqueList(accidents['BOROUGH'], True)
borough_list.insert(0, 'All')
selected_borough = st.sidebar.selectbox('Select Borough:', borough_list)

if consequence != 'Unspecified':
    maps_data = accidents[['DATE', 'LATITUDE', "LONGITUDE", 'BOROUGH', consequence]].dropna()
    maps_data = maps_data[maps_data[consequence] != 0]
else:
    maps_data = accidents[['DATE', 'LATITUDE', "LONGITUDE", 'BOROUGH']].dropna()

if selected_borough != 'All':
    maps_data = maps_data[maps_data.BOROUGH == selected_borough]
else:
    maps_data = maps_data[:][:]
maps_data.columns = [column.lower() for column in maps_data.columns]

max_date = maps_data['date'].max()
max_date = timestamp_datetime_convert(max_date)
min_date = maps_data['date'].min()
min_date = timestamp_datetime_convert(min_date)

if min_date != max_date:
    time = st.sidebar.slider('Date Range:', min_value=min_date, max_value=max_date, value=(min_date, max_date))
    maps_data = maps_data.loc[maps_data['date'].between(time[0], time[1])]
    one_date = False
    if time[0] == time[1]:
        maps_data = maps_data.loc[maps_data.date == time[0]]
        one_date = True
else:
    time = min_date
    maps_data = maps_data.loc[maps_data.date == time]
    one_date = True



hexlayer = pdk.Layer(
    'HexagonLayer',
    data=maps_data,
    get_position="[longitude, latitude]",
    elevation_scale=100,
    elevation_range=[0, 200],
    extruded=True,
    coverage=1,
    opacity=.4,
    pickable=True,
    auto_highlight=True,
)

scatterplot = pdk.Layer(
    'ScatterplotLayer',
    maps_data,
    get_position='[longitude, latitude]',
    get_radius=80,
    get_color=[255, 0, 0],
    pickable=True
)

view_state = pdk.ViewState(
    longitude=maps_data['longitude'].mean(), latitude=maps_data['latitude'].mean(), zoom=8.9, pitch=30
)

tooltip_hex = {'html': "<b>Elevation Value:</b> {elevationValue} "}
tooltip_scatter = {'html': '<b>Longitude:</b> {longitude} <br> <b>Latitude:</b> {latitude}'}

hex = st.sidebar.button('Show Hex Layer')
scatter = st.sidebar.button('Show Scatter Layer')

if hex:
    scatter = False
    layer = hexlayer
    tooltip = tooltip_hex
    graph_type = 'HexLayer Graph'
elif scatter:
    hex = False
    layer = scatterplot
    tooltip = tooltip_scatter
    graph_type = 'Scatter Plot'
else:
    layer = hexlayer
    tooltip = tooltip_hex
    graph_type = 'HexLayer Graph'

r = pdk.Deck(
    map_style="mapbox://styles/mapbox/light-v9",
    layers=layer,
    initial_view_state=view_state,
    tooltip=tooltip
)

if one_date:
    st.header(f"{graph_type.title()} of {consequence.title()} on {min_date.month}-{min_date.day}-{min_date.year}")
else:
    st.header(
        f'{graph_type.title()} of {consequence.title()} Between {time[0].month}-{time[0].day}-{time[0].year} & {time[1].month}-'
        f'{time[1].day}-{time[1].year}')

st.pydeck_chart(r)

columns = uniqueList(accidents.columns)
copy = columns.copy()

for column in copy:
    if 'FACTOR' not in column and 'TYPE' not in column and column != 'BOROUGH':
        columns.remove(column)

st.sidebar.title('Second Query')
num_vehicles = st.sidebar.slider('Select Number of Vehicles in Accident: ', min_value=1, max_value=4, value=1)

selected_columns = []

for column in columns:
    for num in range(num_vehicles + 1):
        if str(num) in column or column == 'BOROUGH' and column not in selected_columns:
            selected_columns.append(column)

info_list = [column for column in selected_columns if "FACTOR" in column or 'TYPE' in column]

selected_info = st.sidebar.selectbox('What You Like To See: ', info_list)

borough_list.pop(borough_list.index('All'))

borough = st.sidebar.selectbox('Which Borough Would You Like to See', borough_list)

filtered_data = accidents[selected_columns].dropna()
filtered_data = filtered_data[filtered_data.BOROUGH == borough]

vehicles = {}

for column in filtered_data:
    vehicles[column] = []
    for info in filtered_data[column]:
        if info != 'UNSPECIFIED' and info != 'UNKNOWN':
            vehicles[column].append(info)

top_x = st.sidebar.slider('How Many Top Positions:', min_value=1, max_value=10, value=2)

top_x_results = pd.Series(top_count(vehicles, selected_info, top_x))
top_x_results = top_x_results.to_frame(f"Counts")

if num_vehicles != 1:
    st.header(f"Top {top_x} {selected_info.title()} in {borough.title()} for Accidents With {num_vehicles} Vehicles")
else:
    st.header(f"Top {top_x} {selected_info.title()} in {borough.title()} for Accidents With {num_vehicles} Vehicle")

st.dataframe(top_x_results)

x = top_x_results['Counts'].max()

fig, ax = plt.subplots()

top_x_results.plot.bar(ax=ax, color='#1d1fcc')

plt.xticks(rotation=45, horizontalalignment='right')
plt.yticks(horizontalalignment="right", verticalalignment='center')
plt.legend(facecolor='#0288d1')
plt.xlabel('Count', size=10)
plt.ylabel(f"{selected_info.title()}", size=10)
fig.tight_layout()
st.pyplot(fig)


