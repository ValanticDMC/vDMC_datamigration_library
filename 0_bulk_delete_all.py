import pandas as pd
import methods
import datetime
import copy

### SF Connection ###
env = 'preview'
#env = 'prod'

object_names = [
    'Product2DataTranslation',
    'EmailMessage',
    'vDMC_InvoiceLegacy__c',
    'vDMC_InvoiceLineLegacy__c',
    'vDMC_InvoiceLineGroupLegacy__c',
    'Case',
    'Order',
    'OrderItem',
    'OrderItemGroup',
    'Contract',
    'Event',
    'Task',
    'Quote',
    'QuoteLineGroup',
    'QuoteLineItem',
    'Campaign',
    'CampaignMember',
    'PricebookEntry',
    'ProductSellingModelOption',
    'ProductCategoryProduct',
    'ProductCatalog',
    'ProductCategory',
    'BillingAccount',
    'Lead',
    'Opportunity',
    'OrderAction',
    'AppUsageAssignment',
    'Contact',
    'Account',
    'vDMC_Discount__c',
    'Asset',
    'ContentDocument',
    'Product2',
]
#########

def save_results(results, sobject):
    for result in results:
        job_id = result['job_id']
        sobject.get_failed_records(job_id, file="logs/errors_" + object_name + "_" + str(
            int(datetime.datetime.now().timestamp())) + ".csv")

def delete_job(client, object_name, data, batch_size):
    print('Start delete with Batch Size: ' + str(batch_size))
    sobject = client.bulk2.__getattr__(object_name)  # dynamisch
    results = sobject.delete(records=data, batch_size=batch_size)
    save_results(results, sobject)
    data_sf_after = client.query_all(
        "SELECT Id FROM " + object_name + ""
    )
    print(str(len(data_sf_after['records'])) + ' Records found.')
    return data_sf_after

def deactivate_records(client, object_name, data):
    for record in data:
        record['Status'] = 'Draft'
    methods.update_to_sf(client, object_name, data, None)

def query_records_for_delete(client, object_name):
    data_sf = client.query_all(
        "SELECT Id FROM " + object_name + ""
    )
    ids = []
    for data in data_sf['records']:
        ids.append(data['Id'])
    data = [{"Id": _id} for _id in ids]
    print(str(len(ids)) + ' ' + object_name + ' Records found.')
    return data

#Init client
sf_credentials = methods.load_credentials(env)
client = methods.connect_to_sf(sf_credentials)

for object_name in object_names:
    data = query_records_for_delete(client, object_name)
    if len(data) > 0:
        # First deactivate Order before removal
        if object_name in ['Order']:
            deactivate_records(client, object_name, copy.deepcopy(data))

        batch_size = 10000
        data_sf_after = delete_job(client, object_name, data, batch_size)

        # To Avoid DELETE_OPERATION_TOO_LARGE
        if object_name in ['Contact', 'Account', 'Product2'] and (len(data_sf_after['records']) > 0):
            batch_size = 100
            data_sf_after = delete_job(client, object_name, data, batch_size)

        # To Avoid DELETE_OPERATION_TOO_LARGE
        if object_name in ['Contact', 'Account', 'Product2'] and (len(data_sf_after['records']) > 0):
            batch_size = 10
            data_sf_after = delete_job(client, object_name, data, batch_size)

        # To Avoid DELETE_OPERATION_TOO_LARGE
        if object_name in ['Contact', 'Account', 'Product2'] and (len(data_sf_after['records']) > 0):
            batch_size = 1
            data_sf_after = delete_job(client, object_name, data, batch_size)

    print('Cleaning Done.')
