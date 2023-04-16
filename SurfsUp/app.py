# Import the dependencies.
import numpy as np
import pandas as pd
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///C:/Users/44739/Documents/Module 10 Challenge SQLAlchemy/Starter_Code/Resources/hawaii.sqlite")


# reflect an existing database into a new model

Base = automap_base()

# reflect the tables

Base.prepare(engine, reflect=True)

# Save references to each table

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
@app.route("/")
def main():
    return (
        f"Welcome to the Climate App.<br>"
        f"Available Routes:<br>"
        f"/api/v1.0/precipitation<br>"
        f"/api/v1.0/stations<br>"
        f"/api/v1.0/tobs<br>"
        f"/api/v1.0/start<br>"
        f"/api/v1.0/start/end<br>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():

# # Calculate the date one year from the last date in data set.
    query_date = dt.date(2017, 8, 23)-dt.timedelta(days=365)

 # Perform a query to retrieve the data and precipitation scores
    prcp_query = session.query(Measurement.date, Measurement.prcp).\
    filter(Measurement.date >= query_date).all()

    # Create a dictionary.
    Prcp_data = []
    message = {'message': 'This is the data of precipitation in inches in the past 12 months'}
    Prcp_data.append(message)
    for x in prcp_query:
        prcpDict = {'date':x.date, 'precipitation(inches)':x.prcp}
        Prcp_data.append(prcpDict)

    return jsonify(prcpData)


@app.route("/api/v1.0/stations")
def stations():
    #Query all stations
    station_query = session.query(Station.station, Station.name).all()

    #Convert to a list
    All_stations = list(np.ravel(stations))


    return jsonify(All_stations)


@app.route("/api/v1.0/tobs")
def tobs():
    # Query the dates and temperature observations of the most-active station for the previous year of data
    
    last_data = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    previous_year = (dt.datetime.strptime(last_data[0],'%Y-%m-%d') - dt.timedelta(days=365)).strftime('%Y-%m-%d')

    result =   session.query(Measurement.date, Measurement.tobs).\
                filter(Measurement.date >= previous_year).order_by(Measurement.date).all()
    
    #Convert to a list
        
    tobs_data = []

    for date, tobs in result:
        tobs_dict = {}
        tobs_dict[date] = tobs
        tobs_data.append(tobs_dict)

    return jsonify(tobs_data)

@app.route("/api/v1.0/<start>")
def start(start):

    start_time = dt.datetime.strptime(start, "%Y-%m-%d")

    result = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_time).all()
    
    session.close()
    tobsall = []

    for min,avg,max in result:
        tobs_dict = {}
        tobs_dict["Min"] = min
        tobs_dict["Average"] = avg
        tobs_dict["Max"] = max
        tobsall.append(tobs_dict)
        
    return jsonify(tobsall)

@app.route('/api/v1.0/<start>/<end>')
def start_end(start,end):
    start_time = dt.datetime.strptime(start, "%Y-%m-%d")
    end_time = dt.datetime.strptime(end, "%Y-%m-%d")
    queryresult = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_time).\
        filter(Measurement.date <= end_time).all()

    session.close()

    tobsall = []
    for min,avg,max in queryresult:
        tobs_dict = {}
        tobs_dict["Min"] = min
        tobs_dict["Average"] = avg
        tobs_dict["Max"] = max
        tobsall.append(tobs_dict)

    return jsonify(tobsall)


if __name__ == '__main__':
    app.run(debug=True)



