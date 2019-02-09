from examgen import BatchGenerator

batch = BatchGenerator()
batch.generate("exam1", 3, random_answers=True, merge=True, front_and_back=True)
