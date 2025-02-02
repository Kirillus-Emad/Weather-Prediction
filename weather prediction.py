import os
from pgmpy.models import BayesianNetwork
from pgmpy.factors.discrete import TabularCPD
from pgmpy.inference import VariableElimination
from tkinter import *
from tkinter import messagebox

# Function to discretize continuous temperature and humidity form the entries 
def discretize_temperature(temp):
    if temp <= 10:
        return 0  # Cold
    elif temp <= 25:
        return 1  # Warm
    else:
        return 2  # Hot

def discretize_humidity(hum):
    if hum <= 40:
        return 0  # Low
    elif hum <= 70:
        return 1  # Medium
    else:
        return 2  # High


# Create the Bayesian Network model
model = BayesianNetwork([('Temperature', 'Outlook'), ('Humidity', 'Outlook'),('Temperature', 'Season'),
                        ('Humidity', 'Season'), ('Temperature', 'Wind')])

# Define the conditional probability distributions (CPDs)
cpd_temperature = TabularCPD(variable='Temperature', variable_card=3,
                             values=[[0.3], [0.4], [0.3]])  # Probabilities for Cold, Warm, Hot

cpd_humidity = TabularCPD(variable='Humidity', variable_card=3,
                          values=[[0.4], [0.3], [0.3]])  # Probabilities for Low, Medium, High

# Corrected Rain CPD with 6 values for combinations of Temperature and Humidity
cpd_outlook = TabularCPD(variable='Outlook', variable_card=2,
                      values=[[0.45, 0.35, 0.25, 0.65, 0.5, 0.35, 0.9 ,0.75, 0.65],  # Probabilities for Sunny 
                              [0.55, 0.65, 0.75, 0.35, 0.5, 0.65, 0.1 ,0.25, 0.35]],  # Probabilities for Rain 
                      evidence=['Temperature', 'Humidity'],
                      evidence_card=[3, 3])
cpd_season = TabularCPD(variable='Season', variable_card=4,
                      values=[[0.03, 0.1, 0.05, 0.05, 0.05, 0.05, 0.9 ,0.8, 0.7],  # Probabilities for summer
                              [0.8, 0.6, 0.5, 0.2, 0.05, 0.05, 0.025 ,0.025, 0.025], # Probabilities for winter
                              [0.07, 0.1, 0.15, 0.15, 0.7, 0.8, 0.025 ,0.075, 0.175], # Probabilities for spring
                              [0.1, 0.2, 0.3, 0.6, 0.2, 0.1, 0.05 ,0.1, 0.1]], # Probabilities for autumn
                      evidence=['Temperature', 'Humidity'],
                      evidence_card=[3, 3])
cpd_wind = TabularCPD(variable='Wind', variable_card=2,
                      values=[[0.15, 0.45, 0.6],     # NO Wind
                               [0.85, 0.55, 0.4]],   # wind
                      evidence=['Temperature'], 
                      evidence_card=[3])

# Add CPDs to the model
model.add_cpds(cpd_temperature, cpd_humidity, cpd_outlook,cpd_season, cpd_wind)

model.check_model()

inference = VariableElimination(model)


def predict_weather(temperature, humidity):
    # Set the evidence (Temperature and Humidity)
    evidenceO = {'Temperature': temperature, 'Humidity': humidity}
    evidenceS = {'Temperature': temperature, 'Humidity': humidity}
    evidenceW = {'Temperature': temperature}
    # Perform inference for outlook , season, and wind
    outlook_pred = inference.query(variables=['Outlook'], evidence=evidenceO)
    season_pred = inference.query(variables=['Season'], evidence=evidenceS)
    wind_pred = inference.query(variables=['Wind'], evidence=evidenceW)
    return outlook_pred,season_pred ,wind_pred

# handle button click
def on_predict_button_click():
    # Get the values from the inputs
    try:
        temp = float(temperature_entry.get())  
        hum = float(humidity_entry.get())  
    except ValueError:
        messagebox.showerror("Invalid Input", "Please enter valid numeric values for Temperature and Humidity.")
        return
    
    # Discretize the continuous values
    temp_discretized = discretize_temperature(temp)
    hum_discretized = discretize_humidity(hum)
    
    # Get the prediction results
    outlook_result,season_result ,wind_result = predict_weather(temp_discretized, hum_discretized)
    
    # Display the results 
    # we use (value) attribute as it's from DiscreteFactor type
    if outlook_result.values[1] >= 0.6:

        outlook_status = "Rain"
    elif outlook_result.values[1] < 0.6 and outlook_result.values[1] >= 0.5:
        outlook_status = "Might Rain"
    else:
        outlook_status ="Sunny"
    
    # Extracting the most probable season 
    season_probs = season_result.values  # Access the probabilities of each season
    season_labels = ['Summer', 'Winter', 'Spring', 'Autumn'] #labels arranged to correspond the probability
    max_prob_index = season_probs.argmax()  # Get the index of the highest probability
    season_status = season_labels[max_prob_index]  # Get the season label corresponding to the highest probability

    if wind_result.values[1] >= 0.6:
        wind_status = "Wind"
    elif wind_result.values[1] < 0.6 and wind_result.values[1] >= 0.5:
         wind_status = "May be"
    else:
        wind_status = "No Wind"

    # replace the label text to display the prediction
    result_label.config(text=f"Prediction:\noutlook: {outlook_status}\nWind: {wind_status}\nseason: {season_status}")

# image that represent the baysen structure
def open_image():

    image_path = r"G:\BNU\Knowledge\project\weather prediction\Base.png"  # Replace with your specific image path
    
    # Open the image
    os.startfile(image_path)

# create an object to start the GUI
win = Tk()
win.title("Weather Prediction app")
win.geometry('800x600')
win.config(bg='#1e1e1e')

# Creating input labels and fields

title_label = Label(win, text="Weather prediction",bg='#1e1e1e',font=('arial',25,'bold'),fg='#56B6C2')
title_label.place(x=240,y=40)

temperature_label = Label(win, text="Temperature",bg='#1e1e1e',font=('arial',14,'bold'),fg='#56B6C2')
temperature_label.place(x=90,y=150)


temperature_entry = Entry(win)
temperature_entry.place(x=240,y=155)

# celsius label of humidity
c_label = Label(win, text="°C",bg='#1e1e1e',font=('arial',14,'bold'),fg='#56B6C2')
c_label.place(x=370,y=150)


humidity_label = Label(win, text="Humidity",bg='#1e1e1e',font=('arial',14,'bold'),fg='#56B6C2')
humidity_label.place(x=100,y=220)


humidity_entry = Entry(win)
humidity_entry.place(x=240,y=225)

# percent label of humidity
perc_label = Label(win, text="%",bg='#1e1e1e',font=('arial',14,'bold'),fg='#56B6C2')
perc_label.place(x=371,y=225)

# Prediction button that will display the prediction
predict_button = Button(win, text="Predict Weather",bg='#56B6C2',fg='white',font=('arial',9,'bold'),
                command=on_predict_button_click, activebackground='#56B6C2', 
                activeforeground='white',relief='flat',bd=0)

predict_button.place(x=260,y=289,width=100,height=35)


# basic button that will display the baysen structure
base_button = Button(win, text="Basic structure",bg='#56B6C2',fg='white',font=('arial',9,'bold'),
                     command=open_image, activebackground='#56B6C2', activeforeground='white',
                     relief='flat',bd=0)

base_button.place(x=392,y=289,width=100,height=35)


# Result label
result_label = Label(win, text="Prediction: ",bg='#1e1e1e',fg='#56B6C2',font=('arial',14,'bold'),width=17)
result_label.place(x=270,y=350)

# Start the GUI loop
win.mainloop()