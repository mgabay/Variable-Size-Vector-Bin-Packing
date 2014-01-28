"""
Various size functions (measures)
They are all defined by :
    measure(items, bins, init=False)
A first run, with init = True is supposed to be run. During this run,
all structures are initialized.
In the following runs, sizes are updated.

These mesures alter attributes sizes from bins and items

Note that most measures perform some unnecessary redundant computations
"""

import random
import itertools
import math

from .container import *

################## Measures ####################


########## Random measures ##########

def do_nothing(items, bins, init = False):
    """ Stub measure - do not alter any of the sizes """
    return


def shuffleBins(items, bins, init = False):
    """ Assign random sizes to the bins if init is set to False """
    if init: return
    for b in bins:
        b.size = random.random()

def shuffleBinsOnce(items, bins, init = False):
    """ Assign random sizes to the bins on the first invocation
    after a call with init = True """
    if init:
        shuffleBins.go = True
    elif shuffleBins.go:
        random.shuffle(bins)
        shuffleBins.go = False

def shuffleItems(items, bins, init = False):
    """ Assign random sizes to the items if init is set to False """
    if init: return
    for i in items:
        i.size = random.random()

def shuffleItemsOnce(items, bins, init = False):
    """ Assign random sizes to the items on the first invocation
    after a call with init = True """
    if init:
        shuffleItems.go = True
    elif shuffleItems.go:
        random.shuffle(items)
        shuffleItems.go = False
        
 
########## Some useful functions ##########     

def compute_item_req(items):
    """ Computes total requirements """
    if not items:
        return 0
    s = len(items[0].requirements)
    req = [0]*s
    for i in items:
        for j in xrange(s):
            req[j] += i.requirements[j]
    return req

def compute_bin_res(bins):
    """ Computes total remaining bin resources """
    if not bins:
        return 0
    s = len(bins[0].remaining)
    rem = [0]*s
    for b in bins:
        for j in xrange(s):
            rem[j] += b.remaining[j]
    return rem


########## Normalize by 1/C ##########

def staticBinsOneOverC(items, bins, init = False):
    """ Static measure : bins sizes are updated once.
    alpha = beta = 1/C(r) """
    if init:
        dynamicBinsOneOverC(items, bins)

def staticItemsOneOverC(items, bins, init = False):
    """ Static measure : items sizes are updated once.
    alpha = beta = 1/C(r) """
    if init:
        dynamicItemsOneOverC(items, bins)

def dynamicBinsOneOverC(items, bins, init = False):
    """ Dynamic measure : bins sizes are always recomputed.
    alpha = beta = 1/C(r) """
    if init: return
    res = compute_bin_res(bins)
    if res == 0: return
    res = [1/float(i) if i != 0 else 0 for i in res]
    for i in bins:
        i.size = 0
        for j, r in enumerate(i.remaining):
            i.size += res[j]*r

def dynamicItemsOneOverC(items, bins, init = False):
    """ Dynamic measure : items sizes are always recomputed.
    alpha = beta = 1/C(r) """
    if init: return
    res = compute_bin_res(bins)
    if res == 0: return
    res = [1/float(i) if i != 0 else 0 for i in res]
    for i in items:
        i.size = 0
        for j, r in enumerate(i.requirements):
            i.size += res[j]*r


########## Normalize by 1/R ##########

def staticBinsOneOverR(items, bins, init = False):
    """ Static measure : bins sizes are updated once.
    alpha = beta = 1/R(r) """
    if init:
        dynamicBinsOneOverR(items, bins)

def staticItemsOneOverR(items, bins, init = False):
    """ Static measure : items sizes are updated once.
    alpha = beta = 1/R(r) """
    if init:
        dynamicItemsOneOverR(items, bins)

def dynamicBinsOneOverR(items, bins, init = False):
    """ Dynamic measure : bins sizes are always recomputed.
    alpha = beta = 1/R(r) """
    if init: return
    res = compute_item_req(items)
    if res == 0: return
    res = [1/float(i) if i != 0 else 0 for i in res]
    for i in bins:
        i.size = 0
        for j, r in enumerate(i.remaining):
            i.size += res[j]*r

def dynamicItemsOneOverR(items, bins, init = False):
    """ Dynamic measure : items sizes are always recomputed.
    alpha = beta = 1/R(r) """
    if init: return
    res = compute_item_req(items)
    if res == 0: return
    res = [1/float(i) if i != 0 else 0 for i in res]
    for i in items:
        i.size = 0
        for j, r in enumerate(i.requirements):
            i.size += res[j]*r

########## Normalize by R/C ##########

def staticBinsROverC(items, bins, init = False):
    """ Static measure : bins sizes are updated once.
    alpha = beta = R(r)/C(r) """
    if init:
        dynamicBinsROverC(items, bins)

def staticItemsROverC(items, bins, init = False):
    """ Static measure : items sizes are updated once.
    alpha = beta = R(r)/C(r) """
    if init:
        dynamicItemsROverC(items, bins)

def dynamicBinsROverC(items, bins, init = False):
    """ Dynamic measure : bins sizes are always recomputed.
    alpha = beta = R(r)/C(r) """
    if init: return
    req = compute_item_req(items)
    if req == 0: return
    res = compute_bin_res(bins)
    if res == 0: return
    for i,v in enumerate(res):
        if v == 0: req[i] = 0
        else : req[i] /= float(v)

    for i in bins:
        i.size = 0
        for j, r in enumerate(i.remaining):
            i.size += req[j]*r

def dynamicItemsROverC(items, bins, init = False):
    """ Dynamic measure : items sizes are always recomputed.
    alpha = beta = R(r)/C(r) """
    if init: return
    req = compute_item_req(items)
    if req == 0: return
    res = compute_bin_res(bins)
    if res == 0: return
    for i,v in enumerate(res):
        if v == 0: req[i] = 0
        else : req[i] /= float(v)

    for i in items:
        i.size = 0
        for j, r in enumerate(i.requirements):
            i.size += req[j]*r            
            
########## Norm based ##########
def norm(item, bin):
    # x is the coefficient minimizing sum_{p,m}((x*R(p,r)-C(m,r))^2)
    # in other word : x is the projection of C over normalized R
    x = 0
    div = 0
    for i,b in itertools.izip(item.requirements,bin.remaining):
        if i > b: return float('inf')
        x += i*b
        div += i*i
    x /= float(div)
    s = 0
    for i,b in itertools.izip(item.requirements,bin.remaining):
        s += (x*i-b)**2
    return s

def similarity(items,bins,init=False):
    """ Finds bins and items which are the most similar """
    if init: return
    best = float('inf')
    # without initialization, will crash if no item can be packed
    best_item = items[0]
    best_bin = bins[0]
    for i in items:
        for b in bins:
            n = norm(i,b)
            if n < best:
                best = n
                best_bin = b
                best_item = i
    
    for b in bins:
        if b == best_bin: b.size = 0
        else: b.size = 1
    for i in items:
        if i == best_item: i.size = 2
        else: i.size = 1


def dp(item, bin, normC, normR):
    """ dot product, if normR, normalize requirements by ||R|| and capacities by ||C||
    if normC, normalize requirements and capacities by ||C||
    Very unefficient : if we memorize previous results, dp on one bin only need
    to be computed on a given iteration """
    scal = 0
    normI = 0
    normB = 0
    for i,b in itertools.izip(item.requirements,bin.remaining):
        if i > b: return -1 # i cannot be packed into b
        scal += i*b
        normI += i*i
        normB += b*b
    if not normC and not normR:
        return scal
    if normR:
        return scal / (math.sqrt(normI)*math.sqrt(normB))
    return scal / float(normB)


def dot_product(items,bins,init=False, normC=False, normR=False):
    """ Finds bins and items which are the most similar, using dot product """
    if init: return # more efficient approach would use this step to initialize sizes
    best = -1
    # without initialization, will crash if no item can be packed
    best_item = items[0]
    best_bin = bins[0]
    for i in items:
        for b in bins:
            n = dp(i,b,normC,normR)
            if n > best:
                best = n
                best_bin = b
                best_item = i
    
    for b in bins:
        if b == best_bin: b.size = 0
        else: b.size = 1
    for i in items:
        if i == best_item: i.size = 2
        else: i.size = 1
        
def dp_nonorm(items,bins,init=False):
    dot_product(items,bins,init=False, normC=False, normR=False)
        
def dp_normC(items,bins,init=False):
    dot_product(items,bins,init=False, normC=True, normR=False)
    
def dp_normR(items,bins,init=False):
    dot_product(items,bins,init=False, normR=True)
        
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

    def testComputeRem(self):
        assert compute_item_req(self.items) == [14, 16, 19]
        assert compute_bin_res(self.bins) == [106, 10, 113]
        self.b1.add(self.i4)
        assert compute_bin_res(self.bins) == [106, 10, 113]
        self.b3.add(self.i3)
        assert compute_bin_res(self.bins) == [106, 9, 113]
        
    def testCMes(self):
        staticBinsOneOverC(self.items, self.bins, False)
        staticItemsOneOverC(self.items, self.bins, False)
        assert self.i1.size == 1; assert self.i2.size == 2;
        assert self.i3.size == 3; assert self.i4.size == 0;
        assert self.b1.size==1; assert self.b2.size==2; assert self.b3.size==3; 
        
        staticBinsOneOverC(self.items, self.bins, True)
        staticItemsOneOverC(self.items, self.bins, True)
        assert abs(self.i1.size - ( 1./106+2./10+9./113 )) < 10**-14
        assert abs(self.i2.size - ( 4./106+5./10+3./113 )) < 10**-14
        assert abs(self.i3.size - ( 1./10 )) < 10**-14
        assert abs(self.i4.size - ( 9./106+8./10+7./113 )) < 10**-14
        assert abs(self.b1.size - ( 5./106+8./10+4./113 )) < 10**-14
        assert abs(self.b2.size - ( 100./106+100./113 )) < 10**-14
        assert abs(self.b3.size - ( 1./106+2./10+9./113 )) < 10**-14
        
        self.bins.pop()
        dynamicBinsOneOverC(self.items, self.bins, True)
        dynamicItemsOneOverC(self.items, self.bins, True)
        assert abs(self.i1.size - ( 1./106+2./10+9./113 )) < 10**-14
        assert abs(self.i2.size - ( 4./106+5./10+3./113 )) < 10**-14
        assert abs(self.i3.size - ( 1./10 )) < 10**-14
        assert abs(self.i4.size - ( 9./106+8./10+7./113 )) < 10**-14
        assert abs(self.b1.size - ( 5./106+8./10+4./113 )) < 10**-14
        assert abs(self.b2.size - ( 100./106+100./113 )) < 10**-14
        assert abs(self.b3.size - ( 1./106+2./10+9./113 )) < 10**-14
        
        dynamicBinsOneOverC(self.items, self.bins)
        dynamicItemsOneOverC(self.items, self.bins)
        assert abs(self.i1.size - ( 1./105+2./8+9./104 )) < 10**-14
        assert abs(self.i2.size - ( 4./105+5./8+3./104 )) < 10**-14
        assert abs(self.i3.size - ( 1./8 )) < 10**-14
        assert abs(self.i4.size - ( 9./105+8./8+7./104 )) < 10**-14
        assert abs(self.b1.size - ( 5./105+8./8+4./104 )) < 10**-14
        assert abs(self.b2.size - (100./105+100./104)) < 10**-14
        assert abs(self.b3.size - ( 1./106+2./10+9./113 )) < 10**-14
        
    def testRMes(self):
        staticBinsOneOverR(self.items, self.bins, False)
        staticItemsOneOverR(self.items, self.bins, False)
        assert self.i1.size == 1; assert self.i2.size == 2;
        assert self.i3.size == 3; assert self.i4.size == 0;
        assert self.b1.size==1; assert self.b2.size==2; assert self.b3.size==3; 
        
        staticBinsOneOverR(self.items, self.bins, True)
        staticItemsOneOverR(self.items, self.bins, True)
        assert abs(self.i1.size - ( 1./14+2./16+9./19 )) < 10**-14
        assert abs(self.i2.size - ( 4./14+5./16+3./19 )) < 10**-14
        assert abs(self.i3.size - ( 1./16 )) < 10**-14
        assert abs(self.i4.size - ( 9./14+8./16+7./19 )) < 10**-14
        assert abs(self.b1.size - ( 5./14+8./16+4./19 )) < 10**-14
        assert abs(self.b2.size - ( 100./14+100./19 )) < 10**-14
        assert abs(self.b3.size - ( 1./14+2./16+9./19 )) < 10**-14
        
        self.items.pop(0)
        dynamicBinsOneOverR(self.items, self.bins, True)
        dynamicItemsOneOverR(self.items, self.bins, True)
        assert abs(self.i1.size - ( 1./14+2./16+9./19 )) < 10**-14
        assert abs(self.i2.size - ( 4./14+5./16+3./19 )) < 10**-14
        assert abs(self.i3.size - ( 1./16 )) < 10**-14
        assert abs(self.i4.size - ( 9./14+8./16+7./19 )) < 10**-14
        assert abs(self.b1.size - ( 5./14+8./16+4./19 )) < 10**-14
        assert abs(self.b2.size - ( 100./14+100./19 )) < 10**-14
        assert abs(self.b3.size - ( 1./14+2./16+9./19 )) < 10**-14
        
        dynamicBinsOneOverR(self.items, self.bins)
        dynamicItemsOneOverR(self.items, self.bins)
        assert abs(self.i1.size - ( 1./5+2./8+9./12 )) < 10**-14
        assert abs(self.i2.size - ( 4./5+5./8+3./12 )) < 10**-14
        assert abs(self.i3.size - ( 1./8 )) < 10**-14
        assert abs(self.i4.size - ( 9./14+8./16+7./19 )) < 10**-14
        assert abs(self.b1.size - ( 5./5+8./8+4./12 )) < 10**-14
        assert abs(self.b2.size - (100./5+100./12)) < 10**-14
        assert abs(self.b3.size - ( 1./5+2./8+9./12 )) < 10**-14
        
    def testRCMes(self):
        staticBinsROverC(self.items, self.bins, False)
        staticItemsROverC(self.items, self.bins, False)
        assert self.i1.size == 1; assert self.i2.size == 2;
        assert self.i3.size == 3; assert self.i4.size == 0;
        assert self.b1.size==1; assert self.b2.size==2; assert self.b3.size==3; 
        
        staticBinsROverC(self.items, self.bins, True)
        staticItemsROverC(self.items, self.bins, True)
        assert abs(self.i1.size - ( 14./106.+2.*16./10.+9.*19./113. )) < 10**-14
        assert abs(self.i2.size - ( 4.*14./106.+5.*16./10.+3.*19./113. )) < 10**-14
        assert abs(self.i3.size - ( 16./10. )) < 10**-14
        assert abs(self.i4.size - ( 9.*14./106.+8.*16./10.+7.*19./113. )) < 10**-14
        assert abs(self.b1.size - ( 5.*14./106.+8.*16./10.+4.*19./113. )) < 10**-14
        assert abs(self.b2.size - ( 100.*14./106.+100.*19./113. )) < 10**-14
        assert abs(self.b3.size - ( 14./106.+2.*16./10.+9.*19./113. )) < 10**-14
        
        i=self.items.pop(2)
        assert self.b1.add(i)
        dynamicBinsROverC(self.items, self.bins, True)
        dynamicItemsROverC(self.items, self.bins, True)
        assert abs(self.i1.size - ( 14./106.+2.*16./10.+9.*19./113. )) < 10**-14
        assert abs(self.i2.size - ( 4.*14./106.+5.*16./10.+3.*19./113. )) < 10**-14
        assert abs(self.i3.size - ( 16./10. )) < 10**-14
        assert abs(self.i4.size - ( 9.*14./106.+8.*16./10.+7.*19./113. )) < 10**-14
        assert abs(self.b1.size - ( 5.*14./106.+8.*16./10.+4.*19./113. )) < 10**-14
        assert abs(self.b2.size - ( 100.*14./106.+100.*19./113. )) < 10**-14
        assert abs(self.b3.size - ( 14./106.+2.*16./10.+9.*19./113. )) < 10**-14
        
        dynamicBinsROverC(self.items, self.bins)
        dynamicItemsROverC(self.items, self.bins)
        assert abs(self.i1.size - ( 10./102.+2.*11./5.+9.*16./110. )) < 10**-14
        assert abs(self.i2.size - ( 4.*14./106.+5.*16./10.+3.*19./113. )) < 10**-14
        assert abs(self.i3.size - ( 11./5. )) < 10**-14
        assert abs(self.i4.size - ( 9.*10./102.+8.*11./5.+7.*16./110. )) < 10**-14
        assert abs(self.b1.size - ( 10./102.+3.*11./5.+16./110. )) < 10**-14
        assert abs(self.b2.size - ( 100.*10./102.+100.*16./110. )) < 10**-14
        assert abs(self.b3.size - ( 10./102.+2.*11./5.+9.*16./110. )) < 10**-14
        
        
if __name__ == "__main__":
    unittest.main()
