import datetime
import hashlib
import hmac
import json
import os
import time
import urllib.parse
from pprint import pprint

import pandas as pd
import requests
import streamlit as st
import urllib3
from dotenv import load_dotenv

if load_dotenv(".env"):
    # for local development
    CLOAK_PRIVATE_KEY = os.getenv("CLOAK_PRIVATE_KEY")
    CLOAK_PUBLIC_KEY = os.getenv("CLOAK_PUBLIC_KEY")
else:
    CLOAK_PRIVATE_KEY = st.secrets.get("CLOAK_PRIVATE_KEY")
    CLOAK_PUBLIC_KEY = st.secrets.get("CLOAK_PUBLIC_KEY")

base_url = "https://ext-api.cloak.gov.sg/prod/L4"

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def generate_signature(http_method, path, query_params, headers, payload, private_key, service):
    # Generate Signature

    # Ensure query_params is a dictionary
    query_params = query_params if query_params else {}

    # Step 1: Create the canonical request
    canonical_uri = urllib.parse.quote(path, safe="/")
    canonical_querystring = "&".join(
        f"{urllib.parse.quote(k, safe='')}={urllib.parse.quote(v, safe='')}"
        for k, v in sorted(query_params.items())
    )
    signed_headers = sorted(headers.keys())
    canonical_headers = "".join(
        f"{k.lower()}:{v.strip()}\n" for k, v in sorted(headers.items())
    )
    signed_headers_string = ";".join(k.lower() for k in signed_headers)

    if isinstance(payload, dict):
        payload_str = json.dumps(payload, separators=(
            ",", ":"), sort_keys=True)  # Ensure consistent key order
        payload_bytes = payload_str.encode("utf-8")
        payload_hash = hashlib.sha256(payload_bytes).hexdigest()
    else:
        payload_hash = hashlib.sha256(payload).hexdigest()

    canonical_request = (
        f"{http_method}\n"
        f"{canonical_uri}\n"
        f"{canonical_querystring}\n"
        f"{canonical_headers}\n"
        f"{signed_headers_string}\n"
        f"{payload_hash}"
    )
    # Step 2: Create the string to sign
    algorithm = "CLOAK-AUTH"
    # formatted_date = datetime.date.today().strftime("%Y%m%d") + "T000000Z"
    formatted_date = datetime.datetime.now(
        datetime.timezone.utc).strftime("%Y%m%d") + "T000000Z"
    date_stamp = formatted_date[:8]

    string_to_sign = (
        f"{algorithm}\n"
        f"{formatted_date}\n"
        f"{hashlib.sha256(canonical_request.encode('utf-8')).hexdigest()}"
    )
    # Step 3: Calculate the signing key

    def sign(key, msg):
        return hmac.new(key, msg.encode("utf-8"), hashlib.sha256).digest()

    date_key = sign(("CLOAK-AUTH" + private_key).encode("utf-8"), date_stamp)
    date_service_key = sign(date_key, service)
    signing_key = sign(date_service_key, "cloak_request")

    # Step 4: Calculate the signature
    signature = hmac.new(signing_key, string_to_sign.encode(
        "utf-8"), hashlib.sha256).hexdigest()

    return signature


def extract_url_info(url):
    # Extract URL Information
    parsed_url = urllib.parse.urlparse(url)
    path = parsed_url.path
    query_params = urllib.parse.parse_qs(parsed_url.query)
    # Convert query_params values from list to single value
    query_params = {k: v[0] for k, v in query_params.items()}
    return path, query_params


def downgrade_classification(text):
    analyse_result = cloak_analyse(text)

    result = ""
    index = 0
    for identifier in sorted(analyse_result, key=lambda x: x["start"]):
        start_index = identifier["start"]
        end_index = identifier["end"]
        result += text[index:start_index]
        result += f"**{text[start_index:end_index]}**"
        index = end_index
    result += text[index:len(text)]
    return result


def cloak_it(text):
    return cloak_transform(text)["text"]


def cloak_analyse(text):
    url = f"{base_url}/analyze"
    payload = {
        "text": text,
        "language": "en",
        "score_threshold": 0.5,
        "entities": [
            "PERSON",
            "SG_NRIC_FIN",
            "EMAIL_ADDRESS",
            "SG_BANK_ACCOUNT_NUMBER",
            "SG_ADDRESS",
            "PHONE_NUMBER"
        ],
        "allow_list": [""],
        "analyze_parameters": {
            "nric": {
                "checksum": False
            }
        }
    }
    #####################
    http_method = "POST"
    service = "fta"

    path, query_params = extract_url_info(url)

    signed_headers = {
        "Content-Type": "application/json"
    }

    signature = generate_signature(
        http_method, path, query_params, signed_headers, payload, CLOAK_PRIVATE_KEY, service)
    authorization = f"CLOAK-AUTH Credential={CLOAK_PUBLIC_KEY},SignedHeaders=Content-Type,Signature={signature}"
    headers = {"Content-Type": "application/json", "Accept": "application/json",
               "Authorization": f"{authorization}", "x-cloak-service": f"{service}"}
    response = requests.post(url, headers=headers, json=payload, verify=False)
    #####################
    # pprint(response.json())
    analyzer_results = response.json()
    return analyzer_results


def cloak_transform(text):
    # FTA Transform Endpoint
    url = f"{base_url}/transform"
    payload = form_transform_payload(text)

    #####################
    http_method = "POST"
    service = "fta"

    path, query_params = extract_url_info(url)
    signed_headers = {
        "Content-Type": "application/json"
    }
    signature = generate_signature(
        http_method, path, query_params, signed_headers, payload, CLOAK_PRIVATE_KEY, service)
    authorization = f"CLOAK-AUTH Credential={CLOAK_PUBLIC_KEY},SignedHeaders=Content-Type,Signature={signature}"
    headers = {"Content-Type": "application/json", "Accept": "application/json",
               "Authorization": f"{authorization}", "x-cloak-service": f"{service}"}
    response = requests.post(url, headers=headers, json=payload, verify=False)
    #####################
    # pprint(response.json())
    transform_results = response.json()
    return transform_results


entity_parameter_mapping = {
    "Name": "PERSON",
    "NRIC": "SG_NRIC_FIN",
    "Email Address": "EMAIL_ADDRESS",
    "Phone Number": "PHONE_NUMBER",
    "Nationality/Race/Religion": "NRP",
    "Full Address": "SG_ADDRESS",
    "Street": "SG_ADDRESS_STREET",
    "Postal Code": "SG_ADDRESS_POSTAL_CODE",
    "Unit Number": "SG_ADDRESS_UNIT_NUMBER",
    "Country": "LOCATION",
    "Currency": "CURRENCY",
    "Credit Card": "CREDIT_CARD",
    "SG Bank Account Number": "SG_BANK_ACCOUNT_NUMBER",
    "Intl. Bank Account Number": "IBAN_CODE",
    "IP Address": "IP_ADDRESS",
    "URL": "URL",
    "Date and Time": "DATE_TIME",
    "UEN": "SG_UEN"
}


def form_transform_payload(text, score_threshold=0.5):

    entities = []
    anonymizers = {}
    for name in entity_parameter_mapping.keys():
        if st.session_state.get(f"toggle_{name.lower()}", True):
            entities.append(entity_parameter_mapping[name])

            technique = st.session_state.get(
                f"technique_{name.lower()}").lower()
            anonymizers[entity_parameter_mapping[name]] = {
                "type": technique
            }
            if technique == "replace":
                anonymizers[entity_parameter_mapping[name]]["new_value"] = st.session_state.get(
                    f"replace_text_{name.lower()}", f"<{name}>")
            elif technique == "mask":
                anonymizers[entity_parameter_mapping[name]]["masking_char"] = st.session_state.get(
                    f"mask_char_{name.lower()}", "*")
                anonymizers[entity_parameter_mapping[name]]["chars_to_mask"] = st.session_state.get(
                    f"mask_length_{name.lower()}", 1)
                anonymizers[entity_parameter_mapping[name]]["from_end"] = not st.session_state.get(
                    f"mask_prefix_{name.lower()}", False)
            elif technique == "alias" or technique == "redact":
                pass

    payload = {
        "text": text,
        "language": "en",
        "entities": entities,
        "analyze_parameters": {
            "nric": {
                "checksum": False
            }
        },
        "score_threshold": score_threshold,
        "anonymizers": anonymizers
    }

    return payload
