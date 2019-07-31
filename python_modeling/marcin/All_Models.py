# -*- coding: utf-8 -*-
"""
Created on Tue Jul 30 15:25:47 2019

@author: grzechu
"""

######################################### Imports ######################
# Basic 
import pandas as pd
import numpy as np

#Modeling/evaluatiing/Plots
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from math import sqrt
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

#Ridge Regression
from sklearn.linear_model import RidgeCV
from sklearn.linear_model import Ridge

#Lasso
from sklearn.linear_model import LassoCV
from yellowbrick.regressor import AlphaSelection
from sklearn import linear_model

#XGBoost 
from xgboost import XGBRegressor
from xgboost import plot_importance
from sklearn.feature_selection import SelectFromModel

#KNN
from sklearn import neighbors

###################################### FUNCTIONS ########################
# Histogram to compare predcited vs. actual
def lineplot_compare(actual, y_pred, title, filename=None):
    fig, ax = plt.subplots()
    ax.plot(actual, color = 'blue')
    ax.plot(y_pred, color = 'red')
    ax.legend(['Real', 'Predicted'])
    ax.title.set_text(title)
    if (filename!=None):
        fig.savefig(filename)
    plt.show()
   # return y_pred

def hist_diff_test(y_test,y_train, pred_test, pred_train, title):
    #histogram of difference for TRAIN
    fig, ax = plt.subplots()
    y_train = pd.DataFrame(y_train)
    y_train['new']=y_train.index
    pred_reg = pd.DataFrame(pred_train)
    pred_reg.index=y_train['new'].values
    y_train = y_train.drop('new',axis=1)
    pred_reg = pred_reg.rename(columns={0:'predicted'})
    x =pd.DataFrame(y_train['assessland']-pred_reg['predicted'])
    x = x.rename(columns={0:'difference'})
    done = pd.concat([x,y_train,pred_reg],axis=1)
    
    p = x['difference'].values
    type(p)
    ax.hist(p, bins='auto', range=(-75000, 75000))
    
    #histogram of difference for TEST
    y_test = pd.DataFrame(y_test)
    y_test['new']=y_test.index
    pred_reg = pd.DataFrame(pred_test)
    pred_reg.index=y_test['new'].values
    y_test = y_test.drop('new',axis=1)
    pred_reg = pred_reg.rename(columns={0:'predicted'})
    x =pd.DataFrame(y_test['assessland']-pred_reg['predicted'])
    x = x.rename(columns={0:'difference'})
    done = pd.concat([x,y_test,pred_reg],axis=1)
    
    p = x['difference'].values
    type(p)
    ax.hist(p, bins='auto', range=(-75000, 75000))
    ax.title.set_text(title)
    ax.legend(['Test Error', 'Train Error'])
    
def show_coefs(coefs, title):
    largest=coefs.nlargest(5,'coef_value')
    smallest=coefs.nsmallest(5,'coef_value')
    both=pd.concat([largest,smallest], axis=0)
    # make a bar up and down
    baseline = 1
    plt.bar(range(len(both['coef_value'])),[x-baseline for x in both['coef_value']])
    plt.xticks(np.arange(10), (both.index.values))
    plt.xticks(rotation=90)
    plt.suptitle(title, fontsize=15)
    plt.show()

# you gives the function X and y and it chooses the best predictors and gives 
# a list of predictors and append the target variable at the end
def gradient_boosting(X,y):
    model = XGBRegressor()
    model.fit(X, y)
    # plot feature importance
    plot_importance(model)
    plt.show()
    # Create data frame where columns are sorted by their importance
    results=pd.DataFrame()
    results['columns']=X.columns
    results['importances'] = model.feature_importances_
    results.sort_values(by='importances',ascending=False,inplace=True)  
    # All variables where importance is bigger than 0
    # Cuz we want use those predictors 
    import_not_0=results[results['importances']>0]
    ## So since now we have a list with variables which importance is above 0.0
    list_variables=import_not_0['columns'].values.tolist()
    # Return 
    return list_variables

######################################### Read the data ######################
############# Read transformed data (dummies scaled)
data = pd.read_csv("pluto5_samplestd.csv")

######################## TARGET IS: ASSESSLAND #############################
data=data.drop(['bldgarea', 'numfloors', 'unitsres', 'unitstotal','bldgfront', 'bldgdepth', 
                'ext.1','proxcode.1', 'proxcode.2',
                'yearbuilt', 'yearalter','income', 'assesstot' ],axis=1)

X = data.drop(['assessland'], axis=1)
y = data['assessland']#.values.reshape(-1,1)

X_train, X_test , y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=1)
#############################################################################
############################### MODELING ######################################
#############################################################################


################################### RIDGE REGRESSION #########################

####### a) looking for best parameters
#Run it to find the best alpha
#Set a ranges for alphas
alphas_range=np.arange(1, 400, 10)
# Crossvalidate for the best alphas
regr_cv = RidgeCV(alphas=alphas_range)
#Visualize alpha 
visualizer = AlphaSelection(regr_cv)
# Fit the linear regression
visualizer.fit(X, y)
g = visualizer.poof()
visualizer.alpha_ # best parameter shows up to be 81


####### b) Implement Ridge Regression
ridge = Ridge(alpha = visualizer.alpha_) # this parameter is choosen by RidgeCV
ridge.fit(X_train, y_train) # Fit a ridge regression on the training data
coefs_ridge = pd.DataFrame(ridge.coef_.T, index =[X.columns]) # Print coefficients
coefs_ridge = coefs_ridge.rename(columns={0:'coef_value'})       

# TRAIN SET
pred_train = ridge.predict(X_train) # Use this model to predict the train data
# Calculate RMSE train
print("RMSE for Train:",sqrt(mean_squared_error(y_train, pred_train))) #RMSE
print("R^2 for Train:",ridge.score(X_train, y_train)) #R2

# TEST SET
pred_test = ridge.predict(X_test)
#RMSE test
print("RMSE for Test:",sqrt(mean_squared_error(y_test, pred_test))) #RMSE
print("R^2 for Test:",ridge.score(X_test, y_test)) #R2

##### c) plots
#i) lines plot
lineplot_compare(actual=y_test.values, y_pred=pred_test,title="Ridge", filename=None)
#ii) histogram of difference for TEST
hist_diff_test(y_test,y_train, pred_test, pred_train)

#iii) Show the biggest coeficient (Top 10)
largest=coefs_ridge.nlargest(5,'coef_value')
smallest=coefs_ridge.nsmallest(5,'coef_value')
both=pd.concat([largest,smallest], axis=0)
# make a bar up and down
baseline = 1
plt.bar(range(len(both['coef_value'])),[x-baseline for x in both['coef_value']])
plt.xticks(np.arange(10), (both.index.values))
plt.xticks(rotation=90)
plt.show()

################################### LASSO ####################################

####### a) looking for best parameters
# reference: https://www.scikit-yb.org/en/latest/api/regressor/alphas.html
# Create a list of alphas to cross-validate against
alphas2=np.arange(1, 100, 10) #range for alpha
# Instantiate the linear model and visualizer
model2 = LassoCV(alphas=alphas2)
visualizer2 = AlphaSelection(model2)
visualizer2.fit(X, y)
g = visualizer2.poof()
visualizer2.alpha_

####### b) Implement Lasso Regression
las = linear_model.Lasso(alpha=visualizer2.alpha_)
las.fit(X_train, y_train)  
coefs_lasso = pd.DataFrame(las.coef_.T, index =[X.columns])
coefs_lasso = coefs_lasso.rename(columns={0:'coef_value'})   

# TRAIN SET
pred_train_las = las.predict(X_train) # Use this model to predict the train data
# Calculate RMSE train
print("RMSE for Train:",sqrt(mean_squared_error(y_train, pred_train_las))) #RMSE
print("R^2 for Train:",las.score(X_train, y_train)) #R2

# TEST SET
pred_test_las = las.predict(X_test)
#RMSE test
print("RMSE for Test:",sqrt(mean_squared_error(y_test, pred_test_las))) #RMSE
print("R^2 for Test:",las.score(X_test, y_test)) #R2

## Coef restriction
print("Lasso restricted", coefs_lasso[coefs_lasso['coef_value'] == 0].count(), "variables to zero")

###### c) plots
#i) lines plot
lineplot_compare(actual=y_test.values, y_pred=pred_test_las,title="Lasso, error vs. predicted", filename=None)

#ii) histogram of difference for TEST
hist_diff_test(y_test,y_train, pred_test_las, pred_train_las,title="Lasso, Difference error for Test and Train")

#iii)
show_coefs(coefs=coefs_lasso, title = "Lasso - Top 5 biggest and smallest coeficients")


################################### KNN ####################################

#########a) find the best parameters (k)
# Run XBoost to find the best predictors -> function gradient_boosting()
best_variables_xgb = gradient_boosting(X,y)

rmse_train = [] #to store rmse values for different k
rmse_test = []
for K in range(1,20):
    K = K+1
    
    #Initialize KNN
    model = neighbors.KNeighborsRegressor(n_neighbors = K)
    #fit the model
    model.fit(X_train, y_train)

    # TRAIN SET
    pred_train_KNN = model.predict(X_train) #make prediction on test set
    error_train = sqrt(mean_squared_error(y_train,pred_train_KNN)) #calculate rmse
    rmse_train.append(error_train) #store rmse values
    print('RMSE Train value for k= ' , K , 'is:', error_train)
    
    # TEST SET
    pred_test_KNN = model.predict(X_test) #make prediction on test set
    error_test = sqrt(mean_squared_error(y_test,pred_test_KNN)) #calculate rmse
    rmse_test.append(error_test) #store rmse values
    print('RMSE Test value for k= ' , K , 'is:', error_test)   
    
#plotting the rmse values against k values
fig, ax = plt.subplots()
ax.plot(rmse_train, color = 'blue')
ax.plot(rmse_test, color = 'red')
ax.legend(['Train', 'Test'])
ax.title.set_text('Error')


#########b) use best k in the final model
##### KNN RUN WITH BEST K #####
#the lowest K run
best_k=np.argmin(rmse_test)
# run KNN model with bestk value
model2 = neighbors.KNeighborsRegressor(n_neighbors = best_k)
model2.fit(X_train, y_train)
model2_pred_KNN_test = model2.predict(X_test)
model2_pred_KNN_train = model2.predict(X_train)

########## c) plots
#i) lines plot
lineplot_compare(actual=y_test.values, y_pred=model2_pred_KNN_test, title="KNN, error vs. predicted")

#ii) histogram of difference for TEST
hist_diff_test(y_test,y_train, model2_pred_KNN_test, model2_pred_KNN_train,title="KNN, Error of difference for Test and Train")
