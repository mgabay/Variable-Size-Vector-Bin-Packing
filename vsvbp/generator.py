import random
import itertools

from .container import *

""" Generate VSVBP instances
There are several various generators.
Instances are always feasible and Instance objects
are returned with such a solution
"""

################## Constants ####################
MAX_NUM_RES = 101
MAX_RES = 1000
MIN_RES = 10
MAX_TRY = 100 # max number of try to generate an item


################## Utility functions ####################
def volume(item, bin):
    """ Return a float in [0 ; 1] corresponding to the percentage
    of capacity used from the bin """
    ll = len(item.requirements)
    sm = 0
    for x in itertools.izip(item.requirements,bin.capacities):
        if x[0] > x[1]: return 2.0; # item cannot be packed
        if x[1]: sm += float(x[0])/x[1]
        else: ll -= 1

    return sm/ll
    #return sum(map(lambda x: float(x[0])/x[1] if x[1] else 1.0,
    #        itertools.izip(item.requirements,bin.capacities))) / len(item.requirements)

def update(items, item_req, bin, cur_vol):
    if max(item_req) <= 0: return False
    it = Item(item_req)
    if bin.add(it):
        items.append(it)
        return cur_vol + volume(it,bin)
    return False


################## Instances generator ####################

def unif_bin(num_resources, min_fill, rem_cons=1.0, proc_rate = 1.0, minr=MIN_RES, maxr=MAX_RES):
    """
    Makes a bin containing non-correlated items and
    Either Volume(items) > min_fill or a 0 weighted item was generated.
    If proc_rate < 1, the last resource is rare :
    it is 0 with probability 1-proc_rate
    Item capacities are generated in [0,rem_cons*b.remaining]
    """

    mf = min(min_fill, 1-1e-15) # helps getting rid of numerical instabilities
    bin_cap = [random.randint(minr,maxr) for x in xrange(num_resources)]
    if (proc_rate < 1) and (random.random() > proc_rate):
        bin_cap[-1] = 0
    b = Bin(bin_cap)
    item_vol = 0.0
    items = []
    while item_vol < mf:
        it_res = [random.randint(0,int(rem_cons*x)) for x in b.remaining]
        item_vol = update(items, it_res, b, item_vol)
        if not item_vol: break
        prev_vol = item_vol

    return items, b


def correlated_capacities(num_resources, min_fill, dev=.05,
                          rem_cons=1.0, correlated_items = False, minr=MIN_RES, maxr=MAX_RES):
    """
    Generates a bin. Bin capacities are correlated,
    and if correlated_items is True item requirements are correlated
    Either Volume(items) > min_fill or a 0 weighted item was generated.
    base*dev is the standard deviation
    Item capacities are generated in [0,rem_cons*b.remaining].
    """
    mf = min(min_fill, 1-1e-15) # helps getting rid of numerical instabilities
    base = random.randint(minr,maxr)
    mean = base*dev
    lbd = 1.0/mean
    bin_cap = [max(0,int(round(base+(random.expovariate(lbd)-mean))))
               for x in xrange(num_resources)]
    b = Bin(bin_cap)
    item_vol = 0.0
    items = []
    while item_vol < mf:
        if correlated_items:
            for tr in xrange(MAX_TRY):
                base = random.randint(1,int(rem_cons*min(bin_cap)))
                mean = base*dev
                lbd = 1.0/mean
                it_res = [max(0,int(round(base+(random.expovariate(lbd)-mean))))
                      for x in xrange(num_resources)]
                vl = update(items, it_res, b, item_vol)
                if vl: break
            item_vol = vl
        else:
            it_res = [random.randint(0,int(rem_cons*x)) for x in b.remaining]
            item_vol = update(items, it_res, b, item_vol)
        if not item_vol: break

    return items, b

def similar_items(num_resources, min_fill, base_item, dev=.05, minr=MIN_RES, maxr=MAX_RES):
    """
    Generates a bin. Bin capacities are not correlated.
    All items are similar to the given base item.
    base*dev is the standard deviation
    """
    mf = min(min_fill, 1-1e-15) # helps getting rid of numerical instabilities

    base = random.randint(minr,maxr)
    mean = base*dev
    lbd = 1.0/mean
    bin_cap = base_item.requirements[:]
    for i,v in enumerate(bin_cap):
        base = 5*v
        mean = base*dev
        lbd = 1.0/mean
        bin_cap[i] = max(0,int(round(base+(random.expovariate(lbd)-mean))))

    b = Bin(bin_cap)
    item_vol = 0.0
    items = []
    vl = 0
    while item_vol < mf:
        for tr in xrange(MAX_TRY):
            it_res = base_item.requirements[:]
            for i,base in enumerate(it_res):
                mean = base*dev
                lbd = 1.0/mean
                it_res[i] = max(0,int(round(base+(random.expovariate(lbd)-mean))))
            vl = update(items, it_res, b, item_vol)
            if vl : break
        item_vol = vl
        if not item_vol: break

    return items, b


def similar(num_resources, min_fill, dev=.05, minr=MIN_RES, maxr=MAX_RES):
    """
    Generates a bin using a uniform distribution. Bin capacities are not correlated.
    This bin contains items with weight ~ cap/5 + exponential perturbation.
    base*dev is the standard deviation
    """
    mf = min(min_fill, 1-1e-15) # helps getting rid of numerical instabilities
    # generates bin
    bin_cap = [random.randint(minr,maxr) for x in xrange(num_resources)]
    b = Bin(bin_cap)

    item_vol = 0.0
    items = []
    vl = 0
    while item_vol < mf:
        for tr in xrange(MAX_TRY):
            it_res = [bc/5. for bc in bin_cap]
            for i,base in enumerate(it_res):
                mean = base*dev
                lbd = 1.0/mean
                it_res[i] = max(0,int(round(base+(random.expovariate(lbd)-mean))))
            vl = update(items, it_res, b, item_vol)
            if vl : break
        item_vol = vl
        if not item_vol: break

    return items, b


def generator(num_bins, num_resources, min_fill, bin_generator = unif_bin, seed=-1, **kwargs):
    """
    Generates a non-correlated, uniformly distributed instance,
    with num_bins bins and Volume(items) < min_fill * Volume(bin)
    for any set of items in a bin.
    The instance is guaranteed to be feasible.
    """
    assert 0.0 < min_fill <= 1.0
    assert num_resources < MAX_NUM_RES
    if seed != -1: random.seed(seed)
    items = []
    bins = []
    for i in xrange(num_bins):
        it, bi = bin_generator(num_resources, min_fill, **kwargs)
        items.extend(it)
        bins.append(bi)

    random.shuffle(items)
    random.shuffle(bins)
    return Instance(items, bins)


class ItemBinTestCase(unittest.TestCase):
    def setUp(self):
        self.i1 = Item([1,2,9]); self.i2 = Item([4,5,3])
        self.i3 = Item([0,1,0]); self.i4 = Item([9,8,7])
        self.i1.size = 1; self.i2.size = 2; self.i3.size = 3; self.i4.size = 0;
        self.items = [self.i4, self.i3, self.i2, self.i1]
        self.b1=Bin([5,8,4]); self.b2=Bin([100,0,100]); self.b3=Bin([1,2,9]);
        self.b1.size=1; self.b2.size=2; self.b3.size=3;
        self.bins = [self.b1,self.b2,self.b3]
        self.ins = Instance(self.items, self.bins)

    def testInstance(self):
        assert str(self.ins)=="Items:\n"+str(self.items)+"\nBins:\n"+str(self.bins)

    def testGenerator(self):
        iss=generator(2,2,.5,seed=0)
        assert iss.items[1].requirements==[356, 197]
        assert iss.bins[1].capacities == [516,411]


def main():
    # Show example instances
    print "-" * 80
    print "Unif Bins"
    iss = generator(3, 3, .9, unif_bin)
    iss.empty()
    print iss
    print "-" * 80
    print "Correlated Bins"
    print generator(3, 3, .9, correlated_capacities)
    print "-" * 80
    print "Correlated Bins and Items"
    print generator(3, 3, .75, correlated_capacities, correlated_items = False)
    print "-" * 80
    print "Similar Items"
    print generator(3, 3, .75, similar_items, base_item=Item([50,50,50]),dev=.15,seed=0)

if __name__ == "__main__":
    main()
