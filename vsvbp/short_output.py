"""
Main program
    Generates and run banchmark
"""

from .container import *
from .heuristics import *
from .generator import *
from .measures import *

NUM_HEUR = 31

rank_t = 0
results = [0]*NUM_HEUR

hlist = ["nothing","shuff1","1/C","1/R","R/C",
         "ic_shuff","ic_dyn_1/C","ic_dyn_1/R","ic_dyn_R/C",
         "bc_shuff","bc_dyn_1/C","bc_dyn_1/R","bc_dyn_R/C",
         "bb_nothing","bb_shuff1","bb_shuff","bb_st_1/C","bb_dyn_1/C","bb_st_1/R",
         "bb_dyn_1/R","bb_st_R/C","bb_dyn_R/C","sbb_nothing","sbb_shuff1","sbb_shuff",
         "sbb_st_1/C","sbb_dyn_1/C","sbb_st_1/R","sbb_dyn_1/R","sbb_st_R/C","sbb_dyn_R/C"]

def upd(inst,ret):
    """ Update results
    %packed / #success"""
    global results
    global rank_t
    dic = results[rank_t]
    if not dic:
        dic = {}
        dic['total'] = 0
        dic['sp_packed'] = 0.0
        dic['n_success'] = 0
        results[rank_t] = dic
    rank_t = (rank_t + 1) % NUM_HEUR
    
    dic['total'] += 1
    dic['sp_packed'] += float(len(inst.items)-len(ret))/len(inst.items)
    if not ret:
        dic['n_success'] += 1

def print_res(desc):
    global results
    s=repr_instance(desc)
    for r in results:
        s+=str(r['sp_packed'] / r['total']) + ';' + str(r['n_success']) + ';'
    instance_file.write(s+'\n')
    instance_file.flush()
    results = [0]*NUM_HEUR


def repr_instance(instances):
    """ Print instance characteristics
    #bins ; #resources; Avg #items ; Avg %usage ; Avg max % usage"""
    inst = instances[0]
    s = str(len(inst.bins)) + ';' + str(len(inst.items[0].requirements)) +';'
    
    ni = 0; usg = 0; max_usg = 0
    for inst in instances:
        ni += len(inst.items)
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
        usg += sum(req)/ll
        max_usg += max(req)
    
    s+= str(ni/len(instances))+";"+str(usg/len(instances))+";"+str(max_usg/len(instances))+";"
    return s

   
def open_files(suffix=''):
    global instance_file, ic_file, bc_file, bb_file, sbb_file
    instance_file = open('../results'+suffix+'.csv', 'w')
    s = '#bins ; #resources; Avg #items ; Avg %usage ; Avg max % usage;'
    for heu in hlist:
        s += heu+'_pn;'+heu+'_ns;'
    instance_file.write(s+'\n')
    instance_file.flush()
    
def close_files():
    instance_file.close()  
  
def run():
    min_fill = .7
    rem_cons = .8
    correlated_items = False
    dev = 0.2
    rt = .25
    global NUM_HEUR, results
    NUM_HEUR=1
    results = [0]
    #open_files('_unif-rare_mf-'+str(min_fill)+'_rem_cons-'+
    #           str(rem_cons)+'_rate'+str(rt))
    open_files('_correlated_mf-'+str(min_fill)+'_rem_cons-'+
               str(rem_cons)+'_sd-'+str(dev)+'_coritems-'+str(correlated_items))
    #open_files('_similar_mf-'+str(min_fill)+'_sd-'+str(dev))
    inst = run_pr(10, 2, min_fill, rem_cons,rate=.25,sd=dev,cori=correlated_items)
    print_res(inst)
    inst = run_pr(10, 5, min_fill, rem_cons,rate=.25,sd=dev,cori=correlated_items)
    print_res(inst)
    inst = run_pr(10, 10, min_fill, rem_cons,rate=.25,sd=dev,cori=correlated_items)
    print_res(inst)
    inst = run_pr(30, 2, min_fill, rem_cons,rate=.25,sd=dev,cori=correlated_items)
    print_res(inst)
    inst = run_pr(30, 5, min_fill, rem_cons,rate=.25,sd=dev,cori=correlated_items)
    print_res(inst)
    inst = run_pr(30, 10, min_fill, rem_cons,rate=.25,sd=dev,cori=correlated_items)
    print_res(inst)
    inst = run_pr(100, 2, min_fill, rem_cons,rate=.25,sd=dev,cori=correlated_items)
    print_res(inst)
    inst = run_pr(100, 5, min_fill, rem_cons,rate=.25,sd=dev,cori=correlated_items)
    print_res(inst)
    inst = run_pr(100, 10, min_fill, rem_cons,rate=.25,sd=dev,cori=correlated_items)
    print_res(inst)
    close_files()


def run_pr(num_bins,num_resources,min_fill,rem,rate=1.,sd=.1, cori = False):
    seed = 0
    num_instances = 100
    instances = []
    
    for i in xrange(num_instances):
        #inst = generator(num_bins, num_resources, min_fill, unif_bin, seed, rem_cons=rem, proc_rate=rate)
        inst = generator(num_bins, num_resources, min_fill, correlated_capacities, seed, rem_cons=rem, dev=sd, correlated_items = cori)
        #inst = generator(num_bins, num_resources, min_fill, similar, seed, dev=sd)
        instances.append(inst)
        seed += 1
        run_tests(inst)
    
    return instances

def run_similarity_measure(instance):
    instance.empty()
    ret = bfd_item_centric(instance.items[:], instance.bins[:], similarity, do_nothing)
    upd(instance,ret)
    
def run_tests(instance):
    global NUM_HEUR, results
    run_similarity_measure(instance)
    return
    
    # Static bfd ic/bc heuristics
    instance.empty()
    ret = bfd_item_centric(instance.items[:], instance.bins[:], do_nothing, do_nothing)
    upd(instance,ret)
    instance.empty()
    ret = bfd_item_centric(instance.items[:], instance.bins[:], shuffleItemsOnce,shuffleBinsOnce)
    upd(instance,ret)
    instance.empty()
    ret = bfd_item_centric(instance.items[:], instance.bins[:], staticItemsOneOverC,staticBinsOneOverC)
    upd(instance,ret)
    instance.empty()
    ret = bfd_item_centric(instance.items[:], instance.bins[:], staticItemsOneOverR,staticBinsOneOverR)
    upd(instance,ret)
    instance.empty()
    ret = bfd_item_centric(instance.items[:], instance.bins[:], staticItemsROverC,staticBinsROverC)
    upd(instance,ret)


    # Item centric dynamic heuristics
    instance.empty()
    ret = bfd_item_centric(instance.items[:], instance.bins[:], shuffleItems,shuffleBins)
    upd(instance,ret)
    instance.empty()
    ret = bfd_item_centric(instance.items[:], instance.bins[:], dynamicItemsOneOverC,dynamicBinsOneOverC)
    upd(instance,ret)
    instance.empty()
    ret = bfd_item_centric(instance.items[:], instance.bins[:], dynamicItemsOneOverR,dynamicBinsOneOverR)
    upd(instance,ret)
    instance.empty()
    ret = bfd_item_centric(instance.items[:], instance.bins[:], dynamicItemsROverC,dynamicBinsROverC)
    upd(instance,ret)
 
    # Bin centric dynamic heuristics
    instance.empty()
    ret = bfd_bin_centric(instance.items[:], instance.bins[:], shuffleItems,shuffleBins)
    upd(instance,ret)
    instance.empty()
    ret = bfd_bin_centric(instance.items[:], instance.bins[:], dynamicItemsOneOverC,dynamicBinsOneOverC)
    upd(instance,ret)
    instance.empty()
    ret = bfd_bin_centric(instance.items[:], instance.bins[:], dynamicItemsOneOverR,dynamicBinsOneOverR)
    upd(instance,ret)
    instance.empty()
    ret = bfd_bin_centric(instance.items[:], instance.bins[:], dynamicItemsROverC,dynamicBinsROverC)
    upd(instance,ret)
    
    # Bin balancing
    instance.empty()
    ret = bin_balancing(instance.items[:], instance.bins[:], do_nothing, do_nothing)
    upd(instance,ret)
    instance.empty()
    ret = bin_balancing(instance.items[:], instance.bins[:], shuffleItemsOnce,shuffleBinsOnce)
    upd(instance,ret)
    instance.empty()
    ret = bin_balancing(instance.items[:], instance.bins[:], shuffleItems,shuffleBins)
    upd(instance,ret)
    instance.empty()
    ret = bin_balancing(instance.items[:], instance.bins[:], staticItemsOneOverC,staticBinsOneOverC)
    upd(instance,ret)
    instance.empty()
    ret = bin_balancing(instance.items[:], instance.bins[:], dynamicItemsOneOverC,dynamicBinsOneOverC)
    upd(instance,ret)
    instance.empty()
    ret = bin_balancing(instance.items[:], instance.bins[:], staticItemsOneOverR,staticBinsOneOverR)
    upd(instance,ret)
    instance.empty()
    ret = bin_balancing(instance.items[:], instance.bins[:], dynamicItemsOneOverR,dynamicBinsOneOverR)
    upd(instance,ret)
    instance.empty()
    ret = bin_balancing(instance.items[:], instance.bins[:], staticItemsROverC,staticBinsROverC)
    upd(instance,ret)
    instance.empty()
    ret = bin_balancing(instance.items[:], instance.bins[:], dynamicItemsROverC,dynamicBinsROverC)
    upd(instance,ret)
    
    # Single Bin balancing
    instance.empty()
    ret = bin_balancing(instance.items[:], instance.bins[:], do_nothing, do_nothing, single=True)
    upd(instance,ret)
    instance.empty()
    ret = bin_balancing(instance.items[:], instance.bins[:], shuffleItemsOnce,shuffleBinsOnce, single=True)
    upd(instance,ret)
    instance.empty()
    ret = bin_balancing(instance.items[:], instance.bins[:], shuffleItems,shuffleBins, single=True)
    upd(instance,ret)
    instance.empty()
    ret = bin_balancing(instance.items[:], instance.bins[:], staticItemsOneOverC,staticBinsOneOverC, single=True)
    upd(instance,ret)
    instance.empty()
    ret = bin_balancing(instance.items[:], instance.bins[:], dynamicItemsOneOverC,dynamicBinsOneOverC, single=True)
    upd(instance,ret)
    instance.empty()
    ret = bin_balancing(instance.items[:], instance.bins[:], staticItemsOneOverR,staticBinsOneOverR, single=True)
    upd(instance,ret)
    instance.empty()
    ret = bin_balancing(instance.items[:], instance.bins[:], dynamicItemsOneOverR,dynamicBinsOneOverR, single=True)
    upd(instance,ret)
    instance.empty()
    ret = bin_balancing(instance.items[:], instance.bins[:], staticItemsROverC,staticBinsROverC, single=True)
    upd(instance,ret)
    instance.empty()
    ret = bin_balancing(instance.items[:], instance.bins[:], dynamicItemsROverC,dynamicBinsROverC, single=True)
    upd(instance,ret)
    
def main():
    run()
    
    
if __name__ == "__main__":
    main()
