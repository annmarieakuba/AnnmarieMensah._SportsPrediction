# -*- coding: utf-8 -*-
"""AnnmarieMensah_.SportsPrediction.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1UA4egb-QSU7aTtfX1x65xhXv4nPZeDaC
"""

from google.colab import drive
drive.mount('/content/drive')

import pandas as pd
import numpy as np
from sklearn.impute import SimpleImputer as si
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, VotingRegressor, AdaBoostRegressor
from sklearn.model_selection import RandomizedSearchCV, KFold, GridSearchCV
from sklearn.tree import DecisionTreeRegressor
import xgboost as xgb
from sklearn.preprocessing import LabelEncoder
from scipy.stats import norm

"""Import datasets for training the model and testing the model with new data"""

legacy_dataset = pd.read_csv('/content/drive/MyDrive/legacymaleplayers.csv')
players_dataset = pd.read_csv('/content/drive/MyDrive/players_22-1-3.csv')

players_dataset.head()

players_dataset.info(verbose=True, show_counts=True)

"""#Preprocessing the data

Remove the clearly useless variables according to the description of the attributes in the dataset.
"""

# take out url and id values because they are categorised as useless
useless = ['player_face_url', 'club_logo_url', 'club_flag_url', 'nation_logo_url', 'nation_flag_url', 'sofifa_id', 'player_url','gk', 'rb', 'rcb', 'cb', 'lcb', 'lb', 'rwb', 'rdm', 'cdm', 'ldm', 'lwb', 'rm', 'rcm', 'cm', 'lcm', 'lm', 'ram', 'cam', 'lam', 'rw', 'rf', 'cf', 'lf', 'lw', 'rs', 'st', 'ls']
players_dataset.drop(columns=useless, inplace=True)
players_dataset

"""Remove attributes with 30% or more missing values"""

null_attributes = players_dataset.columns[players_dataset.count()/18944 < 0.7]
players_dataset.drop(columns=null_attributes, inplace=True)

players_dataset.shape

players_dataset

"""Extract and Show all categorical attributes based on the data types"""

categorical_df = players_dataset.select_dtypes(include=['object'])
categorical_df

"""Select and show only the attributes that are numerical attributes"""

numerical_df = players_dataset.select_dtypes(exclude=['object'])
numerical_df

# Show to check which attributes have null values in the categorical dataset
categorical_df.info(verbose=True, show_counts=True)

"""Select the attributes with null values based on the count of non-null rows and impute them using a forward fill"""

# Select categorical attributes with null values
columns_to_fill = categorical_df.columns[categorical_df.count() < 18944]
columns_to_fill

# Forward fill attributes with na values
categorical_df[columns_to_fill] = categorical_df[columns_to_fill].fillna(method='ffill')





# Check to see that there are no null values
categorical_df.info(verbose=True, show_counts=True)

"""Create an object to encode the categorical variables and fit_transform all the cells inside of the data frame that contains just categorical variables"""

encoder = LabelEncoder()
categorical_df= categorical_df.apply(encoder.fit_transform)
categorical_df

"""Create object and impute the data frame containing numerical attributes to get rid of null values"""

# Impute numerical attributes
imputer = si(strategy='median')

# checking if null values exist in numerical attributes
numerical_df.info(verbose=True, show_counts=True)

imputed_numerical = imputer.fit_transform(numerical_df)
imputed_numerical_df = pd.DataFrame(imputed_numerical, columns=numerical_df.columns)
imputed_numerical_df

"""Combine both the dataframes of the the categorical and numerical attributes into a single data frame"""

new_legacy_dataset = pd.concat([imputed_numerical_df, categorical_df], axis=1)
new_legacy_dataset

# Confirm that there are no null values
new_legacy_dataset.info(verbose=True, show_counts=True)

"""#Feature Engineering
**Select the needed attributes to train the regression model with**

Here, I picked attributes with a correlation of more than |0.5| to ensure that we get the attributes with a strong correlation.
"""

correlation_vals = new_legacy_dataset.corr()['overall'] # check correlation of other attributes with overall
corr_attributes = correlation_vals[abs(correlation_vals.values) >= 0.5]  # which attributes have a strong correlation with the overall rating
corr_attributes.index

"""**Create new dataframe of needed attributes**"""

needed_att_legacy = new_legacy_dataset[corr_attributes.index]
needed_att_legacy

"""**Scale dataset inputs only, by separating output attribute from the rest of the dataset**

This is to prevent overall score from being scaled. It was separated from the rest of the dataset and stored in a separate variable (overall_att) before going ahead to scale the input attributes
"""

overall_att = needed_att_legacy.overall

model_legacy = overall_att.drop(columns='overall')
model_legacy

"""Create standard scalar object"""

sc = StandardScaler()

# Ensure model_legacy is a DataFrame
model_legacy = pd.DataFrame(model_legacy)

# scale input values of data
scaled_data = sc.fit_transform(model_legacy)
ready_legacy_players= pd.DataFrame(scaled_data, columns=model_legacy.columns)
ready_legacy_players

"""#Model development and testing

Using the test/train split and splitting the X(input attributes) and Y(Output attribute) to train and test the models
"""

X = ready_legacy_players
Y = overall_att

# test/train split for cross-validation
Xtrain, Xtest, Ytrain, Ytest = train_test_split(X, Y, test_size=0.2, random_state=42)

Xtrain.shape

"""**Train, test, and measure accuracy of RandomForestRegressor model with training split of dataset and testing split of dataset**"""

# Instantiate Regression model
rf_model = RandomForestRegressor(n_estimators=2000, max_depth=1000, n_jobs=-1, random_state=42)

# train the regression model
rf_model.fit(Xtrain, Ytrain)

# use model for prediction
model_prediction = rf_model.predict(Xtest)

mean_abs_err_results = mean_absolute_error(Ytest, model_prediction)
mean_abs_err_results

"""**Train, test and measure accuracy of AdaBoostRegressor model with training split of dataset and testing split of dataset**

Create an AdaBoostRegressor with a base model as a decisiontreeregressor
"""

base_model = DecisionTreeRegressor(max_depth=1000)

adaboost_regressor = AdaBoostRegressor(base_model, n_estimators=1000, random_state=42)

adaboost_regressor.fit(Xtrain, Ytrain)

ada_predict = adaboost_regressor.predict(Xtest)
mae = mean_absolute_error(Ytest, ada_predict)
mae

"""**Train, test, and measure accuracy of Gradient Boosting model with training split of dataset and testing split of dataset**

Create and train a GradientBoosting model (gb_model) Use the test data-set ( Xtest ) to make predictions and then check the accuracy using mean absolute error
"""

# Instantiate GradientBoosting model
gb_model = GradientBoostingRegressor(n_estimators=50, random_state=42)

# Train the GradientBoosting model
gb_model.fit(Xtrain, Ytrain)

# use GradientBoosting model for prediction
gb_prediction = gb_model.predict(Xtest)

gb_mean_abs_err = mean_absolute_error(Ytest, gb_prediction)
gb_mean_abs_err

"""Train, test, and measure accuracy of XGboost model with training split of dataset and testing split of dataset"""

# Create model that looks to minimize mean squared error as much as possible
xg_model = xgb.XGBRegressor(objective="reg:squarederror", n_estimators=50)

xg_model.fit(Xtrain, Ytrain)

# predict with model
xg_prediction = xg_model.predict(Xtest)

xg_mean_abs_err = mean_absolute_error(Ytest, xg_prediction)
xg_mean_abs_err

"""Train, test and measure accuracy of VotingRegressor ensemble using all previously used models"""

# Create model instance
soft_ensemble = VotingRegressor(estimators=[
    ('randomforest', rf_model),
    ('gradientboosing', gb_model),
    ('xgb', xg_model)
], weights=[0.5, 0.1, 0.4])

soft_ensemble.fit(Xtrain, Ytrain)

ensemble_prediction = soft_ensemble.predict(Xtest)

ensemble_mean_abs_err = mean_absolute_error(Ytest, ensemble_prediction)
ensemble_mean_abs_err

"""Comparing the models"""

print("RandomForest Model: ", mean_abs_err_results)
print("ADA Model: ", mae)
print("GradientBoosting Model: ", gb_mean_abs_err)
print("XGBBoost Model: ", xg_mean_abs_err)
print("SoftEnsemble Model: ", ensemble_mean_abs_err)

"""From observation, the AdaBoostRegressor Model is the more accurate one so it's the preference to fine tune

#Fine tuninig
"""

n_estimators = [int(x) for x in np.linspace(start = 100, stop = 2000, num = 10)]
max_depth = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
min_samples_split = [2, 5, 10, 15, 20]
param_grid = {'n_estimators':n_estimators, 'max_depth':max_depth, 'min_samples_split':min_samples_split}

cv=KFold(n_splits=3)

#random_search = GridSearchCV(rf_model,param_grid=param_grid,cv=cv,scoring="neg_mean_absolute_error")

n_estimators = [1000, 2000, 4000]
learning_rate = [0.1, 0.2, 0.3]
param_grid = {'n_estimators':n_estimators,'learning_rate':learning_rate}

random_search = GridSearchCV(adaboost_regressor,param_grid=param_grid,cv=cv,scoring="neg_mean_absolute_error", n_jobs=3)

random_search.fit(X, Y)

print('best estimator: ', random_search.best_estimator_)
print('best param: ', random_search.best_params_)

base_model_2 = DecisionTreeRegressor(max_depth=1000)
model_2 = AdaBoostRegressor(base_model_2, n_estimators=2000, learning_rate=0.2, random_state=42)
model_2.fit(Xtrain, Ytrain)

model_prediction_2 = model_2.predict(Xtest)

mean_abs_err_results_2 = mean_absolute_error(Ytest, model_prediction_2)
mean_abs_err_results_2

"""#Testing

An attempt to fix a bug
"""

import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
import pickle



if 'overall' in legacy_dataset.columns:
    Y_train = legacy_dataset['overall']
    X_train = legacy_dataset.drop(columns='overall')
else:
    raise ValueError("'overall' column not found in the legacy_dataset DataFrame")

print("Columns in X_train before training:")
print(X_train.columns)


numerical_columns = X_train.select_dtypes(include=['number']).columns.tolist()

imputer = SimpleImputer(strategy='mean')
X_train_imputed = X_train.copy()
X_train_imputed[numerical_columns] = imputer.fit_transform(X_train[numerical_columns])

sc = StandardScaler()
X_train_scaled = X_train_imputed.copy()
X_train_scaled[numerical_columns] = sc.fit_transform(X_train_imputed[numerical_columns])

Train the model
model = LinearRegression()
model.fit(X_train_scaled[numerical_columns], Y_train)


with open('model_2.pkl', 'wb') as f:
    pickle.dump(model, f)


with open('trained_feature_names.pkl', 'wb') as f:
    pickle.dump(numerical_columns, f)

print("Model and feature names saved successfully.")

import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
import pickle


with open('model_2.pkl', 'rb') as f:
    model_2 = pickle.load(f)

with open('trained_feature_names.pkl', 'rb') as f:
    trained_feature_names = pickle.load(f)


if 'overall' in df_22.columns:
    Y_new = df_22['overall']
    X_new = df_22.drop(columns='overall')
else:
    raise ValueError("'overall' column not found in the new dataset DataFrame")

print("Columns in the new dataset (X_new):")
print(X_new.columns.tolist())

print("\nTrained feature names:")
print(trained_feature_names)

# Identify missing columns
missing_columns = [col for col in trained_feature_names if col not in X_new.columns]
print("\nMissing columns in X_new:")
print(missing_columns)

# Identify extra columns in X_new
extra_columns = [col for col in X_new.columns if col not in trained_feature_names]
print("\nExtra columns in X_new:")
print(extra_columns)

X_new = imputed_df_22.drop(columns='overall')
Y_new = imputed_df_22['overall']

# Filter the data again
filtered_trained_feature_names = [col for col in trained_feature_names if col in X_new.columns]

print("\nFiltered trained feature names (used for prediction):")
print(filtered_trained_feature_names)

# I want to select only the numerical data
X_new = X_new[filtered_trained_feature_names]

# Impute again
imputer = SimpleImputer(strategy='mean')
X_new_imputed = pd.DataFrame(imputer.fit_transform(X_new), columns=X_new.columns)


sc = StandardScaler()
X_new_scaled = pd.DataFrame(sc.fit_transform(X_new_imputed), columns=X_new.columns)

import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
import pickle


with open('model_2.pkl', 'rb') as f:
    model_2 = pickle.load(f)

with open('trained_feature_names.pkl', 'rb') as f:
    trained_feature_names = pickle.load(f)

# Ensure the 'overall' column is in the new dataset
if 'overall' in df_22.columns:
    Y_new = df_22['overall']
    X_new = df_22.drop(columns='overall')
else:
    raise ValueError("'overall' column not found in the new dataset DataFrame")


print("Columns in the new dataset (X_new):")
print(X_new.columns.tolist())

print("\nTrained feature names:")
print(trained_feature_names)


missing_columns = [col for col in trained_feature_names if col not in X_new.columns]
print("\nMissing columns in X_new:")
print(missing_columns)


for col in missing_columns:
    X_new[col] = 0  # using 0 for now


X_new = X_new[trained_feature_names]

imputer = SimpleImputer(strategy='mean')
X_new_imputed = pd.DataFrame(imputer.fit_transform(X_new), columns=X_new.columns)


sc = StandardScaler()
X_new_scaled = pd.DataFrame(sc.fit_transform(X_new_imputed), columns=X_new.columns)


players_22_prediction = model_2.predict(X_new_scaled)


from sklearn.metrics import mean_absolute_error
mae = mean_absolute_error(Y_new, players_22_prediction)
print(f"Mean Absolute Error on the new dataset: {mae}")

print("Predictions for the new dataset:")
print(players_22_prediction)

"""#Save Model"""

import pickle

# Scaler object as file to scale user input with the necessary parameters
pickle.dump(sc, open('/content/drive/MyDrive/Colab Notebooks/new_scaler_parameters.pkl', 'wb'))

# Model object as file to predict the scaled values after user input
pickle.dump(model_2, open('/content/drive/MyDrive/Colab Notebooks/new_player_ratings_model.pkl', 'wb'))

