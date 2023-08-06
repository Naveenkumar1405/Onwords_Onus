import requests
from app import fast_api_server_ip
from datetime import datetime


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
        print(e)
        return e

    return client_data


def convert_to_timestamp(date, time):
    dt_string = date + " " + time
    dt_object = datetime.strptime(dt_string, '%Y-%m-%d %H:%M:%S')

    timestamp = dt_object.timestamp()
    return timestamp
