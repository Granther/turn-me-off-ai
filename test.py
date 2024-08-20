from infer import Inference

inf = Inference()

for x in inf.user_infer_stream():
    print(x)