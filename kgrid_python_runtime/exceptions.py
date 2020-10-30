import json
import werkzeug.exceptions as exceptions
import flask

error_handlers = flask.Blueprint('exceptions', __name__)
exception_prefix = 'Exception in python runtime'


@error_handlers.app_errorhandler(exceptions.HTTPException)
def handle_http_exception(e):
    response = e.get_response()
    response.data = json.dumps({
        'code': e.code,
        'name': e.name,
        'description': e.description,
    })
    response.content_type = 'application/json'
    print('Http Exception: ' + str(e))
    return response


@error_handlers.app_errorhandler(SyntaxError)
def handle_syntax_error(e):
    print('Syntax Error: ' + e.msg)
    return build_response(e, 400)


@error_handlers.app_errorhandler(Exception)
def handle_exception(e):
    print('Execution error: ' + str(e))
    return build_response(e, 400)


@error_handlers.app_errorhandler(KeyError)
def handle_key_error(e):
    print('Execution error: ' + str(e))
    return build_response(e, 400)


def build_response(e, code):
    resp = {
        'code': code,
        'name': type(e).__name__,
        'description': str(e),
    }
    return resp, code
