#!/usr/bin/env python
import optparse
import sys
import models
from collections import namedtuple

optparser = optparse.OptionParser()
optparser.add_option("-i", "--input", dest="input", default="data/input", help="File containing sentences to translate (default=data/input)")
optparser.add_option("-t", "--translation-model", dest="tm", default="data/tm", help="File containing translation model (default=data/tm)")
optparser.add_option("-l", "--language-model", dest="lm", default="data/lm", help="File containing ARPA-format language model (default=data/lm)")
optparser.add_option("-n", "--num_sentences", dest="num_sents", default=sys.maxsize, type="int", help="Number of sentences to decode (default=no limit)")
optparser.add_option("-k", "--translations-per-phrase", dest="k", default=1, type="int", help="Limit on number of translations to consider per phrase (default=1)")
optparser.add_option("-s", "--stack-size", dest="s", default=1, type="int", help="Maximum stack size (default=1)")
optparser.add_option("-v", "--verbose", dest="verbose", action="store_true", default=False,  help="Verbose mode (default=off)")
opts = optparser.parse_args()[0]

##### FUNCTIONS ###########

def generate_swap_hypothesis(f, h, stacks, start, end):
  '''
    This function checks if the swaps in between the phrase splits may produce better results or not
    start : start of the phrase 
    end : ending of the phrase + 1
    ph_split : split the phrase f[start : end] into f[start : ph_split] and f[ph_split : end], where start <= ph_split < end
    logprob_ph1 : if f[start : ph_split] in tm, logprob of the first phrase part f[start : ph_split]
    logprob_ph2 : if f[ph_split : end] in tm, logprob of the second phrase part f[ph_split : end]
    hyp1_new : hypothesis of f[start : end] when f[ph_split : end] comes before f[start : ph_split], if both are in tm
  '''
  for ph_split in range(start+1, end ):
      if f[start:ph_split] in tm and f[ph_split : end] in tm:
        for ph1 in tm[f[start:ph_split]]:
          for ph2 in tm[f[ph_split : end]]:
            logprob_ph2 = h.logprob + ph2.logprob
            lm_state_ph2 = h.lm_state
            for word in ph2.english.split(): 
              (lm_state_ph2, word_logprob) = lm.score(lm_state_ph2, word)
              logprob_ph2 += word_logprob
            
            hyp2_new = hypothesis(logprob_ph2, lm_state_ph2, h, ph2)
            logprob_ph1 = logprob_ph2 + ph1.logprob
            lm_state_ph1 = lm_state_ph2
            for word in ph1.english.split():
              (lm_state_ph1, word_logprob) = lm.score(lm_state_ph1, word)
              logprob_ph1 += word_logprob
            
            logprob_ph1 += lm.end(lm_state_ph1) if end == len(f) else 0.0
            hyp1_new = hypothesis(logprob_ph1, lm_state_ph1, hyp2_new, ph1)
            if lm_state_ph1 not in stacks[end] or stacks[end][lm_state_ph1].logprob < logprob_ph1:
              stacks[end][lm_state_ph1] = hyp1_new

  return stacks

##### END OF FUNCTIONS#####

tm = models.TM(opts.tm, opts.k)
lm = models.LM(opts.lm)
french = [tuple(line.strip().split()) for line in open(opts.input).readlines()[:opts.num_sents]]

# tm should translate unknown words as-is with probability 1
for word in set(sum(french,())):
  if (word,) not in tm:
    tm[(word,)] = [models.phrase(word, 0.0)]

hypothesis = namedtuple("hypothesis", "logprob, lm_state, predecessor, phrase")

sys.stderr.write("Decoding %s...\n" % (opts.input,))
for f in french:
  # The following code implements a monotone decoding
  # algorithm (one that doesn't permute the target phrases).
  # Hence all hypotheses in stacks[i] represent translations of 
  # the first i words of the input sentence. You should generalize
  # this so that they can represent translations of *any* i words.
  initial_hypothesis = hypothesis(0.0, lm.begin(), None, None)
  stacks = [{} for _ in f] + [{}]
  stacks[0][lm.begin()] = initial_hypothesis
  for i, stack in enumerate(stacks[:-1]):
    for h in sorted(stack.values(),key=lambda h: -h.logprob)[:opts.s]: # prune
      for j in range(i+1,len(f)+1):
        if f[i:j] in tm:
          for phrase in tm[f[i:j]]:
            logprob = h.logprob + phrase.logprob
            lm_state = h.lm_state
            for word in phrase.english.split():
              (lm_state, word_logprob) = lm.score(lm_state, word)
              logprob += word_logprob
            logprob += lm.end(lm_state) if j == len(f) else 0.0
            new_hypothesis = hypothesis(logprob, lm_state, h, phrase)
            if lm_state not in stacks[j] or stacks[j][lm_state].logprob < logprob: # second case is recombination
              stacks[j][lm_state] = new_hypothesis 

        #### Reordering ####
        #### Consider a split between i and j, reverse the phrase splits
        #### Check if they are in tm and hypothesize that the phrases have swaps and get the log probs

        stacks = generate_swap_hypothesis(f, h, stacks, i, j)

  winner = max(stacks[-1].values(), key=lambda h: h.logprob)
  def extract_english(h): 
    return "" if h.predecessor is None else "%s%s " % (extract_english(h.predecessor), h.phrase.english)
  print(extract_english(winner))

  if opts.verbose:
    def extract_tm_logprob(h):
      return 0.0 if h.predecessor is None else h.phrase.logprob + extract_tm_logprob(h.predecessor)
    tm_logprob = extract_tm_logprob(winner)
    sys.stderr.write("LM = %f, TM = %f, Total = %f\n" % 
      (winner.logprob - tm_logprob, tm_logprob, winner.logprob))
