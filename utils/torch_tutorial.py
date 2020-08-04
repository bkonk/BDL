import torch
import numpy as np

x = torch.ones(2,2,requires_grad=True)


y = x + 2

z = y * y * 3

out = z.mean()

out.backward()

print(x.grad)