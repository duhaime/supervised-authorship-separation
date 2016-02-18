import random, glob, shutil, os

# read in all infiles, and copy each to a new directory within
# ../random_distribution/{1:14}

if not os.path.exists("../data/random_distributions"):
  os.makedirs("../data/random_distributions")

for i in xrange(14):
  i += 1
  if not os.path.exists("../data/random_distributions/" + str(i)):
    os.makedirs("../data/random_distributions/" + str(i))

infiles = glob.glob("../data/stylometry_infiles/*/*.txt")
for i in infiles:
  # draw a random number 1:14
  random_number = random.randint(1,14)
  shutil.copy(i, "../data/random_distributions/" + str(random_number) + "/" + os.path.basename(i))

