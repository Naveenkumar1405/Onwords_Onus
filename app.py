import requests
from flask import Flask, render_template, redirect, request, session, url_for, make_response, flash
import functions
from flask_session import Session
import logging
from datetime import datetime


def convert_timestamp(timestamp):
    return datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')


app = Flask(__name__)
app.config["SESSION_PERMANENT"] = True
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

fast_api_server_ip = "192.168.1.16:8000"
logging.basicConfig(level=logging.INFO)


@app.route('/signin', methods=['GET', 'POST'])
def signin():
    print("Inside singin!")
    if request.method == 'POST':
        password = request.form.get('password')
        email = request.form.get('email')

        if not email or not password:
            return render_template('signin.html', message="Email or password not provided")

        data = {
            "email": email,
            "password": password
        }
        print(email, password)
        try:
            response = requests.post(url=f"http://{fast_api_server_ip}/staff/login", json=data)
            response_data = response.json()
            if response.status_code == 200:
                print("login successful..!!!")
                print("cookies set", response_data)
                session['uid'] = response_data
                resp = redirect('/')
                resp.set_cookie('uid', str(response_data))
                return resp
            else:
                raise Exception('Invalid response')
        except Exception as e:
            message = e
            print(e)
            return render_template('signin.html', message=message)
    else:
        return render_template('signin.html')


# from datetime import datetime

@app.route('/my_schedule')
def my_schedule():
    uid = request.cookies.get('uid')
    username = request.cookies.get('user_name')
    userrole = request.cookies.get('user_role')
    userpod = request.cookies.get('user_pod')

    schedule_data = requests.get(f"http://{fast_api_server_ip}/schedule/{uid}").json()

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
            # Format to days, hours, minutes
            hours, remainder = divmod(remaining_time.seconds, 3600)
            minutes, _ = divmod(remainder, 60)
            schedules['remaining_time'] = f"{hours}:{str(minutes).zfill(2)}" if days == 0 else f"{days} days, {hours}:{str(minutes).zfill(2)}"
        else:
            schedules['remaining_time'] = "Already occurred."

        # Check if the event is today
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




@app.route('/pod', methods=['GET', 'POST'])
def pod():
    username = request.cookies.get('user_name')
    userrole = request.cookies.get('user_role')
    userpod = request.cookies.get('user_pod')
    print(request.method)
    if request.method == 'POST':
        pod_name = request.form['pod_name']
        members = request.form.getlist('members')
        print(members)

        print(f'Pod Name: {pod_name}')
        print(f'Members: {members}')
        data = {
            "name": pod_name,
            "members": members
        }
        print(data)
        requests.post(f"http://{fast_api_server_ip}/pod/create", json=data)

        flash(f'{pod_name} pod created successfully!')
        staff_list = functions.get_all_staff_name()
        staff_data = functions.get_all_staff_data()
        staff_name = staff_data[0]
        staff_uid = staff_data[1]
        staff_zip = zip(staff_name, staff_uid)
        print(f"staff = {staff_zip}")
        return render_template('pod.html', staff_zip=staff_zip, username=username, role=userrole, pod=userpod)
    else:
        print("inside post get else")
        staff_list = functions.get_all_staff_name()
        staff_data = functions.get_all_staff_data()
        staff_name = staff_data[0]
        staff_uid = staff_data[1]
        staff_zip = zip(staff_name, staff_uid)
        print(f"staff = {staff_zip}")
        return render_template('pod.html', staff_zip=staff_zip, username=username, role=userrole, pod=userpod)


@app.route('/', methods=['GET', 'POST'])
def home():
    try:
        uid = request.cookies.get('uid')
        if uid:
            print(request.method)
            user_name = requests.post(f"http://{fast_api_server_ip}/staff/data", json={'uid': uid}).json()
            pod = requests.get(f"http://{fast_api_server_ip}/staff/pod/{uid}").json()
            new_client_data = requests.get(f"http://{fast_api_server_ip}/client/pod/{pod}").json()
            client_state = requests.get(f"http://{fast_api_server_ip}/client/state/").json()

            if request.method == "POST":
                print("===========")
                state = request.form.get("state")
                new_client_data = requests.post(f"http://{fast_api_server_ip}/client/getstate/{state}/{pod}").json()
                print(new_client_data)
                resp = make_response(
                    render_template('homepage.html', username=user_name['name'], role=user_name['role'], pod=pod,
                                    new_client_data=new_client_data, client_state=client_state, client=new_client_data))
            else:
                resp = make_response(
                    render_template('homepage.html', username=user_name['name'], role=user_name['role'], pod=pod,
                                    new_client_data=new_client_data, client_state=client_state, client=new_client_data))
            # Set cookies
            resp.set_cookie('user_name', str(user_name['name']), max_age=60 * 60 * 24 * 365 * 2)
            resp.set_cookie('user_role', str(user_name['role']), max_age=60 * 60 * 24 * 365 * 2)
            resp.set_cookie('user_pod', str(pod), max_age=60 * 60 * 24 * 365 * 2)
            return resp
        else:
            print(f"Uid not found. giving login page")
            return redirect('/signin')
    except Exception as e:
        print("error", e)


@app.route('/client/profile', methods=['GET', 'POST'])
def client_profile():
    username = request.cookies.get('user_name')
    userrole = request.cookies.get('user_role')
    userpod = request.cookies.get('user_pod')

    if request.method == 'GET':
        return render_template("client_profile.html", username=username, role=userrole, pod=userpod)
    else:
        client_number = request.form.get('client_number')
        logging.info(f'Received form with client number: {client_number}')

        try:
            client_data = requests.get(f"http://{fast_api_server_ip}/client/{client_number}").json()
        except requests.exceptions.RequestException as e:
            logging.error(f"Failed to get client data: {e}")
            return render_template("client_profile.html", username=username, role=userrole, pod=userpod,
                                   client_number=client_number, error="Failed to get client data")

        notes_list = []
        for keys in client_data:
            if keys == "notes":
                for note in client_data[keys]:
                    notes_list.append(client_data[keys][note])
        print(notes_list)

        print(f"client_data = {client_data}")

        if client_data:
            return render_template("client_profile.html", username=username, role=userrole, pod=userpod,
                                   client_number=client_number, client=client_data, convert_timestamp=convert_timestamp,
                                   notes=notes_list)
        else:
            return render_template("client_profile.html", username=username, role=userrole, pod=userpod,
                                   client_number=client_number, error=f"Client {client_number} not found",
                                   convert_timestamp=convert_timestamp, notes=notes_list)


@app.route('/client/profile/<client_number>/<sts>', methods=['GET', 'POST'])
def change_client_status(client_number, sts):
    print(client_number, sts)
    data = {
        "pr_uid": request.cookies.get('uid'),
        "state": "sts",
        "reason": "Unknown"
    }
    code = requests.post(f"http://{fast_api_server_ip}/client/{client_number}/sts/{sts}", json=data)
    print(code)

    client_data = functions.get_client_data_using_phonenumber(client_number)
    print(client_data)
    notes_list = []
    for keys in client_data:
        if keys == "notes":
            for note in client_data[keys]:
                notes_list.append(client_data[keys][note])
    print(notes_list)

    return render_template("client_profile.html", client=client_data, message="Status changed!", notes=notes_list)


@app.route('/client/notes', methods=['POST'])
def add_note():
    note = request.form.get('notes')
    client_number = request.form.get('client_number')
    role = request.form.get('role')
    username = request.form.get("username")
    pod = request.form.get('pod')

    data = {
        "pr_user_id": request.cookies.get('uid'),
        "notes": note
    }
    x = requests.post(f"http://{fast_api_server_ip}/client/{client_number}/add_notes", json=data)
    print(x)
    print(x.json())
    client_data = functions.get_client_data_using_phonenumber(client_number)
    print(client_data)
    print(note)
    notes_list = []
    for keys in client_data:
        if keys == "notes":
            for note in client_data[keys]:
                notes_list.append(client_data[keys][note])
    print(notes_list)
    return render_template("client_profile.html", client=client_data, notes=notes_list, role=role, username=username,
                           pod=pod)


@app.route('/client/schedule', methods=['POST'])
def add_schedule():
    schedule_type = request.form.get('schedule_type')
    pod = request.form.get('pod')
    client_number = request.form.get('client_number')
    schedule_time = request.form.get('schedule_time')
    role = request.form.get('role')
    username = request.form.get("username")
    print("pod = ", pod)
    data = {
        "pr_user_id": request.cookies.get('uid'),
        "type": schedule_type,
        "pod_id": pod,
        "date_and_time": schedule_time
    }
    x = requests.post(f"http://{fast_api_server_ip}/client/{client_number}/create_schedule", json=data)
    print(x)
    print(x.json())
    client_data = functions.get_client_data_using_phonenumber(client_number)
    print(client_data)
    # print(note)
    notes_list = []
    for keys in client_data:
        if keys == "notes":
            for note in client_data[keys]:
                notes_list.append(client_data[keys][note])
    print(notes_list)
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
            # "pod_id": pod_id,
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
        print(staff)
        fastapi_url = f"http://{fast_api_server_ip}/create_staff"
        try:
            response = requests.post(url=fastapi_url, json=staff)
            print(response)
            return render_template('createstaff.html', message=response, username=username, role=userrole, pod=userpod)
        except:
            message = "Server Down"
            return render_template('createstaff.html', message=message, username=username, role=userrole, pod=userpod)
    else:
        return render_template('createstaff.html', username=username, role=userrole, pod=userpod)


# @app.route('/client_search', methods=['GET', 'POST'])
# def client_search():
#     if request.method == 'POST':
#         client_number = request.form['clientnumber']
#         fastapi_url = f"http://{fast_api_server_ip}:8000/client/{client_number}"
#         try:
#             response = requests.get(url=fastapi_url)
#             return render_template('staffdashboard.html', message=response.json())
#         except:
#             message = "Server Down"
#             return render_template('staffdashboard.html', message=message)
#     else:
#         return render_template('staffdashboard.html')


# @app.route('/statuschange', methods=['GET', 'POST'])
# def statuschange():
#     if request.method == 'POST':
#         pr_uid = request.cookies.get('uid')
#         clientid = request.form['clientid']
#         state = request.form['state']
#         reason = request.form['reason']
#         status = {
#             "pr_uid": pr_uid,
#             "state": state,
#             "reason": reason
#         }
#
#         fastapi_url = f"http://{fast_api_server_ip}:8000/client/{clientid}/sts/{state}"
#         try:
#             response = requests.post(url=fastapi_url, json=status)
#             return render_template('statuschange.html', message=response.json())
#         except Exception as e:
#             print(e)
#             message = e
#             return render_template('statuschange.html', message=message)
#     else:
#         return render_template('statuschange.html')

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
                "created_by": uid,
                "enquired_for": enquiry_enquired_for
            },

        }
        # URL of the FastAPI endpoint
        fastapi_url = f"http://{fast_api_server_ip}/create_client"
        # Make an HTTP POST request to the FastAPI endpoint
        try:
            response = requests.post(url=fastapi_url, json=client)
            print(response)
            pod_name_list = functions.get_all_pod_names()

            return render_template('clientcreate.html', message=response.json(), pod_names=pod_name_list,
                                   username=username, role=userrole, pod=userpod)
        except:
            message = "Server Down"
            return render_template('clientcreate.html', message=message, username=username, role=userrole, pod=userpod)
    else:
        pod_name_list = functions.get_all_pod_names()

        print(pod_name_list)
        return render_template('clientcreate.html', pod_names=pod_name_list, username=username, role=userrole,
                               pod=userpod)


if __name__ == '__main__':
    app.run(debug=True, host='192.168.1.16', port=8182)
