import time, threading, csv, datetime
from collections import deque
from arduino_iot_cloud import ArduinoCloudClient
from dash import Dash, dcc, html, Input, Output, Patch
import cv2

DEVICE_ID = "secret"
SECRET_KEY = "secret"

Variables = ["x", "y", "z"]
#using deque but drains the whole storage every cycle
data = {a: deque() for a in Variables}
starttime = time.time()
iteration = 1


def clientSetup():
    #connect to arduino
    client = ArduinoCloudClient(device_id=DEVICE_ID, username=DEVICE_ID, password=SECRET_KEY)
    #get the values for each variable
    client.register("x",value=None, on_write=CallBack("x"))
    client.register("y", value=None, on_write=CallBack("y"))
    client.register("z", value=None, on_write=CallBack("z"))
    client.start()


#adds cloud variables to data[] apphends the time as well.
def CallBack(axis):
    def callback(client, value):
        #stamps time
        data[axis].append((time.time() - starttime, value))
    return callback



def capture_loop():
    global iteration
    #open camera
    camera = cv2.VideoCapture(0)
    while True:
        time.sleep(30)#30 second interval

        #time with specifics for name save
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        nameTemplate = f"{iteration}_{timestamp}"
         #save this segment to csv
        with open(f"{nameTemplate}.csv", "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["time", "axis", "value"])
            for a in Variables:
                for t, v in data[a]:
                    writer.writerow([t, a, v])
                data[a].clear()
        # get image capture. 
        ret, frame = camera.read()
        if ret:
            cv2.imwrite(f"{nameTemplate}.jpg", frame)

        iteration += 1 #increase to update new file names n increment

if __name__ == "__main__":
    threading.Thread(target=clientSetup, daemon=True).start()
    capture_loop()
