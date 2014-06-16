import unittest
import itertools
import operator


################## Utility functions ####################
def maxl(list):
    """ Return max using size attribute """
    return max(list, key=lambda x: x.size)

def minl(list):
    """ Return min using size attribute """
    return min(list, key=lambda x: x.size)

def sortl(list, dec=True):
    """ Sort list using size attribute.
    Items are sorted by decreasing order if rev = True,
    by increasing order otherwise """
    list.sort(key=lambda x: x.size, reverse=dec)
    return list


################## Instance ####################

class Instance:
    """ An instance """
    def __init__(self, items, bins):
        self.items = items[:]
        self.bins = bins[:]

    def __repr__(self):
        return "Items:\n"+str(self.items)+"\nBins:\n"+str(self.bins)

    def empty(self):
        for i in self.items: i.size = 0
        for b in self.bins: b.empty()


################## Items ####################

class Item:
    """ An item """
    def __init__(self, requirements):
        self.requirements = requirements[:]
        self.size = 0

    def __repr__(self):
        return str(self.requirements)

def vp_lower_bound(items, tbin):
    """ Return a lower bound on the minimum number of bins required
    assuming that all bins have the same capacities as tbin.
    This is a lower bound for the vector packing problem """
    if not items: return 0

    reqs = [0] * len(tbin.capacities)
    for i in items:
        reqs = map(operator.add, reqs, i.requirements)

    nbins = 0
    for w, c in zip(reqs, tbin.capacities):
        nb = w / c
        if w % c: nb += 1
        nbins = max(nbins, nb)

    return nbins

################## Bins ####################

class Bin:
    """ A bin """
    def __init__(self, capacities):
        self.capacities = capacities[:]
        self.remaining = capacities[:]
        self.items = []
        self.size = 0

    def __repr__(self):
        return str([self.capacities,self.remaining])

    def feasible(self, item):
        """ Return True iff item can be packed in this bin """
        for req, rem in itertools.izip_longest(item.requirements,self.remaining):
            if (req > rem):
                return False
        return True

    def insert(self, item):
        """
            Adds item to the bin
            Requires: the assignment is feasible
        """
        for i, req in enumerate(item.requirements):
            self.remaining[i] -= req
        self.items.append(item)

    def add(self, item):
        """
            Test feasibility and add item to the bin
            Return True if the item has been added, False o.w.
        """
        if self.feasible(item):
            self.insert(item)
            return True
        return False

    def empty(self):
        """ Empty the bin """
        self.items = []
        self.remaining = self.capacities[:]


################## Unit tests ####################

class ItemBinTestCase(unittest.TestCase):
    def dummy_item_size(self,list):
        for i in list:
            i.size = i.requirements[1]

    def setUp(self):
        l = [1,5,9]
        self.b0 = Bin(l)
        l[0] = 10; l[1] = 1;  l[2] = 7
        self.b1 = Bin(l)
        self.totalCap = [sum(v) for v in zip(self.b0.capacities, self.b1.capacities)]
        self.i1 = Item([0,4,3])
        self.i2 = Item([1,1,3])

    def testItem(self):
        assert self.i1.requirements == [0,4,3]
        assert self.i2.requirements != [0,4,3]

    def testBin(self):
        assert self.b0.capacities == [1,5,9]
        assert not self.b1.add(self.i1)
        assert self.b1.add(self.i2)
        assert self.b1.capacities == [10,1,7]
        assert self.b1.remaining == [9,0,4]
        assert not self.b1.add(self.i2)
        self.b1.empty()
        assert self.b1.remaining == self.b1.capacities

    def testItemUnchanged(self):
        assert not self.b1.add(self.i1)
        assert self.i1.requirements == [0,4,3]
        assert self.b0.add(self.i1)
        assert self.i1.requirements == [0,4,3]

    def testMaxAndSort(self):
        i3 = Item([.5,2,1])
        l = [self.i1,self.i2,i3]
        self.dummy_item_size(l)
        assert maxl(l) == self.i1
        assert minl(l) == self.i2
        sortl(l)
        assert l == [self.i1,i3,self.i2]
        sortl(l,False)
        assert l == [self.i2,i3,self.i1]
        assert maxl(l) == self.i1
        assert minl(l) == self.i2

    def testLB(self):
        assert vp_lower_bound([], None) == 0
        items = [self.i1,self.i2]
        assert vp_lower_bound(items, Bin([1,1,1])) == 6
        assert vp_lower_bound(items, Bin([8,8,8])) == 1
        assert vp_lower_bound(items, Bin([2,4,6])) == 2
        assert vp_lower_bound(items, Bin([2,5,2])) == 3


if __name__ == "__main__":
    unittest.main()
