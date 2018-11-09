from flask import Flask, render_template, redirect
import scraper
from ski_resort import Base, SkiResort
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy_utils import create_database, database_exists
from config import un, pw, uri, port

conn_string = f'mysql://{un}:{pw}@{uri}:{port}/snow_report'
if not database_exists(conn_string):
	create_database(conn_string)
engine = create_engine(conn_string)
Base.metadata.create_all(engine)
session = Session(bind=engine)

app = Flask(__name__)

@app.route("/")
def home():

	# Return template and data
	return render_template("index.html")


@app.route("/scrape")
def scrape():
	scraped_resorts = scraper.scrape_page()
	resort_list = []
	scrape_ts = datetime.now()
	for k, v in scraped_resorts.items():
		resort_list.append(SkiResort(
			resort_name=k,
			open_status=v['open_status'],
			inches_24_hr=v['new_snow_24_hr'],
			inches_72_hr=v['new_snow_72_hr'],
			open_lift_pct=v['open_lift_pct'],
			open_trail_pct=v['open_trail_pct'],
			scrape_ts=scrape_ts
			))

	session.add_all(resort_list)
	session.commit()

	# Return template and data
	return redirect('/')


if __name__ == "__main__":
	app.run(debug=True)