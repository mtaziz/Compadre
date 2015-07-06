import random

"initial pool of organisms for testing"
initial_pool_ = [(0.05, 0.1, 0.1),
                (0.04, 0.1, 0.2),
                (0.05, 0.2, 0.2),
                (0.048, 0.2, 1.0),
                (0.049, 1.0, 0.3)]

"best constants after 20 generations for n0*pmi + n1*frequency"
best_addition = [(0.005956095865679523, 0.8221104204538621, 0.007352881885527851), 
                (0.006145872038018127, 0.9009544044452957, 0.00858503010435533), 
                (0.006054769683361744, 1.1708753178730655, 0.02111922487975089), 
                (0.006088804122235905, 0.9196975120606208, 0.009456202138401908), 
                (0.005642846491121206, 0.9725525244043128, 0.016934542993977213)]

"best constants after 20 generations for (n0+pmi) * (n1+frequency)"

def run_ga(generations=10, organisms_per_generation=10, cutoff=5, initial_pool=initial_pool_, fitness=lambda o:o+1, max_=False):
    organisms = initial_pool
    for g in range(generations):
        """sort organisms by fitness and apply cutoff"""
        organisms_ = sorted(organisms, key=lambda f:fitness(f)[0], reverse=max_)[0:min(cutoff, len(organisms))]

        print "generation:%s organisms:\n%s\n\n" % (g, "\n".join([str((o, fitness(o)[0])) for o in organisms_]))

        """fill pool with random organisms generated from top orgs"""
        for index in range(organisms_per_generation - len(organisms_)):
            """pick two random organisms and combine their traits randomly"""
            org1 = organisms_[int(random.random() * (len(organisms_) - 1))]
            #org2 = organisms_[int(random.random() * (len(organisms) - 1))]
            rnd = random.random()
            #new_org = (rnd*org1[0] + (1-rnd)*org2[0], rnd*org1[1] + (1-rnd)*org2[1], rnd*org1[2] + (1-rnd)*org2[2])
            new_org = (abs(random.uniform(-1, 1)+org1[0]), abs(random.uniform(-1, 1)+org1[1]), abs(random.uniform(-1, 1)+org1[2]))
            organisms_.append(new_org)

        organisms = organisms_

    print "top organisms:\n%s" % sorted(organisms, key=lambda f:fitness(f)[0], reverse=max_)[0:cutoff]


