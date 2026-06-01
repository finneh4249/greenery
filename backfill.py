#!/usr/bin/env python3
import os
import random
import subprocess
import datetime

# Import list of fortunes from fortune.py or define locally
from fortune import fortunes

def run_git_command(args, env=None):
    current_env = os.environ.copy()
    if env:
        current_env.update(env)
    result = subprocess.run(args, env=current_env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return result

def main():
    start_date = datetime.date(2020, 1, 1)
    end_date = datetime.date(2020, 12, 31)
    
    delta = end_date - start_date
    total_days = delta.days
    
    print(f"Generating backdated commits from {start_date} to {end_date} ({total_days} days)...")
    
    commits_count = 0
    
    # Iterate through each day
    for i in range(total_days + 1):
        current_day = start_date + datetime.timedelta(days=i)
        
        # Decide if we commit on this day (weekday vs weekend)
        is_weekend = current_day.weekday() >= 5
        probability = 0.25 if is_weekend else 0.70
        
        if random.random() > probability:
            continue
            
        # Determine number of commits for the day
        num_commits = random.randint(1, 4) if not is_weekend else random.randint(1, 2)
        
        for _ in range(num_commits):
            # Generate a random time during active hours (08:00 to 22:00)
            hour = random.randint(8, 21)
            minute = random.randint(0, 59)
            second = random.randint(0, 59)
            
            commit_time = datetime.datetime.combine(current_day, datetime.time(hour, minute, second))
            date_str = commit_time.isoformat()
            
            # Select a random fortune
            fortune_msg = random.choice(fortunes)
            if len(fortune_msg) > 32:
                # Truncate or use a short subset for commit msg if desired, or just use the fortune
                pass
            
            # Update file.txt
            with open("file.txt", "w") as f:
                f.write(fortune_msg + "\n")
                
            # Git add
            run_git_command(["git", "add", "file.txt"])
            
            # Git commit with backdated environment variables
            env = {
                "GIT_AUTHOR_DATE": date_str,
                "GIT_COMMITTER_DATE": date_str
            }
            commit_res = run_git_command(["git", "commit", "-m", fortune_msg], env=env)
            if commit_res.returncode == 0:
                commits_count += 1
                
        if i % 100 == 0:
            print(f"Processed day {i}/{total_days}... (Total commits: {commits_count})")
            
    print(f"Finished! Created {commits_count} backdated commits.")
    print("Run 'git push origin master' to push them to GitHub.")

if __name__ == "__main__":
    main()
