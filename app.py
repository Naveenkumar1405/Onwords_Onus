import requests
from flask import Flask, render_template, redirect, request, session,url_for,make_response
from flask_session import Session
from datetime import datetime
app = Flask(__name__)
app.config["SESSION_PERMANENT"] = True
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.route('/')
def login():
    return render_template('signin.html')

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        password = request.form.get('password')
        email = request.form.get('email')

        if not email or not password:
            return render_template('signin.html', message="Email or password not provided")

        data = {
            "email": email,
            "password": password
        }
        print(email,password)
        try:
            response = requests.post(url="http://192.168.128.87:8000/staff/login", json=data)
            response_data = response.json()
            if response.status_code == 200:
                print("cookies set",response_data)
                session['uid'] = response_data
                resp = redirect(url_for('get_data'))
                resp.set_cookie('uid', str(response_data))
                return resp
            else:
                raise Exception('Invalid response')
        except Exception as e:
            message = "Server Down"
            return render_template('signin.html', message=message)
    else:
        return render_template('signin.html')

@app.route('/get_data', methods=['GET', 'POST'])
def get_data():
    try:
        uid = request.cookies.get('uid')
        print(uid)
        fastapi_url ="http://192.168.128.87:8000/staff/data"
        customer_url ="http://192.168.128.87:8000/cust/data"
        try:
            response = requests.post(url=fastapi_url, json={'uid': uid})
            customer = requests.post(url=customer_url, json={'uid': uid})
            response=response.json()
            customer=customer.json()
            print(response)
            print(customer)
            customernumber=[]
            customername=[]
            customerplace=[]
            customerenquire=[]
            customernotes=[]
            customerstate=[]
            for sublist in customer:
                for item in sublist:
                    if isinstance(item, dict):
                        customernumber.append(item["phone"])
                        print(item["phone"])
                        customername.append(item["name"])
                        customerplace.append(item["address"]["city"])
                        customerenquire.append(item["enquiry"]["enquired_for"])
                        customernotes.append(item["notes"])
                    elif isinstance(item, str): 
                        customerstate.append(item)
            name=response["name"]
            role=response["role"]  
            dataall=zip(customernumber,customername,customerplace,customerenquire,customernotes,customerstate)
            if role =="superadmin":
                return render_template('admindashboard.html',name=name,role=role)
            elif role =="admin":
                return render_template('admindashboard.html',name=name,role=role)
            else:
                return render_template('admindashboard.html',name=name,role=role,dataall=dataall)
        except:
            message="Server Down"
            return render_template('admindashboard.html',message=message)
    except:
        return redirect(url_for("login"))

def convert_to_timestamp(date, time):
    dt_string = date + " " + time
    dt_object = datetime.strptime(dt_string, '%Y-%m-%d %H:%M:%S')
    
    timestamp = dt_object.timestamp()
    return timestamp

@app.route('/schedule', methods=['GET', 'POST'])
def schedules():
    if request.method == 'POST':
        clientid=request.form['clientid']
        type = request.form['type']
        pod_id = request.form['pod_id']
        notes = request.form['notes']
        date = request.form['date']
        time = request.form['time']+":00"
        timestamp = convert_to_timestamp(date, time)
        schedule = {
            "type": type,
            "pod_id": pod_id,
            "notes": notes,
            "date_and_time":timestamp
        }
        fastapi_url = f"http://192.168.128.87:8000/client/{clientid}/create_schedule"
        try:
            response = requests.post(url=fastapi_url, json=schedule)
            return render_template('schedule.html',message=response.json())
        except:
            message="Server Down"
            return render_template('schedule.html',message=message)
    else:
        return render_template('schedule.html')
      
@app.route('/logout')
def logout():
    session.pop('uid', None)
    resp = redirect(url_for('signin'))
    resp.delete_cookie('uid')
    return redirect(url_for("signin"))

@app.route('/admindashboard', methods=['GET', 'POST'])
def admin():
    return render_template("admindashboard.html")

@app.route('/create_staff', methods=['GET', 'POST'])
def staffcreate():
    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        email = request.form['email']
        department = request.form['department']
        pod_id = request.form['pod_id']
        dob = request.form['dob']
        blood_group = request.form['blood_group']
        profile_pic_url = request.form['profile_pic_url']
        address = request.form['address']
        family_father_name = request.form['family_father_name']
        family_mother_name = request.form['family_mother_name']
        family_spouse_name = request.form['family_spouse_name']
        family_sibling_name = request.form['family_sibling_name']
        family_child_name= request.form['family_child_name']
        designation = request.form['designation']
        emp_id= request.form['emp_id']
        bank_data_acc_no = request.form['bank_data_acc_no']
        bank_data_acc_holder_name = request.form['bank_data_acc_holder_name']
        bank_data_branch = request.form['bank_data_branch']
        bank_data_ifsc_code = request.form['bank_data_ifsc_code']
        bank_data_acc_type = request.form['bank_data_acc_type']
        mode_of_transport = request.form['mode_of_transport']
        laptop = request.form['laptop']
        government_id_aadhar_no = request.form['government_id_aadhar_no']
        government_id_pan_no = request.form['government_id_pan_no']
        role = request.form['role']
        password=request.form['Password']
        staff = {
            "name": name,
            "phone": phone,
            "email": email,
            "department": department,
            "pod_id": pod_id,
            "dob": dob,
            "blood_group": blood_group,
            "profile_pic_url": profile_pic_url,
            "address": address,
            "family": {
                "father_name": family_father_name,
                "mother_name": family_mother_name,
                "spouse_name": family_spouse_name,
                "sibling_name": family_sibling_name,
                "child_name": family_child_name
            },
            "designation": designation,
            "emp_id": emp_id,
            "bank_data": {
                "acc_no": bank_data_acc_no,
                "acc_holder_name": bank_data_acc_holder_name,
                "branch": bank_data_branch,
                "ifsc_code": bank_data_ifsc_code,
                "acc_type": bank_data_acc_type
            },
            "mode_of_transport": mode_of_transport,
            "laptop": laptop,
            "government_id": {
                "aadhar_no": government_id_aadhar_no,
                "pan_no": government_id_pan_no
            },
            "role": role,
            "password":password
        }
        fastapi_url = "http://192.168.128.87:8000/create_staff"
        try:
            response = requests.post(url=fastapi_url, json=staff)
            return render_template('createstaff.html',message=response)
        except:
            message="Server Down"
            return render_template('createstaff.html',message=message)
    else:
        return render_template('createstaff.html')

@app.route('/addnotes', methods=['GET', 'POST'])
def addnotes():
    if request.method == 'POST':
        uid = request.cookies.get('uid')
        pr_user_id = request.form['pr_user_id']
        notes = request.form['notes']
        notes = {
            "pr_user_id": uid,
            "notes": notes
        }
        
        # URL of the FastAPI endpoint
        fastapi_url = f"http://192.168.128.87:8000/client/{pr_user_id}/add_notes"

        # Make an HTTP POST request to the FastAPI endpoint
        try:
            response = requests.post(url=fastapi_url, json=notes)
            return render_template('addnotes.html',message=response.json())
        except:
            message="Server Down"
            return render_template('addnotes.html',message=message)
    else:
        return render_template('addnotes.html')

@app.route('/client_search', methods=['GET', 'POST'])
def client_search():
    if request.method == 'POST':
        clientid = request.form['clientnumber']
        fastapi_url = f"http://192.168.128.87:8000/client/{clientid}"
        try:
            response = requests.get(url=fastapi_url)
            return render_template('staffdashboard.html',message=response.json())
        except:
            message="Server Down"
            return render_template('staffdashboard.html',message=message)
    else:
        return render_template('staffdashboard.html')

@app.route('/payment_details', methods=['GET', 'POST'])
def client_payment():
    if request.method == 'POST':
        uid = request.cookies.get('uid')
        customerid = request.form['customerid']
        payment_id = request.form['payment_id']
        amount = request.form['amount']
        paid_for = request.form['paid_for']
        pending_payment = request.form['pending_payment']
        timestamp = datetime.now().timestamp()
        payment={
        "payment_id": payment_id,
        "payment_time": timestamp,
        "amount": amount,
        "paid_for": paid_for,
        "pending_payment": pending_payment,
        "uid": uid
        }
        fastapi_url = f"http://192.168.128.87:8000/client/{customerid}/payments"
        try:
            response = requests.post(url=fastapi_url, json=payment)
            return render_template('payment.html',message=response.json())
        except:
            message="Server Down"
            return render_template('payment.html',message=message)
    else:
        return render_template('payment.html')

@app.route('/statuschange', methods=['GET', 'POST'])
def statuschange():
    if request.method == 'POST':
        pr_uid = request.cookies.get('uid')
        clientid = request.form['clientid']
        state = request.form['state']
        reason = request.form['reason']
        status={
        "pr_uid":pr_uid ,
        "state":state,
        "reason": reason
        }

        fastapi_url = f"http://192.168.128.87:8000/client/{clientid}/sts/{state}"
        try:
            response = requests.post(url=fastapi_url, json=status)
            return render_template('statuschange.html',message=response.json())
        except:
            message="Server Down"
            return render_template('statuschange.html',message=message)
    else:
        return render_template('statuschange.html')
    
@app.route('/createclient', methods=['GET', 'POST'])
def clientcreate():
    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        address_door_no = request.form['address_door_no']
        address_street = request.form['address_street']
        address_city = request.form['address_city']
        address_state = request.form['address_state']
        address_pincode = request.form['address_pincode']
        address_landmark = request.form['address_landmark']
        rating = request.form['rating']
        pod_id = request.form['pod_id']
        enquiry_lead_source = request.form['enquiry_lead_source']
        uid = request.cookies.get('uid')
        enquiry_enquired_for = request.form['enquiry_enquired_for']
        notes = request.form['notes']

        client = {
            "name": name,
            "phone": phone,
            "address": {
                "door_no": address_door_no,
                "street": address_street,
                "city": address_city,
                "state": address_state,
                "pincode": address_pincode,
                "landmark": address_landmark
            },
            "rating": rating,
            "pod_id": pod_id,
            "enquiry": {
                "lead_source": enquiry_lead_source,
                "created_by": uid,
                "enquired_for": enquiry_enquired_for
            },
            "notes": notes
        }
        
        # URL of the FastAPI endpoint
        fastapi_url = "http://192.168.128.87:8000/create_client"

        # Make an HTTP POST request to the FastAPI endpoint
        try:
            response = requests.post(url=fastapi_url, json=client)
            return render_template('clientcreate.html',message=response.json())
        except:
            message="Server Down"
            return render_template('clientcreate.html',message=message)
    else:
        return render_template('clientcreate.html')

if __name__ == '__main__':
    app.run(debug=True, port=8000)
