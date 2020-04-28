from http import HTTPStatus

from flask import Blueprint, jsonify
from flask import request

from .extract import extractData

recipe_api = Blueprint('recipe_api', __name__)

@recipe_api.route('/recipe')
def getRecipeJSON():
    url = request.args.get('url')
    if len(url) == 0 or not isinstance(url, str):
        return jsonify({'status': 'failure', 'result': 'Please provide a recipe url'}), HTTPStatus.BAD_REQUEST
    try:
        response = extractData(url)
    except:
        response = False
    if response:
        return jsonify({'status': 'success', 'result': response}), HTTPStatus.OK
    else:
        return jsonify({'status': 'failure', 'result': 'we couldn\'t fetch the recipe you\'re looking for'}), HTTPStatus.INTERNAL_SERVER_ERROR
