'''
Name: Nathaniel Vil
Date: 2/10/21
Section: HB3
File:
Description:
I pledge that I have completed the programming assignment independently.
I have not copied the code from a student or any source.
I have not given my code to any student.

Link for webpage https://share.streamlit.io/nv18134/final_project/main/Project.py

Note: Due to the fact that streamlit treats multiline comments as strings comments will now have brackets as opposed to
quote marks

The purpose of this program is to serve as a tool to breakdown information about New York City car accidents, and
gets this information from 'nyc_veh_crash_sample.xlsx'. The program breaks the data down in two queries.

First Query
The first query is designed to create a map of user specified accidents, in specified boroughs, during a specified date
range. The map has two layers that the user can choose between, the hexagonallayer and the scatterplotlayer. The
hexagonallayer is the default, but the user can alternate between the two using buttons.

The hexagonallayer essentially shows the user where accidents, based on the user specifications, are more concentrated.
Areas of high concentration have higher more red like columns, while less concentrated are lower columns and more bronze
like. Also, the user can hover over these columns and what's known as the elevation value appears, this tells the user
how many accidents were within the range of the columns.

The scatterplotlayer shows the user each individual accident on the map, and also shows the user the longitude and
latitude of that accident.

Inputs
    Consequence (Injuries or Fatalities)
    Borough
    Date Range
Computations
    Filters Data to only show the data that fits the user specifications and creates a map
Output
    Map

Second Query
The Second Query is designed to allow the user to select a number of vehicles involved in the accident, the vehicle type
or factor of a certain vehicle. For example, the user can select to see the Vehicle 2 Factors for an vehicle that was
in involved in an accident that had 4 vehicles involved. The user can also specify the borough that the accident was in.
Finally, the user selects how many top positions they want to see, and based on that a chart is created. Continuing with
the earlier example a user may decide to see the top 3 factors for Vehicle 2, so the bar graph would show the user the
top 3 contributing factors, based on the times those factors were mentioned. There is also a dataframe above the graph
that shows the user its exact count.
Inputs
    Vehicles Involved
    Type or Factors For Certain Vehicles
    Borough
    Which Top Ranks
Computations
    Filters Data to only show the data that fits the user specifications and creates a bar chart
Output
    Bar Chart

Universal Functions
    uniqueList(dataset, dropna=False)
        Takes a dataset and creates a unique list of values. The dropna parameter is for whether or not the user wants
        it dropna, in case it was already dropped or they simply don't want to for whatever reason.
    top_count(dict, key, top)
        Takes in a dictionary and key, and show the top 'top' values within that dictionary key and returns a new
        dictionary of those top values and their respective counts.
    timestamp_datetime_convert(time, ts_to_dt=True)
        The streamlit slider didn't work with pandas Timestamp, so this converter converts timestamps into datetime or
        vice versa.
'''
import datetime as dt
import pandas_datareader as pdr
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
import pydeck as pdk


# Functions
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


# Inputs & Computations First Query
FILENAME = 'nyc_veh_crash_sample.xlsx'
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

# Following Code gets min and max values for the slider control
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

# Following Codes Used to Create Pydeck Map
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

# Following Codes Allow User To Alternate Between Layers
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

# First Query Output
if one_date:
    st.header(f"{graph_type.title()} of {consequence.title()} on {min_date.month}-{min_date.day}-{min_date.year}")
else:
    st.header(
        f'{graph_type.title()} of {consequence.title()} Between {time[0].month}-{time[0].day}-{time[0].year} & {time[1].month}-'
        f'{time[1].day}-{time[1].year}')

st.pydeck_chart(r)

# Second Query Input/Input Creation

# Following Codes Filter the columns to only those that have 'FACTOR', 'TYPE', or 'BOROUGH'
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
top_x = st.sidebar.slider('How Many Top Positions:', min_value=1, max_value=10, value=2)

filtered_data = accidents[selected_columns].dropna()
filtered_data = filtered_data[filtered_data.BOROUGH == borough]


# Second Query Computations
# To Satisfy the Dictionary Project Requirement The Second Query Used Dictionaries in Executing the Query
# As Opposed to Pandas

vehicles = {}

for column in filtered_data:
    vehicles[column] = []
    for info in filtered_data[column]:
        if info != 'UNSPECIFIED' and info != 'UNKNOWN':
            vehicles[column].append(info)

top_x_results = pd.Series(top_count(vehicles, selected_info, top_x))
top_x_results = top_x_results.to_frame(f"Counts")

# Second Query Output
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
