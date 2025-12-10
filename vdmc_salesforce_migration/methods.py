import os
from simple_salesforce import SalesforceLogin
import datetime
import csv
import requests
import math
from concurrent.futures import ThreadPoolExecutor

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



def get_latest_file(sql_folder, pattern):
    filelist = os.listdir(sql_folder)
    return sorted(
        [f for f in filelist if f.lower().startswith(pattern)],
        reverse=True
    )


