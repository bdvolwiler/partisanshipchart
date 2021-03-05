# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd
import plotly as py
import plotly.graph_objs as go
from plotly.subplots import make_subplots

print("\n\n\n")

# -------- set up the dash environment -------------
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

# --------------- open data -------------------------
data = pd.read_csv("all_movies.csv")

# -------------- Process data -------------------------

# generate master list of genres
genre_list = []
for x in data["Genre"].values:
    try:
        movie_list = x.split(",")
        for y in movie_list:
            if y not in genre_list:
                genre_list.append(y)
    except:
        pass

# convert string into list in genre column
genre_replace = []
for x in data["Genre"].values:
    try:
        movie_list = x.split(",")
    except:
        pass
    
    genre_replace.append(movie_list)
    
data["Genre"] = genre_replace

# ------------------- Create Graphs ----------------------

# create keys of genres
genre_keys = []

for x in data["Genre"].values:
    movie_key = []
    for y in genre_list:
        movie_key.append(y in x)
    genre_keys.append(movie_key)

rating_traces = []

# adding traces to our data arrat
for row in data.index:
    
    # add the trace to rating traces
    rating_traces.append(go.Scatter(x = (data.loc[row,"Genre"], ), 
                                    y = (data.loc[row,"BoxOffice"], ),
                                    name = row,
                                    mode = 'markers',
                                    )
                 )
    
# adding buttons for dropdown
# the visible arg takes an array of booleans,
# so we will loop each time and set the appropriate
# True value
for trace_no in range(len(data)):
    trace = data[trace_no]
    
    visible = []
    
    for x in range(len(data)):
        if x == trace_no:
            visible.append(True)
        else:
            visible.append(False)
            
    buttons.append(dict(method = 'update',
                    label = trace["name"],
                    args = [{'visible': visible}],
                       
                  ))

# declare figure    
fig = go.Figure(data = data)
    
# style our graph
fig = set_style(fig)

# some adjustments to the updatemenu
updatemenu=[]
your_menu = dict()
updatemenu.append(your_menu)
updatemenu[0]['buttons'] = buttons
updatemenu[0]['direction'] = 'down'
updatemenu[0]['showactive'] = True



# send graph to html page
app.layout = html.Div(children=[

    html.Center(
        dcc.Graph(
            id='Rating10',
            figure=fig
        )
    )
])

if __name__ == '__main__':
    app.run_server(debug=True)