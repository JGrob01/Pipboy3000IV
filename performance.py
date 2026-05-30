import pstats
p = pstats.Stats('thing.txt')
p.sort_stats('cumulative').print_stats(100)
