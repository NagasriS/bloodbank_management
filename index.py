from flask import *
from twilio.rest import Client
from werkzeug.utils import secure_filename
from flask_ngrok import run_with_ngrok
import mysql.connector 
import os
import csv
app=Flask(__name__)
run_with_ngrok(app)
app.secret_key="Don't share"
myconn=mysql.connector.connect(
	host="localhost",
	user="root",
	passwd="",
	database="bloodbank"
	)


@app.route("/")
@app.route("/bloodbank")
def bloodbank():
	return render_template("bloodbank.html")
@app.route("/home")
def home():
	cur=myconn.cursor()
	cur.execute("select count(*) from donor where status=1")
	data=cur.fetchall()
	return render_template("index.html",data=data)
@app.route("/login",methods=['GET','POST'])
def login():
	if request.method == "POST":
		username=request.form['username']
		password=request.form['password']
		cur=myconn.cursor()
		cur.execute("""select * from admin where 
			username=%s and password=%s""",(username,password))
		data=cur.fetchall()
		if data:
			session['loggedin']=True
			flash("Login Successfully")
			return render_template("info.html")
		else:
			flash("Incorrect Username or Password")
	return render_template("login.html")

@app.route("/register",methods=['GET','POST'])
def register():
	if request.method == "POST":
		name=request.form['name']
		email=request.form['email']
		phno=request.form['phno']
		blood_group=request.form['blood_group']
		weight=request.form['weight']
		gender=request.form['gender']
		dob=request.form['dob']
		address=request.form['address']
		adharno=request.form['adharno']
		mycur=myconn.cursor()
		mycur.execute("select * from donor where adharno=(%s)"%(adharno))
		data=mycur.fetchall()
		if len(data)==0:
			mycur.execute("""insert into donor(name,email,phno,blood_group,
				weight,gender,dob,address,adharno)values(%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
				(name,email,phno,blood_group,weight,gender,dob,address,adharno))
			myconn.commit()
			flash("Registered Successfully")
		else:
			flash("Already Registered")
		return redirect(url_for('register'))

	else:
		return render_template("about.html")
@app.route("/send",methods=['GET','POST'])
def send():
	if request.method=="POST":
		id=request.form['send']
		mycur=myconn.cursor()
		mycur.execute("select phno from donor where sno=%s"%(id))
		data=mycur.fetchall()
		
		account_sid = 'AC1916849916eb04c1ff50a8e93bb94390' 
		auth_token = 'a1d1e952b3ae57a4583d2beb6849e27f' 
		client = Client(account_sid, auth_token) 
		message = client.messages.create( 
   	                  	from_='+12067373432',  
   	                  	body="""Hi Donor! There is an urgent need of blood of your group. 
   	                  			looking forward for your help""",      
   	                  	to='+91'+str(data) 
   	                  	) 
		if message.sid:
			flash("message sent")

			return redirect('viewdonor')
@app.route("/view",methods=['GET','POST'])
def view():
	if not session.get('loggedin'):
		return render_template("login.html")
	cur=myconn.cursor()
	cur.execute("select * from donor where status=1")
	data=cur.fetchall()

	return render_template("view.html",data=data)
@app.route("/inactive",methods=['GET','POST'])
def inactive():
	if not session.get('loggedin'):
		return render_template("login.html")
	cur=myconn.cursor()
	cur.execute("select * from donor where status=0")
	data=cur.fetchall()
	return render_template("inactive.html",data=data)
@app.route("/viewdonor",methods=['GET','POST'])	
def viewdonor():
	cur=myconn.cursor()
	cur.execute("select distinct blood_group from donor where status=1")
	data=cur.fetchall()
	return render_template("select.html",data=data)
@app.route("/viewselected",methods=['GET','POST'])	
def viewselected():
	blood_group=request.form['blood_group']
	cur=myconn.cursor()
	cur.execute("select * from donor where blood_group=(%s) and status=1",(blood_group,))
	data=cur.fetchall()
	return render_template("view2.html",data=data)
@app.route("/viewall",methods=['GET','POST'])	
def viewall():
	cur=myconn.cursor()
	cur.execute("select * from donor where status=1")
	data=cur.fetchall()
	return render_template("view2.html",data=data)
@app.route("/delete",methods=['GET','POST'])
def delete():
	if not session.get('loggedin'):
		return render_template("login.html")
	if request.method == "POST":
		id=request.form['delete']
		cur=myconn.cursor()
		cur.execute("delete from donor where sno=%s"%(id))
		myconn.commit()
		flash('Deleted Successfully')
	return redirect(url_for('view')) 
@app.route("/hold",methods=['GET','POST'])
def hold():
	if not session.get('loggedin'):
		return render_template("login.html")
	if request.method == "POST":
		id=request.form['hold']
		cur=myconn.cursor()
		cur.execute("update donor set status=0 where sno=%s"%(id))
		myconn.commit()
		return redirect(url_for('view'))
@app.route("/activate",methods=['GET','POST']) 
def activate():
	if not session.get('loggedin'):
		return render_template("login.html")
	if request.method == "POST":
		id=request.form['activate']
		cur=myconn.cursor()
		cur.execute("update donor set status=1 where sno=%s"%(id))
		myconn.commit()
		return redirect(url_for('inactive')) 
@app.route("/edit",methods=['GET','POST'])
def edit():
	if not session.get('loggedin'):
		return render_template("login.html")
	if request.method == "POST":
		id=request.form['edit']
		cur=myconn.cursor()
		cur.execute("select * from donor where sno=%s"%(id))
		data=cur.fetchall()
		return render_template("edit.html",data=data)

@app.route("/update",methods=['GET','POST'])
def update():
	if not session.get('loggedin'):
		return render_template("login.html")
	if request.method == "POST":
		id=request.form['id']
		name=request.form['name']
		email=request.form['email']
		phno=request.form['phno']
		blood_group=request.form['blood_group']
		weight=request.form['weight']
		gender=request.form['gender']
		dob=request.form['dob']
		address=request.form['address']
		adharno=request.form['adharno']
		mycur=myconn.cursor()
		mycur.execute("""update donor set name=%s,email=%s,phno=%s,blood_group=%s,
			weight=%s,gender=%s,dob=%s,address=%s,adharno=%s where sno=%s""",
			(name,email,phno,blood_group,weight,gender,dob,address,adharno,id))
		myconn.commit()
		return redirect(url_for('view'))

@app.route("/logout")
def logout():
	session['loggedin']=False
	return render_template("index.html")

if __name__=="__main__":
	app.run()
