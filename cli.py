import argparse
import json
from scheduler import Scheduler
from memory_manager import MemoryManager
from process import Process
from visualization import plot_gantt, plot_memory_timeline


def load_processes_from_file(file_path):
    try:
        with open(file_path, "r") as f:
            data = json.load(f)

        return [
            Process(
                process_id=p["process_id"],
                arrival_time=p["arrival_time"],
                burst_time=p["burst_time"],
                memory_required=p["memory_required"]
            )
            for p in data["processes"]
        ]

    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        return []

    except json.JSONDecodeError:
        print(f"Error: Failed to parse JSON from '{file_path}'.")
        return []

    except KeyError as e:
        print(f"Error: Missing expected key in JSON: {e}")
        return []


def run_simulation():
    parser = argparse.ArgumentParser(description="OS Scheduler Simulator")
    parser.add_argument("--file", required=True, help="Path to JSON file with processes")
    parser.add_argument("--scheduler", choices=["FCFS", "RR"], default="FCFS", help="Scheduling algorithm to use")
    parser.add_argument("--quantum", type=int, default=4, help="Time quantum for Round Robin")
    parser.add_argument("--memory", type=int, default=1024, help="Total memory size")
    parser.add_argument("--strategy", choices=["first_fit", "best_fit"], default="first_fit",
                        help="Memory allocation strategy")

    args = parser.parse_args()

    # Setup memory manager with chosen allocation strategy
    memory_manager = MemoryManager(total_memory=args.memory, strategy=args.strategy)

    # Setup scheduler
    scheduler = Scheduler(memory_manager, algorithm=args.scheduler, time_quantum=args.quantum)

    # Load processes
    processes = load_processes_from_file(args.file)

    scheduler.run(processes)

    # Visualization
    plot_gantt(scheduler.execution_log, scheduler.get_stats(), scheduler.get_rejected_processes())
    plot_memory_timeline(scheduler.execution_log)


if __name__ == "__main__":
    run_simulation()
