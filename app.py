# -*- coding: utf-8 -*-
"""
Created on Tue Sep  5 21:12:56 2023

@author: Mahil
"""
import os
os.add_dll_directory('D:\IBMProjCloud\edulab\.venv\Lib\site-packages\clidriver\\bin')

from flask import Flask, render_template, request, session
import ibm_db
import ibm_boto3
from ibm_botocore.client import Config
import re
import random
import string
import datetime
import requests

app = Flask(__name__)
app.config['SESSION_TYPE'] = 'memcached'
app.config['SECRET_KEY'] = 'Key1'

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")

@app.route("/")
def index():
    return render_template("index.html");

@app.route("/contact")
def contact():
    return render_template("contact.html");

@app.route("/admincontact")
def admincontact():
    sql="SELECT EMAIL,USER,USERNAME FROM REGISTER WHERE ROLE=?;"
    stmt = ibm_db.prepare(conn, sql)
    role=3
    ibm_db.bind_param(stmt, 1, role)
    ibm_db.execute (stmt)
    account = ibm_db.fetch_assoc(stmt)
    if account:
        Username=account['USERNAME']
        email=account['EMAIL']
        # Namen=account['NAME']
        return render_template("admincontact.html",  role="ADMIN", username=Username, email = email);
    else:
        return render_template("admincontact.html")

conn = ibm_db.connect("DATABASE=bludb; HOSTNAME=9938aec0-8105-433e-8bf9-0fbb7e483086.c1ogj3sd0tgtu0lqde00.databases.appdomain.cloud; PORT=32459; UID=swy31428;PASSWORD=86Oql6qC0YBnp7x5; SECURITY=SSL;SSLServerCertificate = DigiCertGlobalRootCA.crt", '','')

@app.route("/login_new", methods=['POST', 'GET'])
def login_new():
    global Userid
    global Username
    msg = ' '
    if request.method == "POST":
        email = request.form.get("email", False) #request.form["email"]
        print (email)
        password = request.form["password"]
        sql = "SELECT * FROM REGISTER WHERE EMAIL=? AND PASSWORD=?" # from db2 sql table
        stmt = ibm_db.prepare(conn, sql)
        # this username & password is should be same as db-2 details & order also
        ibm_db.bind_param(stmt, 1, email)
        ibm_db.bind_param(stmt, 2, password)
        ibm_db.execute (stmt)
        account = ibm_db.fetch_assoc(stmt)
        print (account)
        if account:
            session['Loggedin'] = True
            session['id'] = account['EMAIL']
            Userid = account['EMAIL']
            session['email'] = account['EMAIL']
            Username = account['USERNAME']
            Name = account['NAME']
            msg = "logged in successfully 1"
            sql = "SELECT ROLE FROM register where email = ?"
            stmt = ibm_db.prepare(conn, sql)
            ibm_db.bind_param(stmt, 1, email)
            ibm_db.execute(stmt)
            r = ibm_db.fetch_assoc(stmt)
            print(r)
            if r['ROLE'] == 1:
                print ("STUDENT")
                return render_template("studentprofile.html", msg=msg, user=email, name= Name, role="STUDENT", username=Username, email = email)

            elif r['ROLE'] == 2:
                print ("FACULTY")
                return render_template("facultyprofile.html", msg=msg, user=email, name= Name, role= "FACULTY", username=Username, email = email)

            else:
                print("Admin")
                return render_template("adminprofile.html", msg=msg, user=email, name =Name, role= "ADMIN", username=Username, email = email)
        else:
            msg = "Incorrect Email/password"
            return render_template("login_new.html", msg=msg)
    else:
        return render_template("login_new.html")

@app.route("/adminprofile")
def aprofile():
    return render_template("adminprofile.html");


@app.route("/register", methods=['POST', 'GET'])
def signup():
    msg = ''
    if request.method == 'POST':
        name = request.form["sname"]
        email = request.form["semail"]
        username = request.form["susername"]
        role =int(request.form['role'])
        password = ''.join(random.choice(string.ascii_letters) for i in range(0,8))
        link = 'https://127.0.0.1:5000/portal'
        print (password)
        sql = "SELECT* FROM register WHERE email= ?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt, 1, email)
        ibm_db.execute (stmt)
        account = ibm_db.fetch_assoc(stmt)
        print (account)
        if account:
            msg = "Already Registered"
            return render_template('adminregister.html', error=True, msg=msg)
        elif not re.match(r'[*@]+@["@]+\.["@]+"', email):
            msg = "Invalid Email Address!"
        else:
            insert_sql = "INSERT INTO register VALUES (?,2,?,?,?)"
            prep_stmt = ibm_db.prepare(conn, insert_sql)
            # this username & password is should be same as db-2 details & order also
            ibm_db.bind_param(prep_stmt, 1, name)
            ibm_db.bind_param(prep_stmt, 2, email)
            ibm_db.bind_param(prep_stmt, 3, username)
            ibm_db.bind_param(prep_stmt, 5, role)
        payload = { "personalizations": [{
          "to": [{"email": email}],
         "subject": "Student Account Details"}],
         "from": {"email": "<Enter Your Sender Email Id"},
         "content": [
         {
            "type": "text/plain",
            "value": """Dear {} , \n Welcome to University,
            Here there the details to Login Into your student portal link : {} \n
            YOUR Username : {} \n PASSWORD : {} \n Thank you \n Sincerely\n
            Office of Admissions\n Mahidhar Institute of Technology \n
            E-Mail: admission@university.ac.in ; Website: www.university.ac.in""".format( name,link, username, password)
         }]
        }
        headers = {"content-type": "application/json","X-RapidAPI-Key": "822ede7669mshb713e5ef2fa2a56p16901bjsne120f101155a","X-RapidAPI-Host":"rapidprod-sendgrid-vi1.p.rapidapi.com"}

    response = requests.request("POST", link, json=payload, headers=headers)
    print(response.text)
    msg = "Registration Successful"
    return render_template('adminregister.html', msg=msg)

@app.route("/studentprofile")
def sprofile():
    return render_template("studentprofile.html");

@app.route("/studentsubmit", methods=['POST','GET'])
def sassignment():
    u = Username.strip()
    subtime = []
    ma = []
    sql = "SELECT CSUBMITTIME, MARKS from SUBMIT WHERE STUDENTNAME = ?"
    stmt = ibm_db.prepare(conn, sql)
    ibm_db.bind_param(stmt, 1, u)
    ibm_db.execute(stmt)
    st = ibm_db.fetch_tuple(stmt)
    while st !=False:
        subtime.append(st[0])
        ma.append(st[1])
        st = ibm_db.fetch_tuple(stmt)
    print(subtime)
    print(ma)
    if request.method == "POST":
        for x in range (1,5):
            x = str(x)
            y = str("file"+x)
            print(type(y))
            f=request.files[y]
            print (f)
            print (f.filename)
            if f.filename !=' ':
                basepath=os.path.dirname(__file__) #getting the current path i.e where app.py is present
                #print(“"current path",basepath)
                filepath=os.path.join(basepath, 'uploads' ,u+x+".pdf") #from anywhere in the system we can give image but we want that image 1
                #print ("upload folder is",filepath)
                f.save(filepath)

                # connecting with cloud object storage
                COS_ENDPOINT = "https://control.cloud-object-storage.cloud.ibm.com/v2/endpoints"
                COS_API_KEY_ID = "UZhmyj2B8up4Yx1mB8OJlQx41YyjjoAdYv1-3qz_QAuX"
                COS_INSTANCE_CRN = "crn:v1:bluemix:public:iam-identity::a/ffec9de38c3746659cbd8fce0ee6a765::serviceid:ServiceId-6ad347b1-a21a-489f-8aa7-9787a631d3a3"
                cos = ibm_boto3.client("s3",ibm_api_key_id=COS_API_KEY_ID,ibm_service_instance_id=COS_INSTANCE_CRN,config=Config(signature_version="oauth"),endpoint_url=COS_ENDPOINT)
                cos.upload_file(Filename= filepath,Bucket="studentassignment",Key= u+x+".pdf")
                msg = "Uploding Successful"
                ts = datetime.datetime.now()
                t = ts.strftime("%Y-%m-%d %H:%M:%S")
                sqll = "SELECT * FROM SUBMIT WHERE STUDENTNAME = ? AND ASSIGNMENTNUM = ?"
                stmt = ibm_db.prepare(conn, sqll)
                ibm_db.bind_param(stmt,1, u)
                ibm_db.bind_param(stmt,2, x)
                ibm_db.execute (stmt)
                acc = ibm_db.fetch_assoc(stmt)

                print(acc)
                if acc == False:
                    sql = "INSERT into SUBMIT (STUDENTNAME, ASSIGNMENTNUM, SUBMITTIME) values (?,?,?)"
                    stmt = ibm_db.prepare(conn, sql)
                    ibm_db.bind_param(stmt, 1, u)
                    ibm_db.bind_param(stmt, 2, x)
                    ibm_db.bind_param(stmt, 3, t)
                    ibm_db.execute(stmt)
                else:
                    sql = "UPDATE SUBMIT SET SUBMITTIME = ? WHERE STUDENTNAME = ? and ASSIGNMENTNUM = ?"
                    stmt = ibm_db.prepare(conn, sql)
                    ibm_db.bind_param(stmt, 1, t)
                    ibm_db.bind_param(stmt, 2, u)
                    ibm_db.bind_param(stmt, 3, x)
                    ibm_db.execute(stmt)

            return render_template("studentsubmit.html", msg=msg, datetime=subtime, marks=ma)
            continue
    return render_template("studentsubmit.html", datetime=subtime, Marks=ma)

@app.route("/facultyprofile")
def fprofile():
    return render_template("facultyprofile.html");

@app.route("/facultymarks")
def facultymarks():
    data=[]
    sql = "SELECT USERNAME from REGISTER WHERE ROLE=1"
    stmt = ibm_db.prepare(conn, sql)
    ibm_db.execute(stmt)
    name = ibm_db.fetch_tuple(stmt)
    while name!= False:
        data.append(name)
        name=ibm_db.fetch_tuple(stmt)
    datal = []
    for i in range(0,len(data)):
        y = data[i][0].strip()
        datal.append(y)
        datal = set(datal)
        datal = list(datal)
    print(datal)
    return render_template("facultystulist.html", names=datal, Lle=len(datal))

@app.route("/marksassign/<string:stdname>", methods=['POST', 'GET'])
def marksassign(stdname):
    global u
    global g
    global file
    da = []

    COS_ENDPOINT = "https://control.cloud-object-storage.cloud.ibm.com/v2/endpoints"
    COS_API_KEY_ID = "UZhmyj2B8up4Yx1mB8OJlQx41YyjjoAdYv1-3qz_QAuX"
    COS_INSTANCE_CRN = "crn:v1:bluemix:public:iam-identity::a/ffec9de38c3746659cbd8fce0ee6a765::serviceid:ServiceId-6ad347b1-a21a-489f-8aa7-9787a631d3a3"
    cos = ibm_boto3.client("s3",ibm_api_key_id=COS_API_KEY_ID,ibm_service_instance_id=COS_INSTANCE_CRN,config=Config(signature_version="oauth"),endpoint_url=COS_ENDPOINT)
    output = cos.list_objects(Bucket="studentassignmentsb")
    output
    l=[]
    for i in range(0,len(output['Contents'])):
        j = output['Contents'][i]['Key']
        l.append(j)
    l
    u = stdname
    print(len(u))
    print(len(l))

    n=[]
    for i in range(0,len(l)):
        for j in range(0,len(u)):
            if u[j]==l[i][j]:
                n.append(l[i])

@app.route("/facultymarks")
def afacultymarks():
    data=[]
    sql = "SELECT USERNAME from REGISTER WHERE ROLE=1"
    stmt = ibm_db.prepare(conn, sql)
    ibm_db.execute(stmt)
    name = ibm_db.fetch_tuple(stmt)
    while name!= False:
        data.append(name)
        name=ibm_db.fetch_tuple(stmt)
    datal = []
    for i in range(0,len(data)):
        y = data[i][0].strip()
        datal.append(y)
    datal = set(datal)
    datal = list(datal)
    print(datal)
    return render_template("facultystulist.html", names=datal, Lle=len(datal))

@app.route("/marksupdate/<string:anum>", methods=['POST', 'GET'])
def marksupdate(anum):  
    ma = []
    da = []

    mark = request.form['mark']
    print(mark)

    print (u)

    sql = "UPDATE SUBMIT SET MARKS = ? WHERE STUDENTNAME = ? and ASSIGNMENTNUM = ?"
    stmt = ibm_db.prepare(conn, sql)
    ibm_db.bind_param(stmt, 1, mark)
    ibm_db.bind_param(stmt, 2, u)
    ibm_db.bind_param(stmt, 3, anum)
    ibm_db.execute (stmt)
    msg = "MARKS UPDATED"
    sql = "SELECT MARKS, SUBMITTIME from SUBMIT WHERE STUDENTNAME=?"
    stmt = ibm_db.prepare(conn, sql)
    ibm_db.bind_param(stmt , 1, u)
    ibm_db.execute (stmt)
    m = ibm_db.fetch_tuple(stmt)
    while m != False:
        ma.append(m[0])
        da.append(m[1])
        m = ibm_db.fetch_tuple(stmt)
            #ma = ma[@]
    print(ma)
    print(da)
    return render_template("facultymarks.html", msg =msg, marks = ma, g=g, file=file, datetime=da)

@app.route("/logout")
def logout():
    session.pop('loggedin®', None)
    session.pop('id', None)
    session.pop( 'username', None)
    return render_template("logout.html")
                           

