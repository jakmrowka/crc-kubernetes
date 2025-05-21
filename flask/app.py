from flask import Flask
app = Flask(__name__)

@app.route('/')
def index():
    print("wywołano strone")
    return "<h1>Witamy na CRC4.COM (Flask)</h1>"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
