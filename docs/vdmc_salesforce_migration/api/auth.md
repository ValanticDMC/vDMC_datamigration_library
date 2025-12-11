Module vdmc_salesforce_migration.api.auth
=========================================

Functions
---------

`get_salesforce_client()`
:   Creates a Salesforce client using only environment variables.
    Automatically detects sandbox vs production.
    Automatically fetches the latest API version.

`get_session_id()`
:   Returns a Salesforce session ID and instance URL.
    Useful for Postman or manual API testing.

Classes
-------

`SalesforceConnectionError(*args, **kwargs)`
:   Common base class for all non-exit exceptions.

    ### Ancestors (in MRO)

    * builtins.Exception
    * builtins.BaseException