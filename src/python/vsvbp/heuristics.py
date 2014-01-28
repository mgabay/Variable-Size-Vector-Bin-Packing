import unittest
from measures import *
from container import *
from collections import deque


################## Heuristics ####################

def bfd_item_centric(items, bins, item_measure, bin_measure):
    """
    Best fit heuristic - item centric :
        Place successive items in the the first feasible bin.
        Sort bins after each iteration
        (one iteration = one item is placed).

    Return the list of unpacked items.
    If all items have been packed, this list is empty.
    Otherwise, failed[i] is a tuple (r,i). r is the rank of the item
    (means r items have been tried before) and i is the item
    """

    # create list of items
    it = deque(items)
    failed = [] # set of unpacked items
    
    # Initializing measures
    item_measure(it, bins, init=True)
    bin_measure(it, bins, init=True)
    
    iter = 0
    while it:
        # Compute sizes
        item_measure(it, bins)
        bin_measure(it, bins)
        
        # Get biggest item
        i = maxl(it)
        it.remove(i)
        
        # Sort bins by increasing order of their sizes
        sortl(bins, dec=False)
        
        packed = False
        for b in bins:
            if b.add(i):
                packed = True
                break
        if not packed:
            failed.append((iter, i))
        iter += 1

    return failed


def bfd_bin_centric(items, bins, item_measure, bin_measure):
    """
    Best fit heuristic - bin centric :
        Pack items in selected bin.
        Sort items after each iteration
        (one iteration = one bin is consumed).

    Return the list of unpacked items.
    If all items have been packed, this list is empty.
    Otherwise, failed[i] is a tuple (r,i). r is the rank of the item
    (means r items have been tried before) and i is the item --
    In the bin centric heuristic, failed[0][0] is the number of
    items successfully packed
    """

    # create lists of bins and items
    bi = deque(bins)
    r = len(items)
    
    # Initializing measures
    item_measure(items, bi, init=True)
    bin_measure(items, bi, init=True)
    
    item_measure(items, bi)
    while bi:
        # Compute sizes
        bin_measure(items, bi)
        
        # Get smallest bin
        b = minl(bi)
        
        keep_going = True
        while keep_going:
            keep_going = False

            # Sort items by decreasing order of their sizes
            item_measure(items, bi)
            sortl(items, dec=True)
            
            # Pack an item
            for i in items:
                if b.add(i):
                    keep_going = True
                    items.remove(i) # VERY UNEFFICIENT !!!
                    break
        
        bi.remove(b)

    failed = []
    r -= len(items)   # number of unpacked items
    for i in items:
        failed.append((r, i))
        r += 1
        
    return failed


def bin_balancing(items, bins, item_measure, bin_measure, single=False):
    """
    Bin Balancing Heuristic :
        Place an item in a bin, then :
        - if single is true : place this bin to the end of the bins list
        - if single is false : place all bin tried during current iteration
            to the end of the bins list
        (one iteration = one item is placed).

    Return the list of unpacked items.
    If all items have been packed, this list is empty.
    Otherwise, failed[i] is a tuple (r,i). r is the rank of the item
    (means r items have been tried before) and i is the item
    """

    # create list of items
    it = deque(items)
    failed = [] # set of unpacked items
    
    # Initialization
    item_measure(it, bins, init=True)
    bin_measure(it, bins, init=True)
    bin_measure(it, bins)
    sortl(bins, dec=False)
    
    mod = len(bins)
    offset = 0    
    iter = 0
    while it:
        # Compute sizes
        item_measure(it, bins)
        
        # Get biggest item
        i = maxl(it)
        it.remove(i)
                
        packed = False
        gen = (bins[(i+offset) % mod] for i in xrange(mod))
        for rk, b in enumerate(gen):
            if b.add(i):
                packed = True
                if single:
                    bins.remove(b)
                    bins.append(b)
                else:
                    offset = (offset+rk+1) % mod
                break
        if not packed:
            failed.append((iter, i))
        iter += 1

    return failed

################## Unit tests ####################

class HeuristicsTestCase(unittest.TestCase):
    def setUp(self):
        self.i1 = Item([1,2,9]); self.i2 = Item([4,5,3])
        self.i3 = Item([0,1,0]); self.i4 = Item([9,8,7])
        self.i1.size = 1; self.i2.size = 2; self.i3.size = 3; self.i4.size = 0; 
        self.items = [self.i4, self.i3, self.i2, self.i1]
        self.b1=Bin([5,8,4]); self.b2=Bin([100,0,100]); self.b3=Bin([1,2,9]);
        self.b1.size=1; self.b2.size=2; self.b3.size=3; 
        self.bins = [self.b1,self.b2,self.b3]


    def testItemCentricSuccess(self):
        ret = bfd_item_centric(self.items[1:], self.bins, do_nothing, do_nothing)
        assert ret == []
        
    def testItemCentricFailure(self):
        ret = bfd_item_centric(self.items, self.bins, do_nothing, do_nothing)
        assert self.b3.items == [self.i1]
        assert self.b2.items == []
        assert self.b1.items == [self.i3,self.i2]
        assert ret == [(3,self.i4)]
        
    def testBinCentricSuccess(self):
        ret = bfd_bin_centric(self.items[1:], self.bins, do_nothing, do_nothing)
        assert ret == []
        
    def testBinCentricFailure(self):
        ret = bfd_bin_centric(self.items, self.bins, do_nothing, do_nothing)
        assert self.b3.items == [self.i1]
        assert self.b2.items == []
        assert self.b1.items == [self.i3,self.i2]
        assert ret == [(3,self.i4)]
        
    def testFailure(self):
        self.i4.size = 10; 
        ret = bfd_item_centric(self.items, self.bins, do_nothing, do_nothing)
        assert self.b3.items == [self.i1]
        assert self.b2.items == []
        assert self.b1.items == [self.i3,self.i2]
        assert ret == [(0,self.i4)]
        self.setUp(); self.i4.size = 10; 
        ret = bfd_bin_centric(self.items, self.bins, do_nothing, do_nothing)
        assert self.b3.items == [self.i1]
        assert self.b2.items == []
        assert self.b1.items == [self.i3,self.i2]
        assert ret == [(3,self.i4)]
        
    def testOriginalBinBalancing(self):
        self.i2.requirements=[1,1,1]
        ret = bin_balancing(self.items, self.bins, do_nothing, do_nothing, False)
        assert self.b1.items == [self.i3]
        assert self.b2.items == []
        assert self.b3.items == [self.i2]
        assert ret == [(2,self.i1),(3,self.i4)]    
        
    def testSingleBinBalancing(self):
        self.i2.requirements=[1,1,1]
        ret = bin_balancing(self.items, self.bins, do_nothing, do_nothing, True)
        assert self.b1.items == [self.i3]
        assert self.b2.items == []
        assert self.b3.items == [self.i2]
        assert ret == [(2,self.i1),(3,self.i4)] 
        
if __name__ == "__main__":
    unittest.main()
