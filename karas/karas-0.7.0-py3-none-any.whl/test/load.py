import pickle

trainer = pickle.load(open('output/snapshot_iter_3750.pkl', 'rb'))
trainer.run()