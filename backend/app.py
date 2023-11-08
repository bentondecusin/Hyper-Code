import json
import pandas as pd
from flask import Flask, request
import os
# import db

# TODO enable sessions 

UPLOAD_FOLDER = os.path.join('static', 'uploads')
# Define allowed files
ALLOWED_EXTENSIONS = {'csv'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

df = pd.DataFrame()
 
# generalized response formats
def success_response(data, code=200):
    return json.dumps({"success": True, "data": data}), code

def failure_response(message, code=404):
    return json.dumps({"success": False, "error": message}), code

@app.route("/api/upload_csv",  methods=["POST"])
def upload_csv():
    f = request.files.get('file')
    data_filename = f.filename
    try:
        f.save(os.path.join(app.config['UPLOAD_FOLDER'], data_filename))
        # read csv
        df = pd.read_csv(os.path.join(app.config['UPLOAD_FOLDER'], data_filename), encoding='unicode_escape')

        return success_response(df.to_html())
    except:
        return failure_response()



@app.route("/api/SQL/",  methods=["POST"])
def sql_query(s):
    print(s)
    # do query result and return visualized result

    # TODO
    return success_response()


@app.route("/api/henlo")
def hello_world():
    return "<p>henlo</p>"

if __name__ == '__main__':
    app.run(debug=True)