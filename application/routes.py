from application import app, db
from flask import render_template, request, session, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime, date
import re

class Userstore(db.Model):
    __tablename__ = 'userstore'
    id = db.Column(db.Integer, primary_key=True)
    uname = db.Column(db.String(20))
    password = db.Column(db.String(20))

class Hospital(db.Model):
    __tablename__ = 'hospital'
    hospital_id = db.Column(db.Integer, primary_key=True)
    hospital_name = db.Column(db.String(20))
    hospital_location = db.Column(db.String(20))

class Equipments(db.Model):
    __tablename__ = 'equipments'
    equipment_id = db.Column(db.Integer, primary_key=True)
    equipment_name = db.Column(db.String(20))
    quantity = db.Column(db.Integer)
    e_hospital_id = db.Column(Integer, ForeignKey('hospital.hospital_id'))

class Department(db.Model):
     __tablename__ = 'department'
     department_id = db.Column(db.Integer, primary_key=True)
     department_name = db.Column(db.String(20))
     department_head_ssn = db.Column(db.Integer)
     d_hospital_id = db.Column(db.Integer, ForeignKey('hospital.hospital_id'))

class Staff(db.Model):
    __tablename__ = 'staff'
    ssn_id = db.Column(db.Integer, primary_key=True)
    s_name = db.Column(db.String(20), nullable=False)
    age = db.Column(db.Integer, db.CheckConstraint('1<age<101'))
    sex = db.Column(db.String(1))
    designation = db.Column(db.String(20))
    s_dno = db.Column(db.Integer, ForeignKey('department.department_id'))
    s_eqp_id = db.Column(db.Integer, ForeignKey('equipments.equipment_id'))
    s_hospital_id = db.Column(Integer, ForeignKey('hospital.hospital_id'))

class Patients(db.Model):
    __tablename__ = 'patients'
    p_id = db.Column(db.Integer, primary_key=True)
    pname = db.Column(db.String(20), nullable=False)
    sex = db.Column(db.String(1))
    age = db.Column(db.Integer, db.CheckConstraint('1<age<101'))
    risk = db.Column(db.String(20))
    p_eqp_id = db.Column(db.Integer, ForeignKey('equipments.equipment_id'))
    p_dno = db.Column(db.Integer, ForeignKey('department.department_id'))
    p_hospital_id = db.Column(Integer, ForeignKey('hospital.hospital_id'))


db.create_all()


@app.route('/', methods=['GET', 'POST'])
def login():
    if 'username' in session:                # Checking for session login
        return redirect( url_for('home') )

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        usr = Userstore.query.filter_by(uname = username).first()
        if usr == None:
            flash('User Not Found', category='error')
            return redirect( url_for('login') )

        elif username == usr.uname and password == usr.password:
            session['username'] = username  # saving session for login
            return redirect( url_for('home') )

        else:
            flash('Wrong Credentials. Check Username and Password Again', category="error")

    return render_template("login.html")


@app.route('/registration', methods=['GET', 'POST'])
def registration():
    if request.method == 'POST':
        uname = request.form['uname']
        password = request.form['pass']
        cnfrm_password = request.form['cpass']

        query = Userstore.query.filter_by(uname = uname).first()

        if query != None:
            if uname == str(query.uname):
                flash('Username already taken')
                return redirect( url_for('registration') )

        if password != cnfrm_password:
            flash('Passwords do not match')
            return redirect( url_for('registration') )

        regex = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{6,20}$"
        pattern = re.compile(regex)

        match = re.search(pattern, password)

        if match:
            user = Userstore(uname = uname, password = password)
            db.session.add(user)
            db.session.commit()
            flash('Staff Registred Successfully', category='info')
            return redirect( url_for('login') )
        else:
            flash('Password should contain one Uppercase, one special character, one numeric character')
            return redirect( url_for('registration') )
    return render_template('registration.html')


@app.route('/home')
def home():
    if 'username' in session:
        return render_template('home.html')
    else:
        flash('You are logged out. Please login again to continue')
        return redirect( url_for('login') )


@app.route('/create_hospital', methods=['GET', 'POST'])
def create_hospital():
    if 'username' in session:
        if request.method == "POST":
            hospital_id = request.form['hid']
            hospital_name = request.form['hname']
            hospital_location = request.form['hlocation']

            hosp = Hospital.query.filter_by( hospital_id = hospital_id ).first()

            if hosp == None:
                hospital = Hospital(hospital_id=hospital_id, hospital_name=hospital_name, hospital_location=hospital_location)
                db.session.add(hospital)
                db.session.commit()
                flash('Hospital creation initiated successfully')
                return redirect( url_for('create_hospital') )

            else:
                flash('Hospital already exists')
                return redirect( url_for('create_hospital') )
    else:
        flash('You are logged out. Please login again to continue')
        return redirect( url_for('login') )

    return render_template('create_hospital.html')

@app.route('/update_hospital')
def update_hospital():
    if 'username' in session:
        usern = session['username']
        print(usern)
        updatep = Hospital.query.all()

        if not updatep:
            flash('No hospital exists in database')
            return redirect( url_for('create_hospital') )
        else:
            print("inside else")
            return render_template('update_hospital.html', updatep = updatep)

    else:
        flash('You have been logged out. Please login again')
        return redirect( url_for('login') )
    return render_template('update_hospital.html')

@app.route('/edithospitaldetail/<id>', methods=['GET', 'POST'])
def edithospitaldetail(id):
    print("id is : ", id)
    if 'username' in session:
        print("inside sesssss")
        print(datetime.now())
        editpat = Hospital.query.filter_by( hospital_id = id )

        if request.method == 'POST':
            print("inside editpat post mtd")
            hospital_id = request.form['hid']
            hospital_name = request.form['hname']
            hospital_location = request.form['hlocation']

            row_update = Hospital.query.filter_by( hospital_id = hospital_id ).update(dict(hospital_id=hospital_id, hospital_name=hospital_name, hospital_location=hospital_location))
            db.session.commit()
            print("Roww update", row_update)

            if row_update == None:
                flash('Something Went Wrong')
                return redirect( url_for('update_hospital') )
            else:
                flash('Hospital update initiated successfully')
                return redirect( url_for('update_hospital') )

        return render_template('edithospitaldetail.html', editpat = editpat)

@app.route('/deletehosp')
def deletehosp():
    if 'username' in session:
        usern = session['username']
        print(usern)
        updatep = Hospital.query.all()


        if not updatep:
            flash('No Hospitals exists in database')
            return redirect( url_for('create_hospital') )
        else:
            print("inside else")
            return render_template('deletehosp.html', updatep = updatep)

    else:
        flash('You have been logged out. Please login again')
        return redirect( url_for('login') )

    return render_template('deletehosp.html')

@app.route('/deletehospitaldetail/<id>')
def deletehospitaldetail(id):
    if 'username' in session:
        delpat = Hospital.query.filter_by(hospital_id = id).delete()
        db.session.commit()

        if delpat == None:
            flash('Something Went Wrong')
            return redirect( url_for('update_hospital') )
        else:
            flash('Patient deletion initiated successfully')
            return redirect( url_for('update_hospital') )

    return render_template('update_hospital.html')


# Departments section


@app.route('/create_department', methods=['GET', 'POST'])
def create_department():
    if 'username' in session:
        if request.method == "POST":
            department_id = request.form['dno']
            department_name = request.form['dname']
            department_head_ssn = request.form['dhead']
            d_hospital_id = request.form['hid']

            dept = Department.query.filter_by( department_id = department_id ).first()

            if dept == None:
                department = Department(department_id=department_id, department_name=department_name, department_head_ssn=department_head_ssn, d_hospital_id=d_hospital_id)
                db.session.add(department)
                db.session.commit()
                flash('Department creation initiated successfully')
                return redirect( url_for('create_department') )

            else:
                flash('Department already exists')
                return redirect( url_for('create_department') )
    else:
        flash('You are logged out. Please login again to continue')
        return redirect( url_for('login') )

    return render_template('create_department.html')

@app.route('/update_department')
def update_department():
    if 'username' in session:
        usern = session['username']
        print(usern)
        updatep = Department.query.all()


        if not updatep:
            flash('No Departments exists in database')
            return redirect( url_for('create_department') )
        else:
            print("inside else")
            return render_template('update_department.html', updatep = updatep)

    else:
        flash('You have been logged out. Please login again')
        return redirect( url_for('login') )

    return render_template('update_department.html')

@app.route('/editdepartmentdetail/<id>', methods=['GET', 'POST'])
def editdepartmentdetail(id):
    print("id is : ", id)
    if 'username' in session:
        print("inside sesssss")
        print(datetime.now())
        editdep = Department.query.filter_by( department_id = id )


        if request.method == 'POST':

            print("inside editpat post mtd")
            department_id = request.form['d_id']
            department_name = request.form['d_name']
            department_head_ssn = request.form['d_head']
            d_hospital_id = request.form['d_hid']

            ldate = datetime.today()
            row_update = Department.query.filter_by( department_id = id ).update(dict(department_id=department_id, department_name=department_name, department_head_ssn=department_head_ssn, d_hospital_id=d_hospital_id))
            db.session.commit()
            print("Roww update", row_update)

            if row_update == None:
                flash('Something Went Wrong')
                return redirect( url_for('update_department') )
            else:
                flash('Department update initiated successfully')
                return redirect( url_for('update_department') )

        return render_template('editdepartmentdetail.html', editpat = editdep)


@app.route('/deletedep')
def deletedep():
    if 'username' in session:
        usern = session['username']
        print(usern)
        updatep = Department.query.all()


        if not updatep:
            flash('No patients exists in database')
            return redirect( url_for('create_department') )
        else:
            print("inside else")
            return render_template('deletedep.html', updatep = updatep)

    else:
        flash('You have been logged out. Please login again')
        return redirect( url_for('login') )

    return render_template('deletedep.html')

@app.route('/deletedepartmentdetail/<id>')
def deletedepartmentdetail(id):
    if 'username' in session:
        delpat = Department.query.filter_by(department_id = id).delete()
        db.session.commit()

        if delpat == None:
            flash('Something Went Wrong')
            return redirect( url_for('update_department') )
        else:
            flash('Patient deletion initiated successfully')
            return redirect( url_for('update_department') )

    return render_template('update_department.html')




#Staff related operations


@app.route('/create_staff', methods=['GET', 'POST'])
def create_staff():
    if 'username' in session:
        if request.method == "POST":
            ssn_id = request.form['ssn']
            s_name = request.form['sname']
            designation = request.form['sdesignation']
            age = request.form['Age']
            sex = request.form['gender']
            s_eqp_id = request.form['seid']
            s_dno = request.form['sdno']
            s_hospital_id = request.form['shospid']

            staf = Staff.query.filter_by( ssn_id = ssn_id ).first()

            if staf == None:
                staff = Staff(ssn_id=ssn_id, s_name=s_name, designation=designation, age=age, sex=sex, s_eqp_id=s_eqp_id, s_dno=s_dno,  s_hospital_id = s_hospital_id)
                db.session.add(staff)
                db.session.commit()
                flash('Staff creation initiated successfully')
                return redirect( url_for('create_staff') )

            else:
                flash('Staff already exists')
                return redirect( url_for('create_staff') )
    else:
        flash('You are logged out. Please login again to continue')
        return redirect( url_for('login') )

    return render_template('create_staff.html')

@app.route('/search_staff', methods=['GET', 'POST'])
def search_staff():
    if 'username' in session:
        if request.method == 'POST':
            s_id = request.form['id']

            if s_id != "":
                staff = Staff.query.filter_by( ssn_id = s_id)
                if staff == None:
                    flash('No  Staff with  this ID exists')
                    return redirect( url_for('search_staff') )
                else:
                    flash('Staff Found')
                    return render_template('search_staff.html', staff = staff)

            if s_id == "":
                flash('Enter  id to search')
                return redirect( url_for('search_staff') )

    else:
        return redirect( url_for('login') )

    return render_template('search_staff.html')


@app.route('/update_staff')
def update_staff():
    if 'username' in session:
        usern = session['username']
        print(usern)
        updatep = Staff.query.all()


        if not updatep:
            flash('No Staff exists in database')
            return redirect( url_for('create_staff') )
        else:
            print("inside else")
            return render_template('update_staff.html', updatep = updatep)

    else:
        flash('You have been logged out. Please login again')
        return redirect( url_for('login') )
    return render_template('update_staff.html')

@app.route('/editstaffdetail/<id>', methods=['GET', 'POST'])
def editstaffdetail(id):
    print("id is : ", id)
    if 'username' in session:
        print("inside sesssss")
        print(datetime.now())
        editpat = Staff.query.filter_by( ssn_id = id )
        if request.method == 'POST':
            print("inside editpat post mtd")
            staff_ssn = request.form['ssn_id']
            s_name = request.form['s_name']
            age = request.form['Age']
            sex = request.form['gender']
            designation = request.form['designation']
            s_dno = request.form['sdno']
            s_eqp_id = request.form['seid']
            s_hospital_id = request.form['shospid']
            ldate = datetime.today()
            row_update = Staff.query.filter_by( ssn_id = id ).update(dict(ssn_id=staff_ssn, s_name=s_name, age=age, sex=sex, designation=designation, s_dno=s_dno, s_eqp_id = s_eqp_id, s_hospital_id=s_hospital_id))
            db.session.commit()
            print("Roww update", row_update)

            if row_update == None:
                flash('Something Went Wrong')
                return redirect( url_for('update_staff') )
            else:
                flash('Staff update initiated successfully')
                return redirect( url_for('update_staff') )

        return render_template('editstaffdetail.html', editpat = editpat)


@app.route('/deletestaff')
def deletestaff():
    if 'username' in session:
        usern = session['username']
        print(usern)
        updatep = Staff.query.all()


        if not updatep:
            flash('No patients exists in database')
            return redirect( url_for('create_staff') )
        else:
            print("inside else")
            return render_template('deletestaff.html', updatep = updatep)

    else:
        flash('You have been logged out. Please login again')
        return redirect( url_for('login') )

    return render_template('deletestaff.html')

@app.route('/deletestaffdetail/<id>')
def deletestaffdetail(id):
    if 'username' in session:
        delpat = Staff.query.filter_by(ssn_id = id).delete()
        db.session.commit()

        if delpat == None:
            flash('Something Went Wrong')
            return redirect( url_for('update_staff') )
        else:
            flash('Patient deletion initiated successfully')
            return redirect( url_for('update_staff') )

    return render_template('update_staff.html')


















## Creating, Updating, Deleting patient section

@app.route('/create_patient', methods=['GET', 'POST'])
def create_patient():
    if 'username' in session:
        if request.method == "POST":
            p_id = request.form['pid']
            pname = request.form['pname']
            sex = request.form['gender']
            age = request.form['Age']
            risk = request.form['risk']
            p_eqp_id = request.form['peid']
            p_dno = request.form['pdno']
            p_hospital_id = request.form['phospid']

            pat = Patients.query.filter_by( p_id = p_id ).first()

            if pat == None:
                patient = Patients(p_id=p_id, pname=pname, sex=sex, age=age, risk=risk, p_eqp_id=p_eqp_id, p_dno=p_dno,  p_hospital_id = p_hospital_id)
                db.session.add(patient)
                db.session.commit()
                flash('Patient creation initiated successfully')
                return redirect( url_for('create_patient') )

            else:
                flash('Patient with this Patient ID already exists')
                return redirect( url_for('create_patient') )
    else:
        flash('You are logged out. Please login again to continue')
        return redirect( url_for('login') )

    return render_template('create_patient.html')


@app.route('/update_patient')
def update_patient():
    if 'username' in session:
        usern = session['username']
        print(usern)
        updatep = Patients.query.all()


        if not updatep:
            flash('No patients exists in database')
            return redirect( url_for('create_patient') )
        else:
            print("inside else")
            return render_template('update_patient.html', updatep = updatep)

    else:
        flash('You have been logged out. Please login again')
        return redirect( url_for('login') )
    return render_template('update_patient.html')


@app.route('/editpatientdetail/<id>', methods=['GET', 'POST'])
def editpatientdetail(id):
    print("id is : ", id)
    if 'username' in session:
        print("inside sesssss")
        print(datetime.now())
        editpat = Patients.query.filter_by( p_id = id )


        if request.method == 'POST':

            print("inside editpat post mtd")
            p_id = request.form['pid']
            pname = request.form['pname']
            sex = request.form['gender']
            age = request.form['Age']
            risk = request.form['risk']
            p_eqp_id = request.form['peid']
            p_dno = request.form['pdno']
            p_hospital_id = request.form['phospid']
            ldate = datetime.today()
            row_update = Patients.query.filter_by( p_id = id ).update(dict(p_id=p_id, pname=pname, sex=sex, age=age, risk=risk,  p_eqp_id=p_eqp_id, p_dno=p_dno,  p_hospital_id = p_hospital_id))
            db.session.commit()
            print("Roww update", row_update)

            if row_update == None:
                flash('Something Went Wrong')
                return redirect( url_for('update_patient') )
            else:
                flash('Patient update initiated successfully')
                return redirect( url_for('update_patient') )

        return render_template('editpatientdetail.html', editpat = editpat)

@app.route('/deletepat')
def deletepat():
    if 'username' in session:
        usern = session['username']
        print(usern)
        updatep = Patients.query.all()


        if not updatep:
            flash('No patients exists in database')
            return redirect( url_for('create_patient') )
        else:
            print("inside else")
            return render_template('deletepat.html', updatep = updatep)

    else:
        flash('You have been logged out. Please login again')
        return redirect( url_for('login') )
    return render_template('deletepat.html')



@app.route('/deletepatientdetail/<id>')
def deletepatientdetail(id):
    if 'username' in session:
        delpat = Patients.query.filter_by(p_id = id).delete()
        db.session.commit()

        if delpat == None:
            flash('Something Went Wrong')
            return redirect( url_for('update_patient') )
        else:
            flash('Patient deletion initiated successfully')
            return redirect( url_for('update_patient') )

    return render_template('update_patient.html')





@app.route('/search_patient', methods=['GET', 'POST'])
def search_patient():
    if 'username' in session:
        if request.method == 'POST':
            p_id = request.form['id']

            if p_id != "":
                patients = Patients.query.filter_by( p_id = p_id)
                if patients == None:
                    flash('No  Patients with  this ID exists')
                    return redirect( url_for('search_patient') )
                else:
                    flash('Patient Found')
                    return render_template('search_patient.html', patients = patients)

            if p_id == "":
                flash('Enter  id to search')
                return redirect( url_for('search_patient') )

    else:
        return redirect( url_for('login') )

    return render_template('search_patient.html')




@app.route('/create_equipments', methods=['GET', 'POST'])
def create_equipments():
    if 'username' in session:
        if request.method == "POST":
            equipment_id = request.form['eid']
            equipment_name = request.form['ename']
            quantity = request.form['quan']
            e_hospital_id = request.form['ehospid']

            eqp = Equipments.query.filter_by( equipment_id = equipment_id ).first()

            if eqp == None:
                equipment = Equipments(equipment_id=equipment_id, equipment_name=equipment_name, quantity=quantity, e_hospital_id=e_hospital_id)
                db.session.add(equipment)
                db.session.commit()
                flash('Equipment creation initiated successfully')
                return redirect( url_for('create_equipments') )

            else:
                flash('Equipment already exists')
                return redirect( url_for('create_equipments') )
    else:
        flash('You are logged out. Please login again to continue')
        return redirect( url_for('login') )

    return render_template('create_equipments.html')

@app.route('/update_equipment')
def update_equipment():
    if 'username' in session:
        usern = session['username']
        print(usern)
        updatep = Equipments.query.all()
        if not updatep:
            flash('No Departments exists in database')
            return redirect( url_for('create_equipments') )
        else:
            print("inside else")
            return render_template('update_equipment.html', updatep = updatep)

    else:
        flash('You have been logged out. Please login again')
        return redirect( url_for('login') )

    return render_template('update_equipment.html')

@app.route('/editequipmentdetail/<id>', methods=['GET', 'POST'])
def editequipmentdetail(id):
    print("id is : ", id)
    if 'username' in session:
        print("inside sesssss")
        print(datetime.now())
        editdep = Equipments.query.filter_by( equipment_id = id )


        if request.method == 'POST':

            print("inside editpat post mtd")
            equipment_id = request.form['e_id']
            equipment_name = request.form['e_name']
            quantity = request.form['quantity']
            e_hospital_id  = request.form['e_hid']

            ldate = datetime.today()
            row_update = Equipments.query.filter_by( equipment_id = id ).update(dict(equipment_id=equipment_id, equipment_name=equipment_name, quantity=quantity, e_hospital_id=e_hospital_id))
            db.session.commit()
            print("Roww update", row_update)

            if row_update == None:
                flash('Something Went Wrong')
                return redirect( url_for('update_equipment') )
            else:
                flash('Department update initiated successfully')
                return redirect( url_for('update_equipment') )

        return render_template('editequipmentdetail.html', editpat = editdep)


@app.route('/deleteeqp')
def deleteeqp():
    if 'username' in session:
        usern = session['username']
        print(usern)
        updatep = Equipments.query.all()


        if not updatep:
            flash('No patients exists in database')
            return redirect( url_for('create_equipments') )
        else:
            print("inside else")
            return render_template('deleteeqp.html', updatep = updatep)

    else:
        flash('You have been logged out. Please login again')
        return redirect( url_for('login') )

    return render_template('deleteeqp.html')

@app.route('/deleteequipmentdetail/<id>')
def deleteequipmentdetail(id):
    if 'username' in session:
        delpat = Equipments.query.filter_by(equipment_id = id).delete()
        db.session.commit()

        if delpat == None:
            flash('Something Went Wrong')
            return redirect( url_for('update_equipment') )
        else:
            flash('Patient deletion initiated successfully')
            return redirect( url_for('update_equipment') )

    return render_template('update_equipment.html')

@app.route('/hospital_equipments')
def hospital_equipments():
    if 'username' in session:
        usern = session['username']
        print(usern)
        updatep = db.session.query(Hospital.hospital_id,Hospital.hospital_name,Equipments.equipment_id,Equipments.equipment_name,Equipments.quantity).join(Hospital).filter(Equipments.e_hospital_id==Hospital.hospital_id).all()
        if not updatep:
            flash('No hospital exists in database')
            return redirect( url_for('create_hospital') )
        else:
            print("inside else")
            return render_template('hospital_equipments.html', updatep = updatep)

    else:
        flash('You have been logged out. Please login again')
        return redirect( url_for('login') )

    return render_template('hospital_equipments.html')

@app.route('/patient_equipments')
def patient_equipments():
    if 'username' in session:
        usern = session['username']
        print(usern)
        updatep = db.session.query(Patients.p_id,Patients.pname,Equipments.equipment_id,Equipments.equipment_name).join(Equipments).filter(Patients.p_eqp_id==Equipments.equipment_id).all()
        if not updatep:
            flash('No hospital exists in database')
            return redirect( url_for('create_patient') )
        else:
            print("inside else")
            return render_template('patient_equipments.html', updatep = updatep)

    else:
        flash('You have been logged out. Please login again')
        return redirect( url_for('login') )

    return render_template('patient_equipments.html')
@app.route('/staff_equipments')
def staff_equipments():
    if 'username' in session:
        usern = session['username']
        print(usern)
        updatep = db.session.query(Staff.ssn_id,Staff.s_name,Equipments.equipment_id,Equipments.equipment_name).join(Equipments).filter(Staff.s_eqp_id==Equipments.equipment_id).all()
        if not updatep:
            flash('No hospital exists in database')
            return redirect( url_for('create_staff') )
        else:
            print("inside else")
            return render_template('staff_equipments.html', updatep = updatep)

    else:
        flash('You have been logged out. Please login again')
        return redirect( url_for('login') )
    return render_template('staff_equipments.html')


@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('logged out successfully .')
    return redirect( url_for('login') )
