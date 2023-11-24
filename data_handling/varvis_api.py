import streamlit as st
import requests
import pandas as pd
import json
import os
from os.path import exists

import settings.credentials as cr


def varvis_api_login(target, user_name, password):
    token = ""
    session_id = ""
    # 1) Get CSRF token and session ID to log in
    r = requests.head("https://" + cr.varvis_target + ".varvis.com/authenticate")
    token = r.headers['X-CSRF-TOKEN']
    session_id = r.cookies['session']
    # 2) Log in and update CSRF token in an additional step
    r = requests.post("https://" + target + ".varvis.com/login", data = {'_csrf': token, 'username': user_name, 'password': password}, cookies = dict(session=session_id))
    session_id = r.cookies['session']
    ### THIS ADDITIONAL REQUEST IS NECESSARY TO RETRIEVE THE CORRECT CSRF TOKEN:
    r = requests.head("https://" + target + ".varvis.com/authenticate", cookies = dict(session=session_id))
    token = r.headers['X-CSRF-TOKEN']
    
    return session_id

@st.cache_data
def get_analyses_per_person(personID, session_id, target):
    r = requests.get("https://" + target + ".varvis.com/person/" + personID + "/analyses", cookies = dict(session=session_id))
    return r

@st.cache_data
def download_vcf(analysisId, session_id, target):
    res = get_download_link(analysisId, session_id, target)
    vcf_file_name = ""
    download_link = ""
    for item in res["response"]["apiFileLinks"]:
        
        if ("gatk-haplotype" in item["fileName"]) & (not ".tbi" in item["fileName"]):
            download_link = item["downloadLink"]
            vcf_file_name = item["fileName"]
        if ".tbi" in item["fileName"]:
            download_link_tabix = item["downloadLink"]

    # check if vcf_file_name and vcf_file_name.tbi already exists locally 
    if (exists('/tmp/' + vcf_file_name)) and (exists('/tmp/' + vcf_file_name + ".tbi")) :
        return '/tmp/' + vcf_file_name
    else:
        if download_link:
            r = requests.get(download_link, stream=True)
            if r.status_code == 200:
                with open('/tmp/' + vcf_file_name, 'wb') as vcf_file:
                    vcf_file.write(r.content)
                r = requests.get(download_link_tabix, stream=True)    
                with open('/tmp/' + vcf_file_name + ".tbi", 'wb') as vcf_file_index:
                    vcf_file_index.write(r.content)
            else:
                st.write(vcf_file_name + " error: " + r.status_code + r.text)
                st.stop()
            return vcf_file.name

def get_download_link(analysisId, session_id, target):
    r = requests.get("https://" + target + ".varvis.com/api/analysis/" + analysisId + "/get-file-download-links", cookies = dict(session=session_id))
    response = json.loads(r.text)
    return response