import io
import os
import shutil
import time

import py7zr
import requests
from mpds_client import MPDSDataRetrieval, MPDSDataTypes
from utils import get_props_folders_map


def mpds_archives_processing(api_key, arch_dir = "./mpds_archives/"):
    """Downloads MPDS archives, extracts and validates them."""
    mpds_api = MPDSDataRetrieval(dtype=MPDSDataTypes.AB_INITIO, api_key=api_key)
    result_count = {}

    for prop in get_props_folders_map().keys():
        cnt = 0
        try:
            entries = mpds_api.get_data({"props": prop}, fields={})
            len(entries)
        except:
            time.sleep(2)
            continue

        try:
            for entry in entries:
                archive_url = entry["sample"]["measurement"][0]["raw_data"]

                response = requests.get(archive_url)
                if response.status_code == 200:
                    curr_folder = arch_dir + prop + "/" + os.path.basename(archive_url)[:-3]
                    with py7zr.SevenZipFile(
                        io.BytesIO(response.content), mode="r"
                    ) as archive:
                        archive.extractall(path=curr_folder)
                    print(f"The archive {archive_url} is opening successfully")

                    if os.path.exists(curr_folder + "/" + get_props_folders_map()[prop]):
                        cnt += 1
                        shutil.rmtree(curr_folder)
                        os.makedirs(arch_dir + prop + "/true/", exist_ok=True)
                        with open(
                            arch_dir + prop + "/true/" + os.path.basename(archive_url), "wb"
                        ) as f:
                            f.write(response.content)
                    else:
                        shutil.rmtree(curr_folder)
                        os.makedirs(arch_dir + prop + "/false/", exist_ok=True)
                        with open(
                            arch_dir + prop + "/false/" + os.path.basename(archive_url),
                            "wb",
                        ) as f:
                            f.write(response.content)

                elif response.status_code == 400:
                    break
                else:
                    print(
                        f"Failed to load archive {archive_url}. Status:{response.status_code}"
                    )
            result_count[prop] = {"n_mpds_api": len(entries), "n_real": cnt}
            print("Result for current iteration: ", result_count[prop])
        except Exception as e:
            print(f"Error processing property{prop}: {e}")

    print("Result: ", result_count)
    
if __name__ == "__main__":
    # example
    # replace 'your_api_key' with your actual MPDS API key
    mpds_archives_processing(api_key="your_api_key", arch_dir="./mpds_archives/")
