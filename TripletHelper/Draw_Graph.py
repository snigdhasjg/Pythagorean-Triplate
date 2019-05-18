from TripletHelper.Saving import load_list
import matplotlib.pyplot as plt


def draw_treedepth_fitness(logbook, filename):
    gen = logbook.select("gen")
    fit_min = logbook.chapters["fitness"].select("min\t")
    size_avg = logbook.chapters["size"].select("avg\t")

    plt.subplot(211)
    plt.plot(gen, fit_min, "b-", label="Minimum Fitness")
    plt.xlabel("Generation")
    plt.ylabel("Fitness", color="b")
    leg = plt.legend(loc='upper right', shadow=True, fancybox=True)
    leg.get_frame().set_alpha(0.8)

    plt.subplot(212)
    plt.plot(gen, size_avg, "r-", label="Average Size")
    plt.xlabel("Generation")
    plt.ylabel("Size", color="r")
    leg = plt.legend(loc='upper right', shadow=True, fancybox=True)
    leg.get_frame().set_alpha(0.5)

    plt.savefig('../graph/{}20gen.png'.format(filename).replace('.txt', ''), dpi=100)
    # plt.show()


if __name__ == '__main__':
    log, fname = load_list()
    draw_treedepth_fitness(log, fname)
