import numpy as np
import pandas as pd
import pickle
from datetime import datetime
import os
import mysql.connector
from sklearn.neural_network import MLPClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import VotingClassifier

basedir = os.path.abspath(os.path.dirname(__file__))

def predictHCC(Age, TB, DB, AAP, SGPT, SGOT, TP, ALB, ratio_al_gl ,Gender__Female, Gender__Male):
    myData1 = [[Age, TB, DB, AAP, SGPT, SGOT, TP, ALB, ratio_al_gl ,Gender__Female, Gender__Male]]
    myData2 = [[ SGPT, SGOT]]

    conn = mysql.connector.connect(host = "database-3.c4c03nprlfk4.ap-southeast-1.rds.amazonaws.com",user = "admin", passwd = "Jp_0956217807",database = "hccDB", port='3306')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM Models WHERE Status ="+ "'Activated' AND Type =1")
    Model1 = cursor.fetchall()

    cursor.execute("SELECT * FROM Models WHERE Status ="+ "'Activated' AND Type =2")
    Model2 = cursor.fetchall()

    model1 = pickle.load(open(os.path.join(basedir,Model1[0][0]), 'rb'))
    model2 = pickle.load(open(os.path.join(basedir,Model2[0][0]), 'rb'))

    yPredict1 = model1.predict(myData1)
    yPredict2 = model2.predict(myData2)

    if(yPredict1[0] ==1 or yPredict1[0] == "1"):
        y1 = "Liver Patient"
    else:
        y1 = "Normal"
    Predict = np.array([y1,yPredict2[0]])
    return Predict

def registerModel(typeModel):
    Model = "NULL"
    conn = mysql.connector.connect(host = "database-3.c4c03nprlfk4.ap-southeast-1.rds.amazonaws.com",user = "admin", passwd = "Jp_0956217807",database = "hccDB", port='3306')
    SQL_Query = pd.read_sql_query(''' SELECT AgeAtExam as Age,Gender,TB,DB,AAP,SGPT,SGOT,TP,ALB,`A/G`,ClassLabel1 as class,
    `DeRitis ratio`,ClassLabel2 as class2 FROM PhysicalTest where ClassLabel1 IS NOT NULL''', conn)
    DataSet = pd.DataFrame(SQL_Query)
    DataSet = pd.concat([DataSet, pd.get_dummies(DataSet['Gender'], prefix = 'Gender_')], axis=1)
    DataSet = DataSet.loc[:,['Age','TB','DB','AAP','SGPT','SGOT','TP','ALB','A/G','Gender__Female','Gender__Male','class']]
    DeRitis = DataSet['SGOT']/DataSet['SGPT']
    dat2 = pd.DataFrame({'DeRitis ratio': DeRitis})
    DataSet = DataSet.join(dat2)
    DataSet.loc[(DataSet['DeRitis ratio'] < 1), 'class2'] = 'Low'
    DataSet.loc[((DataSet['DeRitis ratio']) < 1.5)& ((DataSet['DeRitis ratio']) >=1), 'class2'] = 'Normal'
    DataSet.loc[(DataSet['DeRitis ratio'] >= 1.5), 'class2'] = 'High'

    ModelANN = MLPClassifier(solver='lbfgs',activation = 'relu',batch_size=15,momentum=0.3,learning_rate_init=0.0000001)
    ModelLogistic = LogisticRegression(solver='lbfgs',class_weight='balanced',tol=0.000001,C= 100)
    ModelRandomForest = RandomForestClassifier(criterion ='entropy',n_estimators=500,max_depth=500)
    eclf = VotingClassifier(estimators=[('ANN', ModelANN), ('Logistic', ModelLogistic), ('RandomForest', ModelRandomForest)], voting='hard',weights=[1,1,2])

    dateModel = datetime.now().strftime("%Y-%d-%m")
    if (typeModel == '1') :
        Model = "HCCM1-" +dateModel+ ".sav"
        x = DataSet.iloc[:,:-3]
        y = DataSet['class']
        eclf = eclf.fit(x,y)
        pickle.dump(eclf, open("HCCWebSite/patients/"+Model, 'wb'))
    else:
        Model = "HCCM2-" +dateModel + ".sav"
        x = DataSet.loc[::,'SGPT':'SGOT']
        y = DataSet['class2']
        eclf = eclf.fit(x,y)
        pickle.dump(eclf, open("HCCWebSite/patients/"+Model, 'wb'))
    return Model
