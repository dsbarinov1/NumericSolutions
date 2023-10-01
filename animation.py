from computation import double_gauss_func,laying_L,stairs_step, B, SIGMA, SHIFT
import numpy as np
from matplotlib import pyplot as plt
from matplotlib import animation
from matplotlib.widgets import Button
path_to_image = ".\\images\\add.png"
j = 0
r = 0.8
h = 0.1
X_MAX = 30
XLIM = (0, X_MAX)
YLIM = (-0.5, 1.5)

stock_img = plt.imread(path_to_image)
fig, axs = plt.subplots(2, 2)
fig.tight_layout(pad=2.0)
lines = []
help_lines = []
steps_texts = []
names = ["two-dimensional", "three-dimensional"]
for ax in axs[0]:
    #for ax in row:
        ax.set(xlim=XLIM, ylim=YLIM)
        line, = ax.plot([], [], lw=2, color='blue')
        lines.append(line)
        help_line_1, = ax.plot([0, X_MAX], [1, 1], lw=2, linestyle='dashed', color='grey', alpha=0.4)
        help_line_2, = ax.plot([0, X_MAX], [0, 0], lw=2, linestyle='dashed', color='grey', alpha=0.4)
        help_lines.append(help_line_1)
        help_lines.append(help_line_2)
        steps_text = ax.text(0.02, 0.8, '', transform=ax.transAxes)
        steps_texts.append(steps_text)
for ax in axs[1]:
    ax.axis('off')
    ax.set(xlim=(0, stock_img.shape[1]), ylim=(stock_img.shape[0], 0))
    ax.imshow(stock_img, origin="upper")
for i in range(len(names)):
    axs[0][i].title.set_text(names[i])
X = np.linspace(0, X_MAX, int(X_MAX/h))
U2 = double_gauss_func(X, B, SIGMA, SHIFT)
U3_1 = double_gauss_func(X, B, SIGMA, SHIFT)
U3_2 = np.zeros(U3_1.size)
STEPS = 1


# initialization function: plot the background of each frame
def init():
    global X, U2, U3_1, U3_2, r, h
    y = double_gauss_func(X, B, SIGMA, SHIFT)
    for line in lines:
        line.set_data(X, y)
    for steps_text in steps_texts:
        steps_text.set_text('')
    U3_2 = laying_L(U3_1, r, h)
    U2 = laying_L(U2, r, h)
    return lines + help_lines + steps_texts

# animation function.  This is called sequentially
def animate(i):
    global X, U2, r, h, j, STEPS, U3_1, U3_2
    lines[0].set_data(X, U2)
    lines[1].set_data(X, U3_2)
    U2 = laying_L(U2, r, h, STEPS)
    U3_1, U3_2 = stairs_step(U3_1, U3_2, r, h, STEPS)
    j+=STEPS
    for steps_text in steps_texts[:2]:
        steps_text.set_text('steps = {}\niteration = {}'.format(STEPS,j))
    return lines + help_lines + steps_texts


def up(event):
    global STEPS
    STEPS+=1


def down(event):
    global STEPS
    if STEPS>1:
        STEPS-=1

axdown = fig.add_axes([0.65, 0.45, 0.1, 0.075])
axup = fig.add_axes([0.8, 0.45, 0.1, 0.075])
bup = Button(axup, 'steps++')
bup.on_clicked(up)
bdown = Button(axdown, 'steps--')
bdown.on_clicked(down)

    # call the animator.  blit=True means only re-draw the parts that have changed.
anim = animation.FuncAnimation(fig, animate, init_func=init,
                                   frames=200, interval=20, blit=True)
plt.show()