import os
import requests
import schedule
import time
from datetime import datetime
import tkinter as tk
from tkinter import filedialog, messagebox
import sys

def read_file():
    root = tk.Tk()
    root.withdraw()
    
    file_path = filedialog.askopenfilename(title="Select a text file for GitHub token", filetypes=[("Text files", "*.txt")])
    if not file_path:
        print("No file selected. Exiting...")
        sys.exit()
    
    with open(file_path, "r", encoding="utf-8") as file:
        token = file.read().strip()
    return token

GITHUB_TOKEN = read_file()

GITHUB_USERNAME = input("Enter your GitHub username: ").strip()
GIT_EMAIL = input("Enter your email: ").strip()
GIT_NAME = input("Enter your name: ").strip()

HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

def select_directory(day):
    root = tk.Tk()
    root.withdraw()
    
    directory = filedialog.askdirectory(title=f"Select a directory for {day}")
    if not directory:
        print("No directory selected. Exiting...")
        sys.exit()
    return directory

def parse_days(day_input):
    days_of_week = ["sunday", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday"]
    selected_days = set()
    
    parts = [day.strip().lower() for day in day_input.split(" to ")]
    if len(parts) == 1:
        if parts[0] in days_of_week:
            selected_days.add(parts[0])
    elif len(parts) == 2:
        start, end = parts
        if start in days_of_week and end in days_of_week:
            start_idx = days_of_week.index(start)
            end_idx = days_of_week.index(end)
            if start_idx <= end_idx:
                selected_days.update(days_of_week[start_idx:end_idx+1])
            else:
                selected_days.update(days_of_week[start_idx:] + days_of_week[:end_idx+1])
    return list(selected_days)

def get_schedule():
    num_days = int(input("Enter the number of days you want to schedule uploads (1-7): ").strip())
    scheduled_days = {}
    
    for _ in range(num_days):
        day_input = input("Enter a day (or range like 'Friday to Monday'): ").strip()
        valid_days = parse_days(day_input)
        for day in valid_days:
            if day not in scheduled_days:
                scheduled_days[day] = {
                    "directory": select_directory(day),
                    "time": input(f"Enter the upload time for {day} (HH:MM 24-hour format): ").strip()
                }
    return scheduled_days


def get_repo_visibility():
    while True:
        visibility = input("Enter whether you want your repository to be Private or Public: ").strip().lower()
        if visibility in ["private", "p"]:
            return True
        elif visibility in ["public", "pub"]:
            return False
        else:
            print("Invalid input. Please enter 'Private' or 'Public'.")

def create_github_repo(repo_name):
    is_private = get_repo_visibility()
    print(f"Creating repository: {repo_name}")
    data = {"name": repo_name, "private": is_private}
    response = requests.post("https://api.github.com/user/repos", json=data, headers=HEADERS)
    if response.status_code == 201:
        print(f"Repository '{repo_name}' created successfully!")
        return True
    elif response.status_code == 422:
        print(f"Repository '{repo_name}' already exists.")
        return True
    else:
        print(f"Error: {response.json()}")
        return False

def push_to_github(directory, repo_name):
    os.chdir(directory)
    repo_url = f"https://github.com/{GITHUB_USERNAME}/{repo_name}.git"
    os.system(f'git config user.email "{GIT_EMAIL}"')
    os.system(f'git config user.name "{GIT_NAME}"')
    
    if not os.path.exists(os.path.join(directory, ".git")):
        os.system("git init")
    
    remote_check = os.popen("git remote").read().strip()
    if "origin" in remote_check:
        os.system(f"git remote set-url origin {repo_url}")
    else:
        os.system(f"git remote add origin {repo_url}")
    
    os.system("git add .")
    os.system('git commit -m "Automated upload via script"')
    branch_check = os.popen("git branch").read().strip()
    if "main" not in branch_check:
        os.system("git branch -M main")
    os.system("git push -u origin main")
    
    messagebox.showinfo("Upload Complete", f"Code pushed to {repo_url}")
    print(f"Code pushed to {repo_url}")

def automate_upload(day):
    if day in SCHEDULED_TASKS:
        directory = SCHEDULED_TASKS[day]["directory"]
        repo_name = os.path.basename(directory).replace(" ", "_")
        print(f"Starting upload process for {day.capitalize()} at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        if create_github_repo(repo_name):
            time.sleep(2)
            push_to_github(directory, repo_name)
            print(f"Upload completed for {day.capitalize()}!")
        else:
            print(f"Upload failed for {day.capitalize()}.")

def schedule_tasks():
    for day, details in SCHEDULED_TASKS.items():
        schedule.every().day.at(details["time"]).do(lambda d=day: automate_upload(d))
        print(f"Scheduled upload for {day.capitalize()} at {details['time']}")

def main():
    global SCHEDULED_TASKS
    SCHEDULED_TASKS = get_schedule()
    schedule_tasks()
    print("Scheduler is running... (Press Ctrl+C to stop)")
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)
    except KeyboardInterrupt:
        print("\nScheduler stopped by user.")
    
    while True:
        response = messagebox.askyesno("Upload More?", "Do you want to upload more repositories?")
        if response:
            main()
        else:
            sys.exit()

if __name__ == "__main__":
    main()
