# list of libraries to load, add here for more
libs <- c('tm','wordcloud','caret','e1071','gmodels')
invisible(lapply(libs,library,verbose = FALSE,quietly = TRUE,warn.conflicts = FALSE,character.only = TRUE))

options(stringsAsFactors = FALSE)

# this script will manipulate tweet data
proj.dir <- '~/prj/Khoj/'
proj.data.dir <- 'data'

# set the current working dir
setwd(proj.dir)

# set the data dir
data.dir <- paste(getwd(),proj.data.dir,sep = "/")

# tweet data file that needs to loaded
tweet.data.file <- paste(data.dir,'tweet_location.csv', sep='/')

# load the file

t.data <- read.csv(file = tweet.data.file,header = T, sep = ",", encoding = "UTF-8")

# add a new column, tweet_sentiment randomly
# 0 = neutral, 1 = +ive, 2 = -ive
set.seed(5)
rand.tweet.sentiment <- sample(c(0,1,2),nrow(t.data),replace = TRUE)
t.data$tweet_sentiment <- factor(rand.tweet.sentiment, levels=c(0,1,2), labels=c('neutral','positive','negative'))


Encoding(t.data$tweet_text) <- 'UTF-8'

get_clean_corpus <- function(iCorpus)
{
  # convert each word to UTF-8
  # to remove hindi words, change UTF-8 to ascii
  tmp.corpus <- tm_map(iCorpus,
                         content_transformer(function(x) iconv(x,to='UTF-8')),
                         mc.cores=1)

  # remove numbers from tweet
  tmp.corpus <- tm_map(tmp.corpus,content_transformer(removeNumbers),
                               mc.cores=1)

  # remove stop words
  tmp.corpus <- tm_map(tmp.corpus,removeWords,stopwords(),mc.cores=1)

  # remove punctuation and strip whitespace between words ( we did in python too)
  tmp.corpus <- tm_map(tmp.corpus,
                               content_transformer(removePunctuation),mc.cores=1)
  tmp.corpus <- tm_map(tmp.corpus,
                               content_transformer(stripWhitespace),mc.cores=1)

  # do stemming
  tmp.corpus <- tm_map(tmp.corpus,
                               content_transformer(stemDocument),mc.cores=1)

  return (tmp.corpus)

}

# Create a clean tweet corpus
tweet.corpus <- get_clean_corpus(Corpus(x = VectorSource(x = t.data$tweet_text)))

strsplit_space_tokenizer <- function(x)
{
  unlist(strsplit(as.character(x), "[[:space:]]+"))
}

# now tweets are cleaned, we will tokenize each tweet
# From here, we'll be able to perform analyses involving word frequency.

tweet.dtm <- DocumentTermMatrix(tweet.corpus,control=list(tokenize=strsplit_space_tokenizer))

#tweet.dtm <- removeSparseTerms(x = tweet.dtm, sparse = 0.2)

# tried to create word cloud with hindi words
# mat <- as.matrix(tweet.dtm)
# freq <- colSums(mat)
# freq <- sort(freq,decreasing = TRUE)
# words <- names(freq)
# head(words)
# wordcloud(words[4:5],freq[4:5])
#
# wordcloud(clean.tweet.corpus, scale=c(5,0.5), max.words=100,min.freq = 40, random.order=FALSE, rot.per=0.35,use.r.layout=FALSE, colors=brewer.pal(8, 'Dark2'))

# now lets partition the raw data set into trainig and test data set
# we are not creating validate set. We wil do later

in_train <- createDataPartition(t.data$tweet_sentiment, p = 0.75, list = FALSE)

# raw data frame
tweet.raw.train <- t.data[in_train, ]
tweet.raw.test <- t.data[-in_train, ]

# document term matrix
tweet.dtm.train <- tweet.dtm[in_train,]
tweet.dtm.test <- tweet.dtm[-in_train,]

# tweet corpus
tweet.corpus.train <- tweet.corpus[in_train ]
tweet.corpus.test <- tweet.corpus[-in_train]

# now creating indicator features for frequent words
# this is basically creating a reduced training and test data set by specifying
# the dictionary. Dictionary is created from earlier document term matrix and have words
# appear at least 3 times

tweet.train <- DocumentTermMatrix(tweet.corpus.train, list(dictionary = findFreqTerms(tweet.dtm.train, 3)))

tweet.test <- DocumentTermMatrix(tweet.corpus.test, list(dictionary = findFreqTerms(tweet.dtm.train, 3)))

convert_counts <- function(x)
{
  x <- ifelse(x > 0, 1, 0)
  x <- factor(x, levels = c(0, 1), labels = c("No", "Yes"))
  return(x)
}

tweet.train <- apply(X = tweet.train, MARGIN = 2,FUN = convert_counts)
tweet.test <- apply(X = tweet.test, MARGIN = 2, FUN = convert_counts)

# Training the model on the data

sentiment.classifier <- naiveBayes(tweet.train,tweet.raw.train$tweet_sentiment)

# The sentiment.classifier variable now contains a naiveBayes classifier object that can be used to make predictions.

tweet.pred <- predict(sentiment.classifier,tweet.test)

CrossTable(tweet.pred,tweet.raw.test$tweet_sentiment,prop.chisq = FALSE, prop.t = FALSE, dnn = c('predicted', 'actual'))

#library(package = ROCR,verbose = FALSE,quietly = TRUE,warn.conflicts = FALSE)
