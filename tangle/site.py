from typing import List, Set
from uuid import uuid4, UUID
from queue import Queue

from tangle.approval import Approval
from tangle.decorators import Toggle, Cache


class Site:
    def __init__(self, data, confidence, approvals: List[Approval]):
        self.id = None  # The number of the sites in the graph when added.
        self.uuid: UUID = uuid4()
        self.data = data
        self.confidence = confidence
        self.approvals: List[Approval] = approvals
        self.approved_by: Set[Site] = set()
        self.height = (max(map(lambda a: a.site.height, self.approvals)) if self.approvals else 0) + 1
        self.weight = (sum(map(lambda a: a.difficulty, self.approvals)) if self.approvals else 0) + 1
        self.score = self._calc_score()
        self.visible_tip = True

    @property
    def is_tip(self):
        return self.visible_tip

    def _calc_score(self) -> int:
        approved_sites: Set[Site] = set()
        queue = Queue()

        for approval in self.approvals:
            queue.put(approval.site)

        while not queue.empty():
            approved_site = queue.get()

            if approved_site not in approved_sites:
                approved_sites.add(approved_site)
            else:
                continue

            for indirect_approval in approved_site.approvals:
                queue.put(indirect_approval.site)

        return sum(map(lambda s: s.weight, approved_sites)) + self.weight

    def add_approving_site(self, approving_site: "Site"):
        self.approved_by.add(approving_site)

    # @Toggle.toggle(off_value=0)
    @Cache.lru
    def cumulative_weight(self) -> int:
        result = self.weight

        for directly_approving_site in self.approved_by:
            result += directly_approving_site.cumulative_weight()

        return result
