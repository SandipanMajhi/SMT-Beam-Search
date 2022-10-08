## Results -

#### Coverage Decoder Results : 
```
k (stack size limit - 2000)     Logprob (tm+lm)
    5                           -1244.3014
    10                          -1240.8207
    15                          -1240.4486
    20                          -1241.1566
    32                          -1240.3612

Stack Size limit s (k = 32)     Logprob (tm+lm)
    10                          -1384.6094
    50                          -1295.4736
    100                         -1276.5399
    200                         -1260.343
    500                         -1252.3489
    1000                        -1242.3797
    1500                        -1240.8273
    2000                        -1240.3612

```

### Swap Reordering Decoder Results :
```
   k    Logprob (tm+lm)
   5    -1306.611
   10   -1301.298
   15   -1301.366
   20   -1300.526
   25   -1300.526


```

### Best Results Comparison :
```
    Model                       Logprob (tm+lm)
    Baseline                    -1354.6421
    Swap Reordering Model       -1300.526
    Cover Model                 -1240.3612


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
    > python3 coverage_decoder.py | python3 compute-model-score

To change the number of translations per phrase use -k like the following,
    > python3 reordering_decoder.py -k 32 | python3 compute-model-score

To change the stack size limit use -s like the following,
    > python3 reordering_decoder.py -s 500 | python3 compute-model-score


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
