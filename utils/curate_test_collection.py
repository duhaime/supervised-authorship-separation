import codecs, glob, os, shutil
from collections import Counter, defaultdict

# retrieve a set number of texts from two classes
# e.g. male/female, within specified parameters

def clean_string(s):
  """Helper function that reads in a string and returns a cleaned version
  of that string"""
  return "".join(i for i in s if i in "abcdefghijklmnopqrstuvwxyz ")


def find_files(only_acceptable_genre=0):
  """Read in all files documented in the metadata file, and build up a hash table
  with form: d[class_label] = [file_0_with_class, file_1_with_class, ... 
  file_n_with_class]"""
  
  # make a counter that can record the number of samples
  # we take for each gender class
  sample_counter = Counter()

  # make a counter that counts the number of files for each class
  file_counter = Counter()

  # create a defaultdict whose values are lists to store
  # the curated samples
  curated_samples = defaultdict(list)

  metadata_dir = "/Users/dduhaime/Desktop/pq/analysis/data/lion/"
  metadata_file = "drama_metadata.txt"

  with codecs.open(metadata_dir + metadata_file, 'r','utf-8') as f:
    f = f.read().split("\n")
    for r in f[:-1]:
      sr = r.split("\t")

      ####################
      # Publication year #
      ####################

      # try to coerce the year field into an int
      try:
        pub_year = int(sr[7])
      except:
        continue
  
      # additionally, limit to years 1700-1800
      if pub_year < 1700:
        continue
      if pub_year > 1800:
        continue

      #########
      # Genre #
      #########

      # if the user has populated the only_acceptable_genre input field,
      # only consider records that have the predetermined genre (drama, poetry, prose) 
      if only_acceptable_genre:
        if sr[1] != genre:
          continue

      # find record genre (if any)
      record_genre = clean_string( sr[10].lower().replace("genre:","") )
      # if that record genre isn't in the global list of good record
      # genres, carry on
      if record_genre not in good_record_genres:
        continue 
      sample_counter[record_genre] += 1

      ##########
      # Gender #
      ##########

      # determine gender of author
      gender = sr[4]

      # only keep m/f records, but change the gender label to
      # male/female
      # if gender not in ["m","f"]:
      #  continue
      if gender == "m":
        gender = "male"
      elif gender == "f":
        gender = "female"

      #############
      # File Name #
      #############

      # extract the file name for the record
      file_name = sr[0].replace(".new","")

      # for each file, add that file to a counter dictionary
      # so we can keep track of the number of records
      # we've seen from within each file
      file_counter[file_name] += 1

      # add the current file to the samples, but append a uid
      # that indicates the index position of this record within
      # the file
      record_id = file_name + "_" + str(file_counter[file_name])
      curated_samples[record_genre].append(record_id)
  return file_counter, curated_samples


def copy_curated_records():
  """Given the curated records, copy those records into the
  appropriate output directories"""

  # identify the root directory of all files to be copied
  record_root_dir = "/Users/dduhaime/Desktop/pq/analysis/data/lion/txt/"
 
  for factor_level in curated_samples.iterkeys():

    # create the directory for this factor level in the output
    # directory (if necessary)
    if not os.path.exists(root_out_dir + "/" + factor_level + "/"):
      os.makedirs(root_out_dir + "/" + factor_level + "/")

    for record in curated_samples[factor_level]:

      # the given record's subdirectory {poetry, prose, drama}
      # is retrievable from its record path
      genre_subdir = record.split("\\")[0].split("lion_")[1]

      # now grab the filename itself
      record_file = record.split("\\")[1].split("_")[0]

      # subtract one from offset because the counter initializes each 
      # object's count at 1
      record_offset = int(record.split("_")[-1]) - 1

      # now find all records within the directory
      directory_path = record_root_dir + "/" + genre_subdir + "/" + record_file + "/" 
      directory_files = glob.glob(directory_path + "/*.txt")

      print record, record_root_dir + record_file + "/", record_offset, len(directory_files)
 
      if record_offset == len(directory_files):  
        continue

      # the file to be copied should now be the record in index position
      # record_offset within the directory files
      selected_file = directory_files[record_offset]
      output_location = root_out_dir + factor_level + "/" + record + ".txt"

      shutil.copy(selected_file, output_location)


if __name__ == "__main__":
  
  # create the output directory in which we'll store 
  # the files we grab
  root_out_dir = "../data/curated_collections/genre/"
  good_record_genres = ["comedy", "drama", "tragedy", "poetry", "farce", "english mystery and miracle plays", "prose fiction", "melodrama", "history", "comic opera", "opera", "masque", "entertainment", "burlesque", "pastoral", "moralities", "ballad opera", "tragedy drama", "university plays", "dramatisation of novel"]

  file_counter, curated_samples = find_files()
  copy_curated_records()
