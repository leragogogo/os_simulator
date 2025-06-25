from collections import deque


class Scheduler:
    def __init__(self, memory_manager, algorithm="FCFS", time_quantum=None):
        self.memory_manager = memory_manager
        self.algorithm = algorithm
        self.time_quantum = time_quantum  # Used for Round Robin
        self.ready_queue = deque()
        self.time = 0  # The current stimulation time
        self.completed_processes = []
        self.execution_log = []  # Record process_id per time unit (testing)

    def add_process(self, process):
        """
        Try to allocate memory and add the process to the ready queue if successful.
        """
        if self.memory_manager.allocate(process):
            self.ready_queue.append(process)
            return True
        return False

    def run(self):
        """
        Main loop to run the scheduling logic based on the chosen algorithm.
        If `max_time` is set, simulate only up to that time.
        """
        if self.algorithm == "FCFS":
            self.run_fcfs()
        elif self.algorithm == "RR":
            self.run_round_robin()
        else:
            raise ValueError(f"Unknown scheduling algorithm: {self.algorithm}")

    def run_fcfs(self):
        """
        First-Come-First-Serve scheduling logic.
        """
        while self.ready_queue:
            # Get the next process in the queue
            process = self.ready_queue.popleft()

            # If this is the first time the process runs, record its start time
            if process.start_time is None:
                process.start_time = self.time

            # Execute the whole process
            self.time += process.burst_time
            process.completion_time = self.time

            # Calculate the time metrics
            process.turnaround_time = process.completion_time - process.arrival_time
            process.waiting_time = process.start_time - process.arrival_time

            # Deallocate memory and mark process as completed
            self.memory_manager.deallocate(process)
            self.completed_processes.append(process)

    def run_round_robin(self):
        """
        Round Robin scheduling logic using time_quantum.
        """
        while self.ready_queue:
            # Get the next process in the queue
            process = self.ready_queue.popleft()

            # Record the execution order (testing/visualization)
            self.execution_log.append(process.process_id)

            # If this is the first time the process runs, record its start time
            if process.start_time is None:
                process.start_time = self.time

            # Determine how much time the process can run in this round
            time_slice = min(self.time_quantum, process.remaining_time)
            self.time += time_slice
            process.remaining_time -= time_slice

            # Process is finished -> calculate metrics, deallocate memory and mark process as completed
            if process.remaining_time == 0:
                process.completion_time = self.time

                process.turnaround_time = process.completion_time - process.arrival_time
                process.waiting_time = process.start_time - process.arrival_time

                self.memory_manager.deallocate(process)
                self.completed_processes.append(process)
            else:  # Process is not finished yet -> add it again to queue
                self.ready_queue.append(process)

    def get_stats(self):
        """
        Return summary statistics for all completed processes.
        """
        return {
            "avg_waiting_time": sum(p.waiting_time for p in self.completed_processes) / len(self.completed_processes),
            "avg_turnaround_time": sum(p.turnaround_time for p in self.completed_processes) / len(
                self.completed_processes),
        }
