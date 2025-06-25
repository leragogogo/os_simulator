import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import pytest
from scheduler import Scheduler
from memory_manager import MemoryManager
from process import Process


@pytest.fixture
def memory_manager():
    return MemoryManager(total_memory=1024)


@pytest.fixture
def scheduler(memory_manager):
    return Scheduler(memory_manager)


@pytest.fixture
def process_a():
    return Process(process_id=1, arrival_time=0, burst_time=10, memory_required=150)


@pytest.fixture
def process_b():
    return Process(process_id=2, arrival_time=2, burst_time=4, memory_required=150)


@pytest.fixture
def process_c():
    return Process(process_id=3, arrival_time=4, burst_time=6, memory_required=200)


@pytest.fixture
def process_large():
    return Process(process_id=3, arrival_time=4, burst_time=6, memory_required=900)


def test_fcfs_handles_memory_allocation(scheduler, memory_manager, process_a):
    # Test that the scheduler interacts correctly with the memory manager
    success = scheduler.add_process(process_a)

    assert success is True, "Process should be accepted into the scheduler"
    allocated = any(block.process_id == process_a.process_id for block in memory_manager.blocks)
    assert allocated, "Process should be allocated in memory"


def test_fcfs_handles_memory_deallocation(scheduler, memory_manager, process_a):
    # Test that the scheduler deallocate memory after runs the processes
    scheduler.add_process(process_a)
    scheduler.run()

    allocated = any(block.process_id == process_a.process_id for block in memory_manager.blocks)
    assert allocated is False, f"Memory must be deallocated"


def test_fcfs(scheduler, process_a, process_b, process_c):
    # Test the correctness of FCFS

    # Add processes to queue
    scheduler.add_process(process_a)
    scheduler.add_process(process_b)
    scheduler.add_process(process_c)

    scheduler.run()

    assert len(scheduler.ready_queue) == 0, 'All processes must be executed'
    assert process_a.completion_time == 10, "Process A must be competed by 10"
    assert process_b.completion_time == 14, "Process B must be competed by 14"
    assert process_c.completion_time == 20, "Process C must be competed by 20"


def test_round_robin(scheduler, process_a, process_b, process_c):
    # Add processes to queue
    scheduler.add_process(process_a)
    scheduler.add_process(process_b)
    scheduler.add_process(process_c)

    # Setup Scheduler to Round Robin algorithm
    scheduler.time_quantum = 4
    scheduler.algorithm = 'RR'

    scheduler.run()

    assert len(scheduler.ready_queue) == 0, 'All processes must be executed'
    assert process_a.completion_time == 20, "Process A must be competed by 20"
    assert process_b.completion_time == 8, "Process B must be competed by 8"
    assert process_c.completion_time == 18, "Process C must be competed by 18"


def test_rejects_process_when_memory_insufficient(scheduler, process_a, process_large):
    # Test that the scheduler handles memory allocation failures

    scheduler.add_process(process_a)
    scheduler.add_process(process_large)  # Large memory requirement

    scheduler.run()

    assert process_large.completion_time is None, "Large process should not complete due to lack of memory"
