import win32com.client
import os
from datetime import datetime

def create_scheduled_task(task_name, app_path):
    # Get the current user's name
    current_user = os.getlogin()

    # Create Task Scheduler COM object
    scheduler = win32com.client.Dispatch('Schedule.Service')
    scheduler.Connect()

    # Get the root task folder
    rootFolder = scheduler.GetFolder("\\")

    # Create a new task definition
    task_def = scheduler.NewTask(0)

    # Set general information
    task_def.RegistrationInfo.Description = "Run Family Rules every 2 minutes"
    task_def.Principal.UserId = current_user
    task_def.Principal.LogonType = 3  # TASK_LOGON_INTERACTIVE_TOKEN

    # Set the trigger (e.g., every 2 minutes)
    trigger = task_def.Triggers.Create(1)  # 1 is for TASK_TRIGGER_TIME

    # Set the StartBoundary to the current time in ISO 8601 format
    current_time = datetime.now().isoformat()
    trigger.StartBoundary = current_time  # Set the start time to now

    trigger.Repetition.Interval = "PT2M"  # Repetition interval: PT2M means 2 minutes
    trigger.Repetition.Duration = "P10000D"   # Repeat indefinitely, with a maximum duration of 1 day

    # Set the action (e.g., Start an application)
    action = task_def.Actions.Create(0)  # 0 is for TASK_ACTION_EXEC
    action.Path = app_path

    # Set the settings (e.g., task enabled)
    task_def.Settings.Enabled = True
    task_def.Settings.StopIfGoingOnBatteries = False
    task_def.Settings.DisallowStartIfOnBatteries = False
    task_def.Settings.AllowHardTerminate = False

    # Register the task
    rootFolder.RegisterTaskDefinition(
        task_name,           # Task name
        task_def,            # Task definition
        6,                   # TASK_CREATE_OR_UPDATE
        None,                # User account to run the task
        None,                # Password (None if not required)
        3,                   # TASK_LOGON_INTERACTIVE_TOKEN
        None                 # Security descriptor (None if not needed)
    )

    print(f"Scheduled task '{task_name}' created successfully.")

# Usage example
task_name = "FamilyRulesEvery2Minutes"
app_path = r"C:\Users\user\Developer\family-rules-client\dist\Family Rules.exe"
create_scheduled_task(task_name, app_path)
