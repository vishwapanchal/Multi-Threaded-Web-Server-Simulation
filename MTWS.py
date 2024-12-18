import threading
import time
import random
import tkinter as tk
from tkinter import ttk

# Simulation parameters
REQUESTS = 20
MAX_PROCESS_TIME = 5

# Shared resources
request_queue = []
queue_lock = threading.Lock()
processed_requests = []
abort_simulation = False

# Tkinter GUI components
root = tk.Tk()
root.title("Multithreaded Web Server Simulation")
root.geometry("1000x700")

# Frames
queue_frame = ttk.LabelFrame(root, text="Request Queue", width=200, height=300)
queue_frame.place(x=50, y=50)
threads_frame = ttk.LabelFrame(root, text="Threads Processing", width=700, height=300)
threads_frame.place(x=300, y=50)
processed_frame = ttk.LabelFrame(root, text="Processed Requests", width=900, height=300)
processed_frame.place(x=50, y=400)

# Widgets for Request Queue
queue_listbox = tk.Listbox(queue_frame, width=25, height=15, bg="lightblue")
queue_listbox.pack(padx=10, pady=10)

# Widgets for Threads
thread_stacks = {}
progress_bars = {}
for i in range(5):
    thread_frame = ttk.LabelFrame(threads_frame, text=f"Thread-{i+1}", width=120, height=250)
    thread_frame.grid(row=0, column=i, padx=10, pady=10)
    stack_listbox = tk.Listbox(thread_frame, width=15, height=10, bg="lightgreen")
    stack_listbox.pack()
    thread_stacks[i] = stack_listbox
    progress = ttk.Progressbar(thread_frame, orient='horizontal', length=100, mode='determinate')
    progress.pack()
    progress_bars[i] = progress


# Widgets for Processed Requests
processed_listbox = tk.Listbox(processed_frame, width=100, height=15, bg="lightyellow")
processed_listbox.pack(padx=10, pady=10)

# Dropdown for scheduling algorithm selection
algorithm_var = tk.StringVar(value="FCFS")
algorithm_menu = ttk.Combobox(root, textvariable=algorithm_var, values=["FCFS", "SJF"])
algorithm_menu.place(x=450, y=10)

# Labels for queue length and average time
queue_length_label = ttk.Label(root, text="Queue Length: 0")
queue_length_label.place(x=50, y=10)
average_time_label = ttk.Label(root, text="Average Time: 0s")
average_time_label.place(x=200, y=10)

# Function to log activity
def log_activity(message):
    pass  # No activity log anymore

# Function to update queue length
def update_queue_length():
    queue_length_label.config(text=f"Queue Length: {len(request_queue)}")

# Function to update average processing time
def update_average_time():
    if processed_requests:
        avg_time = sum(req[2] for req in processed_requests) / len(processed_requests)
        average_time_label.config(text=f"Average Time: {avg_time:.2f}s")

# Simulation setup
def setup_requests():
    global request_queue
    request_queue = [(f"Request-{i}", random.randint(1, MAX_PROCESS_TIME)) for i in range(REQUESTS)]
    for request, process_time in request_queue:
        queue_listbox.insert(tk.END, f"{request} (Time: {process_time}s)")
    update_queue_length()

# Thread function to process requests
def handle_request(thread_id):
    while request_queue and not abort_simulation:
        queue_lock.acquire()
        if request_queue:
            if algorithm_var.get() == "SJF":
                # Sort the queue by process time for SJF
                request_queue.sort(key=lambda x: x[1])
            request, process_time = request_queue.pop(0)
            queue_lock.release()
            
            # Add to thread stack
            thread_stacks[thread_id].insert(0, request)
            progress_bars[thread_id].start(process_time * 100)

            log_activity(f"Thread-{thread_id} processing request {request} for {process_time} seconds.")
            time.sleep(process_time)

            # Remove from thread stack
            thread_stacks[thread_id].delete(0)
            progress_bars[thread_id].stop()

            # Add to processed list
            processed_requests.append((thread_id, request, process_time))
            processed_listbox.insert(tk.END, f"{request} by Thread-{thread_id+1} in {process_time}s")
            update_average_time()
        else:
            queue_lock.release()

# Start simulation in a separate thread
def start_simulation_thread():
    threads = []
    for i in range(5):  # 5 threads
        t = threading.Thread(target=handle_request, args=(i,))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

def start_simulation():
    global abort_simulation
    abort_simulation = False
    simulation_thread = threading.Thread(target=start_simulation_thread)
    simulation_thread.start()

# Abort simulation
def abort_simulation_func():
    global abort_simulation
    abort_simulation = True

# Generate report
def generate_report():
    with open("simulation_report.txt", "w") as file:
        for req in processed_requests:
            file.write(f"Request: {req[1]}, Time: {req[2]}s\n")
    log_activity("Report generated.")

setup_requests()

# Start button
start_button = ttk.Button(root, text="Start Simulation", command=start_simulation)
start_button.place(x=450, y=350)

# Abort button
abort_button = ttk.Button(root, text="Abort Simulation", command=abort_simulation_func)
abort_button.place(x=600, y=350)

# Report button (aligned with abort button)
report_button = ttk.Button(root, text="Generate Report", command=generate_report)
report_button.place(x=750, y=350)  # Adjusted position to align with abort_button

root.mainloop()
