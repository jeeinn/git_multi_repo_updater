import os
import subprocess
import sys
import threading
import tkinter as tk
from tkinter import messagebox, filedialog
from datetime import datetime

class StdoutRedirector:
    def __init__(self, text_widget):
        self.text_widget = text_widget
        self.configure_tags()

    def configure_tags(self):
        self.text_widget.tag_configure('default', foreground='black')
        self.text_widget.tag_configure('success', foreground='green')
        self.text_widget.tag_configure('error', foreground='red')

    def write(self, message, tag='default'):
        if message.strip():
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
            formatted_message = f"[{timestamp}] {message}"
        else:
            formatted_message = message

        self.text_widget.insert(tk.END, formatted_message, (tag,))
        self.text_widget.see(tk.END)

    def flush(self):
        pass

def is_git_repo(path):
    try:
        result = subprocess.run(
            ['git', '-C', path, 'rev-parse', '--git-dir'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=5
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, Exception):
        return False

def get_local_branches(path):
    try:
        result = subprocess.run(
            ['git', '-C', path, 'branch', '--format=%(refname:short)'],
            capture_output=True,
            text=True
        )
        return result.stdout.strip().split('\n') if result.stdout else []
    except Exception:
        return []

def has_uncommitted_changes_or_conflicts(path):
    try:
        result = subprocess.run(
            ['git', '-C', path, 'status', '--porcelain'],
            capture_output=True,
            text=True
        )
        return bool(result.stdout.strip())
    except Exception:
        return False

def get_current_branch(path):
    try:
        result = subprocess.run(
            ['git', '-C', path, 'rev-parse', '--abbrev-ref', 'HEAD'],
            capture_output=True,
            text=True
        )
        return result.stdout.strip()
    except Exception:
        return None

def update_git_repos(root_dir, log_text):
    if not os.path.isdir(root_dir):
        sys.stderr.write(f"Error: {root_dir} is not a valid directory.\n", tag='error')
        return

    if is_git_repo(root_dir):
        update_repo(root_dir, log_text)
    else:
        for folder in os.listdir(root_dir):
            folder_path = os.path.join(root_dir, folder)
            if os.path.isdir(folder_path) and is_git_repo(folder_path):
                update_repo(folder_path, log_text)
    sys.stdout.write(f"\nUpdate Finished!\n", tag='default')

def update_repo(repo_path, log_text):
    try:
        sys.stdout.write(f"\nProcessing repository: {repo_path}\n", tag='default')
        current_branch = get_current_branch(repo_path)
        if not current_branch:
            sys.stderr.write(f"  Skipping {repo_path} due to no current branch.\n", tag='error')
            return

        if has_uncommitted_changes_or_conflicts(repo_path):
            sys.stderr.write(f"  Skipping {repo_path} due to uncommitted changes or conflicts.\n", tag='error')
            return

        branches = get_local_branches(repo_path)
        if not branches:
            sys.stderr.write(f"  No branches found in {repo_path}.\n", tag='error')
            return

        for branch in branches:
            try:
                sys.stdout.write(f"  Switching to branch: {branch}\n", tag='default')
                subprocess.run(
                    ['git', '-C', repo_path, 'checkout', branch],
                    check=True,
                    capture_output=True
                )
                sys.stdout.write(f"  Updating branch {branch}...\n", tag='default')
                result = subprocess.run(
                    ['git', '-C', repo_path, 'pull'],
                    capture_output=True,
                    text=True
                )
                if result.stderr:
                    sys.stderr.write(f"  Error: {result.stderr}\n", tag='error')
                else:
                    sys.stdout.write(f"  Successfully updated branch {branch}.\n", tag='success')
            except subprocess.CalledProcessError as e:
                sys.stderr.write(f"  Error switching to or updating branch {branch}: {e.stderr}\n", tag='error')

        sys.stdout.write(f"  Switching back to original branch: {current_branch}\n", tag='default')
        subprocess.run(
            ['git', '-C', repo_path, 'checkout', current_branch],
            check=True,
            capture_output=True
        )
    except Exception as e:
        sys.stderr.write(f"  Error processing repository {repo_path}: {e}\n", tag='error')

def select_directory(log_text, update_button):
    root_dir = filedialog.askdirectory()
    if root_dir:
        status_label.config(text=f"Selected directory: {root_dir}")
        update_button.config(state=tk.NORMAL)
        sys.stdout.write(f"\nSelected directory: {root_dir}\n", tag='default')

def run_update(root_dir, log_text, update_button):
    try:
        thread = threading.Thread(target=update_git_repos, args=(root_dir, log_text))
        thread.start()
        update_button.config(state=tk.DISABLED)
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")
    finally:
        update_button.config(state=tk.NORMAL)

def center_window(window, width, height):
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    window.geometry(f"{width}x{height}+{x}+{y}")

# Show startup information
def add_startup_info(log_text):
    author_info = "Author: Jeeinn & [AI of Kimi/Tongyi/Doubao]\n"
    project_url = "Project URL: https://github.com/jeeinn/git_multi_repo_updater\n"
    sys.stdout.write(author_info, tag='default')
    sys.stdout.write(project_url, tag='success')

# Main GUI setup
root = tk.Tk()
root.title("Git Multi Repo Updater")

window_width = 800
window_height = 600
center_window(root, window_width, window_height)

status_label = tk.Label(root, text="No directory selected.", wraplength=780, anchor="w", justify="left")
status_label.pack(pady=10, padx=10, fill=tk.X)

button_frame = tk.Frame(root)
button_frame.pack(pady=5, padx=10, fill=tk.X)

select_button = tk.Button(
    button_frame,
    text="Select Directory",
    command=lambda: select_directory(log_text, update_button),
    width=15
)
select_button.pack(side=tk.LEFT, padx=5)

update_button = tk.Button(
    button_frame,
    text="Update Repositories",
    state=tk.DISABLED,
    command=lambda: run_update(
        status_label.cget('text').split(': ')[1],
        log_text,
        update_button
    ),
    width=20
)
update_button.pack(side=tk.LEFT, padx=5)

log_text = tk.Text(
    root,
    height=15,
    width=70,
    state=tk.NORMAL,
    font=('TkDefaultFont', 10),
    wrap=tk.WORD,
    padx=10,
    pady=10
)
log_text.pack(pady=5, padx=10, fill=tk.BOTH, expand=True)

scrollbar = tk.Scrollbar(root, command=log_text.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
log_text.config(yscrollcommand=scrollbar.set)

sys.stdout = StdoutRedirector(log_text)
sys.stderr = StdoutRedirector(log_text)

# Display author and project information on startup
add_startup_info(log_text)

root.mainloop()