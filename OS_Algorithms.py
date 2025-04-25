import tkinter as tk
from tkinter import ttk, messagebox
from collections import deque
import math

class SchedulerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CPU Scheduling Simulator")

        # Initialize variables
        self.selected_algorithm = tk.StringVar()
        self.num_processes = tk.IntVar()
        self.time_quantum = tk.IntVar()

        # Define scheduling algorithms
        self.algorithms = [
            "First-Come, First-Served (FCFS)",
            "Non-Preemptive Shortest Job First (SJF)",
            "Preemptive Shortest Job First (SJF)",
            "Non-Preemptive Priority Scheduling",
            "Preemptive Priority Scheduling",
            "Round Robin"
        ]

        # Top Frame for Algorithm Selection and Number of Processes
        top_frame = tk.Frame(root)
        top_frame.pack(pady=10)

        tk.Label(top_frame, text="Select Scheduling Algorithm:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.algorithm_menu = ttk.Combobox(top_frame, textvariable=self.selected_algorithm, values=self.algorithms, state="readonly", width=40)
        self.algorithm_menu.grid(row=0, column=1, padx=5, pady=5)
        self.algorithm_menu.bind("<<ComboboxSelected>>", self.update_fields)

        tk.Label(top_frame, text="Number of Processes:").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.num_entry = tk.Entry(top_frame, textvariable=self.num_processes)
        self.num_entry.grid(row=1, column=1, padx=5, pady=5, sticky='w')

        self.enter_button = tk.Button(top_frame, text="Enter Processes", command=self.enter_processes)
        self.enter_button.grid(row=2, column=0, columnspan=2, pady=10)

        # Frame for Process Entries
        self.process_frame = tk.Frame(root)
        self.process_frame.pack(pady=10)

        # Calculate & Simulate Button
        self.calculate_button = tk.Button(root, text="Calculate & Simulate", command=self.calculate)
        self.calculate_button.pack(pady=10)

        # Frame for Results
        self.result_frame = tk.Frame(root)
        self.result_frame.pack(pady=10)

        tk.Label(self.result_frame, text="Scheduling Results:").pack()
        self.result_text = tk.Text(self.result_frame, width=100, height=15, state='disabled')
        self.result_text.pack()

        # Canvas for Gantt Chart
        self.canvas = tk.Canvas(root, width=800, height=150, bg="white")
        self.canvas.pack(pady=10)

    def update_fields(self, event=None):
        """
        Update the input fields based on the selected algorithm.
        Show or hide Priority and Time Quantum fields.
        """
        algorithm = self.selected_algorithm.get()
        # Determine if Priority is needed
        if "Priority" in algorithm:
            self.priority_required = True
        else:
            self.priority_required = False

        # Determine if Time Quantum is needed
        if "Round Robin" in algorithm:
            self.time_quantum_required = True
        else:
            self.time_quantum_required = False

    def enter_processes(self):
        """
        Generate input fields for entering process details based on the number of processes.
        """
        # Clear previous process entries
        for widget in self.process_frame.winfo_children():
            widget.destroy()

        try:
            n = self.num_processes.get()
            if n <= 0:
                raise ValueError
        except:
            messagebox.showerror("Input Error", "Please enter a valid positive integer for the number of processes.")
            return

        # Define headers
        headers = ["Process ID", "Arrival Time", "Burst Time"]
        if hasattr(self, 'priority_required') and self.priority_required:
            headers.append("Priority")
        if hasattr(self, 'time_quantum_required') and self.time_quantum_required:
            headers.append("Time Quantum")

        for idx, header in enumerate(headers):
            tk.Label(self.process_frame, text=header, font=('Arial', 10, 'bold')).grid(row=0, column=idx, padx=5, pady=5)

        self.process_entries = []
        for i in range(n):
            process_id = f"P{i+1}"
            tk.Label(self.process_frame, text=process_id).grid(row=i+1, column=0, padx=5, pady=5)
            arrival_entry = tk.Entry(self.process_frame, width=10)
            arrival_entry.grid(row=i+1, column=1, padx=5, pady=5)
            burst_entry = tk.Entry(self.process_frame, width=10)
            burst_entry.grid(row=i+1, column=2, padx=5, pady=5)
            if hasattr(self, 'priority_required') and self.priority_required:
                priority_entry = tk.Entry(self.process_frame, width=10)
                priority_entry.grid(row=i+1, column=3, padx=5, pady=5)
            else:
                priority_entry = None
            if hasattr(self, 'time_quantum_required') and self.time_quantum_required:
                tq_entry = tk.Entry(self.process_frame, width=10)
                tq_entry.grid(row=i+1, column=len(headers)-1, padx=5, pady=5)
            else:
                tq_entry = None
            self.process_entries.append({
                "id": process_id,
                "arrival": arrival_entry,
                "burst": burst_entry,
                "priority": priority_entry,
                "time_quantum": tq_entry
            })

    def calculate(self):
        """
        Perform scheduling based on the selected algorithm and display the results and Gantt chart.
        """
        algorithm = self.selected_algorithm.get()
        if not algorithm:
            messagebox.showerror("Selection Error", "Please select a scheduling algorithm.")
            return

        try:
            processes = []
            for entry in self.process_entries:
                pid = entry["id"]
                arrival = int(entry["arrival"].get())
                burst = int(entry["burst"].get())
                if self.priority_required:
                    priority = int(entry["priority"].get())
                else:
                    priority = None
                if self.time_quantum_required:
                    time_quantum = int(entry["time_quantum"].get())
                else:
                    time_quantum = None
                processes.append({
                    "pid": pid,
                    "arrival": arrival,
                    "burst": burst,
                    "priority": priority,
                    "time_quantum": time_quantum
                })

            # Depending on the algorithm, call the appropriate scheduling function
            if algorithm == "First-Come, First-Served (FCFS)":
                result = self.fcfs_scheduling(processes)
            elif algorithm == "Non-Preemptive Shortest Job First (SJF)":
                result = self.non_preemptive_sjf(processes)
            elif algorithm == "Preemptive Shortest Job First (SJF)":
                result = self.preemptive_sjf(processes)
            elif algorithm == "Non-Preemptive Priority Scheduling":
                result = self.non_preemptive_priority(processes)
            elif algorithm == "Preemptive Priority Scheduling":
                result = self.preemptive_priority(processes)
            elif algorithm == "Round Robin":
                if any(p["time_quantum"] is None for p in processes):
                    # If time quantum not entered per process, take a single time quantum
                    time_quantum = self.prompt_time_quantum()
                    if time_quantum is None:
                        return
                    for p in processes:
                        p["time_quantum"] = time_quantum
                result = self.round_robin_scheduling(processes)
            else:
                messagebox.showerror("Algorithm Error", "Selected algorithm is not supported.")
                return

            # Display results
            self.display_results(result)

            # Draw Gantt chart
            self.draw_gantt_chart(result["gantt_chart"])

        except ValueError:
            messagebox.showerror("Input Error", "Please enter valid integer values for all fields.")

    def prompt_time_quantum(self):
        """
        Prompt the user to enter a single time quantum for Round Robin if not provided per process.
        """
        def set_time_quantum():
            try:
                tq = int(tq_entry.get())
                if tq <= 0:
                    raise ValueError
                self.time_quantum_value = tq
                popup.destroy()
            except:
                messagebox.showerror("Input Error", "Please enter a valid positive integer for Time Quantum.")

        popup = tk.Toplevel(self.root)
        popup.title("Time Quantum")
        tk.Label(popup, text="Enter Time Quantum:").pack(pady=5)
        tq_entry = tk.Entry(popup)
        tq_entry.pack(pady=5)
        tk.Button(popup, text="OK", command=set_time_quantum).pack(pady=5)
        popup.grab_set()
        self.root.wait_window(popup)
        return getattr(self, 'time_quantum_value', None)

    def display_results(self, result):
        """
        Display the scheduling results in the Text widget.
        """
        self.result_text.config(state='normal')
        self.result_text.delete(1.0, tk.END)

        headers = ["Process", "Arrival", "Burst"]
        if "Priority" in result:
            headers.append("Priority")
        headers += ["Waiting Time", "Turnaround Time", "Response Time"]

        header_line = "".join(f"{h:<15}" for h in headers)
        self.result_text.insert(tk.END, header_line + "\n")
        self.result_text.insert(tk.END, "-" * (15 * len(headers)) + "\n")

        for p in result["processes"]:
            line = f"{p['pid']:<15}{p['arrival']:<15}{p['burst']:<15}"
            if "Priority" in result:
                line += f"{p['priority']:<15}"
            line += f"{p['waiting_time']:<15}{p['turnaround_time']:<15}{p['response_time']:<15}\n"
            self.result_text.insert(tk.END, line)

        # Display averages
        self.result_text.insert(tk.END, "\n")
        self.result_text.insert(tk.END, f"Average Waiting Time: {result['avg_waiting_time']:.2f}\n")
        self.result_text.insert(tk.END, f"Average Turnaround Time: {result['avg_turnaround_time']:.2f}\n")
        self.result_text.insert(tk.END, f"Average Response Time: {result['avg_response_time']:.2f}\n")

        self.result_text.config(state='disabled')

    def draw_gantt_chart(self, gantt_chart):
        """
        Draw the Gantt chart on the Canvas widget.
        """
        self.canvas.delete("all")
        if not gantt_chart:
            return

        # Calculate total time
        total_time = len(gantt_chart)

        # Define canvas dimensions
        canvas_width = 800
        canvas_height = 200
        chart_height = 100
        unit_width = (canvas_width - 100) / total_time  # Leave some margin

        # Draw Gantt chart blocks
        current_x = 50
        for idx, pid in enumerate(gantt_chart):
            color = self.get_color(pid)
            self.canvas.create_rectangle(current_x, 50, current_x + unit_width, 100, fill=color, outline="black")
            self.canvas.create_text(current_x + unit_width / 2, 75, text=pid, fill="black")
            current_x += unit_width

        # Draw timeline
        self.canvas.create_line(50, 100, canvas_width - 50, 100, fill="black")
        current_x = 50
        for t in range(total_time + 1):
            x = current_x + t * unit_width
            self.canvas.create_line(x, 100, x, 110, fill="black")
            self.canvas.create_text(x, 120, text=str(t), fill="black")

    def get_color(self, pid):
        """
        Generate a unique color for each process based on its ID.
        """
        colors = {
            "Idle": "lightgrey",
            "P1": "lightblue",
            "P2": "lightgreen",
            "P3": "lightpink",
            "P4": "orange",
            "P5": "violet",
            "P6": "cyan",
            "P7": "yellow",
            "P8": "magenta",
            "P9": "brown",
            "P10": "purple"
        }
        return colors.get(pid, "white")

    # Scheduling Algorithms

    def fcfs_scheduling(self, processes):
        """
        First-Come, First-Served Scheduling.
        """
        processes.sort(key=lambda x: x['arrival'])
        current_time = 0
        gantt_chart = []
        for p in processes:
            if current_time < p['arrival']:
                # CPU is idle
                idle_time = p['arrival'] - current_time
                gantt_chart.extend(["Idle"] * idle_time)
                current_time = p['arrival']
            p['start_time'] = current_time
            p['completion_time'] = current_time + p['burst']
            p['turnaround_time'] = p['completion_time'] - p['arrival']
            p['waiting_time'] = p['start_time'] - p['arrival']
            p['response_time'] = p['waiting_time']
            gantt_chart.extend([p['pid']] * p['burst'])
            current_time += p['burst']

        # Calculate averages
        total_waiting = sum(p['waiting_time'] for p in processes)
        total_turnaround = sum(p['turnaround_time'] for p in processes)
        total_response = sum(p['response_time'] for p in processes)
        n = len(processes)
        avg_waiting = total_waiting / n
        avg_turnaround = total_turnaround / n
        avg_response = total_response / n

        return {
            "processes": processes,
            "gantt_chart": gantt_chart,
            "avg_waiting_time": avg_waiting,
            "avg_turnaround_time": avg_turnaround,
            "avg_response_time": avg_response
        }

    def non_preemptive_sjf(self, processes):
        """
        Non-Preemptive Shortest Job First Scheduling.
        """
        n = len(processes)
        completed = 0
        current_time = 0
        gantt_chart = []
        is_completed = [False] * n

        while completed != n:
            idx = -1
            mn = math.inf
            for i in range(n):
                if processes[i]['arrival'] <= current_time and not is_completed[i]:
                    if processes[i]['burst'] < mn:
                        mn = processes[i]['burst']
                        idx = i
                    elif processes[i]['burst'] == mn:
                        if processes[i]['arrival'] < processes[idx]['arrival']:
                            idx = i
            if idx != -1:
                p = processes[idx]
                if current_time < p['arrival']:
                    # CPU is idle
                    idle_time = p['arrival'] - current_time
                    gantt_chart.extend(["Idle"] * idle_time)
                    current_time = p['arrival']
                p['start_time'] = current_time
                p['completion_time'] = current_time + p['burst']
                p['turnaround_time'] = p['completion_time'] - p['arrival']
                p['waiting_time'] = p['start_time'] - p['arrival']
                p['response_time'] = p['waiting_time']
                gantt_chart.extend([p['pid']] * p['burst'])
                current_time += p['burst']
                is_completed[idx] = True
                completed += 1
            else:
                gantt_chart.append("Idle")
                current_time += 1

        # Calculate averages
        total_waiting = sum(p['waiting_time'] for p in processes)
        total_turnaround = sum(p['turnaround_time'] for p in processes)
        total_response = sum(p['response_time'] for p in processes)
        avg_waiting = total_waiting / n
        avg_turnaround = total_turnaround / n
        avg_response = total_response / n

        return {
            "processes": processes,
            "gantt_chart": gantt_chart,
            "avg_waiting_time": avg_waiting,
            "avg_turnaround_time": avg_turnaround,
            "avg_response_time": avg_response
        }

    def preemptive_sjf(self, processes):
        """
        Preemptive Shortest Job First Scheduling (Shortest Remaining Time First).
        """
        n = len(processes)
        remaining_burst = [p['burst'] for p in processes]
        completed = 0
        current_time = 0
        minm = math.inf
        shortest = None
        finish_time = 0
        gantt_chart = []
        is_completed = [False] * n

        while completed != n:
            for i in range(n):
                if (processes[i]['arrival'] <= current_time and
                    remaining_burst[i] < minm and remaining_burst[i] > 0):
                    minm = remaining_burst[i]
                    shortest = i
            if shortest is None:
                gantt_chart.append("Idle")
                current_time += 1
                continue
            remaining_burst[shortest] -= 1
            minm = remaining_burst[shortest]
            if minm == 0:
                minm = math.inf
            gantt_chart.append(processes[shortest]['pid'])
            if remaining_burst[shortest] == 0:
                finish_time = current_time + 1
                processes[shortest]['completion_time'] = finish_time
                processes[shortest]['turnaround_time'] = finish_time - processes[shortest]['arrival']
                processes[shortest]['waiting_time'] = processes[shortest]['turnaround_time'] - processes[shortest]['burst']
                processes[shortest]['response_time'] = processes[shortest]['start_time'] - processes[shortest]['arrival'] if 'start_time' in processes[shortest] else 0
                is_completed[shortest] = True
                completed += 1
            if remaining_burst[shortest] > 0 and not 'start_time' in processes[shortest]:
                processes[shortest]['start_time'] = current_time
            current_time += 1

        # Calculate averages
        total_waiting = sum(p['waiting_time'] for p in processes)
        total_turnaround = sum(p['turnaround_time'] for p in processes)
        total_response = sum(p['response_time'] for p in processes)
        avg_waiting = total_waiting / n
        avg_turnaround = total_turnaround / n
        avg_response = total_response / n

        return {
            "processes": processes,
            "gantt_chart": gantt_chart,
            "avg_waiting_time": avg_waiting,
            "avg_turnaround_time": avg_turnaround,
            "avg_response_time": avg_response
        }

    def non_preemptive_priority(self, processes):
        """
        Non-Preemptive Priority Scheduling.
        Lower numerical value means higher priority.
        """
        n = len(processes)
        completed = 0
        current_time = 0
        gantt_chart = []
        is_completed = [False] * n

        while completed != n:
            idx = -1
            highest_priority = math.inf
            for i in range(n):
                if processes[i]['arrival'] <= current_time and not is_completed[i]:
                    if processes[i]['priority'] < highest_priority:
                        highest_priority = processes[i]['priority']
                        idx = i
                    elif processes[i]['priority'] == highest_priority:
                        if processes[i]['arrival'] < processes[idx]['arrival']:
                            idx = i
            if idx != -1:
                p = processes[idx]
                if current_time < p['arrival']:
                    # CPU is idle
                    idle_time = p['arrival'] - current_time
                    gantt_chart.extend(["Idle"] * idle_time)
                    current_time = p['arrival']
                p['start_time'] = current_time
                p['completion_time'] = current_time + p['burst']
                p['turnaround_time'] = p['completion_time'] - p['arrival']
                p['waiting_time'] = p['start_time'] - p['arrival']
                p['response_time'] = p['waiting_time']
                gantt_chart.extend([p['pid']] * p['burst'])
                current_time += p['burst']
                is_completed[idx] = True
                completed += 1
            else:
                gantt_chart.append("Idle")
                current_time += 1

        # Calculate averages
        total_waiting = sum(p['waiting_time'] for p in processes)
        total_turnaround = sum(p['turnaround_time'] for p in processes)
        total_response = sum(p['response_time'] for p in processes)
        avg_waiting = total_waiting / n
        avg_turnaround = total_turnaround / n
        avg_response = total_response / n

        return {
            "processes": processes,
            "gantt_chart": gantt_chart,
            "Priority": True,
            "avg_waiting_time": avg_waiting,
            "avg_turnaround_time": avg_turnaround,
            "avg_response_time": avg_response
        }

    def preemptive_priority(self, processes):
        """
        Preemptive Priority Scheduling.
        Lower numerical value means higher priority.
        """
        n = len(processes)
        remaining_burst = [p['burst'] for p in processes]
        completed = 0
        current_time = 0
        gantt_chart = []
        is_completed = [False] * n
        min_priority = math.inf
        shortest = None

        while completed != n:
            idx = -1
            min_priority = math.inf
            for i in range(n):
                if processes[i]['arrival'] <= current_time and remaining_burst[i] > 0:
                    if processes[i]['priority'] < min_priority:
                        min_priority = processes[i]['priority']
                        idx = i
                    elif processes[i]['priority'] == min_priority:
                        if processes[i]['arrival'] < processes[idx]['arrival']:
                            idx = i
            if idx != -1:
                p = processes[idx]
                if remaining_burst[idx] == p['burst']:
                    p['start_time'] = current_time
                    p['response_time'] = current_time - p['arrival']
                remaining_burst[idx] -= 1
                gantt_chart.append(p['pid'])
                current_time += 1
                if remaining_burst[idx] == 0:
                    p['completion_time'] = current_time
                    p['turnaround_time'] = p['completion_time'] - p['arrival']
                    p['waiting_time'] = p['turnaround_time'] - p['burst']
                    is_completed[idx] = True
                    completed += 1
            else:
                gantt_chart.append("Idle")
                current_time += 1

        # Calculate averages
        total_waiting = sum(p['waiting_time'] for p in processes)
        total_turnaround = sum(p['turnaround_time'] for p in processes)
        total_response = sum(p['response_time'] for p in processes)
        avg_waiting = total_waiting / n
        avg_turnaround = total_turnaround / n
        avg_response = total_response / n

        return {
            "processes": processes,
            "gantt_chart": gantt_chart,
            "Priority": True,
            "avg_waiting_time": avg_waiting,
            "avg_turnaround_time": avg_turnaround,
            "avg_response_time": avg_response
        }

    def round_robin_scheduling(self, processes):
        """
        Round Robin Scheduling.
        """
        n = len(processes)
        time_quantum = processes[0]['time_quantum']  # Assuming same time quantum for all
        remaining_burst = [p['burst'] for p in processes]
        arrival_time = [p['arrival'] for p in processes]
        gantt_chart = []
        queue = deque()
        current_time = 0
        completed = 0
        is_in_queue = [False] * n
        first_response = [None] * n

        # Add processes that have arrived at time 0
        for i in range(n):
            if arrival_time[i] <= current_time:
                queue.append(i)
                is_in_queue[i] = True

        while completed != n:
            if not queue:
                gantt_chart.append("Idle")
                current_time += 1
                # Add processes that have arrived during idle time
                for i in range(n):
                    if arrival_time[i] <= current_time and not is_in_queue[i] and remaining_burst[i] > 0:
                        queue.append(i)
                        is_in_queue[i] = True
                continue

            i = queue.popleft()
            is_in_queue[i] = False

            if remaining_burst[i] > 0:
                if first_response[i] is None:
                    first_response[i] = current_time
                exec_time = min(time_quantum, remaining_burst[i])
                gantt_chart.extend([processes[i]['pid']] * exec_time)
                current_time += exec_time
                remaining_burst[i] -= exec_time

                # Check for newly arrived processes during execution
                for j in range(n):
                    if arrival_time[j] > (current_time - exec_time) and arrival_time[j] <= current_time and not is_in_queue[j] and remaining_burst[j] > 0:
                        queue.append(j)
                        is_in_queue[j] = True

                if remaining_burst[i] > 0:
                    queue.append(i)
                    is_in_queue[i] = True
                else:
                    processes[i]['completion_time'] = current_time
                    processes[i]['turnaround_time'] = processes[i]['completion_time'] - processes[i]['arrival']
                    processes[i]['waiting_time'] = processes[i]['turnaround_time'] - processes[i]['burst']
                    processes[i]['response_time'] = first_response[i] - processes[i]['arrival']
                    completed += 1

        # Calculate averages
        total_waiting = sum(p['waiting_time'] for p in processes)
        total_turnaround = sum(p['turnaround_time'] for p in processes)
        total_response = sum(p['response_time'] for p in processes)
        avg_waiting = total_waiting / n
        avg_turnaround = total_turnaround / n
        avg_response = total_response / n

        return {
            "processes": processes,
            "gantt_chart": gantt_chart,
            "avg_waiting_time": avg_waiting,
            "avg_turnaround_time": avg_turnaround,
            "avg_response_time": avg_response
        }

def main():
    root = tk.Tk()
    app = SchedulerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
