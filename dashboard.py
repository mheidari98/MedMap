import os
import dash
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import dcc, html
from dash.dependencies import Input, Output
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

DEBUG = os.getenv('DASH_DEBUG_MODE', 'False').lower() in ['true', '1', 't']
HOST = os.getenv('HOST', '127.0.0.1')
PORT = int(os.getenv('PORT', 8050))

try:
    df = pd.read_csv("medical-centers.csv")
except Exception as e:
    logging.error(f"Failed to load data: {e}")
    raise

provinces = ["All"] + sorted(df["provinceName"].dropna().unique().tolist())
types = ["All"] + sorted(df["type_name"].dropna().unique().tolist())
map_styles = [
    'carto-positron',  # Best for general use - clean and readable
    'open-street-map',  # Good detailed view with Persian labels
    'carto-darkmatter',  # Good for night/dark mode
    'streets',  # Good for showing road networks
    'light'  # Simple and clean alternative
]

# Add province coordinates for centering
PROVINCE_COORDS = {
    'استان تهران': {"lat": 35.6892, "lon": 51.3890, "zoom": 9},
    'استان همدان': {"lat": 34.7939, "lon": 48.5148, "zoom": 9},
    'استان مرکزی': {"lat": 34.0933, "lon": 49.6974, "zoom": 9}, #اراک
    'استان ايلام': {"lat": 33.6348, "lon": 46.4237, "zoom": 9},
    'استان آذربايجان غربی': {"lat": 37.5549, "lon": 45.0747, "zoom": 9}, #ارومیه
    'استان مازندران': {"lat": 36.5649, "lon": 53.0578, "zoom": 9}, #ساری
    'استان زنجان': {"lat": 36.6736, "lon": 48.4946, "zoom": 9},
    'استان فارس': {"lat": 29.5917, "lon": 52.5833, "zoom": 9}, #شیراز
    'استان کرمانشاه': {"lat": 34.3141, "lon": 47.0660, "zoom": 9},
    'استان کرمان': {"lat": 30.2841, "lon": 57.0686, "zoom": 9},
    'استان چهارمحال و بختیاری': {"lat": 32.3292, "lon": 50.8653, "zoom": 9}, #شهرکرد
    'استان بوشهر': {"lat": 28.9734, "lon": 50.8383, "zoom": 9},
    'استان خراسان رضوی': {"lat": 36.2000, "lon": 59.6000, "zoom": 9}, #مشهد
    'استان قم': {"lat": 34.6401, "lon": 50.8764, "zoom": 9},
    'استان گيلان': {"lat": 37.2750, "lon": 49.5897, "zoom": 9}, #رشت
    'استان گلستان': {"lat": 36.8429, "lon": 54.4418, "zoom": 9}, #گرگان
    'استان خوزستان': {"lat": 31.0041, "lon": 48.6657, "zoom": 9}, #اهواز
    'استان اصفهان': {"lat": 32.6546, "lon": 51.6680, "zoom": 9},
    'استان خراسان جنوبی': {"lat": 32.8663, "lon": 59.2181, "zoom": 9}, #بیرجند
    'استان کهگیلویه و بویراحمد': {"lat": 30.6897, "lon": 51.5940, "zoom": 9}, #یاسوج
    'استان اردبيل': {"lat": 38.2498, "lon": 48.2940, "zoom": 9},
    'استان البرز': {"lat": 35.8356, "lon": 50.9922, "zoom": 9}, #کرج
    'استان سیستان و بلوچستان': {"lat": 29.4962, "lon": 60.8354, "zoom": 9}, #زاهدان
    'استان لرستان': {"lat": 33.4854, "lon": 48.3588, "zoom": 9}, #خرم آباد
    'استان آذربايجان شرقی': {"lat": 38.0790, "lon": 46.2919, "zoom": 9}, #تبریز
    'استان يزد': {"lat": 31.8974, "lon": 54.3675, "zoom": 9},
    'استان سمنان': {"lat": 35.5739, "lon": 53.3953, "zoom": 9},
    'استان خراسان شمالی': {"lat": 37.4711, "lon": 56.9810, "zoom": 9}, #بجنورد
    'استان قزوين': {"lat": 36.2796, "lon": 50.0074, "zoom": 9},
    'استان هرمزگان': {"lat": 27.1939, "lon": 56.2892, "zoom": 9}, #بندرعباس
    'استان کردستان': {"lat": 35.2535, "lon": 46.9912, "zoom": 9}, #سنندج
    "All": {"lat": 32.4279, "lon": 53.6880, "zoom": 5}  # Center of Iran
}

app = dash.Dash(__name__, 
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1.0"}
    ]
)

# Custom theme colors
COLORS = {
    'background': '#f0f2f5',
    'primary': '#007bff',
    'secondary': '#6c757d',
    'accent': '#17a2b8',
    'text': '#343a40'
}

app.layout = html.Div([
    # Filters Container
    html.Div([
        html.H1("Medical Centers Map 🏥", 
            style={
                "textAlign": "center",
                "padding": "20px",
                "backgroundColor": COLORS['primary'],
                "color": "white",
                "borderRadius": "10px",
                "margin": "0 0 20px 0",
                "fontFamily": "Arial, sans-serif",
                "fontSize": "24px"
            }
        ),
        
        html.Div([
            html.Label("Center Name", style={"marginBottom": "8px", "fontWeight": "bold"}),
            dcc.Input(
                id="name-filter",
                type="text",
                placeholder="Enter part of center name",
                style={"width": "100%", "marginBottom": "15px", "padding": "8px"}
            ),

            html.Label("Select Province", style={
                "marginBottom": "8px",
                "color": COLORS['text'],
                "fontWeight": "bold"
            }),
            dcc.Dropdown(
                id="province-filter",
                options=[{"label": p, "value": p} for p in provinces],
                value="All",
                style={"marginBottom": "15px"}
            ),
            
            html.Label("Select Type", style={"marginBottom": "8px", "fontWeight": "bold"}),
            dcc.Dropdown(
                id="type-filter",
                options=[{"label": t, "value": t} for t in types],
                value="All",
                style={"marginBottom": "15px"}
            ),
            
            html.Label("Map Style", style={"marginBottom": "8px", "fontWeight": "bold"}),
            dcc.Dropdown(
                id="map-style",
                options=[{"label": m.replace("-", " ").title(), "value": m} for m in map_styles],
                value="carto-positron",
                style={"marginBottom": "15px"}
            ),

            html.Button(
                "📍 Use My Location",
                id="get-location-btn",
                n_clicks=0,
                style={
                    "width": "100%",
                    "padding": "12px",
                    "backgroundColor": COLORS['accent'],
                    "color": "white",
                    "border": "none",
                    "borderRadius": "5px",
                    "cursor": "pointer",
                }
            ),
        ], style={
            "padding": "20px",
            "backgroundColor": "white",
            "borderRadius": "10px",
            "boxShadow": "0 2px 4px rgba(0,0,0,0.1)"
        }),
    ], style={
        "width": "300px",
        "padding": "20px",
        "backgroundColor": COLORS['background'],
        "zIndex": "1000",
        "@media (max-width: 768px)": {
            "width": "100%",
            "padding": "10px"
        }
    }, className="filters-container"),

    # Map Container
    html.Div([
        dcc.Graph(id="map", style={
            "height": "calc(100vh - 40px)",
            "width": "100%",
            "borderRadius": "10px",
        }),
    ], style={
        "marginLeft": "340px",
        "padding": "20px",
        "@media (max-width: 768px)": {
            "marginLeft": "0",
            "padding": "10px"
        }
    }, className="map-container"),

    dcc.Location(id="url", refresh=True),
    dcc.Store(id="user-location", storage_type="session"),
    dcc.Store(id="map-state", storage_type="session"),
    html.Div(id="click-output"),
], style={"position": "relative"})

@app.callback(
    Output("map", "figure"),
    [Input("province-filter", "value"),
     Input("type-filter", "value"),
     Input("name-filter", "value"),
     Input("map-style", "value"),
     Input("user-location", "data"),
     Input("map-state", "data")]
)
def update_map(province, type_name, name_filter, map_style, user_location, map_state):
    filtered_df = df.copy()
    if province is None:
        province = "All"
    elif province != "All":
        filtered_df = filtered_df[filtered_df["provinceName"] == province]
    
    if type_name is None:
        type_name = "All"
    elif type_name != "All":
        filtered_df = filtered_df[filtered_df["type_name"] == type_name]

    if name_filter:
        filtered_df = filtered_df[filtered_df["name"].str.contains(name_filter, case=False, na=False)]

    # Get center coordinates based on province selection
    center_coords = PROVINCE_COORDS.get(province, PROVINCE_COORDS["All"])
    
    if user_location:
        center_lat, center_lon = user_location["lat"], user_location["lon"]
        zoom = 10
    elif map_state:
        center_lat = map_state["lat"]
        center_lon = map_state["lon"]
        zoom = map_state["zoom"]
    else:
        center_lat = center_coords["lat"]
        center_lon = center_coords["lon"]
        zoom = center_coords["zoom"]

    fig = px.scatter_mapbox(
        filtered_df,
        lat="latitude",
        lon="longitude",
        hover_name="name",
        hover_data={
            "provinceName": True,
            "type_name": True,
            "URL": False  # Hide URL from hover data
        },
        custom_data=["URL"],  # Include URL in custom data
        color="type_name",
        color_discrete_sequence=px.colors.qualitative.Set3,
        zoom=zoom,
        height=800
    )

    # Add user location marker if available
    if user_location:
        fig.add_trace(
            go.Scattermapbox(
                lat=[user_location["lat"]],
                lon=[user_location["lon"]],
                mode='markers',
                marker=dict(size=15, color='red', symbol='circle'),
                name="Your Location",
                hoverinfo='name'
            )
        )
    
    fig.update_layout(
        mapbox_style=map_style if map_style else 'carto-positron',
        mapbox_center={"lat": center_lat, "lon": center_lon},
        margin={"r":0,"t":0,"l":0,"b":0},
        clickmode='event+select',
        paper_bgcolor=COLORS['background'],
        plot_bgcolor=COLORS['background']
    )
    
    fig.update_traces(
        marker=dict(size=12),
        hovertemplate="<b>%{hovertext}</b><br>" +
                     "Province: %{customdata[1]}<br>" +
                     "Type: %{customdata[2]}<br>" +
                     "🔗 Click to visit website<extra></extra>"
    )
    return fig

@app.callback(
    Output("map-state", "data"),
    [Input("map", "relayoutData")]
)
def update_map_state(relayout_data):
    if relayout_data and "mapbox.center" in relayout_data and "mapbox.zoom" in relayout_data:
        return {
            "lat": relayout_data["mapbox.center"]["lat"],
            "lon": relayout_data["mapbox.center"]["lon"],
            "zoom": relayout_data["mapbox.zoom"]
        }
    return dash.no_update

@app.callback(
    Output("url", "href"),
    [Input("map", "clickData")]
)
def handle_click(clickData):
    if clickData is not None:
        point_data = clickData["points"][0]
        url = point_data["customdata"][0] 
        if pd.notna(url):
            return url
    return dash.no_update

app.clientside_callback(
    """
    function(n_clicks) {
        if (n_clicks > 0) {
            navigator.geolocation.getCurrentPosition(
                function(position) {
                    return {'lat': position.coords.latitude, 'lon': position.coords.longitude};
                },
                function(error) {
                    console.error("Error getting location: ", error);
                    return null;
                }
            );
        }
        return null;
    }
    """,
    Output("user-location", "data"),
    Input("get-location-btn", "n_clicks")
)


app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            @media (max-width: 768px) {
                .filters-container {
                    position: relative !important;
                    width: 100% !important;
                }
                .map-container {
                    margin-left: 0 !important;
                }
                #map {
                    height: 70vh !important;
                }
            }
            @media (min-width: 769px) {
                .filters-container {
                    position: fixed;
                    left: 0;
                    top: 0;
                    bottom: 0;
                    overflow-y: auto;
                }
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

if __name__ == "__main__":
    app.run_server(
        debug=DEBUG,
        host=HOST,
        port=PORT
    )
