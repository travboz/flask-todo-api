from marshmallow import fields
import datetime
from datetime import datetime, timezone

import enum
import uuid
from flask import Flask, abort
from flask.views import MethodView
from flask_smorest import Api, Blueprint
from marshmallow import Schema

server = Flask(__name__)  # entry point to application

# hello world example in Flask
# @server.route("/hello")
# def hello():
#     return "hello"


# config object
class APIConfig:
    API_TITLE = "TODO API"
    API_VERSION = "v1"
    OPENAPI_VERSION = "3.0.3"
    OPENAPI_URL_PREFIX = "/"
    OPENAPI_SWAGGER_UI_PATH = "/docs"
    OPENAPI_SWAGGER_UI_URL = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    OPENAPI_REDOC_PATH = "/redoc"
    OPENAPI_REDOC_UI_URL = (
        "https://cdn.jsdelivr.net/npm/redoc@next/bundles/redoc.standalone.js"
    )


server.config.from_object(APIConfig)

api = Api(server)

todo = Blueprint("todo", "todo", url_prefix="/todo", description="TODO API")

# routes for todo
tasks = [
    {
        "id": uuid.UUID("1786c168-9300-4ae4-827a-1cee6436a154"),
        "created": datetime.now(timezone.utc),
        "completed": False,
        "task": "Create Flask API",
    }
]


class CreateTask(Schema):
    task = fields.String()  # "task is a String object"


class UpdateTask(CreateTask):
    completed = fields.Bool()


class Task(UpdateTask):
    id = fields.UUID()
    created = fields.DateTime()


class ListTasks(Schema):
    tasks = fields.List(fields.Nested(Task))


class SortByEnum(enum.Enum):
    task = "task"
    created = "created"


class SortDirectionEnum(enum.Enum):
    asc = "asc"
    desc = "desc"


class ListTasksParameters(Schema):
    order_by = fields.Enum(SortByEnum, load_default=SortByEnum.created)
    order = fields.Enum(SortDirectionEnum, load_default=SortDirectionEnum.asc)


@todo.route("/tasks")
class TodoCollection(MethodView):
    # model endpoints using methods

    @todo.arguments(ListTasksParameters, location="query")
    @todo.response(status_code=200, schema=ListTasks)
    def get(self, parameters):
        return {
            "tasks": sorted(
                tasks,
                key=lambda task: task[parameters["order_by"].value],
                reverse=parameters["order"] == SortDirectionEnum.desc,
            )
        }

    @todo.arguments(CreateTask)  # this is our input data for this (the POST) endpoint
    @todo.response(status_code=201, schema=Task)
    def post(self, task_payload):
        task_payload["id"] = uuid.uuid4()
        task_payload["created"] = datetime.now(timezone.utc)
        task_payload["completed"] = False
        task_payload.append(task_payload)
        return task_payload


@todo.route("/tasks/<uuid:task_id>")
class TodoTask(MethodView):

    @todo.response(status_code=200, schema=Task)
    def get(self, task_id):
        for task in tasks:
            if task["id"] == task_id:
                return task

        abort(404, f"Task with ID {task_id} not found.")

    @todo.arguments(UpdateTask)
    @todo.response(status_code=200, schema=Task)
    def put(self, payload, task_id):  # order matters in flask
        for task in tasks:
            if task["id"] == task_id:
                task["completed"] == payload["completed"]
                task["task"] == payload["task"]
                return task

        abort(404, f"Task with ID {task_id} not found.")

    @todo.response(status_code=204)
    def delete(self, task_id):
        for index, task in enumerate(tasks):
            if task["id"] == task_id:
                tasks.pop(index)
                return
        abort(404, f"Task with ID {task_id} not found.")


api.register_blueprint(todo)
