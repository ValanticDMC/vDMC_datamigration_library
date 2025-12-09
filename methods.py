import os
from simple_salesforce import Salesforce, SalesforceLogin
import json
import datetime
import pandas as pd
import re
import csv
import requests
import math
from concurrent.futures import ThreadPoolExecutor

### DEFINITIONS ###
SQL_FOLDER = 'SQL'
MAP_FOLDER = 'Mappings'

def load_credentials(env):
    with open('credentials.json', 'r', encoding='utf-8') as f:
        credentials = json.load(f)
    return credentials[env]
    
def connect_to_sf(sf_credentials):
    # Build the API connection to SF
    if sf_credentials["isSandbox"] == True:
        client = Salesforce(
            username=sf_credentials["user"],
            password=sf_credentials["password"],
            security_token=sf_credentials["token"],
            instance_url=sf_credentials["domain"],
            domain='test',
            version='63.0'
        )
    else:
        client = Salesforce(
            username=sf_credentials["user"],
            password=sf_credentials["password"],
            security_token=sf_credentials["token"],
            instance_url=sf_credentials["domain"],
            version='63.0'
        )

    # Check if connection work
    response = client.query_all("SELECT Id FROM User LIMIT 1")
    if response != None:
        print('Connection to SF established')
    else:
        print('Could not fetch metadata')

    return client

def load_mapping(name):
    with open(MAP_FOLDER + '/' + name, 'r', encoding='utf-8') as f:
        mapping = json.load(f)
    return mapping

def load_file_w_mapping(pattern, map_path, table_name):
    # Get newest Export File
    export = get_latest_file(SQL_FOLDER, pattern)[0]
    # Load File in Pandas
    df = pd.read_csv(SQL_FOLDER + '/' + export)
    # Only non-deleted
    if 'deleted' in df.columns:
        df = df[df['deleted'] == 0]
    # Load Mapping
    mapping = load_mapping(map_path)
    # Keys from Map and Reduce Dataframe by them
    df = df[list(mapping[table_name].keys())]
    # Rename Columns w. SF Names
    df = df.rename(columns=mapping[table_name])
    return df

def get_record_types(client, object_name):
    data_sf = client.query_all(
        "SELECT Id, DeveloperName FROM RecordType WHERE SObjectType = '" + object_name + "'")
    id_name_mapping = {}
    for data in data_sf['records']:
        id_name_mapping[data['DeveloperName']] = data['Id']
    return id_name_mapping

def get_data(client, object_name):
    data_sf = client.query_all(
        "SELECT Id, vDMC_SugarExternalId__c FROM " + object_name)
    id_name_mapping = {}
    for data in data_sf['records']:
        id_name_mapping[data['vDMC_SugarExternalId__c']] = data['Id']
    return id_name_mapping

def get_data_source(client):
    data_sf = client.query_all(
        "SELECT Id FROM ExternalDataSource")
    id_name_mapping = {}
    for data in data_sf['records']:
        return data['Id']

def get_data_int_id(client, object_name):
    data_sf = client.query_all(
        "SELECT Id, Name FROM " + object_name)
    id_name_mapping = {}
    for data in data_sf['records']:
        id_name_mapping[data['Name']] = data['Id']
    return id_name_mapping

def get_data_with_id(client, object_name):
    data_sf = client.query_all(
        "SELECT Id, Name FROM " + object_name)
    id_name_mapping = {}
    for data in data_sf['records']:
        id_name_mapping[data['Id']] = data['Name']
    return id_name_mapping

def get_pricebook_entries(client):
    data_sf = client.query_all(
        "SELECT Id, Product2Id, CurrencyIsoCode FROM PricebookEntry WHERE Pricebook2.IsStandard = TRUE")
    id_name_mapping = {
        "EUR" : {},
        "USD" : {}
    }
    for data in data_sf['records']:
        id_name_mapping[data['CurrencyIsoCode']][data['Product2Id']] = data['Id']
    return id_name_mapping

def get_contacts_accountid(client):
    data_sf = client.query_all(
        "SELECT Id, vDMC_SugarExternalId__c, AccountId FROM Contact")
    id_name_mapping = {}
    for data in data_sf['records']:
        id_name_mapping[data['vDMC_SugarExternalId__c']] = data['AccountId']
    return id_name_mapping

def get_partners(client):
    data_sf = client.query_all(
        "SELECT Id, vDMC_SugarExternalPartnerId__c FROM Account WHERE vDMC_SugarExternalPartnerId__c != NULL")
    id_name_mapping = {}
    for data in data_sf['records']:
        id_name_mapping[data['vDMC_SugarExternalPartnerId__c']] = data['Id']
    return id_name_mapping

def get_profile_id(client, profile_name):
    data_sf = client.query_all(
        "SELECT Id, Name FROM Profile WHERE Name = '" + profile_name + "'")
    id_name_mapping = {}
    for data in data_sf['records']:
        id_name_mapping[data['Name']] = data['Id']
    return id_name_mapping

def get_discount_rate(client):
    data_sf = client.query_all(
        "SELECT Id, vDMC_Rate__c, vDMC_SugarExternalId__c FROM vDMC_Discount__c")
    id_name_mapping = {}
    for data in data_sf['records']:
        id_name_mapping[data['vDMC_SugarExternalId__c']] = data['vDMC_Rate__c']
    return id_name_mapping

def get_payment_term(client):
    data_sf = client.query_all(
        "SELECT Id, Name FROM PaymentTerm")
    id_name_mapping = {}
    for data in data_sf['records']:
        id_name_mapping[data['Name']] = data['Id']
    return id_name_mapping

def get_product_codes(client):
    data_sf = client.query_all(
        "SELECT Id, StockKeepingUnit FROM Product2")
    id_name_mapping = {}
    for data in data_sf['records']:
        id_name_mapping[data['StockKeepingUnit']] = data['Id']
    return id_name_mapping

def get_product_billing_frequency(client):
    data_sf = client.query_all(
        "SELECT Id, BillingFrequency FROM Product2")
    id_name_mapping = {}
    for data in data_sf['records']:
        id_name_mapping[data['vDMC_ProducerArticleNumber__c']] = data['Id']
    return id_name_mapping

def get_catalog_codes(client):
    data_sf = client.query_all(
        "SELECT Id, Code FROM ProductCatalog")
    id_name_mapping = {}
    for data in data_sf['records']:
        id_name_mapping[data['Code']] = data['Id']
    return id_name_mapping

def get_category_names(client):
    data_sf = client.query_all(
        "SELECT Id, Name FROM ProductCategory")
    id_name_mapping = {}
    for data in data_sf['records']:
        id_name_mapping[data['Name']] = data['Id']
    return id_name_mapping

def get_currency_for_account(client):
    data_sf = client.query_all(
        "SELECT Id, CurrencyIsoCode FROM Opportunity")
    id_name_mapping = {}
    for data in data_sf['records']:
        id_name_mapping[data['Id']] = data['CurrencyIsoCode']
    return id_name_mapping

def get_currency_for_opp(client):
    data_sf = client.query_all(
        "SELECT Id, CurrencyIsoCode FROM Opportunity")
    id_name_mapping = {}
    for data in data_sf['records']:
        id_name_mapping[data['Id']] = data['CurrencyIsoCode']
    return id_name_mapping

def get_currency_for_quote(client):
    data_sf = client.query_all(
        "SELECT Id, CurrencyIsoCode FROM Quote")
    id_name_mapping = {}
    for data in data_sf['records']:
        id_name_mapping[data['Id']] = data['CurrencyIsoCode']
    return id_name_mapping

def get_currency_for_invoice(client):
    data_sf = client.query_all(
        "SELECT Id, CurrencyIsoCode FROM vDMC_InvoiceLegacy__c")
    id_name_mapping = {}
    for data in data_sf['records']:
        id_name_mapping[data['Id']] = data['CurrencyIsoCode']
    return id_name_mapping

def get_contact_for_account(client):
    data_sf = client.query_all(
        "SELECT Id, AccountId FROM Contact")
    id_name_mapping = {}
    for data in data_sf['records']:
        id_name_mapping[data['AccountId']] = data['Id']
    return id_name_mapping

def get_currency_for_order(client):
    data_sf = client.query_all(
        "SELECT Id, CurrencyIsoCode FROM Order")
    id_name_mapping = {}
    for data in data_sf['records']:
        id_name_mapping[data['Id']] = data['CurrencyIsoCode']
    return id_name_mapping
    
def get_startdate_from_order(client):
    data_sf = client.query_all(
        "SELECT Id, EffectiveDate FROM Order")
    id_name_mapping = {}
    for data in data_sf['records']:
        id_name_mapping[data['Id']] = data['EffectiveDate']
    return id_name_mapping

def get_enddate_from_order(client):
    data_sf = client.query_all(
        "SELECT Id, EndDate FROM Order")
    id_name_mapping = {}
    for data in data_sf['records']:
        id_name_mapping[data['Id']] = data['EndDate']
    return id_name_mapping

def get_order_action(client):
    data_sf = client.query_all(
        "SELECT Id, OrderId FROM OrderAction")
    id_name_mapping = {}
    for data in data_sf['records']:
        id_name_mapping[data['OrderId']] = data['Id']
    return id_name_mapping

def get_app_usage_assigment(client):
    data_sf = client.query_all(
        "SELECT Id, RecordId FROM AppUsageAssignment")
    id_name_mapping = {}
    for data in data_sf['records']:
        id_name_mapping[data['Id']] = data['RecordId']
    return id_name_mapping

def get_emails_with_message_id(client):
    data_sf = client.query_all(
        "SELECT Id, MessageIdentifier FROM EmailMessage")
    id_name_mapping = {}
    for data in data_sf['records']:
        id_name_mapping[data['MessageIdentifier']] = data['Id']
    return id_name_mapping

def get_pricing_term_from_pricebookentry(client):
    data_sf = client.query_all(
        "SELECT Id, ProductSellingModel.PricingTermUnit FROM PricebookEntry")
    id_name_mapping = {}
    for data in data_sf['records']:
        id_name_mapping[data['Id']] = data['ProductSellingModel']['PricingTermUnit']
    return id_name_mapping

def get_selling_type_from_pricebookentry(client):
    data_sf = client.query_all(
        "SELECT Id, ProductSellingModel.SellingModelType FROM PricebookEntry")
    id_name_mapping = {}
    for data in data_sf['records']:
        id_name_mapping[data['Id']] = data['ProductSellingModel']['SellingModelType']
    return id_name_mapping

def get_emails_with_relation(client):
    data_sf = client.query_all(
        "SELECT Id, RelatedToId, vDMC_SugarExternalId__c FROM EmailMessage")
    id_name_mapping = {}
    for data in data_sf['records']:
        id_name_mapping[data['vDMC_SugarExternalId__c']] = data['RelatedToId']
    return id_name_mapping

def get_account_data_for_billing(client):
    data_sf = client.query_all(
        'SELECT Id, BillingStreet, BillingCity, BillingCountry, BillingPostalCode, Name, vDMC_PaymentTerms__c, vDMC_PurchaseTerms__c FROM Account')
    return data_sf

def get_notes(client):
    data_sf = client.query_all(
        'SELECT Id, Content FROM ContentNote')
    id_name_mapping = {}
    for data in data_sf['records']:
        id_name_mapping[data['Id']] = data['Content']
    return id_name_mapping

def get_assets(client):
    data_sf = client.query_all(
        'SELECT Id, Name FROM Asset')
    id_name_mapping = {}
    for data in data_sf['records']:
        id_name_mapping[data['Id']] = data['Name']
    return id_name_mapping

def get_asset_action(client):
    data_sf = client.query_all(
        'SELECT Id, AssetId FROM AssetAction')
    id_name_mapping = {}
    for data in data_sf['records']:
        id_name_mapping[data['AssetId']] = data['Id']
    return id_name_mapping

def get_asset_action_source(client):
    data_sf = client.query_all(
        'SELECT Id, AssetActionID, ReferenceEntityItemId FROM AssetActionSource')
    id_name_mapping = {}
    for data in data_sf['records']:
        id_name_mapping[data['AssetActionId']] = data['ReferenceEntityItemId']
    return id_name_mapping

def get_orderitem_w_ordername(client):
    data_sf = client.query_all(
        'SELECT Id, Order.Name From OrderItem')
    id_name_mapping = {}
    for data in data_sf['records']:
        id_name_mapping[data['Id']] = data['Order']['Name']
    return id_name_mapping

def threading_upload_chunk(sf_credentials, chunk, object_name, external_identifier, id_field):
    client_thread = connect_to_sf(sf_credentials)        # EIN Client pro Thread
    return upload_to_sf_single_api(
        client_thread,
        object_name,
        chunk,
        external_identifier,
        id_field
    )

def threading_chunk_list(data, num_chunks):
    size = math.ceil(len(data) / num_chunks)
    return [data[i:i+size] for i in range(0, len(data), size)]

def threading_upload_to_sf_single_api(sf_credentials, object_name, data, external_identifier, id_field, num_threads):
    NUM_THREADS = num_threads
    chunks = threading_chunk_list(data, NUM_THREADS)
    print(f"Start Upload with {NUM_THREADS} Threads…")
    print(f"Number of Chunks: {len(chunks)} Records per Chunk: ~{len(chunks[0])}")
    with ThreadPoolExecutor(max_workers=NUM_THREADS) as executor:
        futures = [
            executor.submit(
                threading_upload_chunk,
                sf_credentials,
                chunk,
                object_name,
                external_identifier,
                id_field
            )
            for chunk in chunks
        ]

        for i, future in enumerate(futures, start=1):
            try:
                future.result()
                print(f"✔ Chunk {i}/{NUM_THREADS} done")
            except Exception as e:
                print(f"❌ Error in Chunk {i}: {e}")
    print("Upload done.")

def upload_to_sf_single_api(client, object_name, data, external_identifier, id_field):
    print('Start uploading: ' + object_name)
    sf_object = client.__getattr__(object_name)

    if client.is_sandbox() == True:
        folder = 'sandbox'
    else:
        folder = 'prod'
    output_file = "logs/" + folder + "/id_write_" + object_name + "_" + str(
            int(datetime.datetime.now().timestamp())) + ".csv"

    #Write header
    if not os.path.exists(output_file):
        with open(output_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["sugar_id", "sf_id", "success", "errors"])

    total = len(data)
    for idx, data_item in enumerate(data, start=1):
        print(f"{idx}/{total} ({idx/total:.1%})")
        sugar_id = ''
        if id_field != None:
            sugar_id = data_item.get(id_field)
            del data_item[id_field]
        cleaned_item = {k: v for k, v in data_item.items() if v} #Remove empty pairs
        result = None
        if external_identifier == None:
            try:
                result = sf_object.create(cleaned_item)
            except Exception as e:
                with open(output_file, "a", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerow([sugar_id, data_item, 'False', 'Exception occurred'])
                if "REQUEST_LIMIT_EXCEEDED" in str(e) or "429" in str(e):
                    raise
        else:
            result = sf_object.upsert(cleaned_item, external_id_field=external_identifier)

        if result:
            # Write lines with ids
            sf_id = result.get("id")
            success = result.get("success")
            errors = ";".join(result.get("errors", []))
            with open(output_file, "a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([sugar_id, sf_id, success, errors])
            
    print('Upload done')
    

def upload_to_sf(client, object_name, data, external_identifier, **kwargs):
    print('Start uploading: ' + object_name)

    # Do upsert with external identifier and insert if none provided
    results = []
    sf_object = client.bulk2.__getattr__(object_name)

    batch_size = kwargs.get('batch_size', None)

    if external_identifier == None:
        results = sf_object.insert(records=data, batch_size=batch_size)
    else:
        results =sf_object.upsert(records=data, external_id_field=external_identifier, batch_size=batch_size)

    print(results)
    for result in results:
        job_id = result['job_id']
        sf_object.get_failed_records(job_id, file="logs/errors_" + object_name + "_" + str(
            int(datetime.datetime.now().timestamp())) + ".csv")
    print('Upload done')

def update_to_sf(client, object_name, data, external_identifier, **kwargs):
    print('Start uploading: ' + object_name)

    # Do upsert with external identifier and insert if none provided
    results = []
    sf_object = client.bulk2.__getattr__(object_name)

    batch_size = kwargs.get('batch_size', 10000)

    if external_identifier == None:
        results = sf_object.update(records=data, batch_size=batch_size)
    else:
        results =sf_object.update(records=data, external_id_field=external_identifier, batch_size=batch_size)

    print(results)
    for result in results:
        job_id = result['job_id']
        sf_object.get_failed_records(job_id, file="logs/errors_" + object_name + "_" + str(
            int(datetime.datetime.now().timestamp())) + ".csv")
    print('Upload done')

def activate_assets_via_api(client, sf_credentials, env, order_ids):
    if client.is_sandbox() == True:
        base_url = 'https://sepgmbh--' + env + '.sandbox.my.salesforce.com'
    else:
        base_url = 'https://sepgmbh.my.salesforce.com'
    endpoint = base_url + '/services/data/v65.0/actions/standard/createOrUpdateAssetFromOrder'

    session_id, instance = SalesforceLogin(
        username=sf_credentials['user'],
        password=sf_credentials['password'],
        security_token=sf_credentials['token'],
        domain='test')
    headers = {
        "Authorization": "Bearer " + session_id
    }

    output_file = "logs/" + "/order_to_asset_" + str(
        int(datetime.datetime.now().timestamp())) + ".csv"

    # Write header
    if not os.path.exists(output_file):
        with open(output_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["sf_id", "errors"])

    total = len(order_ids)
    for idx, order_id in enumerate(order_ids, start=1):
        print(f"{idx}/{total} ({idx / total:.1%})")
        body = {
            "inputs": [
                {
                    "orderId": order_id
                }
            ]
        }
        response = requests.post(endpoint, headers=headers, json=body)
        # Logging
        if response.status_code >= 300:
            # Write lines with ids
            sf_id = order_id
            errors = response.text
            with open(output_file, "a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([sf_id, errors])

def get_latest_file(sql_folder, pattern):
    filelist = os.listdir(sql_folder)
    return sorted(
        [f for f in filelist if f.lower().startswith(pattern)],
        reverse=True
    )

def convert_datetime(df, fieldname):
    df[fieldname] = pd.to_datetime(df[fieldname], errors='coerce')
    if df[fieldname].dt.tz is None:
        df[fieldname] = df[fieldname].dt.tz_localize('UTC')
    else:
        df[fieldname] = df[fieldname].dt.tz_convert('UTC')
    df[fieldname] = df[fieldname].dt.strftime('%Y-%m-%dT%H:%M:%SZ').fillna('')
    return df

def extract_email(s):
    if pd.isna(s):
        return []
    s = str(s)
    return re.findall(r'[\w\.-]+@[\w\.-]+\.\w+', s)

def extract_email_from_field(df, field):
    df[field] = df[field].apply(lambda x: ",".join(extract_email(x)))
    return df

def clean_numeric_fields(df):
    """
    Cleans all numeric fields for Salesforce bulk upload compatibility.
    Converts invalid numeric strings ('nan', 'None', '') to np.nan,
    and coerces numeric columns to float64.
    """
    # Detect numeric-like columns: already numeric OR look like they should be
    numeric_candidates = [
        col for col in df.columns
        if df[col].dtype in [int, float, 'int64', 'float64']
        or re.search(r'(Amount|Count|Rate|Percentage|Prob|Qty|Number|Total|Score|Value)', col, re.IGNORECASE)
    ]

    for col in numeric_candidates:
        df[col] = df[col].fillna(0)

    return df

def join_related_fields(row, fields, lookup):
    values = []
    for f in fields:
        v = row.get(f)
        if pd.isna(v):
            continue
        v = str(v).strip()
        if v in lookup:
            values.append(lookup[v])
    return ",".join(values)

def replace_ids_in_list(value, id_map):
    if pd.isna(value) or value == "":
        return ""

    # split by semicolon
    ids = str(value).split(";")

    # replace each id using the map, fallback ""
    replaced = [id_map.get(i.strip(), "") for i in ids]

    # join back together
    return ",".join([r for r in replaced if r != ""])

def sanitize_field(s):
    if pd.isna(s):
        return ""
    # Stelle sicher, dass String in UTF-8 decodierbar ist
    if isinstance(s, bytes):
        s = s.decode("utf-8", errors="ignore")
    else:
        s = str(s).encode("utf-8", errors="ignore").decode("utf-8", errors="ignore")

    # Ersetze problematische Zeichen
    s = s.replace('"', "'")
    s = re.sub(r'[\r\n\t]+', ' ', s)
    s = re.sub(r'[^\x20-\x7EäöüÄÖÜß€°²³]', '', s)
    s = re.sub(r'\s{2,}', ' ', s)

    # Ersetze potenzielle CSV-Trenner (je nach Export-Delimiter!)
    s = s.replace(';', '·')
    s = s.strip()

    return s

def clear_fields(df):
    for col in df.select_dtypes(include='object').columns:
        df[col] = df[col].apply(sanitize_field)

    for col in df.columns:
        df[col] = df[col].replace(
            to_replace=["nan", "NaN", "None", "NONE", "null", "NULL", ""],
            value=''
        )

    df = clean_numeric_fields(df)

    return df

def clean_emails(df, field_name):
    email_pattern = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")
    df[field_name] = df[field_name].apply(
        lambda x: x if isinstance(x, str) and email_pattern.match(x) else ""
    )
    df[field_name] = df[field_name].str.replace('..', '.')
    return df

def replace_text(text, mapping):
    if pd.isna(text):
        return ""
    for old, new in mapping.items():
        text = text.replace(old, new)
    return text
