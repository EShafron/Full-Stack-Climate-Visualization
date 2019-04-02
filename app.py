from flask import Flask, jsonify

# ======== Code from Juypter Notebook to generate Query Data ======= #
import numpy as np
import pandas as pd

import datetime as dt

# Python SQL toolkit and Object Relational Mapper
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, distinct, inspect

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

# Perform a query to retrieve the data and precipitation scores
date_min = dt.datetime(2016, 8, 22)

q=session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= date_min).all()

# Convert to dictionary
rain_data=pd.DataFrame(q)

rain_dict={}
for i in np.arange(len(rain_data)):
    rain_dict[rain_data.iloc[i,0]]=rain_data.iloc[i,1]
rain_dict

# Distinct Stations
distinct_stations=session.query(distinct(Station.name)).all()

# Last 12 months temperature query
last_12=session.query(Measurement.tobs).filter(Measurement.station=='USC00519281').\
    filter(Measurement.date >= date_min).all()

# Flatten query results
last_12=list(np.ravel(last_12))

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    return (
        f"Welcome to da kine Hawaii temperatures~<br/><br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/><br/>"
        f"The following take user due inputs in the form YYYYMMDD:<br/><br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return the precipitation data as json"""

    # Convert the query results to a Dictionary using date as the key and prcp as the value.
    # Return the JSON representation of your dictionary.

    return jsonify(rain_dict)

@app.route("/api/v1.0/stations")
def stations():
    """Return the stations as a json list"""
    # Convert the query results to a Dictionary using date as the key and prcp as the value.
    # Return the JSON representation of your dictionary.

    return jsonify(distinct_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    """Return the last 12 months of temperature data as a json list"""
    # Convert the query results to a Dictionary using date as the key and prcp as the value.
    # Return the JSON representation of your dictionary.

    return jsonify(last_12)

# Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
# When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
# When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.


@app.route("/api/v1.0/<start>")
def start_range(start):
    """ Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
        When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
        When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive."""


    # Calculate Temperature Function from Starter Book
    # This function called `calc_temps` will accept start date and end date in the format '%Y-%m-%d' 
    # and return the minimum, average, and maximum temperatures for that range of dates
    # http://127.0.0.1:5000/api/v1.0/'2017-01-01'/'2017-06-01'

    # session.remove()
    session = Session(engine)

    start_input=dt.datetime(int(str(start)[0:4]),int(str(start)[4:6]),int(str(start)[6:8]))

    def calc_temps(start_date, end_date=dt.datetime.today()):

        """TMIN, TAVG, and TMAX for a list of dates.
        
        Args:
            start_date (string): A date string in the format %Y-%m-%d
            end_date (string): A date string in the format %Y-%m-%d
            
        Returns:
            TMIN, TAVE, and TMAX
        """
        
        return session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
            filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()

    temp_stats=calc_temps(start_input)

    return jsonify(temp_stats)


@app.route("/api/v1.0/<start>/<end>")
def date_range(start,end):
    """ Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
        When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
        When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive."""


    # Calculate Temperature Function from Starter Book
    # This function called `calc_temps` will accept start date and end date in the format '%Y-%m-%d' 
    # and return the minimum, average, and maximum temperatures for that range of dates
    # http://127.0.0.1:5000/api/v1.0/'2017-01-01'/'2017-06-01'

    # session.remove()
    session = Session(engine)

    start_input=dt.datetime(int(str(start)[0:4]),int(str(start)[4:6]),int(str(start)[6:8]))
    end_input=dt.datetime(int(str(end)[0:4]),int(str(end)[4:6]),int(str(end)[6:8]))

    def calc_temps(start_date, end_date):

        """TMIN, TAVG, and TMAX for a list of dates.
        
        Args:
            start_date (string): A date string in the format %Y-%m-%d
            end_date (string): A date string in the format %Y-%m-%d
            
        Returns:
            TMIN, TAVE, and TMAX
        """
        
        return session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
            filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()

    temp_stats=calc_temps(start_input,end_input)

    return jsonify(temp_stats)

if __name__ == "__main__":
    app.run(debug=True)
