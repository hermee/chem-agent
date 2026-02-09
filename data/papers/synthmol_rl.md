# synhtemol-rl

SynthMol-MCTS issues:
- slow -> faster
- single -> multi objective



Implementation:
- RL-ChemProp (value function)
- MLP-RDKit (value functions)


- 10000 rollout

4 filters:

first 2 filters from SynthMol paper:
- prediction score >=0.5
- log solubility >= -4

second:
- tversky similarity between each hit molecules and all known antibiotics in training and CHEMBL antibiotics set
- max similarity <=0.6

Third:
- diverse set of hits by computing largest set of novel hits such that no tow compound in that set had a Tanimoto similarity >0.6

Fourth: to limit the diverse
- novel hits to a pratical number of compounds to test in wet lab

