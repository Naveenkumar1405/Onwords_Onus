import requests,io,csv,functions,logging,json
from flask import Flask, jsonify, render_template, redirect, request, session, url_for, make_response, flash
from flask_session import Session
from datetime import datetime

def convert_timestamp(timestamp):
    return datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = True
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

fast_api_server_ip = "192.168.1.63:8000"
logging.basicConfig(level=logging.INFO)

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
        try:
            response = requests.post(url=f"http://{fast_api_server_ip}/staff/login", json=data)
            response_data = response.json()
            if response.status_code == 200:
                session['uid'] = response_data
                resp = redirect('/')
                resp.set_cookie('uid', str(response_data))
                return resp
            else:
                raise Exception('Invalid response')
        except Exception as e:
            message = e
            return render_template('signin.html', message=message)
    else:
        return render_template('signin.html')
    
@app.route('/create_staff', methods=['GET', 'POST'])
def staffcreate():
    username = request.cookies.get('user_name')
    userrole = request.cookies.get('user_role')
    userpod = request.cookies.get('user_pod')
    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        email = request.form['email']
        department = request.form['department']
        dob = request.form['dob']
        blood_group = request.form['blood_group']
        profile_pic_url = request.form['profile_pic_url']
        address = request.form['address']
        family_father_name = request.form['family_father_name']
        family_mother_name = request.form['family_mother_name']
        family_spouse_name = request.form['family_spouse_name']
        family_sibling_name = request.form['family_sibling_name']
        family_child_name = request.form['family_child_name']
        designation = request.form['designation']
        emp_id = request.form['emp_id']
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
        password = request.form['Password']
        staff = {
            "name": name,
            "phone": phone,
            "email": email,
            "department": department,
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
            "password": password
        }
        fastapi_url = f"http://{fast_api_server_ip}/create_staff"
        try:
            response = requests.post(url=fastapi_url, json=staff)
            return render_template('createstaff.html', message=response, username=username, role=userrole, pod=userpod)
        except:
            message = "Server Down"
            return render_template('createstaff.html', message=message, username=username, role=userrole, pod=userpod)
    else:
        return render_template('createstaff.html', username=username, role=userrole, pod=userpod)    

@app.route('/my_schedule')
def my_schedule():
    uid = request.cookies.get('uid')
    username = request.cookies.get('user_name')
    userrole = request.cookies.get('user_role')
    userpod = request.cookies.get('user_pod')
    
    response = requests.get(f"http://{fast_api_server_ip}/schedule/{uid}")
    if response.status_code != 200:
        schedule_data = []
    else:
        schedule_data = response.json()
    
    if not schedule_data:
        return render_template("my_schedule.html", message="No schedules available", username=username, role=userrole, pod=userpod)

    now = datetime.now()
    
    for schedules in schedule_data:
        date_and_time = schedules['date_and_time']
        date_str, time_str = functions.convert_datetime(date_and_time)
        schedules['date'] = date_str
        schedules['time'] = time_str
        del schedules['date_and_time']

        event_date_time_str = date_str + " " + time_str
        event_date_time = datetime.strptime(event_date_time_str, "%d-%m-%Y %I:%M%p")

        remaining_time = event_date_time - now
        days = remaining_time.days
        if remaining_time.total_seconds() > 0:
            hours, remainder = divmod(remaining_time.seconds, 3600)
            minutes, _ = divmod(remainder, 60)
            schedules['remaining_time'] = f"{hours}:{str(minutes).zfill(2)}" if days == 0 else f"{days} days, {hours}:{str(minutes).zfill(2)}"
        else:
            schedules['remaining_time'] = "Breached"
            
        schedules['is_today'] = True if days == 0 and remaining_time.total_seconds() > 0 else False

        pr_user_id = schedules['pr_user_id']
        pr_name = functions.convert_pr_uid_to_name(pr_user_id)
        time_stamp = schedules['schedule_created_timestamp']
        dt_obj = datetime.fromtimestamp(time_stamp)
        date_str = dt_obj.strftime('%d-%m-%Y')
        time_str = dt_obj.strftime('%I:%M%p').lower()
        schedules['created_time'] = date_str + " " + time_str
        del schedules['schedule_created_timestamp']
        schedules['name'] = pr_name
        del schedules['pr_user_id']

    return render_template("my_schedule.html", schedule_data=schedule_data, username=username, role=userrole,
                           pod=userpod, now_date=datetime.now().strftime('%d-%m-%Y'))

@app.route("/schedule_action", methods=["POST"])
def schedule_action():
    data = request.json
    action = data.get("action")
    schedule_id = data.get("schedule_id")
    if action == "mark_done":
        
        response = requests.put(f"http://{fast_api_server_ip}/mark_schedule_done/{schedule_id}")
        response_data = {"status": "Done"}
        response_data=jsonify(response_data)
        if response.status_code == 200:
            flash("Schedule marked as done", "success")
        else:
            flash("Failed to mark schedule as done", "error")
    elif action == "delete":
        
        response = requests.delete(f"http://{fast_api_server_ip}/delete_schedule/{schedule_id}")
        
        if response.status_code == 200:
            flash("Schedule deleted successfully", "success")
        else:
            flash("Failed to delete schedule", "error")
    
    return redirect(url_for("my_schedule"))

@app.route('/pod', methods=['GET', 'POST'])
def pod():
    username = request.cookies.get('user_name')
    userrole = request.cookies.get('user_role')
    userpod = request.cookies.get('user_pod')
    if request.method == 'POST':
        pod_name = request.form['pod_name']
        members = request.form.getlist('members')

        data = {
            "name": pod_name,
            "members": members
        }
        requests.post(f"http://{fast_api_server_ip}/pod/create", json=data)

        flash(f'{pod_name} pod created successfully!')
        staff_list = functions.get_all_staff_name()
        staff_data = functions.get_all_staff_data()
        staff_name = staff_data[0]
        staff_uid = staff_data[1]
        staff_zip = zip(staff_name, staff_uid)
        return render_template('pod.html', staff_zip=staff_zip, username=username, role=userrole, pod=userpod,staff_list=staff_list )
    else:
        staff_list = functions.get_all_staff_name()
        staff_data = functions.get_all_staff_data()
        staff_name = staff_data[0]
        staff_uid = staff_data[1]
        staff_zip = zip(staff_name, staff_uid)
        return render_template('pod.html', staff_zip=staff_zip, username=username, role=userrole, pod=userpod,staff_list=staff_list)

@app.route('/', methods=['GET', 'POST'])
def home():
    try:
        uid = request.cookies.get('uid')
        if not uid:
            return redirect('/signin')

        user_name = requests.post(f"http://{fast_api_server_ip}/staff/data", json={'uid': uid}).json()
        pod = requests.get(f"http://{fast_api_server_ip}/staff/pod/{uid}").json()

        new_client_data = ""
        try:
            new_client_data = requests.get(f"http://{fast_api_server_ip}/client/pod/{pod}").json()
        except:
            pass

        client_state = requests.get(f"http://{fast_api_server_ip}/client/state/").json()
        if request.method == "POST":
            state = request.form.get("state")
            new_client_data = requests.post(f"http://{fast_api_server_ip}/client/getstate/{state}/{pod}").json()

        resp = make_response(
            render_template('homepage.html', 
                            username=user_name['name'], 
                            role=user_name['role'], 
                            pod=pod,
                            new_client_data=new_client_data, 
                            client_state=client_state, 
                            client=new_client_data))

        for key, value in {"user_name": user_name['name'], "user_role": user_name['role'], "user_pod": pod}.items():
            resp.set_cookie(key, str(value), max_age=60 * 60 * 24 * 365 * 2)

        return resp

    except Exception as e:
        return "An error occurred!", 500,e


@app.route('/client/profile', methods=['GET', 'POST'])
def client_profile():
    username = request.cookies.get('user_name')
    userrole = request.cookies.get('user_role')
    userpod = request.cookies.get('user_pod')

    client_number = None
    error = None
    client_data = None
    notes_list = []

    if request.method == 'POST':
        client_number = request.form.get('client_number')
        client_data = functions.get_client_data_using_phonenumber(client_number)

        notes_list = []

        if client_data:
            try:
                notes_list = process_notes(client_data)
            except (ValueError, KeyError) as e:
                logging.error(f"Error processing client data: {e}")
                error = "Failed to process client data"
        else:
            error = "Failed to get client data"

    return render_template("client_profile.html", username=username, role=userrole, pod=userpod,
                           client_number=client_number, client_data=client_data, notes_list=notes_list,
                           error=error, convert_timestamp=convert_timestamp)

def process_notes(client_data):
    notes_list = []
    for keys in client_data:
        if keys == "notes":
            for note in client_data[keys]:
                notes_list.append(client_data[keys][note])

    for note in notes_list:
        pr_uid = note.get('pr_user_id')
        if pr_uid:
            pr_name = functions.convert_pr_uid_to_name(pr_uid)
            note["pr_name"] = pr_name

        time_stamp = note.get('timestamp')
        if time_stamp:
            dt_obj = datetime.fromtimestamp(time_stamp)
            date_str = dt_obj.strftime('%d-%m-%Y')
            time_str = dt_obj.strftime('%I:%M%p').lower()

            note['date'] = date_str
            note['time'] = time_str

            del note['pr_user_id']
            del note['timestamp']
    
    return notes_list

@app.route('/upload_csv', methods=['POST'])
def upload_csv():
    username = request.cookies.get('user_name')
    userrole = request.cookies.get('user_role')
    userpod = request.cookies.get('user_pod')
    if 'csvfile' not in request.files:
        return 'No file part'

    file = request.files['csvfile']
    if file.filename == '':
        return 'No selected file'

    if file and file.filename.endswith('.csv'):
        content = io.StringIO(file.read().decode('UTF-8'))
        reader = csv.reader(content, delimiter='\t')
        header = next(reader)

        if 'ad_name' not in header:
            return "The column 'ad_name' was not found in the uploaded CSV file. Please check the file and try again."

        uploaded_clients = []

        indices = {
            "ad_name": header.index('ad_name'),
            "platform": header.index('platform'),
            "full_name": header.index('full_name'),
            "phone_number": header.index('phone_number'),
            "email": header.index('email'),
            "city": header.index('city')
        }

        for row in reader:
            phno = row[indices['phone_number']]
            if len(phno) > 10:
                phno = phno[-10:]

            data = {
                "ad_name": row[indices['ad_name']],
                "platform": row[indices['platform']],
                "full_name": row[indices['full_name']],
                "phone_number": phno,
                "email": row[indices['email']],
                "city": row[indices['city']],
            }

            uploaded_clients.append(data)
            
        response = requests.post(f"http://{fast_api_server_ip}/save_uploaded_clients/", json=uploaded_clients)
        if response.status_code == 200:
            return 'Data successfully saved'
        else:
            return f"Error while saving data: {response.text}"

    return render_template('createstaff.html', username=username, role=userrole, pod=userpod)


@app.route('/status_change', methods=['POST','GET'])
def change_client_status():
    data = json.loads(request.data)
    client_number = data['client_number']
    status = data['status']
    data = {
        "pr_uid": request.cookies.get('uid'),
        "status": status
    }
    response = requests.post(f"http://{fast_api_server_ip}/status_change/{client_number}", json=data)
    client_data = functions.get_client_data_using_phonenumber(client_number)
    response_data = response.json()
    
    notes_list = process_notes(client_data)

    return render_template("client_profile.html", client_data=client_data, notes_list=notes_list, message="Status changed!", status=status, response=response_data)

@app.route('/client/notes', methods=['POST'])
def add_note():
    note = request.form.get('notes')
    client_number = request.form.get('client_number')
    
    data = {
        "pr_user_id": request.cookies.get('uid'),
        "notes": note
    }
    
    response = requests.post(f"http://{fast_api_server_ip}/client/{client_number}/add_notes", json=data)
    new_note_data = response.json()
    target_url = f"/client/profile"
    
    return redirect(target_url)

@app.route('/client/schedule', methods=['POST','GET'])
def add_schedule():
    schedule_type = request.form.get('schedule_type')
    pod = request.form.get('pod')
    client_number = request.form.get('client_number')
    schedule_time = request.form.get('schedule_time')
    role = request.form.get('role')
    username = request.form.get("username")
    data = {
        "pr_user_id": request.cookies.get('uid'),
        "type": schedule_type,
        "pod_id": pod,
        "date_and_time": schedule_time
    }
    x = requests.post(f"http://{fast_api_server_ip}/client/{client_number}/create_schedule", json=data)
    
    client_data = functions.get_client_data_using_phonenumber(client_number)

    notes_list = []
    for keys in client_data:
        if keys == "notes":
            for note in client_data[keys]:
                notes_list.append(client_data[keys][note])
    return render_template("client_profile.html", client=client_data, notes=notes_list, pod=pod, role=role,
                           username=username)

@app.route('/logout')
def logout():
    session.pop('uid', None)
    session.pop('user_name', None)
    session.pop('user_role', None)
    session.pop('user_pod', None)
    resp = redirect(url_for('signin'))
    resp.delete_cookie('uid')
    resp.delete_cookie('user_name')
    resp.delete_cookie('user_role')
    resp.delete_cookie('user_pod')
    return redirect(url_for("signin"))

@app.route('/create_client', methods=['GET', 'POST'])
def clientcreate():
    username = request.cookies.get('user_name')
    userrole = request.cookies.get('user_role')
    userpod = request.cookies.get('user_pod')
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
        username = request.cookies.get('user_name')
        enquiry_enquired_for = request.form['enquiry_enquired_for']
        pod_name_list = functions.get_all_pod_names()
        client_number_list = requests.get(f"http://{fast_api_server_ip}/all_numbers").json()
        if phone in client_number_list:
            return "Number already exist"

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
                "created_by": username,
                "enquired_for": enquiry_enquired_for
            },

        }
        
        fastapi_url = f"http://{fast_api_server_ip}/create_client"
        
        try:
            response = requests.post(url=fastapi_url, json=client)
            pod_name_list = functions.get_all_pod_names()

            return render_template('clientcreate.html', message=response.json(), pod_names=pod_name_list,
                                   username=username, role=userrole, pod=userpod)
        except:
            message = "Server Down"
            return render_template('clientcreate.html', message=message, username=username, role=userrole, pod=userpod)
    else:
        pod_name_list = functions.get_all_pod_names()

        return render_template('clientcreate.html', pod_names=pod_name_list, username=username, role=userrole,
                               pod=userpod)

if __name__ == '__main__':
    app.run(debug=True, host='192.168.1.63', port=8118)