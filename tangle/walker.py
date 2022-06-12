from typing import List, Union
from abc import ABC, abstractmethod
from random import choice, choices
from uuid import UUID
import math

from tangle.site import Site
from tangle.decorators import Toggle


class BaseWalker(ABC):
    def walk(self, start_site: Site, stop_on_site: UUID = None) -> (Site, int):
        """
        Walker method used to walk the graph

        ****************
        DO NOT OVERRIDE!
        ****************

        To override the walker behavior override the 'choose' method

        :param start_site: site to start walking from.
        :param stop_on_site: uuid of a site that will be returned if the walker step on in.
        :return: tip site or (site with the uuid passed in stop_on_site), number of steps to get to it.
        """
        if start_site.is_tip:
            return start_site, 0

        steps = 0
        curr_site = start_site
        previous_site = None

        while not curr_site.is_tip:
            if stop_on_site is not None and stop_on_site == curr_site.uuid:
                return curr_site, steps

            next_site = self.choose(curr_site, list(curr_site.approved_by))

            while next_site is None:
                if previous_site is not None:
                    next_site = previous_site
                    break
                next_site = self.choose(curr_site, list(curr_site.approved_by))

            curr_site, previous_site = next_site, curr_site
            steps += 1

        return curr_site, steps

    @abstractmethod
    def choose(self, current_site: Site, sites: List[Site]) -> Site:
        """
        Choose a site the walker will walk to or return None for the worker to go a step back
        NOTE: your function mast have a higher probability to go forward then to go backwards (return None)

        :param current_site: current site the walker is on
        :param sites: list of approving sites
        :return: site to walk to or None to go step back
        """
        raise NotImplementedError


class UnweightedWalker(BaseWalker):
    def choose(self, current_site: Site, sites: List[Site]) -> Site:
        return choice(sites)


class UnweightedWalkerBackTracking(BaseWalker):
    def choose(self, current_site: Site, sites: List[Union[Site, None]]) -> Site:
        sites.append(None)
        return choice(sites)


class IOTAWalker(BaseWalker):
    def __init__(self, a):
        self.a = a

    def choose(self, current_site: Site, sites: List[Site]) -> Site:
        Toggle.reset()
        Hx = current_site.cumulative_weight()
        Ps = []

        for site in sites:
            Toggle.reset()
            Hy = site.cumulative_weight()
            P = math.exp(-self.a * (Hx - Hy))
            Ps.append(P)

        return choices(sites, k=1, weights=Ps)[0]
