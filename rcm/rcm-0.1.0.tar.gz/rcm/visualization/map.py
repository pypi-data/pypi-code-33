import folium
from IPython.display import display, clear_output


def style_function(feature):
    return {
        'fillColor': '#ffaf00',
        'color': 'blue',
        'weight': 1.5,
        'dashArray': '5, 5'
    }


def highlight_function(feature):
    return {
        'fillColor': '#ffaf00',
        'color': 'green',
        'weight': 3,
        'dashArray': '5, 5'
    }


def draw_map(map, model, progress):
    location = [12.9716, 77.5946]  # Bangalore Center
    zoom = 12

    draw_map.m = folium.Map(
        location=location,
        tiles='https://cartodb-basemaps-{s}.global.ssl.fastly.net/light_all/{z}/{x}/{y}.png',
        attr='&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a> &copy; <a href="http://cartodb.com/attributions">CartoDB</a>',
        zoom_start=zoom)

    # x1,y1,x2,y2 = model.grid.bbox
    # draw_map.m.fit_bounds([[y2,x2], [y1,x1]])

    geo_json = {
        "type": "FeatureCollection",
        "features": []
    }
    for agent in model.locations:
        geo_json['features'].append(agent.__geo_interface__())

    # Get the inhabitants data from the agent vars. Using the previous model step
    data = model.datacollector.get_agent_vars_dataframe().Inhabitants.loc[model.schedule.steps-1].dropna().to_frame()
    # Reset the index, because the folium sets the index using the first value in the columns parameter for the choropleth
    data = data.reset_index()

    draw_map.m.choropleth(
        geo_data=geo_json,
        name='Inhabitants',
        data=data,
        columns=['AgentID', 'Inhabitants'],
        key_on='feature.properties.unique_id',
        fill_color='BuGn',
        fill_opacity=0.9,
        line_opacity=0.2,
        legend_name='Inhabitants',
        reset=False
        )

    for agent in model.locations:
        coords = agent.shape.centroid.coords

        marker = folium.Marker(
            location=[coords[0][1], coords[0][0]],
            tooltip=folium.Tooltip(str(agent.unique_id), sticky=False),
            popup=folium.Popup(agent.to_html())
        )
        marker.add_to(draw_map.m)

        progress.value = progress.value + 1

    folium.LayerControl().add_to(draw_map.m)
    with map:
        clear_output(wait=True)
        display(draw_map.m)


# Initialize the function object attribute
draw_map.m = None
