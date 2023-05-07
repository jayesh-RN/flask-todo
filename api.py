from flask import Flask
from flask_restful import Resource, Api , reqparse , abort , fields , marshal_with
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
api=Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db=SQLAlchemy(app)

class TodOModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task = db.Column(db.String(100), nullable=False)
    summary = db.Column(db.String(200), nullable=False)
    
with app.app_context():
    db.create_all()  

# todos = {
#     1: {'task': 'build an API','summary':'this is a summary'},
#     2: {'task': 'task2','summary':'this is a summary'},
#     3: {'task': 'task2','summary':'this is a summary'},
# }

task_post_args = reqparse.RequestParser()
task_post_args.add_argument("task", type=str, help="Task is required", required=True)
task_post_args.add_argument("summary", type=str, help="Summary is required", required=True)

task_put_args = reqparse.RequestParser()
task_put_args.add_argument("task", type=str)
task_put_args.add_argument("summary", type=str)


resource_fields = {
    'id': fields.Integer,
    'task': fields.String,
    'summary': fields.String
}
    

class ToDoList(Resource):
    def get(self):
        tasks = TodOModel.query.all()
        todos ={}
        for task in tasks:
            todos[task.id] = {'task': task.task, 'summary': task.summary}
        return todos    

class ToDo(Resource):
    @marshal_with(resource_fields)
    def get(self, todo_id):
        task = TodOModel.query.filter_by(id=todo_id).first()
        if not task:
            abort(409,message="Task already exists")
        return task
        
    @marshal_with(resource_fields)
    def post(self, todo_id):
        args = task_post_args.parse_args()
        task = TodOModel.query.filter_by(id=todo_id).first()
        if task:
            abort(409,message="Task already exists")
        todo =TodOModel(id=todo_id, task=args['task'], summary=args['summary'])
        db.session.add(todo)
        db.session.commit()
        return todo, 201
    
    @marshal_with(resource_fields)    
    def put(self, todo_id):
        args = task_put_args.parse_args()
        task = TodOModel.query.filter_by(id=todo_id).first()
        if not task:
            abort(409,message="Task already exists")
        if args['task']:
            task.task = args['task']
        if args['summary']:
            task.summary = args['summary']
        db.session.commit()
        return task        
           
    
    def delete(self, todo_id):
        task = TodOModel.query.filter_by(id=todo_id).first()
        db.session.delete(task)
        return 'Todo Deleted', 204         

api.add_resource(ToDo,'/todo/<int:todo_id>')
api.add_resource(ToDoList,'/todos')

if __name__ == '__main__':
    app.run(debug=True)