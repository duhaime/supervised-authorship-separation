from __future__ import division
from nltk.corpus import stopwords
from collections import defaultdict
import glob, codecs, os, operator, multiprocessing

def assign_files_to_classes(files, holdout_directory):
  """
  Read in a glob path and return a dictionary
  that maps each file to its parent directory.
  (We will use the parent directory as the class 
  label for the files within the directory) 
  """
  file_to_class = {}
  for c, i in enumerate(files):
    parent_dir = i.split("/")[-2]

    # assign shakespeare to class A
    # and everyone else to class B
    if parent_dir == holdout_directory:
      class_label = "A"
    else:
      class_label = "B"

    file_to_class[i] = class_label
  return file_to_class


def get_segments(l, n):
  """
  Yield successive n-sized chunks from l.
  """
  for i in xrange(0, len(l), n):
    yield l[i:i+n]


def clean_string(s):
  """
  Read in a string s and return a cleaned
  representation of that string
  """
  return s
  s = ''.join(i for i in s.lower() if i in alphabet)
  s = " ".join(w for w in s.split() if w not in stopwords)
  return s


def get_overrepresented_words(files, file_to_class, holdout_directory, n=500):
  """
  Read in a glob path, find the number of 2000 word
  chunks from class A and class B texts that contain each 
  word. Then return the n words that are more over and 
  underrepresented in class A
  """

  # create the hash table that contains the n most overrepresented
  # words in each class
  overrepresented_words = defaultdict(lambda: defaultdict(list))

  # create a hash table that will store
  # d[class_label][word] = number_of_segments_from_class_with_word
  # for each word in the corpus
  word_counter = defaultdict(lambda: defaultdict(int))

  # create another hash table to count the number of segments
  # in each class
  segment_counter = defaultdict(int)

  # loop over files, open and read each
  for i in files:
    with codecs.open(i, "r", "utf-8") as f:
      f = f.read()

      # retrieve the current file's class label
      file_class = file_to_class[i]

      # retrieve current file's words
      words = clean_string(f).split()

      # segment current file into 2000 word units
      segments = list(get_segments(words, 2000))

      # add the number of segments for the current file to 
      # the total number of segments for the current class
      segment_counter[file_class] += len(segments)

      # skip the last segment, as it won't contain 
      # the desired number of words
      for segment in segments:

        # deduplicate words in segment
        set_of_words_in_segment = list(set(segment))

        for word in set_of_words_in_segment:

            # increase the count of segments from the current
            # class that contain the current word
            word_counter[file_class][word] += 1

  # loop over classes in word_counter
  for current_class in word_counter.iterkeys():

    # given the current class, find the other class
    other_class = ''
    for c in segment_counter.iterkeys():
      if c != current_class:
        other_class = c

    # create a dictionary that contains the degree to which
    # each word is a 'marker' of the current class
    marker_words = defaultdict(float)

    # find the proportion of text segments in the class
    # that contain each word
    for word in word_counter[current_class].iterkeys():
      proportion_of_segments_with_word = (word_counter[current_class][word] / 
        segment_counter[current_class])

      # find the proportion of segments from the other class that
      # don't have the current word
      proportion_of_words_from_other_class_without_word = (
        (segment_counter[other_class] - word_counter[other_class][word]) / 
        segment_counter[other_class])

      marker_words[word] += (proportion_of_segments_with_word +
        proportion_of_words_from_other_class_without_word)

    # identify the n marker words with highest score
    sorted_marker_words = sorted(marker_words.items(), 
      key=operator.itemgetter(1), reverse=True)

    # nb: if you print sorted_marker_words[:n],
    # you can see how overrepresented each word is in
    # the current class
    #print sorted_marker_words[:n]

    # signal sum represents an aggregate measure of the strength of the
    # authorial signal captured for the present author
    signal_sum = sum(i[1] for i in sorted_marker_words[:n])
    print holdout_directory, signal_sum

    # iterate over the n words most overrepresented by the current class
    for t in sorted_marker_words[:n]:

      # add the word as a key in the overrepresented words hash
      # and set its value equal to the class in which the word
      # is overrepresented
      overrepresented_words[t[0]] = current_class
  return overrepresented_words


def count_markers_in_segments(infiles, file_to_class, overrepresented_words):
  """
  Read in a glob path of files, and for each, retrieve that
  file's class, then count the number of overrepresented words 
  it contains from both classes 
  """
  # create a hash table that will store the degree to which
  # each segment 
  overrepresented_words_per_segment = defaultdict(lambda: defaultdict(int))

  # loop over files, open and read each
  for i in infiles:
    with codecs.open(i, "r", "utf-8") as f:
      f = f.read()

      # retrieve the current file's class label
      file_class = file_to_class[i]

      # retrieve current file's words
      words = clean_string(f).split()

      # segment current file into 2000 word units
      word_segments = list(get_segments(words, 2000))

      for c, segment in enumerate(word_segments):

        # in order to be able to access the segment later
        # create a segment id = i + c
        segment_id = i + "." + str(c)

        unique_segment_words = list(set(segment))

        for word in unique_segment_words:

          # try to find the word in the overrepresented words.
          # If it's in the dictionary, determine which class that
          # word is overrepresented in (the class is stored as 
          # the value of the word in overrepresented_words), and
          # add one to the counter for the given class
          try:
            # retrieve the class the current word is overrepresented in
            overrepresented_class = overrepresented_words[word]
            overrepresented_words_per_segment[segment_id][overrepresented_class] += 1

          except TypeError:
            continue

        # to normalize, divide counts of both classes by the number of unique
        # words in the current segment
        for j in overrepresented_words_per_segment[segment_id].iterkeys():
          overrepresented_words_per_segment[segment_id][j] = (
            overrepresented_words_per_segment[segment_id][j] / len(unique_segment_words) )
  return overrepresented_words_per_segment

    
def write_overrepresented_words_per_segment(d, file_to_class, holdout_directory):
  """
  Read in a defaultdict object of form:  
    d[segment_identifier][class_label] = count_of_class_marker_words
  and write to disk a dataframe with the following form:
    segment_id segment_class class_A_word_count class_B_word_count
  where both class_A and class_B words are normalized [0:1]
  by the number of unique words in the segment
  """

  with codecs.open("overrepresented_words_per_segment.txt", 
    "a", "utf-8") as out:

    segment_ids = list(d.iterkeys())
    keys = list(d[segment_ids[0]].iterkeys())

    for segment_id in segment_ids:
      segment_class = file_to_class[ ".".join(segment_id.split(".")[:-1]) ]
      class_A_count = str( d[segment_id][keys[0]] )
      class_B_count = str( d[segment_id][keys[1]] )

      out.write( "\t".join([holdout_directory, segment_id, 
        segment_class, class_A_count, class_B_count]) + "\n" )

def main_process(holdout_directory):
  """
  Main process to be called. Each process will call this 
  process, and this process will call all the others.
  """
  infiles = glob.glob(target_directory + "/*/*.txt")
  file_to_class = assign_files_to_classes(
    infiles, holdout_directory)
  overrepresented_words = get_overrepresented_words(
    infiles, file_to_class, holdout_directory)
  overrepresented_words_per_segment = count_markers_in_segments(
    infiles, file_to_class, overrepresented_words)
  write_overrepresented_words_per_segment(
    overrepresented_words_per_segment, file_to_class, holdout_directory)


if __name__ == "__main__":
  # the 'holdout_directory' is the directory we wish to compare
  # to all other files in the corpus. It could be comprised of an
  # author's works, if we want to compare that author to other
  # authors
  target_directory = "../data/stylometry_infiles"

  alphabet = "abcdefghijklmnopqrstuvwxyz "
  stopwords = set(stopwords.words("english"))

  holdout_directories = [i.split("/")[-1] for i in glob.glob(target_directory + "/*")]
  main_pool = multiprocessing.Pool()
  for result in main_pool.imap(main_process, holdout_directories):
    pass
 
