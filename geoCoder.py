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

        uploaded_file=request.files["csvfile"] # read the csv file which was posted
        df=pd.read_csv(uploaded_file.filename) # read the file to a dataframe
        
        # check that there is a column in the csv with called 'address' or 'Address'
        if checkFileColumns(df) is True:
            #uploaded_file.save(secure_filename("uploaded"+uploaded_file.filename)) # save the file
            
            df["Latitude"]=[getLocation(address).latitude for address in df["Address"]]
            df["Longitude"]=[getLocation(address).longitude for address in df["Address"]]
            
            # use exception handling delete the file if it exists otherwise pass
            try:
                os.remove("geocodedAddress.csv")
            except:
                pass

            df.to_csv("geocodedAddress.csv",index=False) # save df to csv

            return render_template("index.html",btn="download.html",table=df.to_html(classes="tabs",header=True,index=False)) # show the index page but now with the html of download button embedded from download.html
    return render_template("index.html", text="Please ensure that there is an address column in your csv file!")

@app.route("/download")
def download():
    return send_file("geocodedAddress.csv",download_name="geocoded_Address.csv",as_attachment=True)

if __name__=="__main__":
    app.debug=True
    app.run()