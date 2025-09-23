import os
import subprocess

# Path to the folder containing your apps
APPS_FOLDER = "./apps"

def get_app_names(apps_folder):
    """Return a list of all folders in the apps directory."""
    return [
        name for name in os.listdir(apps_folder)
        if os.path.isdir(os.path.join(apps_folder, name))
    ]

def run_app(app_name):
    """Run a Databricks app via the CLI."""
    print(f"Running app: {app_name}")
    result = subprocess.run(
        ["databricks", "bundle", "run", app_name],
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        print(f"App {app_name} failed:\n{result.stderr}")
        return False
    else:
        print(f"App {app_name} succeeded:\n{result.stdout}")
        return True

def main():
    apps = get_app_names(APPS_FOLDER)
    all_passed = True
    for app in apps:
        success = run_app(app)
        if not success:
            all_passed = False

    if not all_passed:
        raise SystemExit("Some apps failed. See output above.")
    else:
        print("All apps ran successfully.")

if __name__ == "__main__":
    main()
