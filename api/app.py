from flask import Flask, render_template, send_from_directory

app = Flask(__name__, static_folder='static')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/static/public/<path:filename>')
def serve_public_file(filename):
    return send_from_directory('static/public', filename)

if __name__ == '__main__':
    app.run(debug=True)
