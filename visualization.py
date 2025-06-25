import matplotlib.pyplot as plt
from collections import defaultdict

def plot_gantt(execution_log, stats):
    """
    Plot a Gantt chart showing when each process is running,
    and append summary statistics below the chart.
    """
    fig, ax = plt.subplots(figsize=(10, 5))
    process_colors = {}  # Assign a unique color for each process
    execution_segments = defaultdict(list)  # Store execution times per process

    # Group all time points where each process runs
    for entry in execution_log:
        process_id = entry["process_id"]
        time = entry["time"]
        if process_id not in process_colors:
            process_colors[process_id] = f"C{process_id % 10}"  # Matplotlib color cycle
        execution_segments[process_id].append(time)

    # Convert time points into (start, duration) segments
    for process_id, times in execution_segments.items():
        times.sort()
        grouped = []
        start = times[0]
        prev = times[0]
        for t in times[1:]:
            if t == prev + 1:
                prev = t
            else:
                grouped.append((start, prev - start + 1))
                start = t
                prev = t
        grouped.append((start, prev - start + 1))

        y_pos = process_id * 10
        for start_time, duration in grouped:
            ax.broken_barh([(start_time, duration)], (y_pos, 2), facecolors=process_colors[process_id])

    ax.set_xlabel("Time")
    ax.set_ylabel("Process ID")
    ax.set_yticks([pid * 10 + 2 for pid in process_colors])
    ax.set_yticklabels(list(process_colors.keys()))
    plt.title("Process Execution Timeline")

    # Make room for stats below the plot
    plt.subplots_adjust(bottom=0.25)

    # Add statistics below the plot
    if stats:
        stat_text = "\n".join([f"{k}: {v:.2f}" for k, v in stats.items()])
        fig.text(0.1, 0.02, "Summary Stats:\n" + stat_text, fontsize=10, ha="left")

    plt.show()



def plot_memory_timeline(execution_log):
    """
    Plot memory allocation and deallocation over time.
    Red blocks = allocated memory (with process_id), green = free memory.
    """
    fig, ax = plt.subplots(figsize=(10, 6))

    for entry in execution_log:
        time = entry["time"]  # Snapshot time
        for block in entry["memory_state"]:
            start, size, is_free, process_id = block  # Unpack block info
            color = 'green' if is_free else 'red'
            label = "Free" if is_free else f"PID {process_id}"

            # Draw memory block as horizontal bar at time line
            ax.broken_barh([(start, size)], (time, 1), facecolors=color, edgecolors='black')

            # Annotate PID inside allocated blocks
            if not is_free:
                ax.text(start + size / 2, time + 0.3, label,
                        ha='center', va='center', fontsize=7, color='white')

    ax.set_xlabel("Memory Address")
    ax.set_ylabel("Time")
    plt.title("Memory Usage Over Time")
    plt.tight_layout()
    plt.show()
