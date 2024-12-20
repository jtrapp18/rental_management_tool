import matplotlib.pyplot as plt
import img2unicode
import os

# plt.plot([1, 2, 3, 4])
# plt.title("Show me some numbers!")
# plt.ylabel('some numbers')
# plt.savefig('temp.png')

optimizer = img2unicode.FastGenericDualOptimizer("block")
renderer = img2unicode.Renderer(default_optimizer=optimizer, max_h=60, max_w=160)

output = 'example.txt'
renderer.render_terminal('./example.png', output)

os.system(f'cat {output}')