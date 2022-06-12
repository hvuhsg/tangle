from tangle.tangle import Tangle
from tangle.site import Site
from tangle.approval import Approval
from tangle.walker import IOTAWalker

genesis = Site(data="Genesis", confidence=1, approvals=[])
t = Tangle(root_site=genesis, walker=IOTAWalker(a=0.12))

for i in range(25):
    t.add_site(Site(i, 1, [Approval(t.get_tip()), Approval(t.get_tip())]))

t.draw()
