from flask import Flask, render_template, url_for

app = Flask(__name__)

@app.route('/')
@app.route('/home/')
def home():
    return render_template('home.html')

@app.route('/how-does-it-work/')
def how_does_it_work():
    return render_template('how_does_it_work.html')

if __name__ == '__main__':
    app.run(debug=True)
