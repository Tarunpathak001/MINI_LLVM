from src.ir import (
    IRProgram, Label, Jump, Branch, Phi
)
from collections import defaultdict, deque

class SSAUnreachableElim:
    def run(self, ir: IRProgram) -> IRProgram:
        """
        Remove unreachable basic blocks.
        """
        instructions = ir.instructions

        # 1. Split into basic blocks
        blocks, order = self._split_blocks(instructions)

        # 2. Build CFG
        cfg = self._build_cfg(blocks)

        # 3. Reachability from entry
        # Assuming entry label is "entry" as enforced in IRBuilder
        reachable = self._reachable_blocks(cfg, entry="entry")

        # 4. Remove unreachable blocks
        new_blocks = {
            lbl: blk for lbl, blk in blocks.items()
            if lbl in reachable
        }

        # 5. Cleanup Phi nodes
        self._cleanup_phis(new_blocks, reachable)

        # 6. Reassemble instructions
        new_instrs = []
        for lbl in order:
            if lbl in new_blocks:
                new_instrs.extend(new_blocks[lbl])

        return IRProgram(new_instrs)

    # -------------------------------------------------
    # Helpers
    # -------------------------------------------------

    def _split_blocks(self, instructions):
        """
        Returns:
          blocks: label -> list[IRInstr]
          order: list of labels in original order
        """
        blocks = {}
        order = []

        current_label = None
        current_block = []

        for instr in instructions:
            if isinstance(instr, Label):
                if current_label is not None:
                    blocks[current_label] = current_block
                current_label = instr.name
                order.append(current_label)
                current_block = [instr]
            else:
                current_block.append(instr)

        if current_label is not None:
            blocks[current_label] = current_block

        return blocks, order

    def _build_cfg(self, blocks):
        """
        label -> set(successor labels)
        """
        cfg = defaultdict(set)

        for label, block in blocks.items():
            if not block:
                continue
            last = block[-1]

            if isinstance(last, Jump):
                cfg[label].add(last.target_label)

            elif isinstance(last, Branch):
                cfg[label].add(last.true_label)
                cfg[label].add(last.false_label)

            else:
                # No fallthrough in this IR by design, except maybe entry falling through to first label?
                # Actually IRBuilder emits Label("entry") first thing.
                # So "entry" block ends with Jump/Branch usually?
                # Or if it falls through (e.g. straight line code)?
                # Wait, IRBuilder for straight line code:
                # Label(entry)
                # x=1
                # ...
                # end.
                # If there is no terminator, where does it go?
                # Standard Basic Block usually demands terminator.
                # My `visit_While` emits Jump. `visit_If` emits Jump.
                # `visit_Program` just emits instructions.
                # If code falls through to next label, my CFG builder misses it?
                # The provided skeleton says: "# No fallthrough in this IR by design".
                # Let's trust that for now, assuming explicit control flow.
                # But wait, straight line code `x=1` `print(x)` doesn't have Jump.
                # It just ends. So no successors. Correct.
                pass

        return cfg

    def _reachable_blocks(self, cfg, entry):
        """
        Standard BFS/DFS
        """
        reachable = set()
        worklist = deque([entry])

        while worklist:
            blk = worklist.popleft()
            if blk in reachable:
                continue
            reachable.add(blk)

            for succ in cfg.get(blk, []):
                if succ not in reachable:
                    worklist.append(succ)

        return reachable

    def _cleanup_phis(self, blocks, reachable):
        """
        Remove Phi inputs whose predecessor block was deleted.
        """
        for label, block in blocks.items():
            for instr in block:
                if isinstance(instr, Phi):
                    instr.inputs = [
                        (val, pred)
                        for (val, pred) in instr.inputs
                        if pred in reachable
                    ]
