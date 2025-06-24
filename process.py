class Process:
    def __init__(self, process_id, arrival_time, burst_time, memory_required):
        self.process_id = process_id
        self.arrival_time = arrival_time
        self.burst_time = burst_time
        self.memory_required = memory_required
        self.remaining_time = burst_time  # Used for Round Robin
        self.start_time = None
        self.completion_time = None
        self.waiting_time = 0
        self.turnaround_time = 0  # Total time from arrival to completion: completion_time - arrival_time
