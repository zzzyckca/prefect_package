import os
import subprocess
import configparser
import pandas as pd
import holidays
from datetime import datetime
from prefect import task, flow
from prefect_email import EmailServerCredentials, email_send_message

# Read config.ini to find VENV_DIR
config = configparser.ConfigParser()
config.read(os.path.join(os.path.dirname(__file__), 'config.ini'))
venv_dir = config.get('Settings', 'VENV_DIR', fallback=r'C:\prefect\venv')
python_exe = os.path.join(venv_dir, 'Scripts', 'python.exe')

def failure_email_hook(flow, flow_run, state):
    """
    Hook to trigger an email via prefect-email when the pipeline fails.
    Requires an EmailServerCredentials block to be configured in your Prefect UI.
    """
    try:
        email_credentials_block = EmailServerCredentials.load("my-email-credentials")
        
        subject = f"Pipeline Failed: {flow.name}"
        msg = f"Flow run {flow_run.name} ({flow_run.id}) entered Failed state!\n\n"
        msg += f"Exception: {state.message}"
        
        email_send_message(
            email_server_credentials=email_credentials_block,
            subject=subject,
            msg=msg,
            email_to="your.email@example.com" # MODIFY THIS
        )
        print("Failure email dispatched successfully.")
    except Exception as e:
        print(f"Failed to send failure email (Did you configure the Email block in the UI?): {e}")

@task
def run_task(script_path):
    print(f"Starting execution: {script_path}")
    if not os.path.exists(script_path):
        raise FileNotFoundError(f"Script not found: {script_path}")
        
    result = subprocess.run([python_exe, script_path], capture_output=True, text=True)
    if result.stdout: 
        print(f"Output:\n{result.stdout.strip()}")
    if result.returncode != 0:
        print(f"Error Output:\n{result.stderr.strip()}")
        raise RuntimeError(f"Script failed: {script_path}")

@task
def check_toronto_business_day(target_day: int):
    print(f"Checking if today is Toronto Business Day #{target_day} of the month...")
    
    today = pd.Timestamp(datetime.today().date())
    
    # Get Ontario holidays for the current year
    on_holidays = holidays.CA(prov='ON', years=today.year)
    holiday_dates = list(on_holidays.keys())
    
    # Create a CustomBusinessDay offset with Ontario holidays
    bday_ca = pd.offsets.CustomBusinessDay(holidays=holiday_dates)
    
    # Get the first day of the current month
    first_day_of_month = today.replace(day=1)
    
    # Generate business days for the current month
    end_of_month = today + pd.offsets.MonthEnd(1)
    business_days = pd.date_range(start=first_day_of_month, end=end_of_month, freq=bday_ca)
    
    # Check if the target day is valid
    if target_day > len(business_days):
        print(f"Skip: Month only has {len(business_days)} business days. Target {target_day} is invalid.")
        return False
        
    # The Nth business day (target_day is 1-indexed)
    nth_business_day = business_days[target_day - 1]
    
    is_target_day = today == nth_business_day
    
    if is_target_day:
        print(f"Match: Today ({today.strftime('%Y-%m-%d')}) IS Toronto Business Day #{target_day}.")
        return True
    else:
        print(f"Skip: Today ({today.strftime('%Y-%m-%d')}) is NOT Toronto Business Day #{target_day}. The target date is {nth_business_day.strftime('%Y-%m-%d')}.")
        return False

@flow(name="Master-Pipeline-Runner", log_prints=True, on_failure=[failure_email_hook], on_crashed=[failure_email_hook])
def run_script_list(scripts_to_run: list[str] = None, target_business_day: int = None):
    if target_business_day is not None:
        is_target_day = check_toronto_business_day(target_business_day)
        if not is_target_day:
            print("Exiting pipeline safely. Today is not the target business day.")
            return

    if not scripts_to_run:
        print("No scripts provided in `scripts_to_run` parameter. Exiting.")
        return
        
    for script_path in scripts_to_run:
        run_task(script_path)
