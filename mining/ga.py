import random

"initial pool of organisms for testing"
initial_pool_ = [(5, 0.1, 0.1),
                (5, 0.1, 0.2),
                (5, 0.2, 0.2),
                (5, 0.2, 1.0),
                (5, 1.0, 0.3)]

"best constants after ~60 generations for n0*pmi + n1*frequency"
best_addition = [(5, 0.3135673133977043, 0.004890210734243838),
                (5, 0.9699263089994359, 0.013003233775384704),
                (5, 0.9804099106296693, 0.012776263015842337),
                (5, 1.0953649343654606, 0.012729834994913869),
                (5, 1.0344276839102837, 0.012812949829223763)]

"""
great with agents_of_shield && amazon_fire
((0.0183513596938029, 0.3135673133977043, 0.004890210734243838), 2)
((0.2528731352604893, 0.9699263089994359, 0.013003233775384704), 2)
((0.2788266998623834, 0.9804099106296693, 0.012776263015842337), 2)
((0.381348689822024, 1.0953649343654606, 0.012729834994913869), 2)
((0.3886202489674002, 1.0344276839102837, 0.012812949829223763), 2)
"""

def run_ga(generations=10, organisms_per_generation=10, cutoff=5, initial_pool=initial_pool_, fitness=lambda o:o+1, max_=False):
    organisms = initial_pool
    for g in range(generations):
        """sort organisms by fitness and apply cutoff"""
        organisms_ = sorted(organisms, key=fitness, reverse=max_)[0:min(cutoff, len(organisms))]

        print "generation:%s organisms:\n%s\n\n" % (g, "\n".join([str((o, fitness(o))) for o in organisms_]))

        """fill pool with random organisms generated from top orgs"""
        for index in range(organisms_per_generation - len(organisms_)):
            """pick two random organisms and combine their traits randomly"""
            org1 = organisms_[int(random.random() * (len(organisms_) - 1))]
            new_org = (abs(random.uniform(-1, 1)+org1[0]), abs(random.uniform(-1, 1)*0.1+org1[1]), abs(random.uniform(-1, 1)+org1[2]))
            organisms_.append(new_org)

        organisms = organisms_

    print "top organisms:\n%s" % sorted(organisms, key=fitness, reverse=max_)[0:cutoff]


#run_ga(organisms_per_generation=100, cutoff=5, fitness=pmi_freq_fitness)