import json
import pandas as pd
from flask import Flask, request
import os
from sqlite3 import connect

import sys
 
import fig8a_mini 

# import db

# TODO enable sessions 

UPLOAD_FOLDER = os.path.join('static', 'uploads')
# Define allowed files
ALLOWED_EXTENSIONS = {'csv'}

COLOR_SET = [
        'rgba(255, 99, 132, 0.2)',
        'rgba(255, 159, 64, 0.2)',
        'rgba(255, 205, 86, 0.2)',
        'rgba(75, 192, 192, 0.2)',
        'rgba(54, 162, 235, 0.2)',
        'rgba(153, 102, 255, 0.2)',
        'rgba(201, 203, 207, 0.2)'
        ]

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# TODO enable session based df & connection
# Global Var
df = pd.DataFrame()
conn = connect(':memory:', check_same_thread=False)
chart_config = {}
backdoor={}
q_type='count'

#TODO delete this
# df=pd.read_csv(UPLOAD_FOLDER+'/german.csv')
# df.to_sql(name='german', con=conn)
# for var in df.columns:
#     backdoor[var]=['age','sex']
# fig8a_mini.set_backdoor(backdoor)
#TODO UP HERE



# generalized response formats
def success_response(data, code=200):
    return json.dumps({"success": True, "data": data}), code

def failure_response(message, code=404):
    return json.dumps({"success": False, "error": message}), code

# Plot config
def gen_chart_config(data):
    globals()['chart_config'] = {
        'type': 'bar',
        'data': data,
        'options': {
            'scales': {
            'y': {
                'beginAtZero': True,
                'title': 'testing'
                }
            }
        }
    }
    print(chart_config)
    return chart_config

## JS config example
# const labels = ['count credit', 'avg credit']
# const data = {
#   labels: labels,
#   datasets: [{
#     label: 'Original',
#     data: [65, 59],
#     backgroundColor: [
#       'rgba(255, 159, 64, 0.2)',
#     ],
#     borderColor: [
#       'rgb(255, 159, 64)',
#     ],
#     borderWidth: 1
#   },
#   {
#     label: 'Updated',
#     data: [60, 100],
#     backgroundColor: [
#       'rgba(255, 99, 132, 0.2)',
#     ],
#     borderColor: [
#       'rgb(255, 99, 132)',
#     ],
#     borderWidth: 1
#   }]
# };
def gen_chart_data(qry_rslt:pd.DataFrame):
    # TODO assumption: COUNT SQL qry w/o group by only gives one row.
    yLabels = list(qry_rslt.columns)
    datasets = [{
            'label': 'Original',
            'data': list(qry_rslt.iloc[0].tolist()),
            'backgroundColor': [COLOR_SET[0]],
            'borderWidth': 1
        }]
    # for i in range(len(qry_rslt.iloc)): 
    #     row = qry_rslt.iloc[i]
    #     datasets.append()
    data = {
        'labels': yLabels,
        'datasets': datasets
    }
    
    return data

def append_bar_chart_config(chart_config, newSeries, newLabel):
    # chart_config not passed in as a reference
    print(chart_config)
    idx = len(chart_config['data']['datasets'])
    # no change to labels, only append to datasets
    # a single dataset contain xSeries for each yLabel
    chart_config['data']['datasets'].append({
        'label': newLabel,
        'data': newSeries,
        'backgroundColor': [COLOR_SET[idx % len(COLOR_SET)]],
        'borderWidth': 1
    })
    globals()['chart_config'] = chart_config
    return chart_config

@app.route("/api/upload_csv",  methods=["POST"])
def upload_csv():
    try:
        f = request.files.get('file')
        data_filename = f.filename
        tablename = data_filename.split(".")[0]
        f.save(os.path.join(app.config['UPLOAD_FOLDER'], data_filename))
        # read csv
        globals()['df'] = pd.read_csv(os.path.join(app.config['UPLOAD_FOLDER'], data_filename), encoding='unicode_escape')
        df.to_sql(name=tablename, con=conn)
        for var in df.columns:
            backdoor[var]=['age','sex']
        fig8a_mini.set_backdoor(backdoor)
        

        return success_response(df.head(200) .to_html())

    except:
        return failure_response("failed to upload")



@app.route("/api/SQL",  methods=["POST"])
def sql_query():
    sql_cmd = request.headers.get('qry')

    # do query result and return visualized result

    # TODO More types

    rslt:pd.DataFrame = pd.read_sql(sql_cmd, conn)
    print(rslt)

    # COUNT
    if 'COUNT' in sql_cmd:
        print("COUNT")
        # 
        chart_data = gen_chart_data(rslt)
        
        print(rslt)
        globals()['chart_config'] = gen_chart_config(chart_data)
        print(chart_config)
        # print(json.dumps(chart_config))

        # 
    else:
        chart_data = gen_chart_data(rslt)
        globals()['chart_config'] = gen_chart_config(chart_data)
    
    # TODO what if analysis 
    # get_query_output(df,q_type,AT,prelst,prevallst,postlst,postvallst,Ac,c,g_Ac_lst,interference, blocks)

    # print(chart_data)
    return success_response(json.dumps(chart_config))

@app.route("/api/whatif_qry", methods=["POST"])
def whatif_query():
    # AT: Any,
    # prelst: Any,
    # prevallst: Any,
    # postlst: Any,
    # postvallst: Any,
    # Ac: Any,
    # c: Any,
    # g_Ac_lst: Any,
    # interference: Any,
    # blocks: Any

    AT=''
    prelst=[]
    prevallst=[]
    postlst=['credit']
    postvallst=[1]
    # Ac=['status']
    # c=['1.0']
    Ac = request.headers.get('Ac').split(',')
    c = request.headers.get('c').split(',')
    g_Ac_lst=['*']
    interference=''
    blocks={}
    # TODO More types
    prob = fig8a_mini.get_query_output(df,q_type,AT,prelst,prevallst,postlst,postvallst,Ac,c,g_Ac_lst,interference,blocks)

    newSeries = [prob * len(df)]
    globals()['chart_config'] = append_bar_chart_config(chart_config, newSeries, "Update {} to {}".format(Ac, c))

    return success_response(json.dumps(globals()['chart_config']))


@app.route("/api/henlo")
def hello_world():
    return "<p>henlo</p>"

if __name__ == '__main__':
    app.run(debug=True)