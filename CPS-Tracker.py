from tkinter import Tk, Label, StringVar, OptionMenu, Canvas, Scrollbar, Frame, Button, Entry
import time
import csv
import json
import os

# Functions to Save and Load Profile
def save_profile(username):
    profile_data = {'username': username}
    with open('user_profile.json', 'w') as f:
        json.dump(profile_data, f)

def load_profile():
    if os.path.exists('user_profile.json'):
        with open('user_profile.json', 'r') as f:
            profile_data = json.load(f)
            return profile_data['username']
    else:
        return None

def update_username():
    global username, username_label
    new_username = username_entry.get()
    if new_username:
        username = new_username
        username_label.config(text=f"Welcome, {username}")
        save_profile(username)

# Initialize the Tkinter window
root = Tk()
root.title("CPS Tracker")
root.geometry("600x800")

# Load or Create Profile
username = load_profile()
if username is None:
    username = "Who are you!"
    save_profile(username)

# Welcome label
username_label = Label(root, text=f"Welcome, {username}")
username_label.pack(pady=5)

username_entry = Entry(root)
username_entry.pack(pady=5)
username_entry.insert(0, username)

username_button = Button(root, text="Update Username", command=update_username)  # Now it knows what update_username is
username_button.pack(pady=5)

# Initialize variables
click_count = 0
timer_var = StringVar(root)
timer_var.set("10")  # Default value for timer dropdown
cps_history = []
is_test_running = False
cooldown_time = 0
cooldown_duration = 3
cooldown_timer_text = None

# Calculate Statistics
def calculate_statistics():
    total_clicks = 0
    total_tests = len(cps_history)
    highest_cps = 0
    
    for cps, _ in cps_history:
        total_clicks += cps
        highest_cps = max(highest_cps, cps)
        
    average_cps = total_clicks / total_tests if total_tests > 0 else 0
    
    statistics_label.config(text=f"Average CPS: {average_cps}\nHighest CPS: {highest_cps}\nTotal Clicks: {total_clicks}\nTotal Tests: {total_tests}")

# Export Data
def export_data():
    with open('cps_history.csv', 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        
        # Writing the header
        csvwriter.writerow(["Test Number", "CPS", "Duration"])
        
        for i, (cps, duration) in enumerate(cps_history):
            csvwriter.writerow([i+1, cps, duration])


# Event Handlers
def on_circle_click(event):
    global click_count, is_test_running, cooldown_time
    current_time = time.time()
    if current_time < cooldown_time:
        return  # Do not start a new test during cooldown

    if not is_test_running:
        is_test_running = True
        start_timer(int(timer_var.get()))
    click_count += 1
    cps_label.config(text=f"CPS: {click_count}")

def start_timer(duration):
    global click_count
    click_count = 0  # Reset click count
    update_progress_bar(duration, duration)
    root.after(duration * 1000, calculate_cps)  # Schedule the CPS calculation

def update_progress_bar(time_left, duration):
    if time_left >= 0:
        clock_label.config(text=f"{time_left}s")
        canvas_progress.delete("progress")
        canvas_progress.create_rectangle(10, 10, 10 + ((duration - time_left) / duration) * 180, 30, fill="green", tags="progress")
        root.after(1000, update_progress_bar, time_left - 1, duration)

# Function to handle cooldown countdown
def start_cooldown_timer():
    global cooldown_timer_text, cooldown_time
    remaining_time = int(cooldown_time - time.time())
    if remaining_time >= 0:
        if cooldown_timer_text:
            canvas.delete(cooldown_timer_text)
        cooldown_timer_text = canvas.create_text(100, 100, text=str(remaining_time), font=("Arial", 44), fill="white")
        root.after(900, start_cooldown_timer)  # Schedule the next update after 1 second
    else:
        if cooldown_timer_text:
            canvas.delete(cooldown_timer_text)
        cooldown_time = 0  # Reset cooldown_time to allow new tests to start

def calculate_cps():
    global is_test_running, cooldown_time
    cps = click_count  # In a simple implementation, CPS will be the same as click count
    cps_history.append((cps, timer_var.get()))  # Add to history as a tuple (cps, duration)
    update_history()  # Update history display
    calculate_statistics()  # Update statistics
    is_test_running = False  # Reset test status flag
    cooldown_time = time.time() + cooldown_duration  # Set the cooldown time
    start_cooldown_timer()  # Start the cooldown countdown timer

# Export Button
export_button = Button(root, text="Export Data", command=export_data)
export_button.pack(pady=10)

def update_history():
    history_str = "\n".join([f"Test {i+1}: {cps} CPS (Duration: {duration}s)" for i, (cps, duration) in enumerate(cps_history)])
    history_label.config(text=f"History:\n{history_str}")

# Create and place widgets
Label(root, text="Clicks Per Second (CPS) Tracker").pack(pady=10)
OptionMenu(root, timer_var, "10", "15", "30", "60").pack(pady=5)
cps_label = Label(root, text="CPS: 0")
cps_label.pack(pady=10)
clock_label = Label(root, text="0s")
clock_label.pack(pady=5)

# Canvas for circle
canvas = Canvas(root, width=200, height=200)
canvas.pack(pady=5)
circle = canvas.create_oval(50, 50, 150, 150, fill="blue")
canvas.tag_bind(circle, '<ButtonPress-1>', on_circle_click)

# Statistics Label
statistics_label = Label(root, text="Statistics will appear here")
statistics_label.pack(pady=10)

# Progress Bar
canvas_progress = Canvas(root, width=200, height=40)
canvas_progress.pack(pady=5)


# New Frame to hold the history Canvas and Scrollbar
history_frame_container = Frame(root)
history_frame_container.pack(side="bottom", fill="both", expand=True)

# Scrollable history Canvas
history_canvas = Canvas(history_frame_container)
history_canvas.pack(side="left", fill="both", expand=True)

# Scrollbar for history
scrollbar = Scrollbar(history_frame_container, orient="vertical", command=history_canvas.yview)
scrollbar.pack(side="right", fill="y")

history_canvas.configure(yscrollcommand=scrollbar.set)

# Internal Frame to hold the history labels
history_frame = Frame(history_canvas)
history_canvas.create_window((0, 0), window=history_frame, anchor="nw")

# Update the history function to populate the frame and set scroll region
def update_history():
    for widget in history_frame.winfo_children():
        widget.destroy()

    for i, (cps, duration) in enumerate(cps_history):
        Label(history_frame, text=f"Test {i+1}: {cps} CPS (Duration: {duration}s)").pack(anchor="w")

    history_frame.update_idletasks()  # Update and redraw inner frame
    history_canvas.config(scrollregion=history_canvas.bbox("all"))  # Update scroll region

root.mainloop()