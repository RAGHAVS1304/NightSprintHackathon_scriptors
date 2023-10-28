from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import bcrypt

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///worklogindb.db'
app.config['SQLALCHEMY_BINDS'] = {"two" : "sqlite:///contlogindb.db",
                                  "three" : "sqlite:///jobsdb.db",
                                  "four" : "sqlite:///fill_formdb.db"}
db = SQLAlchemy(app)
app.secret_key = 'secret_key'

class WorkLogin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100), nullable=False)

    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        # self.password = password
        
    def check_password(self,password):
        return bcrypt.checkpw(password.encode('utf-8'),self.password.encode('utf-8'))
        # return password == self.password

class ContLogin(db.Model):
    __bind_key__ = "two"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100), nullable=False)
    
    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        # self.password = password
        
    def check_password(self,password):
        return bcrypt.checkpw(password.encode('utf-8'),self.password.encode('utf-8'))
        # return password == self.password

class Jobs(db.Model):
    __bind_key__ = "three"
    id = db.Column(db.Integer, primary_key=True)
    company = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    salary = db.Column(db.String(100), nullable=False)
    req = db.Column(db.String(1000), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    desc = db.Column(db.String(1000), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, company, location, salary, req, title, desc):
        self.company = company
        self.location = location
        self.salary = salary
        self.req = req
        self.title = title
        self.desc = desc

class FillForm(db.Model):
    __bind_key__ = "four"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(100), nullable=True)
    email = db.Column(db.String(100), nullable=False)
    jobId = db.Column(db.Integer, nullable=False)
    pno = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(100), nullable=False)


    def __init__(self, name, state, email, jobId, pno, gender):
        self.name = name
        self.state = state
        self.email = email
        self.jobId = jobId
        self.pno = pno
        self.gender = gender

with app.app_context():
    db.create_all()

@app.route("/cont_register", methods=['GET','POST'])
def cont_register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        db.session.add(ContLogin( name, email, password))
        db.session.commit()
        return redirect("/")

    return render_template("cont_register.html")

@app.route("/cont_login", methods = ["GET","POST"])
def cont_login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        user = ContLogin.query.filter_by(email=email).first()
        if user and user.check_password(password):
            session["email"] = user.email
            return redirect("/cont_dashboard")
        else:
            return render_template("cont_login.html", error="Invalid email or password")
    return render_template("cont_login.html")

@app.route("/work_login", methods = ["GET", "POST"])
def work_login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        user = WorkLogin.query.filter_by(email=email).first()
        if user and user.check_password(password):
            session["email"] = user.email
            return redirect("/work_dashboard")
        else:
            return render_template("work_login.html", error="Invalid email or password")
        
    return render_template("work_login.html")


@app.route("/work_register", methods=['GET','POST'])
def work_register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        db.session.add(WorkLogin( name, email, password))
        db.session.commit()
        return redirect("/")

    return render_template("work_register.html")

@app.route("/create_job", methods=["GET","POST"])
def create_job():
    if request.method == "POST":
        company = request.form["company"]
        title = request.form["title"]
        desc = request.form["desc"]
        req = request.form["req"]
        location = request.form["loc"]
        salary = request.form["salary"]
        db.session.add(Jobs( company = company, title = title, desc = desc, req = req, location = location, salary = salary))
        db.session.commit()
        return redirect("/cont_dashboard")
    
    return render_template("create_job.html")

@app.route("/fill_form", methods=["GET","POST"])
def fill_form_input():
    if request.method == "POST":
        name=request.form["name"]
        state=request.form["state"]
        email=request.form["email"]
        pno=request.form["pno"]
        jobId=request.form["jobId"]
        gender=request.form["gender"]
        db.session.add(FillForm(name=name, state=state, email=email, pno=pno, jobId=jobId, gender=gender))
        db.session.commit()
        return redirect("/work_dashboard")

@app.route("/work_dashboard")
def work_dashboard():
    if session["email"]:
        user = WorkLogin.query.filter_by(email=session['email']).first()
        return render_template('work_dashboard.html',user=user)

@app.route("/cont_dashboard")
def cont_dashboard():
    if session["email"]:
        user = ContLogin.query.filter_by(email=session['email']).first()
        return render_template('cont_dashboard.html',user=user)

@app.route("/job_list")
def job_list():
    allJobs = Jobs.query.all()
    return render_template("job_list.html", allJobs = allJobs)

@app.route("/fill_form/<int:jobId>")
def fill_form(jobId):    
    return render_template("fill_form.html", jobId = jobId)

@app.route("/past_forms")
def past_forms():
    fillform = FillForm.query.all()
    return render_template("past_forms.html", fillform = fillform)


@app.route("/logout")
def logout():
    session.pop('email',None)
    return redirect('/work_login')

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug = True)