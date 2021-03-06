import sys
import random
import datetime
import utility.logging as log
import files.parse as parse
import math
from collections import defaultdict
import numpy as np
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.neural_network import MLPClassifier
from sklearn.svm import SVC
from sklearn.model_selection import KFold
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.decomposition import IncrementalPCA
from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt

def getRandomInt():
    return random.randint(0,sys.maxsize)

def predict(fp,games,games_test,sampleperc=1):
    
    predict_list = []#[["Game Name","Popular?"]]
    scaler = MinMaxScaler(feature_range=[0,1])
    features_after = 140
    lim = 100
    for games_test_counter in range(0,len(games_test),lim):
        try:
            games_test_subset = games_test[games_test_counter:games_test_counter+lim]

            game_data = []
            game_classes = []
            for i, game in enumerate(games.values()):
                if i >= len(games)*sampleperc:
                    break
                game_data.append(game.get_vector())
                game_classes.append(game.get_class())

            for i, game in enumerate(games_test_subset):
                game_data.append(game.get_vector())


            rows_prv = len(game_data)
            rows_fed = min(1000,len(game_data))
            features_before = len(game_data[0])
            X_train = None
            X_test = None

            if True: # make vector_np out of scope
                vector_np = scaler.fit_transform(np.asarray(game_data).astype(np.float64)[0:,0:])
                pca = IncrementalPCA(n_components=features_after,batch_size=16)
                for i in range(0,math.floor(rows_prv/rows_fed)): # perform partial fit
                    lower = i*rows_fed
                    upper = (i+1)*rows_fed
                    pca.partial_fit(vector_np[lower:upper])
                X_train = pca.transform(vector_np)[:-len(games_test_subset)]
                X_test = pca.transform(vector_np)[len(games):]
            y_train = np.array(game_classes)

            c = RandomForestClassifier(n_estimators=30,criterion="gini",max_depth=10,random_state=518629550)
            c.fit(X_train,y_train)
            predicted = c.predict(X_test)
            for i, _ in enumerate(predicted):
                predict_list.append([games_test_subset[i].get_name(),"True" if predicted[i] == 1 else "False"])
            log.sofar("Classifying Games",games_test_counter,len(games_test),len(games_test))
        except Exception as e:
            log.info("Memory error occured @ %d." % games_test_counter)
            break
    parse.appendCSV("%s/classified_games.csv" % fp,predict_list)

def testClassifiers(fp,games,pos_ratio,sampleperc=0.1,TestKNN=True,TestDTree=True,TestRForest=True,TestNBayes=True,TestNNetwork=True,TestSVM=True,show=False):

    fullpath = "%s/classifier_data/pos_ratio=%02d%%.csv" % (fp,int(pos_ratio*100))
    kf = KFold(n_splits=10)
    classifiers = []
    game_data = []
    game_classes = []

    for i, game in enumerate(games.values()):
        if i >= len(games)*sampleperc:
            break
        game_data.append(game.get_vector())
        game_classes.append(game.get_class())

    log.info("\tUsing sample size from testing data of %dx%d (%d)." % (len(game_data),len(game_data[0]),len(game_data)*len(game_data[0])))

    scaler = MinMaxScaler(feature_range=[0,1])
    features_before = len(game_data[0])
    features_after = 140 if 140 > features_before else features_before
    rows_prv = len(game_data) # rows previously existing in the vector
    rows_fed = min(1000,len(game_data)) # rows to feed it at a time
    X_pca = None

    if True: # make vector_np out of scope
        vector_np = scaler.fit_transform(np.asarray(game_data).astype(np.float64)[0:,0:])
        pca = IncrementalPCA(n_components=features_after,batch_size=16)
        for i in range(0,math.floor(rows_prv/rows_fed)): # perform partial fit
            lower = i*rows_fed
            upper = (i+1)*rows_fed
            pca.partial_fit(vector_np[lower:upper])
        X_pca = pca.transform(vector_np)

    plt.close('all')
    plt.figure()
    plt.plot(np.cumsum(pca.explained_variance_ratio_))
    plt.xlabel('Components Chosen')
    plt.ylabel('Variance')
    plt.title('Explained Variance')
    plt.savefig("%s/explained_variance.png" % (fp))
    if show:
        plt.show()
    plt.gcf()

    X_train,X_test,y_train,y_test = train_test_split(X_pca,np.asarray(game_classes).astype('float64'),test_size=0.33)

    log.info("Training Data: %dx%d" % (X_train.shape[0],X_train.shape[1]))
    log.info("Training Class Data: %d" % (y_train.shape[0]))
    log.info("Testing Data: %dx%d" % (X_test.shape[0],X_test.shape[1]))
    log.info("Testing Class Data: %d" % (y_test.shape[0]))

    knn_ks = range(1,21,4)
    random_range = range(0,20)
    tree_depth = [10,20,30,40,50,60,70,80,90,100,None]
    rforest_estimators = range(10,100,10)
    dict_to_parse = defaultdict(list)
    acc_data = []

    if TestKNN:
        log.info("\tTesting KNNs")
        for k in knn_ks:
            for weight in ["uniform","distance"]:
                for alg in ["ball_tree","kd_tree","brute"]:
                    c = KNeighborsClassifier(n_neighbors=k,weights=weight,algorithm=alg)
                    c.fit(X_train,y_train)
                    acc = accuracy_score(y_test,c.predict(X_test))
                    parse.appendCSV(fullpath,[["KNN",acc,k,weight,alg]])
                    log.info("\t\tAccuraccy %f with %d,%s,%s" % (acc,k,weight,alg))
        log.info("\tFinished KNNs")
    if TestDTree:
        log.info("\tTesting DTrees")
        for criteria in ["gini","entropy"]:
            for split in ["best","random"]:
                for depth in tree_depth:
                    for _ in random_range:
                        random_state = getRandomInt()
                        c = DecisionTreeClassifier(criterion=criteria,splitter=split,max_depth=depth,random_state=random_state)
                        c.fit(X_train,y_train)
                        acc = accuracy_score(y_test,c.predict(X_test))
                        parse.appendCSV(fullpath,[["DTree",acc,criteria,split,depth,random_state]])
                        log.info("\t\tAccuraccy %f with %s,%s,%s" % (acc,criteria,split,depth))
        log.info("\tFinished DTrees")
    if TestRForest:
        log.info("\tTesting RForests")
        for estimator in rforest_estimators:
            for criteria in ["gini","entropy"]:
                for depth in tree_depth:
                    for _ in random_range:
                        random_state = getRandomInt()
                        c = RandomForestClassifier(n_estimators=estimator,criterion=criteria,max_depth=depth,random_state=random_state)
                        c.fit(X_train,y_train)
                        acc = accuracy_score(y_test,c.predict(X_test))
                        log.info("\t\tAccuraccy %f with %s,%s,%s" % (acc,criteria,estimator,depth))
                        parse.appendCSV(fullpath,[["RForest",acc,estimator,criteria,depth,random_state]])
        log.info("\tFinished RForests")
    if TestNBayes:
        log.info("\tTesting NBayes")
        c = GaussianNB() # nothing to change that I understand
        c.fit(X_train,y_train)
        acc = accuracy_score(y_test,c.predict(X_test))
        log.info("\t\tAccuraccy %f" % (acc))
        parse.appendCSV(fullpath,[["NBayes",acc]])
        log.info("\tFinished NBayes")
    if TestNNetwork:
        log.info("\tTesting NNetworks")
        for active in ["identity","logistic","tanh","relu"]:
            for solve in ["lbfgs","sgd","adam"]:
                for _ in random_range:
                    random_state = getRandomInt()
                    c = MLPClassifier(activation=active,solver=solve,random_state=random_state)
                    c.fit(X_train,y_train)
                    acc = accuracy_score(y_test,c.predict(X_test))
                    log.info("\t\tAccuraccy %f with %s,%s" % (acc,active,solve))
                    parse.appendCSV(fullpath,[["NNetwork",acc,active,solve,random_state]])
        log.info("\tFinished NNetworks")
    if TestSVM:
        log.info("\tTesting SVMs")
        for kern in ["rbf","poly","sigmoid"]: # linear was real slow
            for _ in random_range:
                random_state = getRandomInt()
                c = SVC(gamma="scale",kernel=kern,random_state=random_state)
                c.fit(X_train,y_train)
                acc = accuracy_score(y_test,c.predict(X_test))
                log.info("\t\tAccuraccy %f with %s" % (acc,kern))
                parse.appendCSV(fullpath,[["SVM",acc,kern,random_state]])
        log.info("\tFinished SVMs")

if __name__ == "__main__":
    number_of_items = 100
    size_of_vector = 50
    number_of_classes = 2
    testClassifiers("Testing","",np.random.rand(number_of_items,size_of_vector).tolist(),np.random.randint(number_of_classes,size=number_of_items).tolist())