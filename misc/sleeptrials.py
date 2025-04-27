import os
from dotenv import load_dotenv
import whoop as wh

# Load .env variables
load_dotenv()

# Your WHOOP credentials from .env or hard-coded
username = os.getenv("WHOOP_USERNAME")
password = os.getenv("WHOOP_PASSWORD")

def main():
    if not username or not password:
        print("Error: WHOOP_USERNAME and WHOOP_PASSWORD must be set in .env file")
        return

    try:
        # Create and authenticate the client
        with wh.WhoopClient(username, password) as client:
            # Verify authentication
            if not client.is_authenticated():
                print("Error: Failed to authenticate with WHOOP API")
                return

            print("Successfully authenticated with WHOOP API")
            
            # 1) Get the most recent recovery
            try:
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
                
                # Access the 'score' field for sleep metrics
                sleep_score = latest_sleep["score"]
                
                # Extract the metrics you want
                sleep_perf_pct  = sleep_score.get("sleep_performance_percentage")
                sleep_cons_pct  = sleep_score.get("sleep_consistency_percentage")
                sleep_eff_pct   = sleep_score.get("sleep_efficiency_percentage")
                resp_rate       = sleep_score.get("respiratory_rate")

                # Print out the data
                print("===== WHOOP Latest Metrics =====")
                print(f"Recovery Score: {recovery_score}")
                print(f"Strain: {strain}")
                print(f"HRV (ms): {hrv}")
                print(f"RHR (bpm): {rhr}")

                # Print sleep scores if they exist
                if sleep_perf_pct is not None:
                    print(f"Sleep Performance (%): {sleep_perf_pct}")
                if sleep_cons_pct is not None:
                    print(f"Sleep Consistency (%): {sleep_cons_pct}")
                if sleep_eff_pct is not None:
                    print(f"Sleep Efficiency (%): {sleep_eff_pct}")
                if resp_rate is not None:
                    print(f"Respiratory Rate: {resp_rate}")

                print("================================")
            except Exception as e:
                print(f"Error fetching data: {str(e)}")
                return

    except Exception as e:
        print(f"Error: {str(e)}")
        return

if __name__ == "__main__":
    main()
