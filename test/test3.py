import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures

X = np.array([[0.5], [1], [1.5], [2], [2.5]])  # 自变量
y = np.array([1.35,0.9,1.3,2,3.5])  # 因变量

regressor = LinearRegression()
poly_features = PolynomialFeatures(degree=2)
X = poly_features.fit_transform(X)
regressor.fit(X, y)

slope = regressor.coef_
intercept = regressor.intercept_

print(slope, intercept)