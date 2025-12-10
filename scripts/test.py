from vdmc_salesforce_migration.utils.file_io import load_file_with_mapping

df_accounts = load_file_with_mapping(
    pattern="account",
    mapping_file="accounts.json",
    table_name="field_map"
)

print(df_accounts.head())