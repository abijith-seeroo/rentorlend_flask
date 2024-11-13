from crypt import methods
from functools import wraps
from operator import methodcaller

from flask_cors import CORS
from werkzeug.security import generate_password_hash,check_password_hash
import uuid
from flask import Flask, request, jsonify, make_response, render_template
from flask_sqlalchemy import SQLAlchemy
import datetime
import jwt

app=Flask(__name__)

app.config['SECRET_KEY']='here_is_my_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo_flask.db'

db = SQLAlchemy(app)

class User(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    public_id=db.Column(db.String(50),unique=True)
    name=db.Column(db.String(50))
    password=db.Column(db.String(80))
    admin=db.Column(db.Boolean)

class ToDo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(50))
    complete = db.Column(db.Boolean)
    user_id = db.Column(db.Integer)


def token_required(f):
    @wraps(f)
    def decorated(*args,**kwargs):
        token=None
        if 'x-access-token' in request.headers:
            token=request.headers['x-access-token']
        if not token:
            return jsonify({'message':'Token is missing'}),401

        try:
            data=jwt.decode(token,app.config['SECRET_KEY'],algorithms=["HS256"])
            current_user=User.query.filter_by(public_id=data['public_id']).first()
        except:
            return jsonify({'message': 'Token is missing'}), 401

        return f(current_user, *args, **kwargs)
    return decorated



@app.route('/user',methods=['GET'])
@token_required
def get_all_users(current_user):
    if not current_user.admin:
        jsonify({'message': 'Current function cant perform'})


    users=User.query.all()
    output=[]
    for user in users:
        user_data={}
        user_data['name']=user.name
        user_data['public_id']=user.public_id
        user_data['password']=user.password
        user_data['admin']=user.admin
        output.append(user_data)

    return jsonify({'users':output})

@app.route('/user/<public_id>',methods=['GET'])
@token_required
def get_one_user(current_user,public_id):
    if not current_user.admin:
        jsonify({'message': 'Current function cant perform'})
    user=User.query.filter_by(public_id=public_id).first()
    if not user:
        return jsonify(({'message':'No user Found'}))
    user_data = {}
    user_data['name'] = user.name
    user_data['public_id'] = user.public_id
    user_data['password'] = user.password
    user_data['admin'] = user.admin
    return jsonify({"user data":user_data})

@app.route('/user',methods=['POST'])
@token_required
def create_user(current_user):
    # if not current_user.admin:
    #     jsonify({'message': 'Current function cant perform'})
    data= request.get_json()
    hashed_password=generate_password_hash(data['password'], method='pbkdf2:sha256')
    new_user=User(public_id=str(uuid.uuid4()),name=data['name'],password=hashed_password,admin=False)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message':'New User Is Created'})

@app.route('/user/<public_id>',methods=['PUT'])
@token_required
def promote_user(current_user,public_id):
    if not current_user.admin:
        jsonify({'message': 'Current function cant perform'})
    user=User.query.filter_by(public_id=public_id).first()
    if not user:
        return jsonify(({'message':'No user Found'}))
    user.admin=True
    db.session.commit()

    return jsonify({"message":"The user has been promoted"})

@app.route('/user/<public_id>',methods=['DELETE'])
@token_required
def delete_user(current_user,public_id):
    if not current_user.admin:
        jsonify({'message': 'Current function cant perform'})
    user=User.query.filter_by(public_id=public_id).first()
    if not user:
        return jsonify(({'message':'No user Found'}))
    db.session.delete(user)
    db.session.commit()
    return jsonify(({'message':'user has been deleted'}))


@app.route('/login')
def login():
    auth = request.authorization

    if not auth or not auth.username or not auth.password:
        return make_response('Could not verify!', 401, {'WWW-authenticate': 'Basic realm="login required"'})

    user = User.query.filter_by(name=auth.username).first()

    if not user:
        return make_response('Could not verify!', 401, {'WWW-authenticate': 'Basic realm="login required"'})

    if check_password_hash(user.password, auth.password):
        token = jwt.encode(
            {'public_id': user.public_id, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)},
            app.config['SECRET_KEY'], algorithm="HS256")



        return jsonify({'token': token})

    return make_response('Could not verify!', 401, {'WWW-authenticate': 'Basic realm="login required"'})


@app.route("/todo",methods=['GET'])
@token_required
def get_all_todo(current_user):
    # if not current_user.admin:
    #     jsonify({'message': 'Current function cant perform'})

    todo = ToDo.query.filter_by(user_id=current_user.id).all()
    output = []
    for user in todo:
        user_data = {}
        user_data['text'] = user.text
        user_data['complete'] = user.complete
        user_data['user_id'] = user.id
        output.append(user_data)

    return jsonify({'Todo list': output})

@app.route("/todo/<todo_id>",methods=['GET'])
@token_required
def get_one_todo(current_user,todo_id):
    todo = ToDo.query.filter_by(id=todo_id,user_id=current_user.id).first()

    if not todo:
        return jsonify({'message': 'No user found'})


    output = []

    user_data = {}
    user_data['text'] = todo.text
    user_data['complete'] = todo.complete
    user_data['user_id'] = todo.id
    output.append(user_data)

    return jsonify({'Todo Data': output})

@app.route("/todo",methods=['POST'])
@token_required
def create_todo(current_user):
    data=request.get_json()
    new_todo=ToDo(text=data['text'],complete=False,user_id=current_user.id)
    db.session.add(new_todo)
    db.session.commit()
    return jsonify({'message': 'New todo Created'})

@app.route("/todo/<todo_id>",methods=['PUT'])
@token_required
def complete_todo(current_user,todo_id):
    todo = ToDo.query.filter_by(id=todo_id, user_id=current_user.id).first()

    if not todo:
        return jsonify({'message': 'No user found'})
    todo.complete = True
    db.session.commit()
    return ({"message":"The task has been completed"})

@app.route("/todo/<todo_id>",methods=['DELETE'])
@token_required
def delete_todo(current_user,todo_id):
    todo = ToDo.query.filter_by(id=todo_id, user_id=current_user.id).first()
    if not todo:
        return jsonify(({'message': 'No task Found'}))
    db.session.delete(todo)
    db.session.commit()
    return jsonify(({'message': 'task has been deleted'}))



@app.route('/')
def home():
    return render_template('login.html')

if __name__ == '__main__':
    # with app.app_context():
    #     ToDo.__table__.drop(db.engine)
    #     print("User table dropped!")
    # with app.app_context():
    #     db.create_all()  # This will create the tables
    app.run(debug=True)

CORS(app)