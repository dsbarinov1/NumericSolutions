import tkinter
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.patches import Circle

def click_wrapper(window):
    def onclick(event):
        ix = round(event.xdata)
        iy = round(event.ydata)
        window.scheme[iy, ix] = not window.scheme[iy, ix]
        ax = event.inaxes
        [p.remove() for p in reversed(ax.patches)]
        for (j, i), flag in np.ndenumerate(window.scheme):
            if flag:
                drawObject = Circle((i,j), radius=0.2, fill=True, color="black")
                ax.add_patch(drawObject)
        window.canvas.draw()
    return onclick


def draw_scheme_area(ax, mini_mode=False, scheme=None):
    ax.set_xticks([-0.45, 0, 1, 2, 3, 3.45])
    ax.set_yticks([-0.45, 0, 1, 2, 2.45])
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)
    if not mini_mode:
        ax.set_xticklabels(["", "i-2", "i-1", "i", "i+1", ""], fontsize=16)
        ax.set_yticklabels(["", "n-1", "n", "n+1", ""], fontsize=16)
        ax.tick_params(left=False, bottom=False)
        for i in range(0, 3):
            ax.axhline(i, color='black')
        for i in range(0, 4):
            ax.axvline(i, color='black')
    else:
        ax.set_xticklabels(["", "", "", "", "", ""], fontsize=4)
        ax.set_yticklabels(["", "", "", "", ""], fontsize=4)
        ax.tick_params(left=False, bottom=False)
        for i in range(0, 3):
            ax.axhline(i, color='black', linewidth=0.5, alpha=0.6)
        for i in range(0, 4):
            ax.axvline(i, color='black', linewidth=0.5, alpha=0.6)
        if scheme is not None:
            for (j, i), flag in np.ndenumerate(scheme):
                if flag:
                    drawObject = Circle((i, j), radius=0.2, fill=True, color="black")
                    ax.add_patch(drawObject)

class ChildWindow():
    def __init__(self, window, parent, destiny, idx):
        self.destiny = destiny
        self.idx = idx
        self.root = window
        self.window = window
        self.parent = parent
        self.window.geometry("700x600")
        self.f_top = tkinter.Frame(self.window, borderwidth=1)
        self.f_mid = tkinter.Frame(self.window, borderwidth=1)
        self.f_top.pack(fill=tkinter.BOTH, expand=True, padx=5, pady=5)
        self.f_mid.pack(fill=tkinter.BOTH, expand=True, padx=5, pady=5)
        self.scheme = np.array([
            [False, False, False, False],
            [False, False, False, False],
            [False, False, False, False]
            ])
        self.initUI(destiny)



    def choose_scheme(self):
        self.format_cheme()
        self.parent.set_scheme(self.scheme, self.idx)
        self.on_closing()


    def initUI(self, destiny):
        f_button = tkinter.Button(self.f_top, text="Применить", width=15, command=self.choose_scheme)
        f_button.pack(padx=5, side=tkinter.LEFT)
        fig = plt.figure()
        fig.canvas.mpl_connect('button_press_event', click_wrapper(self))
        ax = plt.gca()
        draw_scheme_area(ax)
        self.canvas = FigureCanvasTkAgg(fig, master=self.f_mid)
        self.canvas.get_tk_widget().pack(side=tkinter.TOP,  expand=0, padx=5, pady=5)
        self.canvas._tkcanvas.pack(side=tkinter.TOP,  expand=0, padx=5, pady=5)



    def on_closing(self):
        self.parent.destroy_child(self.idx)
        #plt.figure(self.idx + 1).clear()
        self.window.destroy()


    def format_cheme(self):
        while(np.any(self.scheme[-1,:]) == False):
            for i in range(self.scheme.shape[0]-1, 0, -1):
                self.scheme[i]=np.copy(self.scheme[i-1])
            self.scheme[0].fill(False)
        while (np.any(self.scheme[:, 0]) == False):
            for i in range(self.scheme.shape[1] - 1):
                self.scheme[:,i] = np.copy(self.scheme[:,i + 1])
            self.scheme[:,-1].fill(False)



    """
        sf = ScrolledFrame(self.root, width=570, height=570)
        sf.pack(side="top", expand=1, fill="both")
        sf.bind_arrow_keys(self.root)
        sf.bind_scroll_wheel(self.root)
        inner_frame = sf.display_widget(Frame)

        row = 2
        for scheme in scheme_dict:
            if scheme_dict[scheme][1] is not None:
                image = scheme_dict[scheme][1]
            else:
                image =unknown_image
            img = plt.imread(image)
            fig = plt.figure(row)
            ax = plt.gca()
            ax.axis('off')
            ax.set(xlim=(0, 50), ylim=(50, 0))
            ax.imshow(img, origin="upper")
            canvas = FigureCanvasTkAgg(fig, master=inner_frame)
            canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=0)
            canvas._tkcanvas.pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=0)
            """
    """
            button = Button(inner_frame, text=scheme, compound=tkinter.LEFT,
                            command=partial(self.choose_scheme, scheme))

            button.grid(row=row,
                       column=0,
                       padx=4,
                       pady=4)"""
    """
            row+=1
            
    """