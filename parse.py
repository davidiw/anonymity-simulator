#!/usr/bin/python2

import math
import pickle
import sys
from anon_sim import AnonymitySimulator
Pseudonym = AnonymitySimulator.Pseudonym
Client = AnonymitySimulator.Client

def mean_stddev(values):
  n = float(len(values))
  if n == 0:
    return (0, 0)
  elif n == 1:
    return (values[0], 0)

  sum_x = 0
  sum_x2 = 0

  for value in values:
    sum_x += value
    sum_x2 += (value * value)

  mean = sum_x / n

  var = (sum_x2 / n) - (mean * mean)
  if var > 0:
    stddev = math.sqrt(var)
  else:
    stddev = 0

  return (mean, stddev)

delivered = {}
delivery_times = {}
metric = {}
metric_correct = {}
intersection = {}

for path in sys.argv[1:]:
  # Switch to a regex and use the last 3 integers?
  parts = path.split(".")
  interval = int(parts[1])
  buddy_set = int(parts[2])
  min_anon = int(parts[3])

  f = open(path, "r")
  on_time = pickle.load(f)
  lost = pickle.load(f)
  delayed_times = pickle.load(f)
  pseudonyms = pickle.load(f)
  clients = pickle.load(f)
  f.close()

  if buddy_set not in delivered:
    delivered[buddy_set] = {}
    delivery_times[buddy_set] = {}
    metric[buddy_set] = {}
    metric_correct[buddy_set] = {}
    intersection[buddy_set] = {}

  cbs = delivered[buddy_set]
  numerator = on_time + len(delayed_times)
  denominator = numerator + lost
  cbs[interval] = numerator / float(denominator)

  delivery_times[buddy_set][interval] = [0 for num in range(on_time)]
  cdt = delivery_times[buddy_set][interval]
  for dtime in delayed_times:
    cdt.append(dtime)
  
  metric[buddy_set][interval] = []
  cm = metric[buddy_set][interval]
  metric_correct[buddy_set][interval] = []
  cmc = metric_correct[buddy_set][interval]
  intersection[buddy_set][interval] = []
  ci = intersection[buddy_set][interval]

#  result = {}
  for pseudonym in pseudonyms:
    if len(pseudonyms) == len(pseudonym.clients):
      continue

#    max_idx = -1
#    max_value = 0
#    accumulated = 0
#    same = 0
#    near = 0
#    up_own = own_value * 1.1
#    down_own = own_value * 0.9

    degree = 0.0
    prob = []
    max_rank = max(pseudonym.client_rank)
    own_rank = 0
    own_value = pseudonym.client_rank[pseudonym.uid]
    for cuid in pseudonym.client_rank.keys():
      cvalue = pseudonym.client_rank[cuid]
#      accumulated += cvalue
#      if cvalue > max_value:
#        max_value = cvalue
#        max_idx = cuid
      cprob = cvalue / float(max_rank)
      prob.append(cprob)
      degree += cprob
      if cvalue > own_value:
        own_rank += 1
#      if cvalue == own_value:
#        same += 1
#      if cvalue > down_own and cvalue < up_own:
#        near += 1

    prob = [cprob / degree for cprob in prob]
    h_x = reduce(lambda x, y: x + y, map(lambda x: x * math.log(x, 2), prob))
    print h_x
    cm.append(-1 * h_x / math.log(len(prob), 2))
    ci.append(len(pseudonym.clients))
    cmc.append(1 if own_rank == 0 else 0)
#    result[pseudonym.uid] = max_idx
#    prob = own_value / float(accumulated)
#    cm.append(prob)
#    to_print.append((pseudonym.uid, max_idx, max_value, own_rank, own_value, same, near, prob))

buddy_sets = delivered.keys()
buddy_sets.sort()

intervals = delivered[buddy_sets[0]].keys()
intervals.sort()

f = open("delivered.data", "w+")
f.write("#")
for interval in intervals:
  f.write(" %s" % interval)

for buddy_set in buddy_sets:
  f.write("\n%s" % buddy_set)
  for interval in intervals:
    val = delivered[buddy_set][interval] if interval in delivered[buddy_set] \
      else 0
    f.write(" %s" % val)
f.close()

f = open("delivery_times.data", "w+")
f.write("#")
for interval in intervals:
  f.write(" %s" % interval)

for buddy_set in buddy_sets:
  f.write("\n%s" % buddy_set)
  for interval in intervals:
    val = delivery_times[buddy_set][interval] \
      if interval in delivery_times[buddy_set] \
      else [0]
    val = mean_stddev(val)
    f.write(" %s %s" % (val[0], val[1]))
f.close()

f = open("intersection.data", "w+")
f.write("#")
for interval in intervals:
  f.write(" %s" % interval)

for buddy_set in buddy_sets:
  f.write("\n%s" % buddy_set)
  for interval in intervals:
    val = intersection[buddy_set][interval] if interval in intersection[buddy_set] \
      else [0]
    summed = 0.0
    for value in val:
      summed += (1 / value)
    val = summed / float(len(val))
    f.write(" %s" % val)
f.close()

f = open("intersection_worst.data", "w+")
f.write("#")
for interval in intervals:
  f.write(" %s" % interval)

for buddy_set in buddy_sets:
  f.write("\n%s" % buddy_set)
  for interval in intervals:
    val = intersection[buddy_set][interval] if interval in intersection[buddy_set] \
      else [1]
    val = 1 / min(val)
    f.write(" %s" % val)
f.close()

f = open("entropy.data", "w+")
f.write("#")
for interval in intervals:
  f.write(" %s" % interval)

for buddy_set in buddy_sets:
  f.write("\n%s" % buddy_set)
  for interval in intervals:
    val = metric[buddy_set][interval] if interval in metric[buddy_set] \
      else [0]
    val = sum(val) / float(len(val))
    f.write(" %s" % val)
f.close()

f = open("entropy_worst.data", "w+")
f.write("#")
for interval in intervals:
  f.write(" %s" % interval)

for buddy_set in buddy_sets:
  f.write("\n%s" % buddy_set)
  for interval in intervals:
    val = metric[buddy_set][interval] if interval in metric[buddy_set] \
      else [0]
    val = min(val)
    f.write(" %s" % val)
f.close()

f = open("probability_correct.data", "w+")
f.write("#")
for interval in intervals:
  f.write(" %s" % interval)

for buddy_set in buddy_sets:
  f.write("\n%s" % buddy_set)
  for interval in intervals:
    val = metric_correct[buddy_set][interval] if interval in metric_correct[buddy_set] \
      else [0]
    val = sum(val) / float(len(val))
    f.write(" %s" % val)
f.close()

f = open("degree.data", "w+")
f.write("#")
for interval in intervals:
  f.write(" %s" % interval)

for buddy_set in buddy_sets:
  f.write("\n%s" % buddy_set)
  for interval in intervals:
    val = intersection[buddy_set][interval] if interval in intersection[buddy_set] \
      else [1]
    val = math.log(sum(val), 2)
    f.write(" %s" % val)
f.close()
