from vdmc_salesforce_migration import get_salesforce_client, activate_assets_via_api, get_field_map

client = get_salesforce_client()

# Get Order Ids dynamically (clean, using our soql module)
order_id_map = get_field_map(
    client,
    object_name="Order",
    key_field="Id",
    value_field="Name",
    where="Status = 'Activated'"
)

order_ids = list(order_id_map.keys())

print(f"Found {len(order_ids)} orders to activate.")

activate_assets_via_api(client, order_ids)

print("✔ Order Activation complete.")
