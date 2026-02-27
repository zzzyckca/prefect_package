# Prefect 3.x Local Windows Architecture

This repository contains the configuration and scripts to deploy a local-only, server-and-worker orchestration pipeline for **Prefect 3.x on Windows**. It is designed specifically to operate without Docker, WSL, or active console windows.

The `C:\prefect_package` directory acts as the **Installer Staging Area**. It fully configures and installs the operational environment directly into `C:\prefect`.

## Prerequisites

- Windows OS
- Python 3.12 (Path defined in `config.ini` by default as `C:\Program Files\Python312\python.exe`)
- `pip.ini` logic handles corporate proxy bypasses automatically.

---

## 🚀 Installation

### Customizing Your Installation (`config.ini`)

Before installing, you can open `config.ini` in this folder to change where Prefect installs and how it behaves. The defaults are:

- `PREFECT_DIR=C:\prefect` (Where the operational files will live)
- `VENV_DIR=C:\prefect\venv` (Where the isolated Python packages install)
- `PREFECT_HOME=C:\prefect\prefect_home` (Where the SQLite DB and logs are stored)
- `WORK_POOL_NAME=local-windows-pool` (The name of your background agent)
- `PYTHON_PATH=C:\Program Files\Python312\python.exe` (Your system Python executable)
- `PIP_CONFIG_FILE=C:\Program Files\Python312\pip.ini` (Your corporate proxy config)

1. Place this `prefect_package` directory anywhere on your machine.
2. Double-click **`install.bat`** from inside the package folder.

**What `install.bat` does:**

- Creates the operational directory (`C:\prefect`).
- Copies all necessary configuration files and `.bat` scripts.
- Uses your local Python installation to dynamically build a virtual environment (`C:\prefect\venv`).
- Installs the locked dependencies defined in `requirements.txt` (`prefect==3.6.19`, `prefect-email==0.4.2`, `pandas==3.0.1`, `selenium==4.41.0`, etc.).

---

## ⚙️ Operations & Execution

Once installed, all interactions happen directly out of **`C:\prefect`**.

### 1. `start.bat`

Starts the Prefect Server and Prefect Worker (`local-windows-pool`).

- **Feature**: Uses internal VBScript to launch in "Session 0". The executables run **completely invisible** in the background. No `cmd.exe` windows remain on your taskbar.

### 2. `deployment.bat`

Creates the `local-windows-pool` work pool and deploys your pipelines defined in `prefect.yaml`.

- Ensure your flow runs are correctly configured in `prefect.yaml` (e.g., Cron schedules).

### 3. `test.bat`

Manually triggers an immediate ad-hoc run of the pipeline without needing to use the Prefect UI.

### 4. `stop.bat`

Cleanly unhooks and terminates the invisible background server and worker processes.

---

## 🖥️ How to Use Prefect (Daily Operations)

Once you have run `start.bat`, the system is fully active in the background.

**Viewing the Dashboard (UI):**

1. Open your web browser (Chrome, Edge, Firefox, etc.).
2. Navigate to: [http://127.0.0.1:4200](http://127.0.0.1:4200)
3. This is your central command center. Here you can:
   - Click **Deployments** to see your active scheduled pipelines.
   - Click **Flow Runs** to see historical success/failure logs of your scripts.
   - Click **Work Pools** to verify your `local-windows-pool` is active and ready.

**Adding New Scripts/Jobs to the Pipeline:**

1. Open `C:\prefect\prefect.yaml`.
2. Locate the `deployments` section at the bottom.
3. Under the `parameters` block, simply add the full path to your new script inside the `scripts_to_run` list. **Use single quotes** so you can use normal Windows backslashes:
   ```yaml
   parameters:
     scripts_to_run:
       - 'c:\temp\temp1.py'
       - 'c:\path\to\your\new_script.py'
   ```
4. **Deploy the Change:** Double-click **`deployment.bat`** so the server registers the completely new job list!

**Adding a Completely New Deployment (New Pipeline & Schedule):**

If you want to create a brand new pipeline that runs on a completely different schedule (e.g., a weekend job vs a daily job), you can add a second deployment block to `prefect.yaml`:

1. Open `C:\prefect\prefect.yaml`.
2. Scroll to the bottom of the `deployments` list.
3. Copy and paste the entire existing deployment block, then change the `name`, `cron` schedule, and the `scripts_to_run` list for your new pipeline.
   **(Note: Ensure `entrypoint` is always set to `"master_pipeline.py:run_script_list"` as this is the generic controller!)**
   ```yaml
   - name: "weekend-historical-deployment"
     entrypoint: "master_pipeline.py:run_script_list"
     parameters:
       scripts_to_run:
         - 'd:\historical_data\weekend_report.py'
     work_pool:
       name: "local-windows-pool"
     schedules:
       - cron: "0 12 * * 6,0"
         timezone: "America/Toronto"
   ```
4. **Deploy the Change:** Double-click **`deployment.bat`**. Both the old and new deployment will now appear in your Prefect UI!

**Updating the Schedule & Pipeline Name:**

1. Open `C:\prefect\prefect.yaml`.
2. Locate the `deployments` section at the bottom.
3. You can change the `name` of the deployment here.
4. To change when the pipeline runs, modify the `cron` string under `schedules` (e.g., `"0 12 * * *"` runs it at noon).
5. **CRUCIAL:** After making any changes to `prefect.yaml` or `master_pipeline.py`, you **MUST double-click `deployment.bat`** to push the changes live to the server!

**Checking Logs:**

- If a pipeline fails, open the Prefect Dashboard URL, click the failed Flow Run, and click the **Logs** tab. It will show you exactly which script crashed and print its Python error output.

---

## 📂 Architecture Rules (The "Never Do This" List)

This infrastructure was explicitly designed around strict Prefect 3.x constraints to avoid SQLite locking and profile-corruption issues on Windows:

1. **Deployment Architecture**: `.deploy()` or `.serve()` are **never** used inside the Python files. Deployment definitions live completely in `prefect.yaml`.
2. **Environment Isolation**: `PREFECT_HOME` is injected strictly at runtime via the `.bat` wrapper scripts. We **never** use `prefect config set` on the host machine.
3. **Pure Execution**: Server and Worker instances are kept strictly separate (`prefect server start` vs `prefect worker start`). `server services start` is disabled.
4. **Local Parsing**: `prefect.yaml` utilizes an absolute directory path for the `set_working_directory` pull step to avoid literal string parsing bugs in prior minor versions.
