import math
x = 1.1
for i in range(5):
    r = x - math.log(math.e**x+math.e**(-x),math.e)/math.tanh(x)
    print(r)
    x = r