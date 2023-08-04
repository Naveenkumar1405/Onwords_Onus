import requests
from app import fast_api_server_ip


def get_client_data_tagged_to_staff_by_uid(uid):
    pass

def get_all_staff_data():
    return requests.get(f"http://{fast_api_server_ip}/staff/alldata/").json()
def get_all_staff_name():
    return requests.get(f"http://{fast_api_server_ip}/staff/data/name").json()

def get_all_pod_names():
    return requests.get(f"http://{fast_api_server_ip}/pod/names").json()

