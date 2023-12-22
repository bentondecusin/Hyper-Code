import json
import sqlite3
import pandas as pd
from flask import Flask, request
import os
from sqlite3 import connect

import sys

from fig11a_mini import get_query_output

# import db

# TODO enable sessions

UPLOAD_FOLDER = os.path.join("static", "uploads")
# Define allowed files
ALLOWED_EXTENSIONS = {"csv"}

COLOR_SET = [
    "rgba(255, 10, 10, 0.2)",
    "rgba(10, 255, 10, 0.2)",
    "rgba(10, 10, 255, 0.2)",
    "rgba(75, 192, 192, 0.2)",
    "rgba(54, 162, 235, 0.2)",
    "rgba(153, 102, 255, 0.2)",
    "rgba(201, 203, 207, 0.2)",
]

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# TODO enable session based df & connection
# Global Var
df = pd.DataFrame()
sql_cmd = ""
conn: sqlite3.Connection = connect(":memory:", check_same_thread=False)
# chart_config = {}
backdoor = {}
rslt: pd.DataFrame = None

# TODO delete this
# df = pd.read_csv(UPLOAD_FOLDER + "/german.csv")
# df.to_sql(name="german", con=conn)
# for var in df.columns:
#     backdoor[var] = ["age", "sex"]
# fig8a_mini.set_backdoor(backdoor)
# TODO UP HERE


# generalized response formats
def success_upload_response(data, header, code=200):
    header.append(len(df))
    return (
        json.dumps({"success": True, "data": data, "header": header}),
        code,
    )


# generalized response formats
def success_response(data, code=200):
    return json.dumps({"success": True, "data": data}), code


def failure_response(message, code=404):
    return json.dumps({"success": False, "error": message}), code


# Plot config
def gen_chart_config(data):
    chart_config = {
        "indexAxis": "y",
        "type": "bar",
        "data": data,
        "options": {
            "scales": {
                "y": {
                    "beginAtZero": True,
                    "title": "testing",
                },
                "xAxes": [{"stacked": True}],
                "yAxes": [
                    {
                        "stacked": False,
                        "ticks": {
                            "beginAtZero": True,
                        },
                    }
                ],
            }
        },
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
def gen_chart_data(qry_rslt: pd.DataFrame):
    # TODO assumption: COUNT SQL qry w/o group by only gives one row.
    yLabels = list(qry_rslt.columns)
    datasets = [
        {
            "label": "Original",
            "data": list(qry_rslt.iloc[0].tolist()),
            "backgroundColor": [COLOR_SET[0]],
            "borderWidth": 1,
            "maxBarThickness": 20,
        }
    ]
    # for i in range(len(qry_rslt.iloc)):
    #     row = qry_rslt.iloc[i]
    #     datasets.append()
    data = {"labels": yLabels, "datasets": datasets}

    return data


def append_bar_chart_config(chart_config, newSeries, newLabel, idx):
    # chart_config not passed in as a reference

    # no change to labels, only append to datasets
    # a single dataset contain xSeries for each yLabel

    return {
        "label": newLabel,
        "data": newSeries,
        "backgroundColor": [COLOR_SET[idx % len(COLOR_SET)]],
        "borderWidth": 1,
        "maxBarThickness": 20,
    }


def new_data(chart_config, newSeries, newLabel):
    # chart_config not passed in as a reference
    print(chart_config)
    idx = len(chart_config["data"]["datasets"])
    # no change to labels, only append to datasets
    # a single dataset contain xSeries for each yLabel
    return {
        "label": newLabel,
        "data": newSeries,
        "backgroundColor": [COLOR_SET[idx % len(COLOR_SET)]],
        "borderWidth": 1,
        "maxBarThickness": 20,
    }


@app.route("/api/upload_csv", methods=["POST"])
def upload_csv():
    try:
        f = request.files.get("file")
        data_filename = f.filename
        tablename = data_filename.split(".")[0]
        f.save(os.path.join(app.config["UPLOAD_FOLDER"], data_filename))
        # read csv
        if "txt" in data_filename:
            globals()["df"] = pd.read_csv(
                os.path.join(app.config["UPLOAD_FOLDER"], data_filename),
                encoding="unicode_escape",
                dtype=str,
                delimiter=" ",
            ).apply(lambda x: x.astype(str).str.lower())
        else:
            globals()["df"] = pd.read_csv(
                os.path.join(app.config["UPLOAD_FOLDER"], data_filename),
                encoding="unicode_escape",
                dtype=str,
            ).apply(lambda x: x.astype(str).str.lower())
        df.columns = map(str.lower, df.columns)
        try:
            df.to_sql(name=tablename, con=conn)
        except:
            pass
        # for var in df.columns:
        #     backdoor[var] = ["age", "sex"]
        # fig8a_mini.set_backdoor(backdoor)
        return success_upload_response(
            data=df.head(200).to_html(classes=["table-fixed", "border-separate"]),
            header=list(df),
            code=200,
        )

    except Exception as e:
        print(e)
        return failure_response("failed to upload")


@app.route("/api/SQL", methods=["POST"])
def sql_query():
    try:
        sql_cmd = request.headers.get("qry")
        plot_mode = request.headers.get("plotMode")
        # do query result and return visualized result
        global rslt
        rslt = pd.read_sql(sql_cmd, conn)
        print(rslt.head())

        # COUNT
        if "COUNT" in sql_cmd.upper():
            print("COUNT")

            chart_data = gen_chart_data(rslt)
            chart_config = gen_chart_config(chart_data)
            print(chart_config)
            # print(json.dumps(chart_config))

            #

        elif "AVG" in sql_cmd.upper():
            chart_data = gen_chart_data(rslt)
            chart_config = gen_chart_config(chart_data)
        else:
            return failure_response("COUNT or AVG queries only")

        # print(chart_data)
        return success_response(json.dumps(chart_config))

    except pd.io.sql.DatabaseError as e:
        return failure_response(message=str(e), code=400)
    except Exception as e:
        return failure_response(e)


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
    # NOTE the REST API can be modified based on need. See more in documentation

    AT = ""
    prelst = []
    prevallst = []
    plot_mode = request.headers.get("plotMode")
    print(request.headers.keys)
    q_type = request.headers.get("qt")
    postlst = request.headers.get("postlst").split(",")
    postvallst = request.headers.get("postvallst").split(",")
    Ac = request.headers.get("Ac").split(",")
    c = request.headers.get("c").split(",")
    AT = request.headers.get("AT", "")
    print(AT)
    g_Ac_lst = ["*"]
    interference = ""
    blocks = {}
    # TODO make the error log more detailed. See examples in SQL call

    # NOTE Sample usage, may use different procedural call, or other implementations of get_query_output
    bar_to_compare = []
    chart_data = gen_chart_data(rslt)
    chart_config = gen_chart_config(chart_data)
    for i in range(len(Ac)):
        prob = get_query_output(
            df=df,
            q_type=q_type,
            AT=AT,
            prelst=prelst,
            prevallst=prevallst,
            postlst=postlst,
            postvallst=postvallst,
            Ac=[Ac[i]],
            c=[c[i]],
            g_Ac_lst=g_Ac_lst,
            interference=interference,
            blocks=blocks,
        )
        newSeries = [prob * len(df)]
        bar_to_compare.append(
            append_bar_chart_config(
                chart_config, newSeries, "Update {} to {}".format(Ac[i], c[i]), i + 1
            )
        )
    new_chart = gen_chart_config(chart_data)
    for new_bar in bar_to_compare:
        new_chart["data"]["datasets"].append(new_bar)

    return success_response(json.dumps(new_chart))


@app.route("/api/henlo")
def hello_world():
    return "<p>henlo</p>"


if __name__ == "__main__":
    app.run(debug=True)
