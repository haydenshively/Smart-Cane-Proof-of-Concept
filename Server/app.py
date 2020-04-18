from flask import Flask, Response
import threading

app = Flask(__name__)

#{THREADING RELATED}
#{import overarching packages}
from queue import Queue
from CustomThread import CustomThread
#{import task-specific classes}
from Cameras import USB

queue_camera = Queue(maxsize=60)
camera = USB.USB(0, queue_camera)

@app.route('/')
def hello_world():
    return """
        <html>
          <head>
          </head>
          <body>
            <script type="text/javascript">

            var source = new EventSource("/updates.cam");

            source.addEventListener('message', function(e) {
              console.log(e.data);
            }, false);
            
            </script>
          </body>
        </html>
        """

@app.route('/updates.cam')
def gyro():
    res = queue_camera.get(block=True, timeout=100)
    print(res[2])
    if res is None:
        res = False, None, (-1, (-1, -1))
    resp = Response("retry: 1\ndata: {}\n\n".format(res[2]))
    resp.headers['Content-type'] = 'text/event-stream'
    resp.headers['Cache-Control'] = 'no-cache'
    resp.headers['Connection'] = 'keep-alive'
    return resp

if __name__ == '__main__':
    app.debug = False
    thread = threading.Thread(target=app.run, kwargs={'host':'0.0.0.0'})
    thread.start()
    try:
        camera.run()
    except KeyboardInterrupt:
        camera.film.release()
        thread.join()
