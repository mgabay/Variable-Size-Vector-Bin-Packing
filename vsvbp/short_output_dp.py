"""
Main program
    Generates and run banchmark
"""

from .container import *
from .heuristics import *
from .generator import *
from .measures import *

NUM_HEUR = 3

rank_t = 0
results = [0]*NUM_HEUR

hlist = ["dp","dp_normC","dp_normR"]

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
    min_fill = .8
    rem_cons = .8
    correlated_items = True
    dev = 0.1
    rt = 1.
    open_files('_unif_mf-'+str(min_fill)+'_rem_cons-'+
               str(rem_cons))
    #open_files('_unif-rare_mf-'+str(min_fill)+'_rem_cons-'+
    #           str(rem_cons)+'_rate-'+str(rt))
    #open_files('_correlated_mf-'+str(min_fill)+'_rem_cons-'+
    #           str(rem_cons)+'_sd-'+str(dev)+'_coritems-'+str(correlated_items))
    #open_files('_similar_mf-'+str(min_fill)+'_sd-'+str(dev))
    inst = run_pr(10, 2, min_fill, rem_cons,rate=rt,sd=dev,cori=correlated_items)
    print_res(inst)
    inst = run_pr(10, 5, min_fill, rem_cons,rate=rt,sd=dev,cori=correlated_items)
    print_res(inst)
    inst = run_pr(10, 10, min_fill, rem_cons,rate=rt,sd=dev,cori=correlated_items)
    print_res(inst)
    inst = run_pr(30, 2, min_fill, rem_cons,rate=rt,sd=dev,cori=correlated_items)
    print_res(inst)
    inst = run_pr(30, 5, min_fill, rem_cons,rate=rt,sd=dev,cori=correlated_items)
    print_res(inst)
    inst = run_pr(30, 10, min_fill, rem_cons,rate=rt,sd=dev,cori=correlated_items)
    print_res(inst)
    inst = run_pr(100, 2, min_fill, rem_cons,rate=rt,sd=dev,cori=correlated_items)
    print_res(inst)
    inst = run_pr(100, 5, min_fill, rem_cons,rate=rt,sd=dev,cori=correlated_items)
    print_res(inst)
    inst = run_pr(100, 10, min_fill, rem_cons,rate=rt,sd=dev,cori=correlated_items)
    print_res(inst)
    close_files()


def run_pr(num_bins,num_resources,min_fill,rem,rate=1.,sd=.1, cori = False):
    seed = 0
    num_instances = 100
    instances = []

    for i in xrange(num_instances):
        inst = generator(num_bins, num_resources, min_fill, unif_bin, seed, rem_cons=rem, proc_rate=rate)
        #inst = generator(num_bins, num_resources, min_fill, correlated_capacities, seed, rem_cons=rem, dev=sd, correlated_items = cori)
        #inst = generator(num_bins, num_resources, min_fill, similar, seed, dev=sd)
        instances.append(inst)
        seed += 1
        run_tests(inst)

    return instances


def run_tests(instance):
    instance.empty()
    ret = bfd_item_centric(instance.items[:], instance.bins[:], dp_nonorm, do_nothing)
    upd(instance,ret)

    instance.empty()
    ret = bfd_item_centric(instance.items[:], instance.bins[:], dp_normC, do_nothing)
    upd(instance,ret)

    instance.empty()
    ret = bfd_item_centric(instance.items[:], instance.bins[:], dp_normR, do_nothing)
    upd(instance,ret)
    return


def main():
    run()


if __name__ == "__main__":
    main()
