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
        self.current_process = None
        self.time_slice_remaining = 0  # Track one tick per operation for RR
        self.remaining_processes = []  # Processes that are not yet added to the ready queue
        self.rejected_processes = []

    def add_process(self, process):
        """
        Try to allocate memory and add the process to the ready queue if successful.
        """
        if self.memory_manager.allocate(process):
            self.ready_queue.append(process)
            return True
        return False

    def run(self, processes):
        """
        Main loop to run the scheduling logic based on the chosen algorithm.
        """
        self.remaining_processes = sorted(processes, key=lambda p: p.arrival_time)

        self.current_process = None
        self.time_slice_remaining = 0

        while self.remaining_processes or self.ready_queue or self.current_process:
            # Add processes to the queue that arrived earlier that the current time
            arrived_now = [p for p in self.remaining_processes if p.arrival_time <= self.time]
            for p in arrived_now:
                if self.add_process(p):
                    self.remaining_processes.remove(p)
                else:
                    # If the process is too big for the memory -> reject
                    if p.memory_required > self.memory_manager.total_memory:
                        self.rejected_processes.append(p)
                        self.remaining_processes.remove(p)

            # Algorithm selection
            if self.algorithm == "FCFS":
                self.run_fcfs_step()
            elif self.algorithm == "RR":
                self.run_round_robin_step()
            else:
                raise ValueError(f"Unsupported algorithm: {self.algorithm}")

    def run_fcfs_step(self):
        """
        Executes one simulation tick for FCFS (First-Come-First-Serve) scheduling.
        """
        # If there's no currently running process, take the next from the ready queue
        if not self.current_process and self.ready_queue:
            self.current_process = self.ready_queue.popleft()
            if self.current_process.start_time is None:
                self.current_process.start_time = self.time  # Record when the process started execution

        if self.current_process:
            # Log current execution (visualization, testing)
            self.execution_log.append({
                "time": self.time,
                "process_id": self.current_process.process_id,
                "memory_state": [
                    (block.start, block.size, block.is_free, block.process_id)
                    for block in self.memory_manager.blocks
                ]
            })

            # Execute one time unit
            self.current_process.remaining_time -= 1
            self.time += 1

            # If the process is finished
            if self.current_process.remaining_time == 0:
                self.current_process.completion_time = self.time
                self.current_process.turnaround_time = self.current_process.completion_time - self.current_process.arrival_time
                self.current_process.waiting_time = self.current_process.start_time - self.current_process.arrival_time

                # Free memory and mark as completed
                self.memory_manager.deallocate(self.current_process)
                self.completed_processes.append(self.current_process)
                self.current_process = None
        else:
            # If there's no process to execute, log idle time
            self.execution_log.append({
                "time": self.time,
                "process_id": None,
                "memory_state": [
                    (block.start, block.size, block.is_free, block.process_id)
                    for block in self.memory_manager.blocks
                ]
            })
            self.time += 1

    def run_round_robin_step(self):
        """
        Executes one simulation tick for Round Robin scheduling.
        """
        # If there's no currently running process, take the next from the ready queue
        if not self.current_process and self.ready_queue:
            self.current_process = self.ready_queue.popleft()
            if self.current_process.start_time is None:
                self.current_process.start_time = self.time  # Mark the start of execution
            self.time_slice_remaining = min(self.time_quantum, self.current_process.remaining_time)

        if self.current_process:
            # Log current execution (visualization, testing)
            self.execution_log.append({
                "time": self.time,
                "process_id": self.current_process.process_id,
                "memory_state": [
                    (block.start, block.size, block.is_free, block.process_id)
                    for block in self.memory_manager.blocks
                ]
            })

            # Execute one time unit
            self.current_process.remaining_time -= 1
            self.time_slice_remaining -= 1
            self.time += 1

            # Check if new processes have arrived after this tick
            arrived_now = [p for p in self.remaining_processes if p.arrival_time <= self.time]
            for p in arrived_now:
                if self.add_process(p):
                    self.remaining_processes.remove(p)

            # Process finished execution
            if self.current_process.remaining_time == 0:
                self.current_process.completion_time = self.time
                self.current_process.turnaround_time = self.current_process.completion_time - self.current_process.arrival_time
                self.current_process.waiting_time = self.current_process.start_time - self.current_process.arrival_time

                self.memory_manager.deallocate(self.current_process)
                self.completed_processes.append(self.current_process)
                self.current_process = None

            # Time slice expired but process not finished — put it back to the queue
            elif self.time_slice_remaining == 0:
                self.ready_queue.append(self.current_process)
                self.current_process = None
        else:
            # If there's no process to execute, log idle time
            self.execution_log.append({
                "time": self.time,
                "process_id": None,
                "memory_state": [
                    (block.start, block.size, block.is_free, block.process_id)
                    for block in self.memory_manager.blocks
                ]
            })
            self.time += 1

    def get_stats(self):
        """
        Return summary statistics for all completed processes.
        """
        if not self.completed_processes:
            return {}

        return {
            "avg_waiting_time": sum(p.waiting_time for p in self.completed_processes) / len(self.completed_processes),
            "avg_turnaround_time": sum(p.turnaround_time for p in self.completed_processes) / len(
                self.completed_processes),
        }

    def get_rejected_processes(self):
        """
        Return rejected processes.
        """
        if not self.rejected_processes:
            return ""

        rejected_processes_str = ""
        for p in self.rejected_processes:
            rejected_processes_str += str(p) + ', '
        return rejected_processes_str

