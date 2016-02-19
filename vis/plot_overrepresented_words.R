library(ggplot2)

#####################
# Author Separation #
#####################

df <- read.table("overrepresented_words_per_segment_authors.txt", sep="\t")

colnames(df) <- c("holdout_directory", "segment_id", 
                  "segment_class", "class_A_words", "class_B_words")

# rename the values in the segment_class column
df$segment_class <- ifelse(df$segment_class=="A", "selected author", "non-selected author")

# add all desired factors to the holdout_directory column
levels(df$holdout_directory) <- c(levels(df$holdout_directory), "Jane Barker", 
                                  "Charles Brockden Brown", "Fanny Burney", "John Bunyan",
                                  "Henry Fielding", "Sarah Fielding", "Oliver Goldsmith",
                                  "Eliza Haywood", "Jane Austen", "Maria Edgeworth",
                                  "Daniel Defoe", "Margaret Cavendish", "Samuel Richardson",
                                  "Tobias Smollett", "Laurence Sterne", "Jonathan Swift") 

# rename holdout directory levels to provide more clear author names
df$holdout_directory[df$holdout_directory=="barker"] <- "Jane Barker" 
df$holdout_directory[df$holdout_directory=="browncha"] <- "Charles Brockden Brown" 
df$holdout_directory[df$holdout_directory=="burney"] <- "Fanny Burney" 
df$holdout_directory[df$holdout_directory=="ee22010"] <- "John Bunyan" 
df$holdout_directory[df$holdout_directory=="fieldinh"] <- "Henry Fielding" 
df$holdout_directory[df$holdout_directory=="fieldins"] <- "Sarah Fielding" 
df$holdout_directory[df$holdout_directory=="goldsmit"] <- "Oliver Goldsmith" 
df$holdout_directory[df$holdout_directory=="haywood"] <- "Eliza Haywood" 
df$holdout_directory[df$holdout_directory=="ncf0204"] <- "Jane Austen" 
df$holdout_directory[df$holdout_directory=="ncf1004"] <- "Maria Edgeworth" 
df$holdout_directory[df$holdout_directory=="pcs00636"] <- "Daniel Defoe" 
df$holdout_directory[df$holdout_directory=="pcs01555"] <- "Margaret Cavendish" 
df$holdout_directory[df$holdout_directory=="richards"] <- "Samuel Richardson" 
df$holdout_directory[df$holdout_directory=="smollett"] <- "Tobias Smollett" 
df$holdout_directory[df$holdout_directory=="sterne"] <- "Laurence Sterne" 
df$holdout_directory[df$holdout_directory=="swift"] <- "Jonathan Swift" 

# plot data
p <- ggplot(df, aes(x=class_A_words, y=class_B_words, color=segment_class)) +
  geom_point(alpha=.3) +
  facet_wrap(~holdout_directory, ncol=4) +
  xlab("Words overused by selected author") +
  ylab("Words overused by non-Selected authors") +
  ggtitle("Supervised Authorship Separation") +
  theme(legend.title=element_blank()) + #remove legend title
  guides(colour = guide_legend(override.aes = list(alpha=1))) #make legend alpha=1

ggsave("supervised_authorship_separation.png", plot=p)


#####################
# Gender Separation #
#####################

df <- read.table("overrepresented_words_per_segment.txt", sep="\t")
colnames(df) <- c("holdout_id", "record_path", "record_class", "female_words", "male_words")

# because we have a gender class factor with two levels (m/f),
# only show the separation for one (as showing the separation for the other)
# is an identical degree of separation
holdout_gender <- "female"

ggplot(subset(df, holdout_id=="female"), aes(x=female_words, y=male_words, colour=record_class)) +
  geom_point(alpha=.7)


####################
# Genre Separation #
####################

df <- read.table("overrepresented_words_per_segment_genre.txt", sep="\t")
colnames(df) <- c("holdout_level", "record_path", "record_class", 
                  "words_abundant_in_holdout_group", "words_abundant_in_rest_of_corpus")


ggplot(df, aes(x=words_abundant_in_holdout_group, y=words_abundant_in_rest_of_corpus, colour=record_class)) +
  geom_point(alpha=.3) +
  facet_wrap(~holdout_level)
  