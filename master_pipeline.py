import os
import subprocess
import configparser
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

@flow(name="Daily-Pipeline", log_prints=True, on_failure=[failure_email_hook], on_crashed=[failure_email_hook])
def run_script_list(scripts_to_run: list[str] = None):
    if not scripts_to_run:
        print("No scripts provided in `scripts_to_run` parameter. Exiting.")
        return
        
    for script_path in scripts_to_run:
        run_task(script_path)
