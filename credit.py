import time, threading
from collections import deque
from arduino_iot_cloud import ArduinoCloudClient
from dash import Dash, dcc, html, Input, Output, Patch

DEVICE_ID = "97c3f2bc-b105-4e39-b311-68b5c0378936"
SECRET_KEY = "n@jN9qwE7U!6@LWmJh8#m4qcz"


#variables xyz for graphing
Variables = ["x", "y", "z"]
#creates dequee size 500 for rolling window
data = {a: deque(maxlen=100) for a in Variables}
#starttime
starttime = time.time()


def clientSetup():
    #connect to arduino
    client = ArduinoCloudClient(device_id=DEVICE_ID, username=DEVICE_ID, password=SECRET_KEY)
    #get the values for each variable
    client.register("x",value=None, on_write=CallBack("x"))
    client.register("y", value=None, on_write=CallBack("y"))
    client.register("z", value=None, on_write=CallBack("z"))
    client.start()

#callback for each x,y,z
def CallBack(axis):
    #cloud calls this  when new value for axis is availabke
    def callback(client, value):
        #stamps time
        data[axis].append((time.time() - starttime, value))
    return callback




#api function
def streamGraph(app, graph_id, getSeries, SeriesName):
    #dash updates every tick and updtaes graph
    @app.callback(Output(graph_id, "figure"), Input("tick", "n_intervals"))
    def UPDATE(_n):
        #patch() used for sliding update not full replacememt
        patch = Patch()
        #get values from xyz
        for i, name in enumerate(SeriesName):
            xs, ys = getSeries(name)
            patch["data"][i]["x"] = xs
            patch["data"][i]["y"] = ys
        return patch
    return UPDATE

def getSeries(axis):
    points = list(data[axis])
    return [p[0] for p in points], [p[1] for p in points]



#init Dash
app = Dash(__name__)
#setup layout
app.layout = html.Div([
    html.H2("Live Accelerometer Stream", style={"color": "#e0e0e0"}),
    dcc.Graph(id="graph", figure={
        "data": [{"x": [], "y": [], "type": "scatter", "mode": "lines", "name": a} for a in Variables],
        "layout": {
            "plot_bgcolor": "#1e1e1e",
            "paper_bgcolor": "#1e1e1e",
            "font": {"color": "#e0e0e0"},
        }
    }),
    dcc.Interval(id="tick", interval=200),
], style={"backgroundColor": "#121212", "padding": "20px"})

streamGraph(app, "graph", getSeries, Variables)

if __name__ == "__main__":
    threading.Thread(target=clientSetup, daemon=True).start()
    app.run(debug=True)