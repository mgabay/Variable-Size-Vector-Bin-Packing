"""
Main program
    Generates and run banchmark
"""

from .container import *
from .heuristics import *
from .generator import *
from .measures import *

def repr_instance(inst):
    """ Print instance characteristics
    #bins ; #items ; mean %usage ; max % usage"""
    s=str(len(inst.bins))+";"+str(len(inst.items))+";"
    tot = [0.0]*len(inst.bins[0].capacities)
    req = tot[:]
    ll = len(req)
    for i in inst.items:
        for j, v in enumerate(i.requirements):
            req[j] += v
    for i in inst.bins:
        for j, v in enumerate(i.capacities):
            tot[j] += v
    for j, v in enumerate(tot):
        if v > 0:
            req[j] /= v
        else:
            ll -= 1
    s+= str(sum(req)/ll)+";"+str(max(req))+";"
    return s

def repr_ic(inst,ret,s):
    """ Print instance characteristics
    ;r_min ; #success ; success ?;"""
    if not ret:
        return s+';'+str(len(inst.items))+';'+str(len(inst.items))+';1;'
    return s+';'+str(ret[0][0])+';'+str(len(inst.items)-len(ret))+';0;'

def repr_bc(inst,ret,s):
    """ Print instance characteristics
    ; #success ; success ?;"""
    if not ret:
        return s+';'+str(len(inst.items))+';1;'
    return s+';'+str(ret[0][0])+';0;'


def open_files(suffix=''):
    global instance_file, ic_file, bc_file, bb_file, sbb_file
    instance_file = open('../instances'+suffix+'.csv', 'w')
    instance_file.write("#bins;#items;mean usage (%);max usage (%)\n")

    ic_file = open('../item_centric'+suffix+'.csv', 'w')
    ic_file.write(";do_nothing;;;;shuffleOnce;;;;shuffle;;;;staticOneOverC;;;;"+
        "dynamicOneOverC;;;;staticOneOverR;;;;dynamicsOneOverR;;;;staticROverC"+
        ";;;;dynamicROverC\n")
    ic_file.write(";r_min ; #success ; success ?;"*9+"\n")
    
    bc_file = open('../bin_centric'+suffix+'.csv', 'w')
    bc_file.write(";do_nothing;;;shuffleOnce;;;shuffle;;;staticOneOverC;;;"+
        "dynamicOneOverC;;;staticOneOverR;;;dynamicsOneOverR;;;staticROverC"+
        ";;;dynamicROverC\n")
    bc_file.write("; #success ; success ?;"*9+"\n")
    
    bb_file = open('../bin_balancing'+suffix+'.csv', 'w')
    bb_file.write(";do_nothing;;;;shuffleOnce;;;;shuffle;;;;staticOneOverC;;;;"+
        "dynamicOneOverC;;;;staticOneOverR;;;;dynamicsOneOverR;;;;staticROverC"+
        ";;;;dynamicROverC\n")
    bb_file.write(";r_min ; #success ; success ?;"*9+"\n")
    
    sbb_file = open('../single_bin_balancing'+suffix+'.csv', 'w')
    sbb_file.write(";do_nothing;;;;shuffleOnce;;;;shuffle;;;;staticOneOverC;;;;"+
        "dynamicOneOverC;;;;staticOneOverR;;;;dynamicsOneOverR;;;;staticROverC"+
        ";;;;dynamicROverC\n")
    sbb_file.write(";r_min ; #success ; success ?;"*9+"\n")
    
    
def close_files():
    instance_file.close()
    ic_file.close()
    bc_file.close()
    bb_file.close()
  
  
def run_benchmark():
    seed = 0
    num_instances = 100
    num_bins = 100
    num_resources = 5
    min_fill = .8
    rate=.25
    rem=.8
    sd = .2
    
    # open_files('_unif_'+str(num_bins)+'_'+str(num_resources))
    # open_files('_unif_rare_'+str(num_bins)+'_'+str(num_resources)+'_'+str(rate))
    #open_files('_cor_'+str(num_bins)+'_'+str(num_resources)+'_'+str(sd))
    open_files('_similar_'+str(num_bins)+'_'+str(num_resources)+'_'+str(sd))
    for i in xrange(num_instances):
        #inst = generator(num_bins, num_resources, min_fill, unif_bin, seed, proc_rate=rate)
        #inst = generator(num_bins, num_resources, min_fill, correlated_capacities, seed, rem_cons=rem, dev=sd, correlated_items = True)
        base = [random.randint(5,200) for i in xrange(num_resources)]
        inst = generator(num_bins, num_resources, min_fill, similar_items, seed, base_item=Item(base), dev=sd)
        instance_file.write(repr_instance(inst)+'\n')
        seed += 1
        run_tests(inst)
        instance_file.flush()
    close_files()
    

def run_tests(instance):
    # Item centric heuristics
    repr = ''
    instance.empty()
    ret = bfd_item_centric(instance.items[:], instance.bins[:], do_nothing, do_nothing)
    repr = repr_ic(instance,ret,repr)
    instance.empty()
    ret = bfd_item_centric(instance.items[:], instance.bins[:], shuffleItemsOnce,shuffleBinsOnce)
    repr = repr_ic(instance,ret,repr)
    instance.empty()
    ret = bfd_item_centric(instance.items[:], instance.bins[:], shuffleItems,shuffleBins)
    repr = repr_ic(instance,ret,repr)
    instance.empty()
    ret = bfd_item_centric(instance.items[:], instance.bins[:], staticItemsOneOverC,staticBinsOneOverC)
    repr = repr_ic(instance,ret,repr)
    instance.empty()
    ret = bfd_item_centric(instance.items[:], instance.bins[:], dynamicItemsOneOverC,dynamicBinsOneOverC)
    repr = repr_ic(instance,ret,repr)
    instance.empty()
    ret = bfd_item_centric(instance.items[:], instance.bins[:], staticItemsOneOverR,staticBinsOneOverR)
    repr = repr_ic(instance,ret,repr)
    instance.empty()
    ret = bfd_item_centric(instance.items[:], instance.bins[:], dynamicItemsOneOverR,dynamicBinsOneOverR)
    repr = repr_ic(instance,ret,repr)
    instance.empty()
    ret = bfd_item_centric(instance.items[:], instance.bins[:], staticItemsROverC,staticBinsROverC)
    repr = repr_ic(instance,ret,repr)
    instance.empty()
    ret = bfd_item_centric(instance.items[:], instance.bins[:], dynamicItemsROverC,dynamicBinsROverC)
    repr = repr_ic(instance,ret,repr)
    ic_file.write(repr+'\n')
    
    # Bin centric heuristics
    repr = ''
    instance.empty()
    ret = bfd_bin_centric(instance.items[:], instance.bins[:], do_nothing, do_nothing)
    repr = repr_bc(instance,ret,repr)
    instance.empty()
    ret = bfd_bin_centric(instance.items[:], instance.bins[:], shuffleItemsOnce,shuffleBinsOnce)
    repr = repr_bc(instance,ret,repr)
    instance.empty()
    ret = bfd_bin_centric(instance.items[:], instance.bins[:], shuffleItems,shuffleBins)
    repr = repr_bc(instance,ret,repr)
    instance.empty()
    ret = bfd_bin_centric(instance.items[:], instance.bins[:], staticItemsOneOverC,staticBinsOneOverC)
    repr = repr_bc(instance,ret,repr)
    instance.empty()
    ret = bfd_bin_centric(instance.items[:], instance.bins[:], dynamicItemsOneOverC,dynamicBinsOneOverC)
    repr = repr_bc(instance,ret,repr)
    instance.empty()
    ret = bfd_bin_centric(instance.items[:], instance.bins[:], staticItemsOneOverR,staticBinsOneOverR)
    repr = repr_bc(instance,ret,repr)
    instance.empty()
    ret = bfd_bin_centric(instance.items[:], instance.bins[:], dynamicItemsOneOverR,dynamicBinsOneOverR)
    repr = repr_bc(instance,ret,repr)
    instance.empty()
    ret = bfd_bin_centric(instance.items[:], instance.bins[:], staticItemsROverC,staticBinsROverC)
    repr = repr_bc(instance,ret,repr)
    instance.empty()
    ret = bfd_bin_centric(instance.items[:], instance.bins[:], dynamicItemsROverC,dynamicBinsROverC)
    repr = repr_bc(instance,ret,repr)
    bc_file.write(repr+'\n')
    
    # Bin balancing
    repr = ''
    instance.empty()
    ret = bin_balancing(instance.items[:], instance.bins[:], do_nothing, do_nothing)
    repr = repr_ic(instance,ret,repr)
    instance.empty()
    ret = bin_balancing(instance.items[:], instance.bins[:], shuffleItemsOnce,shuffleBinsOnce)
    repr = repr_ic(instance,ret,repr)
    instance.empty()
    ret = bin_balancing(instance.items[:], instance.bins[:], shuffleItems,shuffleBins)
    repr = repr_ic(instance,ret,repr)
    instance.empty()
    ret = bin_balancing(instance.items[:], instance.bins[:], staticItemsOneOverC,staticBinsOneOverC)
    repr = repr_ic(instance,ret,repr)
    instance.empty()
    ret = bin_balancing(instance.items[:], instance.bins[:], dynamicItemsOneOverC,dynamicBinsOneOverC)
    repr = repr_ic(instance,ret,repr)
    instance.empty()
    ret = bin_balancing(instance.items[:], instance.bins[:], staticItemsOneOverR,staticBinsOneOverR)
    repr = repr_ic(instance,ret,repr)
    instance.empty()
    ret = bin_balancing(instance.items[:], instance.bins[:], dynamicItemsOneOverR,dynamicBinsOneOverR)
    repr = repr_ic(instance,ret,repr)
    instance.empty()
    ret = bin_balancing(instance.items[:], instance.bins[:], staticItemsROverC,staticBinsROverC)
    repr = repr_ic(instance,ret,repr)
    instance.empty()
    ret = bin_balancing(instance.items[:], instance.bins[:], dynamicItemsROverC,dynamicBinsROverC)
    repr = repr_ic(instance,ret,repr)
    bb_file.write(repr+'\n')
    
    # Single Bin balancing
    repr = ''
    instance.empty()
    ret = bin_balancing(instance.items[:], instance.bins[:], do_nothing, do_nothing, single=True)
    repr = repr_ic(instance,ret,repr)
    instance.empty()
    ret = bin_balancing(instance.items[:], instance.bins[:], shuffleItemsOnce,shuffleBinsOnce, single=True)
    repr = repr_ic(instance,ret,repr)
    instance.empty()
    ret = bin_balancing(instance.items[:], instance.bins[:], shuffleItems,shuffleBins, single=True)
    repr = repr_ic(instance,ret,repr)
    instance.empty()
    ret = bin_balancing(instance.items[:], instance.bins[:], staticItemsOneOverC,staticBinsOneOverC, single=True)
    repr = repr_ic(instance,ret,repr)
    instance.empty()
    ret = bin_balancing(instance.items[:], instance.bins[:], dynamicItemsOneOverC,dynamicBinsOneOverC, single=True)
    repr = repr_ic(instance,ret,repr)
    instance.empty()
    ret = bin_balancing(instance.items[:], instance.bins[:], staticItemsOneOverR,staticBinsOneOverR, single=True)
    repr = repr_ic(instance,ret,repr)
    instance.empty()
    ret = bin_balancing(instance.items[:], instance.bins[:], dynamicItemsOneOverR,dynamicBinsOneOverR, single=True)
    repr = repr_ic(instance,ret,repr)
    instance.empty()
    ret = bin_balancing(instance.items[:], instance.bins[:], staticItemsROverC,staticBinsROverC, single=True)
    repr = repr_ic(instance,ret,repr)
    instance.empty()
    ret = bin_balancing(instance.items[:], instance.bins[:], dynamicItemsROverC,dynamicBinsROverC, single=True)
    repr = repr_ic(instance,ret,repr)
    sbb_file.write(repr+'\n')
    
if __name__ == "__main__":
    run_benchmark()
