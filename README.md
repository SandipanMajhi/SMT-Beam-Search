## Results -

#### Coverage Decoder Results : 
```
Stack Size      Total Logprob of TM
    10           -1384.609459
    50           -1295.473611
    100          -1276.539983
    200          -1260.343
    500          -1252.348908
    1000         -1242.379782
    1500         -1240.827388
    2000         -1240.361212
```

### Reordering Decoder Results :
```
   Total Logprob of TM = -1384.609459
```

## Collaborators -
Sandipan Majhi, MSE Computer Science, Johns Hopkins University\
Sakshi Patil, MSE Computer Science, Johns Hopkins University (https://github.com/skpatil1301)

## Code Information -


There are two python programs here (-h for usage):

- `decode` translates input sentences from French to English using swap reordering.
- `decode-ext` translates input sentences from French to English using Cover Decoder by      Hypothesis expansion.
- `compute-model-score` computes the model score of a translated sentence.
- `translations` contain the best model translation outputs.

These commands work in a pipeline. For example:

    > python3 reordering_decoder.py | python3 compute-model-score
    > python3  | python3 compute-model-score

To change the number of translations per phrase use -k like the following,
    > python3 decode -k 32 | python3 compute-model-score

To change the stack size limit use -s like the following,
    > python3 decode -s 500 | python3 compute-model-score


There is also a module:

- `model.py` implements very simple interfaces for language models
 and translation models, so you don't have to. 

You can finish the assignment without modifying this file at all. 
You should look at it if you need to understand the interface
to the translation and language model.

The `data` directory contains files derived from the Canadian Hansards,
originally aligned by Ulrich Germann:

- `input`: French sentences to translate.

- `tm`: a phrase-based translation model. Each line is in the form:

    French phrase ||| English phrase ||| log_10(translation_prob)

- `lm`: a trigram language model file in ARPA format.

    log_10(ngram_prob)   ngram   log_10(backoff_prob)

The language model and translation model are computed from the data 
in the align directory, using alignments from the Berkeley aligner.
