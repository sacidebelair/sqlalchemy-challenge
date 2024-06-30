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
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
#################################################


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
app= Flask(__name__)



#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    return "hello"

@app.route("/api/v1.0/precipitation")
def precipitation():
    most_recent_date = session.query(func.max(Measurement.date)).scalar()
    one_year_ago = dt.datetime.strptime(most_recent_date, "%Y-%m-%d") - dt.timedelta(days=365)
    precipitation_data= session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >=   one_year_ago).all()
    session.close()
    pr={date:prcp for date,prcp in precipitation_data}
    return jsonify(pr)

@app.route("/api/v1.0/stations")
def stations():
    active_stations = session.query(
    Measurement.station,
    func.count(Measurement.station).label('station_count')
).group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).all()
    session.close()
    stations=list(np.ravel(active_stations))
    return jsonify(stations)
    
@app.route("/api/v1.0/tobs")
def tobs():
    most_recent_date = session.query(func.max(Measurement.date)).scalar()
    one_year_ago = dt.datetime.strptime(most_recent_date, "%Y-%m-%d") - dt.timedelta(days=365)
    most_active_station = session.query(Measurement.station, func.count(Measurement.station))\
                    .group_by(Measurement.station)\
                    .order_by(func.count(Measurement.station).desc())\
                    .first()[0]
    # Query the last 12 months of temperature data for the most active station()
    tobs_data = session.query(Measurement.tobs).filter(Measurement.station == most_active_station).filter(Measurement.date >= one_year_ago).all()
    session.close()
    tobs=list(np.ravel(tobs_data))
    return jsonify(tobs)
    
         

if __name__ == '__main__':
    app.run()
