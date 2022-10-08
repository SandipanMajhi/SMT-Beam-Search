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

tm = models.TM(opts.tm, opts.k)
lm = models.LM(opts.lm)
french = [tuple(line.strip().split()) for line in open(opts.input).readlines()[:opts.num_sents]]

####### Functions ##########

def expand_hypothesis(f_sent, hyp, pstart, pend):
  '''
    This function looks for the multiple possible hypothesis after a hypothesis. The expansion depends on the stack size
    cover : sets the bit of the words in the phrases when it is aligned
    hy_sets : combination of all the expanded hypothesis
  '''
  ### the translation tables does not have any translation for it or it is already translated
  if f_sent[pstart : pend ] not in tm: 
    return None

  for i in range(pstart, pend):
    if hyp.trans_vec[i] is 1:
      return None

  cover = [j for j in hyp.trans_vec]
  for i in range(pstart, pend):
    cover[i] = 1

  cover = tuple(cover)

  hyp_sets = list()
  for trans_ph in tm[f[pstart:pend]]:
    ph_logprob = hyp.logprob + trans_ph.logprob
    ph_lm_state = hyp.lm_state
    for word in trans_ph.english.split():
      (ph_lm_state, word_prob) = lm.score(ph_lm_state, word)
      ph_logprob += word_prob
    ph_logprob += lm.end(ph_lm_state) if sum(cover)==len(f) else 0.0
    ph_hyp = hypothesis(ph_logprob, ph_lm_state, hyp, trans_ph, cover, pstart, pend)
    hyp_sets.append(ph_hyp)

  return hyp_sets

def left_neighbour_hypothesis(f, h, stacks):
  '''
  Checks the expansion of hypothesis towards the left side neighbours of the predecessor phrase
  ph_len : length of the phrase covered by the hypothesis
  '''
  for i in range(0, h.ph_start):
    for j in range(i+1, h.ph_start + 1):
      expanded_hyps = expand_hypothesis(f,h,i,j)
      if expanded_hyps:
        for hyp in expanded_hyps:
          ph_len = sum(hyp.trans_vec)
          hyp_key = ((hyp.ph_start, hyp.ph_end), hyp.trans_vec)
          if hyp_key not in stacks[ph_len] or stacks[ph_len][hyp_key].logprob < hyp.logprob:
            stacks[ph_len][hyp_key] = hyp
  return stacks


def right_neighbour_hypothesis(f, h, stacks):
  '''
  Checks the expansion of the hypothesis towards the right side of the predecessor phrase
  ph_len : length of the phrase covered by the hypothesis
  '''
  for i in range(h.ph_end, len(f)):
    for j in range(i + 1, len(f) + 1):
      expanded_hyps = expand_hypothesis(f,h,i,j)
      if expanded_hyps:
        for hyp in expanded_hyps:
          ph_len = sum(hyp.trans_vec)
          hyp_key = ((hyp.ph_start, hyp.ph_end), hyp.trans_vec)
          if hyp_key not in stacks[ph_len] or stacks[ph_len][hyp_key].logprob < hyp.logprob:
            stacks[ph_len][hyp_key] = hyp
  return stacks

####### End of Functions #########

# tm should translate unknown words as-is with probability 1
for word in set(sum(french,())):
  if (word,) not in tm:
    tm[(word,)] = [models.phrase(word, 0.0)]

hypothesis = namedtuple("hypothesis", "logprob, lm_state, predecessor, phrase, trans_vec, ph_start, ph_end")

sys.stderr.write("Decoding %s...\n" % (opts.input,))
for f in french:
  stacks = [{} for _ in f] + [{}]
  trans_vec = [ 0 for _ in f ]
  trans_vec = tuple(trans_vec)
  
  initial_hypothesis = hypothesis(0.0, lm.begin(), None, None, trans_vec, 0, 0)
  stacks[0][((0,0), trans_vec)] = initial_hypothesis  #### start from the start tag
  for _, stack in enumerate(stacks[:-1]):
    for h in sorted(stack.values(),key=lambda h: -h.logprob)[:opts.s]: # prune
      stacks = left_neighbour_hypothesis(f,h,stacks)
      stacks = right_neighbour_hypothesis(f,h,stacks)

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
