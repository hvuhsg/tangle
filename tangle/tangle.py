from typing import Dict
from uuid import UUID
import random

import networkx as nx
import matplotlib.pyplot as plt

from .site import Site
from .walker import BaseWalker
from .exceptions import SiteCantApproveItself, SiteAlreadyInTheGraph
from .decorators import Toggle, Cache


class Tangle:
    def __init__(self, root_site, walker: BaseWalker):
        self.root_site: Site = root_site
        self.tips: Dict[UUID, Site] = {}
        self.walker: BaseWalker = walker
        self.height = 0
        self.xgraph = nx.DiGraph()
        self.add_site(self.root_site)

    def add_site(self, site: Site):
        if self.xgraph.has_node(site.uuid):
            raise SiteAlreadyInTheGraph()

        for approval in site.approvals:
            if approval.site.uuid == site.uuid:
                raise SiteCantApproveItself()

        site.id = self.xgraph.number_of_nodes()
        self.xgraph.add_node(site)
        self.xgraph.add_edges_from([(site, appr.site) for appr in site.approvals])

        self._remove_tips()
        self.tips[site.uuid] = site

        for approval in site.approvals:
            approval.site.add_approving_site(site)

        self.height = max(self.height, site.height)
        Cache.reset()

    def get_tip(self) -> Site:
        tip, steps = self.walker.walk(self.root_site)
        return tip

    def calculate_site_confidence(self, site_uuid: UUID) -> float:
        found = 0
        for i in range(100):
            end_walk_site, steps = self.walker.walk(self.root_site, stop_on_site=site_uuid)
            if end_walk_site.uuid == site_uuid:
                found += 1

        return found / 100

    def draw(self):
        pos = {}
        sizes = []
        colors = []
        for site in self.xgraph.nodes:
            Toggle.reset()
            pos[site] = (site.id, random.randrange(0, 100))
            sizes.append(min(site.cumulative_weight() * 10, 550))
            colors.append("red" if not site.approved_by else "blue")

        nx.draw_networkx_nodes(self.xgraph, pos, node_size=sizes, node_color=colors)
        nx.draw_networkx_edges(self.xgraph, pos, arrowstyle="->")

        ax = plt.gca()
        ax.set_axis_off()
        plt.show()

    def _remove_tips(self):
        for tip in self.tips.copy():
            site = self.tips[tip]
            if site.approved_by and random.choice([0, 1]):
                self.tips[tip].visible_tip = False
                del self.tips[tip]
