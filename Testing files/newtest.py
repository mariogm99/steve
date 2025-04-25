import os
from dotenv import load_dotenv
import whoop as wh

# Load .env variables
load_dotenv()

# Your WHOOP credentials from .env or hard-coded
username = os.getenv("WHOOP_USERNAME")
password = os.getenv("WHOOP_PASSWORD")

def main():
    # Create and authenticate the client
    with wh.WhoopClient(username, password) as client:
        # 1) Get the most recent recovery
        recovery_collection = client.get_recovery_collection()
        if not recovery_collection:
            print("No recovery data found.")
            return
        latest_recovery = recovery_collection[0]
        
        recovery_score = latest_recovery["score"]["recovery_score"]
        hrv = latest_recovery["score"]["hrv_rmssd_milli"]
        rhr = latest_recovery["score"]["resting_heart_rate"]

        # 2) Get the most recent cycle (for strain data)
        cycle_collection = client.get_cycle_collection()
        if not cycle_collection:
            print("No cycle data found.")
            return
        latest_cycle = cycle_collection[0]
        strain = latest_cycle["score"]["strain"]

        # 3) Get the most recent sleep
        sleep_collection = client.get_sleep_collection()
        if not sleep_collection:
            print("No sleep data found.")
            return
        latest_sleep = sleep_collection[0]

        # Example: Get a sleep performance percentage from the "score" object
        # The exact field name might be "sleep_performance", "sleep_performance_percentage",
        # or something similar, depending on the WHOOP API’s actual response.
        # If you're not sure, you can print out `latest_sleep` to see all available fields.
        sleep_performance = latest_sleep["score"].get("sleep_performance")

        print("===== WHOOP Latest Metrics =====")
        print(f"Recovery Score: {recovery_score}")
        print(f"Strain: {strain}")
        print(f"HRV (ms): {hrv}")
        print(f"RHR (bpm): {rhr}")
        if sleep_performance is not None:
            print(f"Last Night's Sleep Performance: {sleep_performance}%")
        else:
            print("No sleep performance field was found in the data.")
        print("================================")

if __name__ == "__main__":
    main()
