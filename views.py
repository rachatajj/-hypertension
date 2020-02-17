from flask import render_template,url_for,flash,redirect,request,Blueprint,session
from HCCWebSite.patients.forms import RegistrationForm,RegistrationDiagnoseForm,RegistrationModel
from HCCWebSite.patients import PredictModel
from datetime import datetime
import mysql.connector
import math

patients = Blueprint('patients',__name__)


@patients.route("/list",methods =['GET','POST'])
def list():
    if session['id'] != 'nurse' and session['id'] != 'doctor'  :
        return render_template('error_pages/403.html')

    conn = mysql.connector.connect(host = "database-3.c4c03nprlfk4.ap-southeast-1.rds.amazonaws.com",user = "admin", passwd = "Jp_0956217807",database = "hccDB", port='3306')

    cursor = conn.cursor()
    if request.method == 'POST':
        form = RegistrationForm()
        identify = form.identify.data
        results =cursor.execute("SET @row_number = 0; SELECT *,(@row_number:=@row_number + 1)  AS RowNumber,CEILING((@row_number / (10 ))) as Page FROM Patients as P LEFT JOIN PhysicalTest as PT on P.IDCards = PT.IDCards Where P.IDCards  LIKE '%"+identify +"%' Order by P.IDCards", multi=True)
        for cur in results:
            if cur.with_rows:
                rows = cur.fetchall()
        maxNumber = 0
        results2 =cursor.execute("SET @row_number = 0;SELECT  (@row_number:=@row_number + 1) as ROWNUMBER  FROM Patients as P LEFT JOIN PhysicalTest as PT on P.IDCards = PT.IDCards Where P.IDCards  LIKE '%"+identify +"%'   Order by ROWNUMBER DESC limit 1;", multi=True)
        for cur in results2:
            if cur.with_rows:
                maxNumber = cur.fetchone()
        if not maxNumber:
            return render_template('error_pages/400.html')
        else :
            numberOfPages = math.ceil(maxNumber[0]/10)
        return render_template('findPateints.html', datas = rows,numberOfPages=numberOfPages,identify=identify)

    results =cursor.execute('SET @row_number = 0; SELECT *,(@row_number:=@row_number + 1)  AS RowNumber,CEILING((@row_number / (10 ))) as Page FROM Patients as P LEFT JOIN PhysicalTest as PT on P.IDCards = PT.IDCards Order by P.IDCards', multi=True)
    for cur in results:
        if cur.with_rows:
            rows = cur.fetchall()
    maxNumber = 0
    results2 = cursor.execute('SET @row_number = 0;SELECT  (@row_number:=@row_number + 1) as ROWNUMBER  FROM Patients as P LEFT JOIN PhysicalTest as PT on P.IDCards = PT.IDCards Order by ROWNUMBER DESC limit 1;', multi=True)
    for cur in results2:
        if cur.with_rows:
            maxNumber = cur.fetchone()
    numberOfPages = math.ceil(maxNumber[0]/10)
    return render_template('list.html', datas = rows,numberOfPages=numberOfPages)


@patients.route("/nextList",methods =['GET','POST'])
def nextList():
    session['listPage'] = session['listPage']+1
    return redirect(url_for('patients.list'))

@patients.route("/previousList",methods =['GET','POST'])
def previousList():
    session['listPage'] = session['listPage'] -1
    return redirect(url_for('patients.list'))

@patients.route("/firstPage",methods =['GET','POST'])
def firstPage():
    session['listPage'] = 1
    return redirect(url_for('patients.list'))

@patients.route("/lastPage",methods =['GET','POST'])
def lastPage():
    conn = mysql.connector.connect(host = "database-3.c4c03nprlfk4.ap-southeast-1.rds.amazonaws.com",user = "admin", passwd = "Jp_0956217807",database = "hccDB", port='3306')
    cursor = conn.cursor()
    maxNumber = 0
    results2 = cursor.execute('SET @row_number = 0;SELECT  (@row_number:=@row_number + 1) as ROWNUMBER  FROM Patients as P LEFT JOIN PhysicalTest as PT on P.IDCards = PT.IDCards Order by ROWNUMBER DESC limit 1;', multi=True)
    for cur in results2:
        if cur.with_rows:
            maxNumber = cur.fetchone()
    numberOfPages = math.ceil(maxNumber[0]/10)
    session['listPage'] = numberOfPages
    return redirect(url_for('patients.list'))

@patients.route("/register",methods =['GET','POST'])
def register():
    if session['id'] != 'nurse' :
        return render_template('error_pages/403.html')
    form = RegistrationForm()
    conn = mysql.connector.connect(host = "database-3.c4c03nprlfk4.ap-southeast-1.rds.amazonaws.com",user = "admin", passwd = "Jp_0956217807",database = "hccDB", port='3306')

    if request.method == 'POST':
        firstname =form.firstname.data,
        lastname = form.lastname.data,
        birth_date = form.birth_date.data,
        telephone = form.telephone.data,
        identify = form.identify.data,
        gender = form.gender.data,
        address = form.address.data
        sql = "Insert into Patients (IDCards,AgeAtExam,Gender,FirstName,LastName,DateofBirth,Tel,Address) values("+identify[0]+","+str(calculateAge(datetime.combine(birth_date[0], datetime.min.time())))+",'"+ gender[0] +"',"+"'"+ firstname[0] +"',"+"'"+ lastname[0] +"','"+ str(birth_date[0])+"',"+"'"+"0"+ str(telephone[0]) +"',"+"'"+ address.strip() +"'"+")"
        cursorTemp = conn.cursor()
        cursorTemp.execute(sql,( datetime.combine(birth_date[0], datetime.min.time())))
        conn.commit()
        flash("บันทึกเสร็จสิ้น")
        return redirect(url_for('patients.list'))
    else :
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM Patients ')
        rows = cursor.fetchall()
        return render_template('list.html', datas = rows)


@patients.route("/update",methods =['GET','POST'])
def update():
    if session['id'] != 'nurse' :
        return render_template('error_pages/403.html')
    form = RegistrationForm()
    conn = mysql.connector.connect(host = "database-3.c4c03nprlfk4.ap-southeast-1.rds.amazonaws.com",user = "admin", passwd = "Jp_0956217807",database = "hccDB", port='3306')

    if request.method == 'POST':
        firstname =form.firstname.data,
        lastname = form.lastname.data,
        birth_date = form.birth_date.data,
        telephone = form.telephone.data,
        identify = form.identify.data,
        gender = form.gender.data,
        address = form.address.data
        sql = "update Patients set AgeAtExam = "+str(calculateAge(datetime.combine(birth_date[0], datetime.min.time())))+" ,Gender = '"+gender[0]+"',FirstName = '"+firstname[0]+"',LastName = '"+lastname[0]+"',DateofBirth = '"+str(datetime.combine(birth_date[0], datetime.min.time()))+"',Tel = '"+"0"+ str(telephone[0])+"',Address = '"+address.strip()+"' where IDCards = "+identify[0]+" "
        cursorTemp = conn.cursor()
        cursorTemp.execute(sql)
        conn.commit()
        flash("แก้ไขเสร็จสิ้น")
        return redirect(url_for('patients.list'))
    else :
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM Patients ')
        rows = cursor.fetchall()
        return render_template('list.html', datas = rows)

@patients.route("/<int:id>/delete",methods =['GET','POST'])
def delete(id):
    if session['id'] != 'nurse' :
        return render_template('error_pages/403.html')
    conn = mysql.connector.connect(host = "database-3.c4c03nprlfk4.ap-southeast-1.rds.amazonaws.com",user = "admin", passwd = "Jp_0956217807",database = "hccDB", port='3306')
    cursorTemp = conn.cursor()
    cursorTemp.execute('Delete FROM Patients where IDCards = '+ str(id))
    conn.commit()
    flash("ลบสำเร็จ")
    return redirect(url_for('patients.list'))


@patients.route("/<int:id>/diagnose",methods=['GET','POST'])
def diagnose(id):
    if session['id'] != 'doctor' :
        return render_template('error_pages/403.html')
    conn = mysql.connector.connect(host = "database-3.c4c03nprlfk4.ap-southeast-1.rds.amazonaws.com",user = "admin", passwd = "Jp_0956217807",database = "hccDB", port='3306')

    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Patients where IDCards = '+ str(id))
    rows = cursor.fetchall()
    cursor.execute('SELECT * FROM PhysicalTest where IDCards = '+ str(id))
    rows2 = cursor.fetchall()

    #Prediction serctions
    maleEn = 0
    femaleEn = 0
    for row in rows2:
        if row[2] == "Female" :
            maleEn = 0
            femaleEn = 1
        else :
            maleEn = 1
            femaleEn = 0
        predict = PredictModel.predictHCC(row[1], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10] ,femaleEn, maleEn)

    #Check patients was diagnosed already?
    CheckPhtsical = "Diagnosed"
    for row in rows2:
        if row[11] == None:
            CheckPhtsical = "NULL"


    return render_template('diagnose.html',id =id,datasPatients=rows,datasPhysical=rows2,Diagnosed = CheckPhtsical,predict = predict)

@patients.route("/createDiagnose",methods=['GET','POST'])
def createDiagnose():
    if session['id'] != 'doctor' :
        return render_template('error_pages/403.html')
    form = RegistrationDiagnoseForm()
    conn = mysql.connector.connect(host = "database-3.c4c03nprlfk4.ap-southeast-1.rds.amazonaws.com",user = "admin", passwd = "Jp_0956217807",database = "hccDB", port='3306')

    if request.method == 'POST':
        id = form.identify.data,
        class1 = form.class1.data,
        class2 = form.class2.data
        sql = "update PhysicalTest set ClassLabel1 = "+str(class1[0])+" ,ClassLabel2 = '"+str(class2)+ "' where IDCards =" +str(id[0])+" "
        cursorTemp = conn.cursor()
        cursorTemp.execute(sql)
        conn.commit()
        flash("บันทึกการวินิจฉัยเสร็จสิ้น")

    return redirect(url_for('patients.list'))

def calculateAge(birthDate):
    days_in_year = 365.2425
    age = int((datetime.today() - birthDate).days / days_in_year)
    return age





#------------------------------------------------------------------------ admin sections ------------------------------------------------------------------------
@patients.route("/manageModel",methods =['GET','POST'])
def manageModel():
    if session['id'] != 'admin'  :
        return render_template('error_pages/403.html')
    conn = mysql.connector.connect(host = "database-3.c4c03nprlfk4.ap-southeast-1.rds.amazonaws.com",user = "admin", passwd = "Jp_0956217807",database = "hccDB", port='3306')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Models ORDER BY Type')
    rows = cursor.fetchall()
    return render_template('manageModel.html', datas = rows)


@patients.route("/<string:id>/activateModel",methods =['GET','POST'])
def activateModel(id):
    if session['id'] != 'admin'  :
        return render_template('error_pages/403.html')
    conn = mysql.connector.connect(host = "database-3.c4c03nprlfk4.ap-southeast-1.rds.amazonaws.com",user = "admin", passwd = "Jp_0956217807",database = "hccDB", port='3306')

    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Models WHERE ModelName ='"+id+ "'")
    rows = cursor.fetchall()
    chooseActivate = []
    for row in rows:
        chooseActivate.append([x for x in row])

    cursor.execute("update Models set Status = 'Off'  where Type ="+str(chooseActivate[1][0]))
    conn.commit()
    cursor.execute("update Models set Status = 'Activated' where ModelName = '"+ chooseActivate[0][0] +"'")
    conn.commit()

    return redirect(url_for('patients.manageModel'))

@patients.route("/createModel",methods=['GET','POST'])
def createModel():
    if session['id'] != 'admin' :
        return render_template('error_pages/403.html')
    form = RegistrationModel()
    conn = mysql.connector.connect(host = "database-3.c4c03nprlfk4.ap-southeast-1.rds.amazonaws.com",user = "admin", passwd = "Jp_0956217807",database = "hccDB", port='3306')

    if request.method == 'POST':
        type = form.type.data
        model = PredictModel.registerModel(type)
        if(model == "NULL"):
            flash("การสร้างโมเดลเกิดปัญหา")
        else:
            sql = "Insert into Models (ModelName,Type,Status) values('"+model+"',"+type+",'Off')"
            cursorTemp = conn.cursor()
            cursorTemp.execute(sql)
            conn.commit()
            flash("สร้างโมเดล " + model + " เสร็จสิ้น")
    return redirect(url_for('patients.manageModel'))
