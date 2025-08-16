# utils/hometown.py
import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd

# Load the timeline data from JSON
timeline_data = pd.read_json("timeline/timeline.json")

# Create a Dash app
app = dash.Dash(__name__)

# Define the layout of the app
app.layout = html.Div([dcc.Graph(id="line-graph"), html.H1("Timeline Plot")])


# Pass the timeline data to the graph component
@app.callback(
    dash.dependencies.Output("line-graph", "figure"),
    [dash.dependencies.Input("line-graph", "graph")],
)
def update_graph(graph):
    return {
        "data": [
            {
                "x": timeline_data["date"],
                "y": timeline_data["summary"],
                "name": "Timeline Plot",
            }
        ]
    }


# Run the app
if __name__ == "__main__":
    app.run_server(debug=True)
