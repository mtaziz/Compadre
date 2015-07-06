import random

initial_pool_ = [(0.05, 0.1, 0.1),
                (0.04, 0.1, 0.2),
                (0.05, 0.2, 0.2),
                (0.048, 0.2, 1.0),
                (0.049, 1.0, 0.3)]

initial_pool_2 = [(0.005956095865679523, 0.8221104204538621, 0.007352881885527851), 
                (0.006145872038018127, 0.9009544044452957, 0.00858503010435533), 
                (0.00588347273456366, 1.065019447789682, 0.02261439342501856), 
                (0.0056002259967936775, 1.0001733579751741, 0.05081497410394928), 
                (0.005710840555584344, 0.7446334868201906, 0.03861705005172988)]


def run_ga(generations=10, organisms_per_generation=10, cutoff=5, initial_pool=initial_pool_2, fitness=lambda o:o+1, max_=False):
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
            new_org = (abs(random.uniform(-1, 1)*0.1+org1[0]), abs(random.uniform(-1, 1)*0.1+org1[1]), abs(random.uniform(-1, 1)*0.1+org1[2]))
            organisms_.append(new_org)

        organisms = organisms_

    print "top organisms:\n%s" % sorted(organisms, key=lambda f:fitness(f)[0], reverse=max_)[0:cutoff]


