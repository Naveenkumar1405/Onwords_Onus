from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import requests
app = Flask(__name__)

@app.route('/')
def login():
    return render_template('signin.html')

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        password = request.form['password']
        email = request.form['email']
        try:
            uid=requests.post(url="http//:192.168.1.91:8000/login/email/password")
            if uid is not None:
                if uid == "admin":
                    return render_template('admindashboard.html')
                else:
                    return render_template('staffdashboard.html')
            else:
                message="Enter Valid Details"
                return render_template('signin.html',message=message)
        except:
            message="Server Down"
            return render_template('signin.html',message=message)

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
            "role": role
        }

        fastapi_url = "http://192.168.1.91:8000/create_staff"
        try:
            response = requests.post(url=fastapi_url, json=staff)
            return render_template('admindashboard.html',message=response.json())
        except:
            print("+++++++++++++++++++++++++")
            message="Server Down"
            return render_template('admindashboard.html',message=message)
    else:
        return render_template('admindashboard.html') 


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
        enquiry_created_by = request.form['enquiry_created_by']
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
                "created_by": enquiry_created_by,
                "enquired_for": enquiry_enquired_for
            },
            "notes": notes
        }
        
        # URL of the FastAPI endpoint
        fastapi_url = "http://192.168.1.91:8000/create_client"

        # Make an HTTP POST request to the FastAPI endpoint
        try:
            response = requests.post(url=fastapi_url, json=client)
            return render_template('staffdashboard.html',message=response.json())
        except:
            print("+++++++++++++++++++++++++")
            message="Server Down"
            return render_template('staffdashboard.html',message=message)
    else:
        return render_template('staffdashboard.html')   

if __name__ == '__main__':
    app.run(debug=True, port=8000)
