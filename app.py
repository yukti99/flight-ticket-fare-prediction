from flask import Flask, request,render_template
from flask_cors import cross_origin
import sklearn
import pickle
import pandas as pd 

app = Flask(__name__)
model = pickle.load(open("flights_rf.pkl","rb"))

@app.route("/")
@cross_origin()
def home():
    return render_template("index.html")

@app.route("/predict",methods=["GET","POST"])
@cross_origin()
def predict():
    if (request.method == "POST"):
        # get date of journey 
        dep_date = request.form["Dep_Time"]
        Journey_day = int(pd.to_datetime(dep_date, format="%Y-%m-%dT%H:%M").day)
        Journey_month = int(pd.to_datetime(dep_date, format ="%Y-%m-%dT%H:%M").month)

        # get departure and arrival dates from the page entered by the user
        dep_hours = int(pd.to_datetime(dep_date,format ="%Y-%m-%dT%H:%M").hour)
        dep_mins = int(pd.to_datetime(dep_date, format ="%Y-%m-%dT%H:%M").minute)

        arrival_date = request.form["Arrival_Time"]
        arrival_hours = int(pd.to_datetime(arrival_date, format ="%Y-%m-%dT%H:%M").hour)
        arrival_mins = int(pd.to_datetime(arrival_date, format ="%Y-%m-%dT%H:%M").minute)

        # get the duration of flight
        duration_hours = abs(arrival_hours - dep_hours)
        duration_mins = abs(arrival_mins - dep_mins )

        # getting the number of stops of the flight
        total_stops = int(request.form["stops"])

        # we will apply OneHotEncoding here
        # Flight options according to chosen dataset
        airline_names = {"Jet_Airways":0,"IndiGo":0,"Air_India":0,"Multiple_carriers":0,"SpiceJet":0,"Vistara":0,"GoAir":0,"Multiple_carriers_Premium_economy":0,"Jet_Airways_Business":0,"Vistara_Premium_economy":0,"Trujet":0}
        # find the airline name from the html form
        airline  = request.form['airline']
        airline_names[airline] = 1

        # Source of flight departure
        src_places={"Delhi":0,"Kolkata":0,"Mumbai":0,"Chennai":0,"Banglore":0}
        Source = request.form["Source"]        
        try:
            src_places[Source]=1
        except:
            src_places={"Delhi":0,"Kolkata":0,"Mumbai":0,"Chennai":0,"Banglore":0}

        # Destination of flight arrival
        dest_places={"Cochin":0,"Delhi":0,"Hyderabad":0,"Kolkata":0,"New_Delhi":0}
        dest = request.form["Destination"]     
        try:
            dest_places[dest]=1
        except:
            dest_places={"Cochin":0,"Delhi":0,"Hyderabad":0,"Kolkata":0,"New_Delhi":0}


        # use the model created to predict flight fare according to user inputs
        price_prediction = model.predict([[
            total_stops,Journey_day,Journey_month,dep_hours,dep_mins,
            arrival_hours,arrival_mins,duration_hours,duration_mins,

            airline_names["Air_India"], airline_names["GoAir"], airline_names["IndiGo"], airline_names["Jet_Airways"],
            airline_names["Jet_Airways_Business"],airline_names["Multiple_carriers"], airline_names["Multiple_carriers_Premium_economy"],
            airline_names["SpiceJet"], airline_names["Trujet"],airline_names["Vistara"], airline_names["Vistara_Premium_economy"],

            src_places["Chennai"],src_places["Delhi"],src_places["Kolkata"],src_places["Mumbai"],

            dest_places["Cochin"],dest_places["Delhi"],dest_places["Hyderabad"],dest_places["Kolkata"],dest_places["New_Delhi"]
            
        ]])
        # round the prediction upto 2 decimal values
        output = round(price_prediction[0],2)
        return render_template("index.html",price_prediction_text="Your Flight price is Rs. {}".format(output))
    
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
        
