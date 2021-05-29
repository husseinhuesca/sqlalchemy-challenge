#Imports
from flask import Flask, jsonify
import numpy as np
import pandas as pd
import sqlalchemy
import datetime as dt
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from sqlalchemy import and_

#Engines and Database
Climateengine = create_engine("sqlite:///Resources/hawaii.sqlite")
ClimateDB = automap_base()
ClimateDB.prepare(Climateengine, reflect = True)
ClimateDBMeasurement = ClimateDB.classes.measurement
ClimateDBStation = ClimateDB.classes.station
session = Session(Climateengine)

#Set up Flask
app = Flask(__name__)

#Create Flask Routes
@app.route("/")
def intro():
    return(
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>")  
    
#/api/v1.0/precipitation. Convert the query results to a dictionary using date as the key and prcp as the value.
# Return the JSON representation of your dictionary.
@app.route("/api/v1.0/precipitation")    
def precipitation():
    mostrecentdata = dt.date(2017,8,23) - dt.timedelta(days = 365)
    last_day = session.query(ClimateDBMeasurement.date).order_by(ClimateDBMeasurement.date.desc()).first()
    climateprecip = session.query(ClimateDBMeasurement.date, ClimateDBMeasurement.prcp).\
        filter(ClimateDBMeasurement.date > mostrecentdata).order_by(ClimateDBMeasurement.date).all()
    precipitation_data = []
    for cont in climateprecip:
        data = {}
        data['date'] = climateprecip[0]
        data['prcp'] = climateprecip[1]
        precipitation_data.append(data)
    return jsonify(precipitation_data)

#/api/v1.0/stations. Return a JSON list of stations from the dataset.
@app.route("/api/v1.0/stations")
def stations():
    ClimateActiveStations = (session.query(ClimateDBMeasurement.station, 
    func.count(ClimateDBMeasurement.station)).\
    group_by(ClimateDBMeasurement.station).order_by(func.count(ClimateDBMeasurement.station).desc()).all())
    stations_data = []
    for cont in ClimateActiveStations:
        data = {}
        data['stations'] = ClimateActiveStations[0]
        data['observations'] = ClimateActiveStations[1]
        stations_data.append(data)
    return jsonify(stations_data)

#/api/v1.0/tobs. Query the dates and temperature observations of the most active station for the last year of data.
# Return a JSON list of temperature observations (TOBS) for the previous year.

@app.route("/api/v1.0/tobs")
def tobs():
    ClimateTobs = session.query(ClimateDBMeasurement.station, ClimateDBMeasurement.tobs).\
    filter(ClimateDBMeasurement.station == "USC00519281")
    tobslist = []
    for cont in ClimateTobs:
       dict = {}
       dict["Most Active Station"] = ClimateTobs[0]
       dict["tobs"] = ClimateTobs[1]
       tobslist.append(dict)                             
    return jsonify(tobslist)
    
#/api/v1.0/<start> and /api/v1.0/<start>/<end>.
# Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
#When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
#When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.                                                            

@app.route("/api/v1.0/<start>")
def tempstart(start):
    climatetempstart =   session.query(ClimateDBMeasurement.date, func.max(ClimateDBMeasurement.tobs), \
                        func.min(ClimateDBMeasurement.tobs), func.avg(ClimateDBMeasurement.tobs)).\
                        filter(ClimateDBMeasurement.date >= start).\
                        group_by(ClimateDBMeasurement.date).all()
    toblistliststart = []
    for date, max, min, avg in climatetempstart:
        dict = {}
        dict["Date"] = date
        dict["TMax"] = max 
        dict["TMin"] = min
        dict["TAvg"] = avg
        
        toblistliststart.append(dict)
    return jsonify(toblistliststart)               
                            
@app.route("/api/v1.0/<start>/<end>")
def tempstartend(start,end):
    climatetempstartend =  session.query(ClimateDBMeasurement.date, func.max(ClimateDBMeasurement.tobs), \
                        func.min(ClimateDBMeasurement.tobs), func.avg(ClimateDBMeasurement.tobs)).\
                        filter(and_(ClimateDBMeasurement.date >= start, ClimateDBMeasurement.date <= end)).\
                        group_by(ClimateDBMeasurement.date).all()
    toblistliststartend = []
    for date, max, min, avg in climatetempstartend:
        dict = {}
        dict["Date"] = date
        dict["TMax"] = max 
        dict["TMin"] = min
        dict["TAvg"] = avg
        
        toblistliststartend.append(dict)
    return jsonify(toblistliststartend)       
                                 
if __name__ == '__main__':
     app.run(debug=True)                            