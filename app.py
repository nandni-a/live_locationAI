from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/')
def index():
    lat = request.args.get("lat")
    lng = request.args.get("lng")
    name = request.args.get("name")
    return render_template("index.html", lat=lat, lng=lng, name=name)

if __name__ == '__main__':
    app.run(debug=True)
