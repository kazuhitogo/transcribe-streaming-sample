import make_uri
import websocket
wss_url = make_uri.make_ws_uri()
print(wss_url)

def on_message(ws, message):
    print(message.decode('utf-8', 'replace'))

def on_error(ws, error):
    print(error)

def on_close(ws):
    print("closed")

def on_open(ws):
    print("opened")


if __name__ == "__main__":
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp(wss_url,
                              on_message = on_message,
                              on_error = on_error,
                              on_close = on_close)
    ws.on_open = on_open
    ws.run_forever()