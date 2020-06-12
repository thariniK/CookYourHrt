from http import HTTPStatus

from flask import Blueprint, jsonify
from flask import request
from Exception.custom_exceptions import NoSchemaResultSet, URLNotPresent, URLGivesNotFound, ContentNotFound, NoRefinedResult, InvalidURL
import logging

from .extract import extractData

recipe_api = Blueprint('recipe_api', __name__)
logging.basicConfig(filename='error_log',level=logging.DEBUG)

@recipe_api.route('/recipe')
def getRecipeJSON():
    url = request.args.get('url')
    response = dict()
    errorResponse = ''
    errorCode = HTTPStatus.NOT_FOUND
    try:
        validateUrl(url)
        response = extractData(url)
    except URLNotPresent as unp:
        response = False
        errorResponse = unp.message
        errorCode = unp.code
    except InvalidURL as iu:
        response = False
        errorResponse = iu.message
        errorCode = iu.code
    except NoSchemaResultSet as nsrs:
        response = False
        errorResponse = nsrs.message
        errorCode = nsrs.code
    except URLGivesNotFound as ugnf:
        response = False
        errorResponse = ugnf.message
        errorCode = ugnf.code
    except ContentNotFound as cnf:
        response = False
        errorResponse = cnf.message
        errorCode = cnf.code
    except NoRefinedResult as nrr:
        response = False
        errorResponse = nrr.message
        errorCode = nrr.code
    except Exception as e:
        response = False
        logging.exception(e)
    if response:
        return jsonify({'status': 'success', 'result': response}), HTTPStatus.OK
    elif (response == False and errorResponse):
        return jsonify({'status': 'failure', 'result': errorResponse}), errorCode
    else:
        return jsonify({'status': 'failure', 'result': 'We couldn\'t fetch the recipe you\'re looking for'}), errorCode


def validateUrl(url):
    if url == None or len(url) == 0 or not isinstance(url, str):
        raise URLNotPresent
    elif (not "http:" in url and not "https:" in url):
        raise InvalidURL
    return True
