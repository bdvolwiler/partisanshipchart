# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd
import plotly as py
import plotly.graph_objs as go


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

server = app.server


# read in data
# assume you have a "long-form" data frame
# see https://plotly.com/python/px-arguments/ for more options
scores = pd.read_csv("senate_partisanship_scores.csv")
scores.index = scores["Unnamed: 0"]
del scores["Unnamed: 0"]
scores["y"] = 0

# delete no longer active senators
#del scores[scores["Name"] == "Loeffler (R-GA)"]

# this function sets the style of our chart
def set_style(fig):
    
    # update trace sizes
    fig.update_traces(
        marker = dict(
            size = 12,
            line = dict(
                width = .5
            )
        )
    )
    
    # edit chart style
    fig.update_layout(
        title = "Senator Partisanship",
        
        xaxis = dict(
            #fixedrange = True,
            range = (-.25,1.25),
            tickvals = [0, .5, 1],
            ticktext = ["Votes Along Democratic Party", "Votes Independent", "Votes Along Republican Party"],
            title = None
        ),
        
        yaxis = dict(
            fixedrange = True,
            showticklabels = False
        ),
        
        font_family = "Arial",
        title_font_size = 26,
        legend_font_size = 12,
        showlegend = False,
        autosize = False,
        width = 1000,
        height = 500
    )
    
    return fig

# plotly figure setup
fig = go.Figure()

# one button for each row
updatemenu= []
buttons=[]
data = [] # this is where we will hold all of our traces


# define color dictionary
color_map = {"D" : "blue",
             "R" : "red",
             "I" : "green"}

# adding traces to our data arrat
for row in scores.index:
    
    # add the trace to our chart
    data.append(go.Scatter(x = (scores.loc[row,"score"], ), 
                             y = (scores.loc[row,"y"], ),
                             name = row,
                             mode = 'markers',
                             marker = dict({"color" : color_map[scores.loc[row, "Party"]]})
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


# update layout and show figure
fig.update_layout(updatemenus = updatemenu)

app.layout = html.Div(children=[

    html.Center(
        dcc.Graph(
            id='Senator graph',
            figure=fig
        )
    )
])

if __name__ == '__main__':
    app.run_server(debug=True)