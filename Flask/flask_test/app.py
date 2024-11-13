from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import secrets
app = Flask(__name__)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'  # Using SQLite for this example
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = secrets.token_hex(16)

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Primary key
    username = db.Column(db.String(150), unique=True, nullable=False)  # Username field
    password = db.Column(db.String(150), nullable=False)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if the username already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return 'Username already exists! Please choose a different one.'

        # Hash the password for security
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        # Create a new user object
        new_user = User(username=username, password=hashed_password)

        # Add to database and commit
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = False
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Fetch the user from the database
        user = User.query.filter_by(username=username).first()

        # Check if user exists and password matches
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id  # Store user ID in the session
            return redirect(url_for('dashboard'))  # Redirect to home page
        else:
            error = True  # Invalid credentials

    return render_template('login.html', error=error)


@app.route('/users')
def users():
    # Fetch all users from the database
    all_users = User.query.all()
    return render_template('users.html', users=all_users)


@app.route('/logout')
def logout():
    session.clear()  # Clear the session to log the user out
    return redirect(url_for('login'))

@app.route("/")
def hello_world():
    return render_template('base.html')

@app.route("/home")
def home():
    return render_template('home.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' in session:  # Ensure the user is logged in
        return render_template('success.html')
    else:
        return redirect(url_for('login'))  # Redirect to login if not logged in


@app.route("/about")
def about():
    return render_template('about.html')



@app.route("/json_data")
def json_data():
    user_data={
        "name":"thomas",
        "age":34,
        # 'user_id':user_id
    }
    return jsonify(user_data),200




app.add_url_rule('/home','home',home)

if __name__ == '__main__':
    app.run(debug=True)

