"""
    Provides a basic framework for optimization for vector packing problems using the heuristics

    This is not exact and neither run-time optimized
"""

from .container import *
from .heuristics import *
from .generator import *
from .measures import *
import random

######## Create a list of heuristics with valid combinations of measures ########
class HeuristicList:
    pass

__hlist = HeuristicList()

# Static bfd ic/bc heuristics
__hlist.static = [
        (do_nothing, do_nothing),
        (shuffleItemsOnce,shuffleBinsOnce),
        (staticItemsOneOverC,staticBinsOneOverC),
        (staticItemsOneOverR,staticBinsOneOverR),
        (staticItemsROverC,staticBinsROverC)
        ]

# Dynamic heuristics
__hlist.dynamic = [
        (shuffleItems,shuffleBins),
        (dynamicItemsOneOverC,dynamicBinsOneOverC),
        (dynamicItemsOneOverR,dynamicBinsOneOverR),
        (dynamicItemsROverC,dynamicBinsROverC)
        ]

# Bin balancing heuristics
__hlist.balance = [
        (do_nothing, do_nothing),
        (shuffleItemsOnce,shuffleBinsOnce),
        (shuffleItems,shuffleBins),
        (staticItemsOneOverC,staticBinsOneOverC),
        (dynamicItemsOneOverC,dynamicBinsOneOverC),
        (staticItemsOneOverR,staticBinsOneOverR),
        (dynamicItemsOneOverR,dynamicBinsOneOverR),
        (staticItemsROverC,staticBinsROverC),
        (dynamicItemsROverC,dynamicBinsROverC)
        ]

# Dot Product heuristics
__hlist.dotprod = [
        (dp_nonorm, do_nothing),
        (dp_normC, do_nothing),
        (dp_normR, do_nothing)
        ]

def is_feasible(instance, use_dp=False):
    """ Run all heuristics and return True iff a heuristic finds
    a feasible solution. Return False otherwise.

    We emphasize that this code is NOT optimized at all. We could
    make each much faster by sarting with the heuristics which have
    the best success chances."""

    # Run static heuristics
    for m1, m2 in __hlist.static:
        instance.empty()
        ret = bfd_item_centric(instance.items[:], instance.bins[:], m1, m2)
        if not ret: return True

    # Run item centric dynamic heuristics
    for m1, m2 in __hlist.dynamic:
        instance.empty()
        ret = bfd_item_centric(instance.items[:], instance.bins[:], m1, m2)
        if not ret: return True

    # Run bin centric dynamic heuristics
    for m1, m2 in __hlist.dynamic:
        instance.empty()
        ret = bfd_bin_centric(instance.items[:], instance.bins[:], m1, m2)
        if not ret: return True

    # Run bin balancing heuristics
    for m1, m2 in __hlist.balance:
        instance.empty()
        ret = bin_balancing(instance.items[:], instance.bins[:], m1, m2)
        if not ret: return True

    # Run single bin balancing heuristics
    for m1, m2 in __hlist.balance:
        instance.empty()
        ret = bin_balancing(instance.items[:], instance.bins[:], m1, m2, single=True)
        if not ret: return True

    # Run Dot Product heuristics
    if not use_dp:
        return False

    for m1, m2 in __hlist.dotprod:
        instance.empty()
        ret = bfd_item_centric(instance.items[:], instance.bins[:], m1, m2)
        if not ret: return True

    # No solution found
    return False


def optimize(items, tbin, use_dp=False, seed=None):
    """ Performs a binary search and returns the best solution
        found for the vector bin packing problem.

    Keyword arguments:
        items -- a list of items (Item) to pack
        tbin -- a typical Bin: all bins have the same capacities as tbin

    Return the best solution found. len(ret.bins) is the best number of bins found.
    """
    # replace by the following line to return lower bounds
    # return Instance([], [tbin]*vp_lower_bound(items, tbin))

    if seed != None:
        random.seed(seed)

    lb = vp_lower_bound(items, tbin)
    ub = len(items)
    best = None
    while lb <= ub:
        mid = (lb + ub) / 2
        bins = [Bin(tbin.capacities) for i in xrange(mid)]
        inst = Instance(items[:], bins)
        if is_feasible(inst, use_dp):
            best = inst
            ub = mid - 1
        else:
            lb = mid + 1

    return best


################## Unit tests ####################

class OptimizationTestCase(unittest.TestCase):
    def setUp(self):
        self.items = [Item([0,4,3]), Item([1,1,3]), Item([5,2,1]), Item([3,1,7])]
        self.bins = [Bin([5,5,8]), Bin([8,5,9]), Bin([3,3,5])]

    def testFeasible(self):
        bins = [Bin(self.bins[0].capacities) for i in xrange(5)]
        inst = Instance(self.items[:], bins)
        assert is_feasible(inst, True)

        bins = [Bin(self.bins[0].capacities) for i in xrange(2)]
        inst = Instance(self.items[:], bins)
        assert not is_feasible(inst, True)

        # Warning: this test may fail if the heuristics perform poorly
        bins = [Bin(self.bins[1].capacities) for i in xrange(3)]
        inst = Instance(self.items[:], bins)
        assert is_feasible(inst, True)

        bins = [Bin(self.bins[2].capacities) for i in xrange(15)]
        inst = Instance(self.items[:], bins)
        assert not is_feasible(inst, True)


    def testOptimize(self):
        # Warning: these tests may fail if the heuristics perform poorly
        assert len(optimize(self.items, self.bins[0], True).bins) == 3
        assert len(optimize(self.items, self.bins[1], True).bins) == 2
        assert optimize(self.items, self.bins[2], True) == None

if __name__ == "__main__":
    unittest.main()
