class MemoryBlock:
    def __init__(self, start, size, is_free=True, process_id=None):
        self.start = start
        self.size = size
        self.is_free = is_free
        self.process_id = process_id

    def __repr__(self):
        status = "Free" if self.is_free else f"Used by PID {self.process_id}"
        print(f"Start: {self.start:<5} | Size: {self.size:<5} | Status: {status}")


class MemoryManager:
    def __init__(self, total_memory, strategy="first_fit"):
        self.total_memory = total_memory
        self.strategy = strategy
        self.blocks = [MemoryBlock(0, total_memory)]  # Initially, all memory is free

    def allocate(self, process):
        """
        Allocates memory to the given process using the selected strategy.
        Returns True if successful, False otherwise.
        """
        if self.strategy == "first_fit":
            return self.first_fit(process)
        elif self.strategy == "best_fit":
            return self.best_fit(process)
        else:
            raise ValueError(f"Unknown allocation strategy: {self.strategy}")
        pass

    def deallocate(self, process):
        """
        Frees the memory occupied by the given process.
        """
        for block in self.blocks:
            if not block.is_free and block.process_id == process.process_id:
                block.is_free = True
                block.process_id = None

        self.merge_free_blocks()

    def first_fit(self, process):
        """
        Finds the first free block large enough and allocates it.
        """
        for i, block in enumerate(self.blocks):
            if block.is_free and block.size >= process.memory_required:
                allocated_block = MemoryBlock(
                    block.start, process.memory_required,
                    is_free=False, process_id=process.process_id
                )
                self.split_block(allocated_block, process, i)
                return True
        return False

    def best_fit(self, process):
        """
        Finds the smallest free block that fits the process.
        """
        best_index = -1
        min_fit_size = self.total_memory + 1

        for i, block in enumerate(self.blocks):
            if block.is_free and block.size >= process.memory_required:
                if block.size < min_fit_size:
                    best_index = i
                    min_fit_size = block.size

        if best_index == -1:
            return False  # No suitable block found

        allocated_block = MemoryBlock(
            self.blocks[best_index].start, process.memory_required,
            is_free=False, process_id=process.process_id
        )

        self.split_block(allocated_block, process, best_index)

        return True

    def split_block(self, allocated_block, process, block_index):
        remaining_size = self.blocks[block_index].size - process.memory_required
        if remaining_size > 0:
            # If there's leftover space, split the block
            remaining_block = MemoryBlock(
                allocated_block.start + process.memory_required,
                remaining_size, True
            )
            self.blocks[block_index:block_index + 1] = [allocated_block, remaining_block]
        else:
            # No leftover space, occupy the full block
            self.blocks[block_index] = allocated_block

    def merge_free_blocks(self):
        """
        Merges adjacent free blocks into a single block to reduce fragmentation.
        """
        merged_blocks = []
        i = 0

        while i < len(self.blocks):
            current = self.blocks[i]
            while (i + 1) < len(self.blocks) and current.is_free and self.blocks[i+1].is_free:
                current.size += self.blocks[i + 1].size
                i += 1
            merged_blocks.append(current)
            i += 1

        self.blocks = merged_blocks


