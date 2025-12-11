"""
Legacy Delete Script – modernized for new vdmc_salesforce_migration library

- deletes records for a list of sObjects
- handles multi-pass deletes with smaller batch sizes to avoid DELETE_OPERATION_TOO_LARGE
- deactivates Order records before deletion
- saves Bulk API failure logs
"""

from vdmc_salesforce_migration import get_salesforce_client, cleanup_sobject

# ------------------------------------------------------
# Configuration
# ------------------------------------------------------
objects = [
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


# ------------------------------------------------------
# Main Delete Loop
# ------------------------------------------------------
client = get_salesforce_client()

for obj in objects:
    cleanup_sobject(client, obj)

