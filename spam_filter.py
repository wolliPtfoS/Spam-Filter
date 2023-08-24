############################################################
# Imports
import collections
import email
import math
import os

############################################################
# Section 1: Spam Filter
############################################################


def load_tokens(email_path):
    file = open(email_path, "r", encoding = "latin")
    file = open(r"" + email_path, "r", encoding = "latin")
    message = email.message_from_file(file)
    iterator = email.iterators.body_line_iterator(message)

    return [y for x in iterator for y in x.split()]

def log_probs(email_paths, smoothing):
    dic = {}
    # this part helped me get used to using os, had to refer to the API 
    wordlist = [x for path in email_paths for x in load_tokens(path)]

    # get our frequencies, along with total amount of words
    word_freq = dictionary(wordlist)
    word_total = len(wordlist)

    for w in word_freq.keys():
        
        num = word_freq[w] + smoothing
        den = word_total + smoothing * (len(word_freq) + 1)
        prob = num / den
        
        dic[w] = math.log(prob)

    # utilize equation stated in the homework
    prob_unk = smoothing / (word_total + (smoothing * (len(word_freq) + 1)))

    # UNK is for new words
    dic["<UNK>"] = math.log(prob_unk)

    return dic
                    
# get our words along with how frequently they appear, using a simple loop
def dictionary(wordlist):
    total = {}
    for i in wordlist:
        total[i] = total.get(i, 0) + 1
    return total

class SpamFilter(object):

    # initializer as stated in the homework
    def __init__(self, spam_dir, ham_dir, smoothing):

        # more os shinanigans, originally tried utilizing DirEntry but it wasn't cooperating
        # found this better solution in the API
        spam_paths = [os.path.join(spam_dir, file) for file in os.listdir(spam_dir)]
        ham_paths = [os.path.join(ham_dir, file) for file in os.listdir(ham_dir)]

        self.spam_dic = log_probs(spam_paths, smoothing)
        self.ham_dic = log_probs(ham_paths, smoothing)

        total = len(spam_paths) + len(ham_paths)
        self.prob_spam = len(spam_paths) / total
        self.prob_ham = len(ham_paths) / total
    
    def is_spam(self, email_path):

        sum_spam = 0
        sum_ham = 0
        
        tokens = load_tokens(email_path)

        # loop through, if we can find our token in spam, add its entry to our count, otherwise add UNK
        # same for ham
        for token in tokens:
            if token in self.spam_dic:
                sum_spam += self.spam_dic[token]
            else:
                sum_spam += self.spam_dic["<UNK>"]
            if token in self.ham_dic:
                sum_ham += self.ham_dic[token]
            else:
                sum_ham += self.ham_dic["<UNK>"]
                
        return sum_spam > sum_ham

    def most_indicative_spam(self, n):
        return self.ind_helper(self.spam_dic, n)

    def most_indicative_ham(self, n):
        return self.ind_helper(self.ham_dic, n)


    def ind_helper(self, dic, n):
        result_dic = {}
        in_both = self.spam_dic.keys() & self.ham_dic.keys()
        
        # need to set our probabilities as 10 to the x power, otherwise we will
        # run into negatives (leads to issues with finding log)
        prob_spam = math.exp(self.prob_spam)
        prob_ham = math.exp(self.prob_ham)

        # loop through, calculating log of each word
        for w in in_both:
            num = math.exp(dic[w])

            prob_w = math.exp(self.spam_dic[w]) * prob_spam + math.exp(self.ham_dic[w]) * prob_ham

            result_dic[w] = math.log(num / prob_w)

        # ran into a little bit of a hiccup here sorting the dictionary
        # using reversed() led to length disagreement, so this is much
        # cleaner
        return sorted(result_dic, key = result_dic.get, reverse = True)[:n]
