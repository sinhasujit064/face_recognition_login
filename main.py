from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from base64 import b64encode
import cv2
from PIL import Image
import io
import base64
import numpy as np
import face_recognition

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
app.secret_key = "secret key"

# SqlAlchemy Database Configuration With Mysql
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:''@localhost/mini_project'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class Data(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first = db.Column(db.String(100))
    last = db.Column(db.String(100))
    email = db.Column(db.String(100))
    phone = db.Column(db.String(100))
    password = db.Column(db.String(100))
    image = db.Column(db.LargeBinary)

    def __init__(self, first, last, email, phone, password, image):
        self.first = first
        self.last = last
        self.email = email
        self.phone = phone
        self.password = password
        self.image = image


@app.route('/')
def index():
    return render_template('home.html')


@app.route('/signin')
def signup():
    return render_template('signup.html')


@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/verify', methods=["POST"])
def verify():
    name = request.form['fir']
    password = request.form['pass']
    all_data = Data.query.filter_by(first=name).first()
    if all_data and all_data.password == password:
        image = b64encode(all_data.image).decode("utf-8")

        binary_data = base64.b64decode(image)

        img1 = Image.open(io.BytesIO(binary_data))

        img1 = cv2.cvtColor(np.array(img1), cv2.COLOR_RGB2BGR)
        img1 = cv2.cvtColor(img1, cv2.COLOR_BGR2RGB)
        face = face_recognition.face_locations(img1)[0]

        encodeFace = face_recognition.face_encodings(img1)[0]

        cv2.rectangle(img1, (face[3], face[0]), (face[1], face[2]), (255, 0, 255), 2)

        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

        while True:
            ret, frame = cap.read()

            faces = cv2.resize(frame, (0, 0), None, 0.25, 0.25)
            faces = cv2.cvtColor(faces, cv2.COLOR_BGR2RGB)

            facesCurrentFrame = face_recognition.face_locations(faces)
            encodesCurrentFrame = face_recognition.face_encodings(faces, facesCurrentFrame)

            results = face_recognition.compare_faces(encodeFace, encodesCurrentFrame)
            if results[0] == True:
                red = "Log IN Success"
                break
            else:
                red = "Login Failed"
                break
        cap.release()
        # Destroy all the windows
        cv2.destroyAllWindows()
    else:
        red = "Incorrect Username or Password"
    return render_template("loginredirect.html", results=red)


@app.route('/insert', methods=["POST"])
def insert():
    if request.method == "POST":
        first = session['first']
        last = session['last']
        email = session['email']
        phone = session['phone']
        password = session['password']
        file = request.files['image']

        mydata = Data(first, last, email, phone, password, file.read())
        db.session.add(mydata)
        db.session.commit()
        return redirect(url_for('success'))


@app.route('/sessions', methods=["POST"])
def sessions():
    if request.method == "POST":
        first = request.form['first']
        last = request.form['last']
        email = request.form['email']
        phone = request.form['phone']
        password = request.form['password']
        session['first'] = first
        session['last'] = last
        session['email'] = email
        session['phone'] = phone
        session['password'] = password
        return redirect(url_for('photo'))


@app.route('/userpage')
def userpage():
    return render_template('loginredirect.html')


@app.route('/photo')
def photo():
    first = session['first']
    last = session['last']
    email = session['email']
    phone = session['phone']
    password = session['password']
    # image=session['image']
    return render_template('photo_capture.html', first=first, last=last, email=email, phone=phone, password=password)


@app.route('/success')
def success():
    return render_template('success.html')


if __name__ == '__main__':
    app.run(host='localhost', debug=True)
