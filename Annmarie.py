import streamlit as st

import pandas as pd

import numpy as np

import pickle

from sklearn.ensemble import GradientBoostingRegressor

from sklearn.metrics import mean_absolute_error, mean_squared_error



# Load the trained model

model = joblib.load('new_player_ratings_model.pkl')

# Function to predict the rating
def predict_rating(input_data):

    features = pd.array (input_data).reshape(1, -1)
    rating = model. predict (features)[0]
    return rating

# Streamlit App
def main():
    st.title('FIFA Player Rating Prediction' )

    st.write('Enter player details to predict their rating.')


    columns = ['potential', 'value_eur', 'wage_eur', 'passing', 'dribbling',
'movement _reactions', 'mentality_composure']

    player_details = []
    for _ in columns:

        player_details.append(st.number_input(f'Enter (col)', step=1))

#Prediction

    if st.button('Predict Rating'):
        rating = predict_rating(player_details)
        st. success(f'Predicted Rating: {rating:.2f}')

if __name__ == '__main__':
    main()
