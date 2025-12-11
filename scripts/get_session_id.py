from vdmc_salesforce_migration import get_session_id
session_id, instance = get_session_id()

print("Session ID:", session_id)
print("Instance URL:", instance)