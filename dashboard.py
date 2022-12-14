
import dash
from dash import dcc
from dash import html
import pandas as pd
import mariadb
import numpy
from sqlalchemy import create_engine

engine = create_engine('mariadb+mariadbconnector://AbelGB08:agb08@localhost:3306/ina226testdb')

mydb = mariadb.connect (
        host="localhost",
        user="AbelGB08",
        password="agb08",
        database="ina226testdb"
)

mycursor = mydb.cursor()

sql = 'select * from ina226 where date >= "2022-12-07 18:42:06" and date <= "2022-12-07 18:45:05";'
data = pd.read_sql_query(sql, engine)
app = dash.Dash(__name__)

app.layout = html.Div (
	children = [
		html.H1(children="DASHBOARD",
		className="title"),
		dcc.Graph (
			figure = {
				"data": [
					{
						"x": data["date"],
						"y": data["amps"],
						"type": "lines",
					}
				],  "layout": {"title": "Amps over time"},
			},
		),
	]
)


if __name__ == "__main__":
	app.run_server(debug=True)
