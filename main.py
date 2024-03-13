from flask import Flask, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
import json
from validity import check_validity
from datetime import datetime, timedelta
import jwt

# just creating application with flask
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
app.config["SECRET_KEY"] = "\x9a\x98\xb0\xb9\xb7\xa6\xf6\x87\x0e\x07"
db = SQLAlchemy(app)


# this table is for users registration and logins
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    password = db.Column(db.String(120))
    email = db.Column(db.String(120), unique=True)

    def __repr__(self):
        return self.email, self.password


# that is for the workouts I added in the database
class Workouts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.String(200), nullable=True)
    target_muscles = db.Column(db.String(120), nullable=False)


# this used to be users database tables
class UserTable(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.String(200), nullable=True)
    target_muscles = db.Column(db.String(120), nullable=False)

    with app.app_context():
        db.create_all()


# for my case I needed to decode the information which user gives
def decode(item):
    json_string = item.decode().strip()
    data_dict = json.loads(json_string)
    return data_dict


@app.route("/", methods=['GET'])
def home():
    if not session.get('logged_in'):
        return jsonify({'message': "You are not logged in currently"})
    else:
        return jsonify({'message': "you are logged in so here is you workouts "})


@app.route("/register", methods=["POST"])
def register():
    try:
        data_dict = decode(request.get_data())
    except:
        data_dict = request.get_data()

    existing_user = db.session.query(User).filter_by(email=data_dict.get('email')).first()
    if existing_user:
        return jsonify({"message": "User Already Registered"})
    else:
        valid = check_validity(data_dict.get('email'), data_dict.get('password'))
        if valid:
            new_user = User(email=data_dict.get('email'),
                            password=data_dict.get('password'))
            db.session.add(new_user)
            db.session.commit()

            new_table = UserTable()
            new_table.__tablename = data_dict.get('email')

            return jsonify({"OK": "User registered successfully"})
        else:
            return jsonify({"Error": "Invalid email or password"})


@app.route("/login", methods=["POST"])
def login():
    try:
        data = decode(request.get_data())
    except:
        data = request.get_data()
    user = db.session.query(User).filter_by(email=data.get("email")).first()
    if user:
        session['logged_in'] = True
        token = jwt.encode({
            'email': data.get('email'),
            'expiration': str(datetime.utcnow() + timedelta(seconds=300))
        },
            app.config['SECRET_KEY'])
        return jsonify({'Logged In': f"{token}"}), 200

    else:
        return jsonify({"Error": 'email or password is incorrect'}), 400


@app.route('/logout', methods=["POST"])
def logout():
    session['logged_in'] = False
    return jsonify({'Logged out': "You have successfully logged out "})


@app.route("/get_workouts", methods=['GET'])
def get_my_workouts():
    if session['logged_in']:
        with app.app_context():
            result = db.session.execute(db.select(Workouts).order_by(Workouts.id))
            all_workouts = result.scalars()
            my_workouts = {}
            for workout in all_workouts:
                my_workouts[f"{workout.id}"] = f"{workout.name} - {workout.description} - {workout.target_muscles}"
        return jsonify(my_workouts)

    else:
        return jsonify({'message': "you are not logged in"}), 200


@app.route("/get_my_workouts/<email>", methods=["GET"])
def get_user_workouts(email):
    if session['logged_in']:
        with app.app_context():
            result = db.select(UserTable).where(UserTable.__tablename__ == email)
            print(result)
            print(result)

            my_workouts = {}
            for workout in result:
                print(workout + "s")
                my_workouts[f"{workout.id}"] = f"{workout.name} - {workout.description} - {workout.target_muscles}"
        return jsonify(my_workouts)
    else:
        return jsonify({'message': "you are not logged in"})


if __name__ == "__main__":
    app.run(debug=True)
