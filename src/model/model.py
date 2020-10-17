import pandas as pd
import numpy as np
from sklearn.decomposition import PCA
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import accuracy_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler


# Opening the data
sbgr = pd.read_csv('./data/labeled_fog.csv')

# Separating target variable
X = sbgr.drop(['is_fog'], axis=1)
y = sbgr['is_fog']

# Separating into train and test
X_train, X_test, y_train, y_test = train_test_split(X, y)

# Standardize the data
scaler = StandardScaler()
scaler.fit(X_train)
X_train = scaler.transform(X_train)
X_test = scaler.transform(X_test)

# PCA
pca = PCA()
pca.fit(X_train)
X_train = pca.transform(X_train)
X_test = pca.transform(X_test)

# Running a bunch of models to see which one is the best
log = LogisticRegression()
tree = DecisionTreeClassifier()
forest = RandomForestClassifier()
nb = GaussianNB()
knn = KNeighborsClassifier()
svm = SVC()
mlp = MLPClassifier()

models = [log, tree, forest, nb, knn, svm, mlp]
model_names = ['Logistic Regression',
               'Decision Tree',
               'Random Forest',
               'Naive Bayes',
               'K-Nearest Neighbors',
               'Support Vector Machine',
               'Multi-Layer Perceptron']
metrics = ['Accuracy', 'Precision', 'Recall', 'AUC']

classification_summary = pd.DataFrame(columns=metrics)

for model_name, model in list(zip(model_names, models)):
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)
    auc = roc_auc_score(y_test, y_pred)
    classification_summary.loc[model_name] = [accuracy, precision, recall, auc]

print(classification_summary)


# Implementing the model
model = MLPClassifier().fit(X_train, y_train)
y_pred = model.predict(X_test)

input = {'direction': 40, 'speed': 5, 'visibility': 1000, 'temperature': 20, 'slp': 1013, 'rh': 90}