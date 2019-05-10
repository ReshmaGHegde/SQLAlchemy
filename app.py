from matplotlib import style
style.use('fivethirtyeight')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, inspect, func, desc
from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)
Base.classes.keys()
# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################
""" results = session.query(Station.name).all()
for record in list(results):
    print(record) """
@app.route("/")
def welcome():
    return (
		f"Available route address with base URL http://127.0.0.1:5000 <br/>"
		f"--------------------------------------------------------------------------<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/YYYY-MM-DD<br/>"
		f"/api/v1.0/YYYY-MM-DD/YYYY-MM-DD<br/>"
		f"---------------------------------------------------------------------------"
    )

@app.route('/api/v1.0/precipitation')
def precipitation():
       	session = Session(engine)
        results=session.query(Measurement.date,Measurement.prcp.label( "precipitation")).all()
        prcp_data=[]
        for date,precipitation in results:
            prcp_dict={}
            prcp_dict[date] = precipitation
            # prcp_dict['precipitation']=precipitation
            prcp_data.append(prcp_dict)
        return jsonify(prcp_data)
    
@app.route('/api/v1.0/stations')
def stations():
    	session = Session(engine)
    	results=session.query(Station).all()
    	station_data=[]
    	for row in results:
        	station_dict={}
        	station_dict['station_id']=row.station
        	station_dict['name']=row.name
        	station_dict['latitude']=row.latitude
        	station_dict['longitude']=row.longitude
        	station_dict['elevation']=row.elevation
        	station_data.append(station_dict)
    	return jsonify(station_data)

@app.route('/api/v1.0/tobs')
# function to get temprature data for a yearfrom last date
def tobs():
    # calculate the last date in the dataset
    session = Session(engine)
    date_last=session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    # print(date_last)
    # calcuating the date year agofrom last date
    date_year_ago=dt.datetime.strptime(date_last,'%Y-%m-%d').date()-dt.timedelta(days=365)
    # print(date_year_ago)
    # # Perform a query to retrieve the data and precipitation scores
    temprature_data=session.query(Measurement.date,Measurement.tobs).filter(Measurement.date>= date_year_ago).all()
    temp_obs=[]
    for row in temprature_data:
        temp_dict={}
        temp_dict[row.date]=row.tobs
        # temp_dict['temprature']=row.tobs
        temp_obs.append(temp_dict)
    return jsonify(temp_obs)

@app.route('/api/v1.0/<string:start>')
def date1(start):
	session = Session(engine)
	min_maxlist1=[]
	results1 = session.query(func.min(Measurement.tobs).label("min"), func.avg(Measurement.tobs).label("average"),func.max(Measurement.tobs).label("max")).filter(func.strftime("%Y-%m-%d",Measurement.date) >= start).all()
	for row in results1:
		minmax_dict1={}
		minmax_dict1['Minimum Temprature']=row.min
		minmax_dict1['Average Temprature']=row.average
		minmax_dict1['Maximum Temprature']=row.max
		min_maxlist1.append(minmax_dict1)
	return jsonify(min_maxlist1)
	
@app.route('/api/v1.0/<string:start>/<string:end>')
def date(start,end):
	session = Session(engine)
	min_maxlist=[]
	results=session.query(func.min(Measurement.tobs).label("min"), func.avg(Measurement.tobs).label("average"), func.max(Measurement.tobs).label("max")).filter(func.strftime("%Y-%m-%d",Measurement.date) >= start).filter(func.strftime("%Y-%m-%d",Measurement.date) <= end).all()
	for row in results:
		minmax_dict={}
		minmax_dict['Minimum Temprature']=row.min
		minmax_dict['Average Temprature']=row.average
		minmax_dict['Maximum Temprature']=row.max
		min_maxlist.append(minmax_dict)
	return jsonify(min_maxlist)

if __name__ == '__main__':
    app.run(debug=True)