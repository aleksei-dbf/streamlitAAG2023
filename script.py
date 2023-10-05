import streamlit as st
import pandas as pd
import numpy as np
import joblib

# Load the model from the file
st.header("ML prediction of the embodied carbon of the structure")
# model = joblib.load('model_RF.pkl')
uploaded_file = st.file_uploader('Upload a pickle file', type='pkl')
if uploaded_file is not None:
    model = joblib.load(uploaded_file)

    # Create a function to take user inputs
    st.write('Provide your inputs:')
    Floors = st.slider('Floors', 2, 19, 5)
    X = st.slider('X', 5.0, 10.0, 6.0, 0.1)
    Y = st.slider('Y', 5.0, 10.0, 6.0, 0.1)
    # ConstructionType = st.slider('ConstructionType', 0, 10, 1)
    ConstructionType_options = ['Steel+Timber', 'Steel+Concrete', 'Timber', 'Concrete']
    ConstructionType = st.selectbox('Material', ConstructionType_options)

    # Convert the selected string option to a numerical value
    construction_type_mapping = {
        'Steel+Timber': 0,
        'Steel+Concrete': 1,
        'Timber': 2,
        'Concrete': 3
    }
    ConstructionType = construction_type_mapping[ConstructionType]
    # Floor_Height = st.sidebar.slider('Floor Height', 0, 10, 1)
    Floor_Height = st.slider('Floor height', 3.0, 4.5, 3.0, 0.1)
    Area_m2 = st.slider('Area m2', 700, 9000, 20000)

    # Store a dictionary into a data frame
    user_data = {'Floors': Floors,
                    'X': X,
                    'Y': Y,
                    'ConstructionType': ConstructionType,
                    'Floor Height': Floor_Height,
                    'Area m2': Area_m2}

    features = pd.DataFrame(user_data, index=[0])

    carbon_coefficient_steel = st.sidebar.text_input('Carbon Coefficient Steel', '1.13')  # Default value of '0.0'
    carbon_coefficient_timber = st.sidebar.text_input('Carbon Coefficient Timber', '0.43')
    carbon_coefficient_concrete = st.sidebar.text_input('Carbon Coefficient Concrete', '0.175')
    carbon_coefficient_reinforcement = st.sidebar.text_input('Carbon Coefficient Reinforcement', '1.99')
    material_sourcing_options = ['Local', 'Global']
    material_sourcing_coefficient = st.sidebar.selectbox('The source of material', material_sourcing_options)
    material_sourcing_mapping = {'Local': 0.032, 'Global': 0.183}
    material_sourcing_coefficient = material_sourcing_mapping[material_sourcing_coefficient]
    carbon_coefficient_steel  = float(carbon_coefficient_steel) + float(material_sourcing_coefficient)
    carbon_coefficient_timber  = float(carbon_coefficient_timber) + float(material_sourcing_coefficient)
    carbon_coefficient_concrete  = float(carbon_coefficient_concrete) + float(material_sourcing_coefficient)



    # Store the user input into a variable
    # user_input = get_user_input()

    # Set a subheader and display the user input

    # st.write(features)

    # Create a form for submission
    with st.form(key='prediction_form'):
        st.write("Click 'Submit' to make a prediction.")
        submitted = st.form_submit_button('Submit')

        # Prediction logic when the form is submitted
        if submitted:
            embodied_carbon = 0
            # Predict the output and store it into a variable
            prediction = model.predict(features) # kg
            print(prediction)
            if ConstructionType == 0: #"Steel+Timber"
                embodied_carbon = prediction * float(carbon_coefficient_steel)
                embodied_carbon += 0.24 * Area_m2 *600 * float(carbon_coefficient_timber)
                
            elif ConstructionType == 1: #"Steel+Concrete"
                embodied_carbon = prediction * float(carbon_coefficient_steel)
                embodied_carbon += 0.15 * Area_m2 *2400 * float(carbon_coefficient_concrete)
                reinforcement_weight = 0.15* Area_m2 * 100
                embodied_carbon += reinforcement_weight * float(carbon_coefficient_reinforcement)
            elif ConstructionType == 2: # Timber
                embodied_carbon = prediction * float(carbon_coefficient_timber)
                embodied_carbon += 0.24 * Area_m2 *600 * float(carbon_coefficient_timber)
            elif ConstructionType == 3: # Concrete
                embodied_carbon = prediction * float(carbon_coefficient_concrete)
                embodied_carbon += 0.15 * Area_m2 *2400 * float(carbon_coefficient_concrete)
                reinforcement_weight = 0.15* Area_m2 * 100 + prediction / 2400 * 200
                embodied_carbon += reinforcement_weight * float(carbon_coefficient_reinforcement)
            st.subheader('Prediction:')
            st.write(round(float(embodied_carbon / 1000), 1), 'Tonne CO2 total')
            st.write(round(float(embodied_carbon  /Area_m2), 1), 'KG CO2 per GIA(m2)')