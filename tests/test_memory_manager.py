# tests/test_memory_manager.py
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import pytest
from memory_manager import MemoryManager, MemoryBlock
from process import Process


@pytest.fixture
def memory_manager():
    return MemoryManager(total_memory=1024)


@pytest.fixture
def process_small():
    return Process(process_id=1, arrival_time=0, burst_time=5, memory_required=150)


@pytest.fixture
def process_large():
    return Process(process_id=2, arrival_time=0, burst_time=10, memory_required=900)


def test_split_block_partial_allocation(memory_manager, process_small):
    # Test that if there's leftover space, the block is split

    memory_manager.blocks = [MemoryBlock(0, size=300, is_free=True)]

    # Create an allocated block manually
    allocated_block = MemoryBlock(start=0, size=150, is_free=False, process_id=process_small.process_id)

    memory_manager.split_block(allocated_block, process_small, 0)

    assert len(memory_manager.blocks) == 2
    assert memory_manager.blocks[0].size == 150
    assert memory_manager.blocks[0].is_free is False
    assert memory_manager.blocks[0].process_id == process_small.process_id

    assert memory_manager.blocks[1].size == 150
    assert memory_manager.blocks[1].is_free is True


def test_split_block_exact_fit(memory_manager):
    # Test that if there's no leftover space, the block is not split

    # Create a process that requires the exact amount of memory as total number
    process = Process(process_id=3, arrival_time=0, burst_time=10, memory_required=300)

    memory_manager.blocks = [MemoryBlock(0, size=300, is_free=True)]

    # Create an allocated block manually
    allocated_block = MemoryBlock(start=0, size=300, is_free=False, process_id=process.process_id)

    memory_manager.split_block(allocated_block, process, 0)

    assert len(memory_manager.blocks) == 1
    assert memory_manager.blocks[0].size == 300
    assert memory_manager.blocks[0].is_free is False
    assert memory_manager.blocks[0].process_id == process.process_id


def test_first_fit_allocation(memory_manager, process_small):
    # Test that first_fit allocates correctly
    memory_manager.blocks = [
        MemoryBlock(0, 100, True),
        MemoryBlock(100, 500, True),
        MemoryBlock(600, 200, True),
    ]

    result = memory_manager.first_fit(process_small)

    assert result is True, 'Expected the successful fit'

    allocated_block = next(
        (block for block in memory_manager.blocks if block.process_id == process_small.process_id),
        None
    )
    assert allocated_block is not None, "Expected to find a block allocated to the process"
    assert allocated_block.start == 100, \
        f"Expected allocation at start=100, got start={allocated_block.start}"
    assert allocated_block.is_free is False, \
        f"Expected block to be allocated, but got: is_free={allocated_block.is_free}"
    assert allocated_block.size == process_small.memory_required, \
        f"Expected block size to be {process_small.memory_required}, got {allocated_block.size}"


def test_best_fit_allocation(memory_manager, process_small):
    # Test that best_fit allocates to the smallest fitting block

    memory_manager.blocks = [
        MemoryBlock(0, 100, True),
        MemoryBlock(100, 500, True),
        MemoryBlock(600, 200, True),
    ]

    result = memory_manager.best_fit(process_small)

    assert result is True, 'Expected the successful fit'

    # Find the allocated block
    allocated_block = next(
        (block for block in memory_manager.blocks if block.process_id == process_small.process_id),
        None
    )
    assert allocated_block is not None, "Expected to find a block allocated to the process"
    assert allocated_block.start == 600, \
        f"Expected allocation at start=100, got start={allocated_block.start}"
    assert allocated_block.is_free is False, \
        f"Expected block to be allocated, but got: is_free={allocated_block.is_free}"
    assert allocated_block.size == process_small.memory_required, \
        f"Expected block size to be {process_small.memory_required}, got {allocated_block.size}"


def test_first_fit_allocation_failure_when_no_space(memory_manager, process_large):
    # Test that insufficient memory returns False

    memory_manager.total_memory = 500
    memory_manager.blocks = [MemoryBlock(0, 500, True)]
    result = memory_manager.first_fit(process_large)
    assert result is False, "First-fit should fail when no block is large enough"


def test_best_fit_allocation_failure_when_no_space(memory_manager, process_large):
    # Test that insufficient memory returns False

    memory_manager.total_memory = 500
    memory_manager.blocks = [MemoryBlock(0, 500, True)]
    result = memory_manager.best_fit(process_large)
    assert result is False, "Best-fit should fail when no block is large enough"


def test_deallocate(memory_manager, process_small):
    # Test freeing memory makes it available again
    memory_manager.blocks = [
        MemoryBlock(0, 100, True),
        MemoryBlock(100, 150, False, process_small.process_id),
        MemoryBlock(250, 350, True),
        MemoryBlock(600, 200, True),
    ]
    allocated_block = next(
        (block for block in memory_manager.blocks if block.process_id == process_small.process_id),
        None
    )
    memory_manager.deallocate(process_small)
    assert allocated_block.is_free is True, f'The block {process_small.process_id} should be deallocated'
    assert allocated_block.process_id is None, "process_id should be cleared after deallocation"


def test_deallocate_multiple_blocks(memory_manager, process_small):
    memory_manager.blocks = [
        MemoryBlock(0, 100, True),
        MemoryBlock(100, 150, False, process_small.process_id),
        MemoryBlock(250, 200, False, process_small.process_id),
        MemoryBlock(450, 574, True),
    ]

    memory_manager.deallocate(process_small)

    for block in memory_manager.blocks:
        if block.process_id == process_small.process_id:
            assert block.is_free is True, f"Block at {block.start} should be freed"
            assert block.process_id is None


def test_deallocate_nonexistent_process(memory_manager):
    process = Process(999, 0, 5, 100)
    # No blocks belong to PID 999
    memory_manager.deallocate(process)
    # Nothing should be marked free that wasn’t already
    assert all(block.is_free for block in memory_manager.blocks if block.process_id is None)


def test_merge_free_blocks(memory_manager):
    # Test that two adjacent free blocks are merged

    memory_manager.blocks = [
        MemoryBlock(0, 100, True),
        MemoryBlock(100, 150, True),
        MemoryBlock(250, 300, False, process_id=1),
        MemoryBlock(550, 200, True),
    ]

    memory_manager.merge_free_blocks()

    assert len(memory_manager.blocks) == 3, "Expected 3 blocks after merge"
    merged_block = memory_manager.blocks[0]
    assert merged_block.start == 0, "Merged block should start at 0"
    assert merged_block.size == 250, f"Merged block size should be 250, got {merged_block.size}"
    assert merged_block.is_free is True, "Merged block should be free"
    assert merged_block.process_id is None, "Merged block should not have a process_id"


def test_fragmentation_case(memory_manager):
    # Arrange: create alternating used and free blocks
    memory_manager.blocks = [
        MemoryBlock(0, 100, False, 1),
        MemoryBlock(100, 100, True),
        MemoryBlock(200, 150, False, 2),
        MemoryBlock(350, 100, True),
        MemoryBlock(450, 150, False, 3),
        MemoryBlock(600, 100, True),
    ]

    # Act: Try to allocate a process that needs more space than any one free block
    process = Process(99, 0, 5, 180)

    result = memory_manager.first_fit(process)

    # Assert: Allocation should fail due to fragmentation
    assert result is False, "Expected allocation to fail due to fragmented memory"

    # Also verify that total free memory > required, but no single block fits
    total_free = sum(block.size for block in memory_manager.blocks if block.is_free)
    assert total_free >= process.memory_required, (
        f"Total free memory is {total_free}, which should be enough, but fragmentation prevented allocation"
    )
