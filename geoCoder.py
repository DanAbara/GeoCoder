""" 
Date: 19/06/2021
Author: DA  

"""
from flask import Flask, render_template, request, send_file
from werkzeug.utils import secure_filename
import pandas as pd
from geopy.geocoders import ArcGIS
import os

app=Flask(__name__)

# check if column name address exists
def checkFileColumns(df):
    if "address" in df.columns or "address".title() in df.columns:
        return True
    else:
        return False  

# for geocoding supplied addresses
def getLocation(address):
    geoLocator=ArcGIS()
    location=geoLocator.geocode(address)
    return location

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/success", methods=["POST","GET"])
def success():
    if request.method=="POST":

        # read and save uploaded csv and convert to dataframe
        uploaded_file=request.files["csvfile"] 
        uploaded_file.save(secure_filename(uploaded_file.filename)) 
        df=pd.read_csv(uploaded_file.filename) 

        # create and populate lon/lat columns if address column exists
        if checkFileColumns(df) is True:
            try:
                df["Latitude"]=[getLocation(address).latitude for address in df["Address"]]
            except:
                df["Latitude"]="Incomplete address"
            
            try:
                df["Longitude"]=[getLocation(address).longitude for address in df["Address"]]
            except:
                df["Longitude"]="Incomplete address"

            # delete file from any previous geocoding task
            try:
                os.remove("geocodedAddress.csv")
            except:
                pass

            # save dataframe to csv       
            df.to_csv("geocodedAddress.csv",index=False) 
            
            # show only first 5 rows if the no of rows is greater than 5
            if df.index.max() > 5:
                tableshown=df.loc[0:4].to_html(classes="tabs",header=True,index=False)
            else:
                tableshown=df.to_html(classes="tabs",header=True,index=False)
            
            # return index page with download button and text
            return render_template("index.html",
                                    btn="download.html",
                                    table=tableshown,
                                    text2="Only the first 5 rows are shown. Use the button below to download the entire CSV file.") 
    
    return render_template("index.html", text="Please ensure that there is an address column in your csv file!")

@app.route("/download")
def download():
    return send_file("geocodedAddress.csv",download_name="geocoded_Address.csv",as_attachment=True)

if __name__=="__main__":
    app.debug=True
    app.run()