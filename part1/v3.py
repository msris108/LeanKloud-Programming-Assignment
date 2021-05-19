import pymongo
from datetime import date
from functools import wraps
from flask import Flask, request
from werkzeug.contrib.fixers import ProxyFix
from flask_restplus import Api, Resource, fields

# Initialising the Database
client 	= pymongo.MongoClient("mongodb://localhost:27017/")
db 		= client["workspace"]
col 	= db["todos"]

# Authorization
authorizations = {
	'apikey_rw' : {
		'type'  : 'apiKey',
		'in'	: 'header',
		'name'	: 'X-API-KEY'
	},
	'apikey_r' : {
		'type'  : 'apiKey',
		'in'	: 'header',
		'name'	: 'X-API-KEY'
	}
}

def token_required_R(f):
	@wraps(f)
	def decorated(*args, **kwargs):

		token = None

		if 'X-API-KEY' in request.headers:
			token = request.headers['X-API-KEY']

		if not token:
			return {'message' : 'Not Authorized'}, 401

		if token != 'rpermission':
			if token != 'rwpermission':
				return {'message' : 'Invalid token'}, 401

		print("TOKEN: {}".format(token))

		return f(*args, **kwargs)

	return decorated

def token_required_RW(f):
	@wraps(f)
	def decorated(*args, **kwargs):

		token = None

		if 'X-API-KEY' in request.headers:
			token = request.headers['X-API-KEY']

		if not token:
			return {'message' : 'Not Authorized'}, 401

		print("TOKEN: {}".format(token))

		if token != 'rwpermission':
			return {'message' : 'Invalid token'}, 401

		return f(*args, **kwargs)

	return decorated

# Instantiating the Flask App
app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)
api = Api(app, version='3.0', title='TodoMVC API',
    description='A simple TodoMVC API',
    authorizations = authorizations
)

# adding namespace '/todos' to the API
ns = api.namespace('todos', description='TODO operations')

# API Schema
todo = api.model('Todo', {
    '_id': fields.Integer(readonly=True, description='The task unique identifier'),
    'task': fields.String(required=True, description='The task details'),
    'status': fields.String(required=True, description='The task status'),
    'date': fields.Date(required=True, description='The task due date')
})

# Modelling thr TODO APP
class TodoDAO(object):
    def __init__(self):
        self.counter = col.count_documents({})
        self.todos = []

    def get(self, _id):
        todo = col.find_one({"_id" : _id})
        if todo is None:
            api.abort(404, "Todo {} doesn't exist".format(_id))
        else:
            return todo

    def create(self, data):
        todo = data
        todo['_id'] = self.counter = self.counter + 1
        col.insert_one(todo)
        return todo

    def update(self, _id, data):
        new_val = {"$set" : data}
        col.update_one({"_id" : _id}, new_val)

        return self.get(_id)

    def delete(self, _id):
        col.delete_one({"_id": _id})

    def get_all(self):
        todo_list = []
        todos = col.find({})
        for todo in todos:
            todo_list.append(todo)
        if len(todo_list) == 0:
            api.abort(404, "No Records")
        else:
            return todo_list

    def get_status(self, status):
        todo_list = []
        todos = col.find({"status" : status})
        for todo in todos:
            todo_list.append(todo)
        if len(todo_list) == 0:
            api.abort(404, "Todo with status: '{}' doesn't exist".format(status))
        else:
            return todo_list

    def get_date(self, date):
        todo_list = []
        todos = col.find({"date" : date})
        for todo in todos:
            todo_list.append(todo)
        if len(todo_list) == 0:
            api.abort(404, "Todo with due date: '{}' doesn't exist".format(date))
        else:
            return todo_list

    def get_overdue(self):
        todos = []
        todos_db = col.find({ "status": { "$regex": "Not Started|Finished" } })
        for i in todos_db:
            todos.append(i)

        today = date.today()
        todo_list = []
        for todo in todos:
            if todo['status'] == 'In Progress' or todo['status'] == 'Not Started':
                t = [int(i) for i in todo['date'].split('-')]
                if date(t[0], t[1], t[2]) < today:
                    todo_list.append(todo)
        if len(todo_list) == 0: 
            api.abort(404, "No Todo overdue today: {}".format(today))
        else:
            return todo_list

# Creating a instance of the TODO class DAO
DAO = TodoDAO()

# Controller Section
@ns.route('/')
class TodoList(Resource):
    '''Shows a list of all todos, and lets you to POST to add new todos'''
    @ns.doc('list_todos', security='apikey_r')
    @token_required_R
    @ns.marshal_list_with(todo)
    def get(self):
        '''List all todos'''
        return DAO.get_all()

    @ns.doc('create_todo', security='apikey_rw')
    @token_required_RW
    @ns.expect(todo)
    @ns.marshal_with(todo, code=201)
    def post(self):
        '''Create a new todo'''
        return DAO.create(api.payload), 201


@ns.route('/<int:_id>')
@ns.response(404, 'Todo not found')
@ns.param('_id', 'The task identifier')
class Todo(Resource):
    '''Show a single todo item and lets you delete it, update it'''
    @ns.doc('get_todo', security='apikey_r')
    @token_required_R
    @ns.marshal_with(todo)
    def get(self, _id):
        '''Fetch a given resource'''
        return DAO.get(_id)

    @ns.doc('delete_todo', security='apikey_rw')
    @token_required_RW
    @ns.response(204, 'Todo deleted')
    def delete(self, _id):
        '''Deletes a todo given its id'''
        DAO.delete(_id)
        return '', 204

    @ns.doc('update_todo', security='apikey_rw')
    @token_required_RW
    @ns.expect(todo)
    @ns.marshal_with(todo)
    def put(self, _id):
        '''Updates a todo given its id'''
        return DAO.update(_id, api.payload)

@ns.route('/<string:status>')
@ns.response(404, 'Todo not found')
@ns.param('status', 'The task status')
class TodoList(Resource):
    @ns.doc('get_todo_status', security='apikey_r')
    @token_required_R
    @ns.marshal_with(todo)
    def get(self, status):
        '''Fetches all todos for the given status'''
        return DAO.get_status(status)

@ns.route('/due/<string:date>')
@ns.response(404, 'No due todos')
@ns.param('date', 'The task due date')
class Due(Resource):
    @ns.doc('get_todo_due', security='apikey_r')
    @token_required_R
    @ns.marshal_with(todo)
    def get(self, date):
        '''Fetches all todos that are due given due date'''
        return DAO.get_date(date)

@ns.route('/overdue')
@ns.response(404, 'No overdue todos')
class Overdue(Resource):
    @ns.doc('get_todo_overdue', security='apikey_r')
    @token_required_R
    @ns.marshal_with(todo)
    def get(self):
        '''Fetches all todos that are overdue as of today'''
        return DAO.get_overdue()

@ns.route('/finished')
@ns.response(404, 'No todos finished')
class Overdue(Resource):
    @ns.doc('get_todo_finished', security='apikey_r')
    @token_required_R
    @ns.marshal_with(todo)
    def get(self):
        '''Fetches all todos that are finished'''
        return DAO.get_status('Finished')

# Creating the dummy instances of the tasks only to be run once

# DAO.create({
#     'task': 'Task 1', 
#     'status': 'Not Started',
#     'date': '2021-05-25'
#     })
# DAO.create({
#     'task': 'Task 2', 
#     'status': 'In Progress',
#     'date': '2021-05-20'
#     })
# DAO.create({
#     'task': 'Task 3', 
#     'status': 'Finished',
#     'date': '2021-05-18'
#     })
# DAO.create({
#     'task': 'Task 4', 
#     'status': 'Finished',
#     'date': '2021-05-22'
#     })
# DAO.create({
#     'task': 'Task 5', 
#     'status': 'Not Started',
#     'date': '2021-04-25'
#     })

if __name__ == '__main__':
    app.run(debug=True)