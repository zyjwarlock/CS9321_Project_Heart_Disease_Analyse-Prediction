import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import accuracy_score
from sklearn.model_selection import LeaveOneOut, cross_val_score, StratifiedKFold, GridSearchCV
from sklearn.externals import joblib
from sklearn import svm
from sklearn.neighbors import KNeighborsClassifier
import numpy as np
from collections import defaultdict
from sklearn.datasets import make_classification
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.model_selection import ShuffleSplit
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import r2_score
from sklearn.decomposition import PCA
from sklearn.svm import LinearSVC
from sklearn.svm import SVC
#import eli5
#from eli5.sklearn import PermutationImportance

import os


class MyModel:
	def __init__(self, filename='mymodel.pkl', algorithm='RF'):
		if not os.path.exists(filename):
			self._train_model(model_name=algorithm, save=True)

		self.acc = self._get_acc()

	def _get_data(self):
		df = pd.read_csv('processed.cleveland.data')
		df.columns = [
			'age', 'sex', 'cp', 'trestbps', 'chol', 'fbs', 'restecg', 'thalach',
			'exang', 'oldpeak', 'slope', 'ca', 'thal', 'target'
		]

		df['target'] = df['target'].apply(lambda x: 0 if x == 0 else 1)
		df = df.applymap(lambda x: 0 if x == '?' else x)

		X = df.drop('target', axis=1)
		y = df['target']
		return X, y

	def _train_model(self, model_name='RF', save=False):
		X, y = self._get_data()
		X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
		#X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.2, random_state=0)

		if model_name.lower() in ['rf']:
			model = RandomForestClassifier(
				n_estimators=60, max_depth=11, max_leaf_nodes=24
			)

		elif model_name.lower() in ['svm']:
			model = svm.SVC(C=2, gamma=0.125, kernel='linear')
		elif model_name.lower() in ['gmb']:
			model = GradientBoostingClassifier(
				n_estimators=100,
				learning_rate=0.01,
				max_depth=1,
				random_state=0
			)
		model.fit(X, y)

		#l1o = LeaveOneOut()
		scores = cross_val_score(model, X, y, cv=10, scoring='accuracy')
		print(scores.mean())
		if save:
			joblib.dump(model, 'mymodel.pkl')

	def _get_acc(self, modelfile='mymodel.pkl'):
		X, y = self._get_data()
		model = joblib.load(modelfile)
		scores = cross_val_score(model, X, y, cv=5, scoring='accuracy')
		return scores.mean()

	def predict(self, data, modelfile='mymodel.pkl'):
		model = joblib.load(modelfile)
		return model.predict([data])[0], self.acc

	def xv(self):
		df = pd.read_csv('processed.cleveland.data')
		df.columns = [
			'age', 'sex', 'cp', 'trestbps', 'chol', 'fbs', 'restecg', 'thalach',
			'exang', 'oldpeak', 'slope', 'ca', 'thal', 'target'
		]

		df['target'] = df['target'].apply(lambda x: 0 if x == 0 else 1)
		df = df.applymap(lambda x: 0 if x == '?' else x)

		X = df.drop('target', axis=1)
		y = df['target']
		model = RandomForestClassifier(n_estimators=30, max_depth=10)
		cv_scores = cross_val_score(model, X, y, cv=10)
		print(cv_scores.mean())

	def feature_importance(self, top=5):
		X, y = self._get_data()
		forest = ExtraTreesClassifier(
			n_estimators=60, max_depth=11, max_leaf_nodes=24
		)
		forest.fit(X, y)
		importances = forest.feature_importances_
		std = np.std(
			[tree.feature_importances_ for tree in forest.estimators_], axis=0
		)
		indices = np.argsort(importances)[::-1]
		Ranking = []
		for f in range(X.shape[1]):
			Ranking.append((X.columns[indices[f]], importances[indices[f]]))
		if top >= X.shape[1]:
			return Ranking
		return Ranking[:top]

	def bonus(self, neighbours = 40):
		X, y = self._get_data()
		
		new_features = [e[0] for e in self.feature_importance(top = 8)]
		X = X[new_features]
		
		skf = StratifiedKFold(n_splits=10, shuffle=True, random_state=5)

		scaler = StandardScaler().fit(X)
		X_scaled = scaler.transform(X)

		knn_params = {'n_neighbors': range(1, neighbours) }

		knn_grid = GridSearchCV(KNeighborsClassifier(), knn_params, cv=skf)
		knn_grid.fit(X_scaled, y);


		score = cross_val_score(knn_grid.best_estimator_, X_scaled, y, cv=skf)
#		print(X_scaled.shape)
#		print(score.mean())
		L = [(i, knn_grid.cv_results_['mean_test_score'][i-1]) for i in range(1,neighbours)]
#		print(knn_grid.cv_results_)
		return L
		
		
#	def bonus(self):
#		X, y = self._get_data()
#		pca = PCA(7).fit(X)
#		X_pca = pca.transform(X)
#		svm = SVC(C=2, gamma=0.125, kernel='linear')
#		svm.fit(X_pca, y)
#
#		score = cross_val_score(svm, X_pca, y, cv=10)
#		print(score.mean())

#mm = MyModel()
#print(mm.feature_importance(top = 5))
#x = [56.0,1.0,3.0,130.0,256.0,1.0,2.0,142.0,1.0,0.6,2.0,1.0,6.0]
#for _ in mm.bonus():
#	print(_)
#print(mm.bonus())
	

