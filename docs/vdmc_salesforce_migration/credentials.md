Module vdmc_salesforce_migration.credentials
============================================

Functions
---------

`load_credentials(env: str = None) ‑> dict`
:   Loads Salesforce credentials from environment variables.
    Supports multiple environments, e.g.: dev, stage, preview, prod.

Classes
-------

`CredentialError(*args, **kwargs)`
:   Common base class for all non-exit exceptions.

    ### Ancestors (in MRO)

    * builtins.Exception
    * builtins.BaseException