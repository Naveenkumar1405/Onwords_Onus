import requests,app
from datetime import datetime
fast_api_server_ip = app.fast_api_server_ip

def get_client_data_tagged_to_staff_by_uid(uid):
    pass

def get_all_staff_data():
    return requests.get(f"http://{fast_api_server_ip}/staff/alldata/").json()

def get_all_staff_name():
    return requests.get(f"http://{fast_api_server_ip}/staff/data/name").json()

def get_all_pod_names():
    return requests.get(f"http://{fast_api_server_ip}/pod/names").json()

def get_client_data_using_phonenumber(client_number):
    try:
        client_data = requests.get(f"http://{fast_api_server_ip}/client/{client_number}").json()
    except requests.exceptions.RequestException as e:
        return e
    return client_data


staff_data = requests.get(f"http://{fast_api_server_ip}/staff/data/all").json()

def convert_pr_uid_to_name(uid):
    for staff in staff_data:
        if uid == staff:
            staff_name = staff_data[staff]['name']
            return staff_name
    return None

def convert_to_timestamp(date, time):
    dt_string = date + " " + time
    dt_object = datetime.strptime(dt_string, '%Y-%m-%d %I:%M %p')
    timestamp = dt_object.timestamp()
    return timestamp

def convert_datetime(date_and_time):
    dt_obj = datetime.strptime(date_and_time, '%Y-%m-%dT%H:%M')
    date_str = dt_obj.strftime('%d-%m-%Y')
    time_str = dt_obj.strftime('%I:%M%p')
    return date_str, time_str

def get_client_notes(client_number):
    client_data = get_client_data_using_phonenumber(client_number)
    notes_list = []

    if client_data:
        for keys in client_data:
            if keys == "notes":
                for note in client_data[keys]:
                    notes_list.append(client_data[keys][note])
    print("List of Notes :",notes_list)
    return notes_list