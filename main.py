from flask import Flask
import random, string

from content.send_response import recipe_api

app = Flask(__name__)

app.config['JSON_AS_ASCII'] = False
app.register_blueprint(recipe_api, url_prefix='/v1')

if __name__ == "__main__":  # Makes sure this is the main process
    app.run( # Starts the site
        host='0.0.0.0',  # EStablishes the host, required for repl to detect the site
        port=random.randint(2000, 9000)  # Randomly select the port the machine hosts on.
    )   
