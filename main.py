import tkinter
from tkinter import Tk, BOTH, IntVar, StringVar, LEFT, messagebox
from tkinter.ttk import Frame,Progressbar, Label, Scale, Style
from matplotlib import pyplot as plt
import matplotlib
matplotlib.use('TkAgg')
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from functools import partial
import sys
from matplotlib import animation
from computation import double_gauss_func,laying_L,stairs_step, B, SIGMA, SHIFT, scheme_step
from child_windows import ChildWindow
iteration_counter = 0
r = 0.8
h = 0.1
X_MAX = 30
XLIM = (0, X_MAX)
YLIM = (-0.5, 1.5)

STOCK_IMG = plt.imread(".\\images\\add.png")
fig, axs = plt.subplots(2, 2)
axs = [ax for row in axs for ax in row]
fig.tight_layout(pad=2.0)
lines = [None]*4
help_lines = [[],[],[],[]]
steps_texts = [None]*4

X = np.linspace(0, X_MAX, int(X_MAX/h))
U1_arr = [double_gauss_func(X, B, SIGMA, SHIFT)]*4
U2_arr = [double_gauss_func(X, B, SIGMA, SHIFT)]*4
STEPS = SAVED_STEPS = 1
SCHEMES = [None]*4
IS_RUNNING = False
pause_button = None#объявится в основном окне, знаю что говнокод, но каждый раз тащить через параметры еще хуже
anim = None#та же фигня

def init():
    global iteration_counter, U1_arr, U2_arr, steps_texts, axs
    iteration_counter = 1
    for i in range(len(U1_arr)):
        U1_arr[i] = double_gauss_func(X, B, SIGMA, SHIFT)
    for i in range(len(U2_arr)):
        U2_arr[i] = laying_L(U1_arr[i], r, h, 1)
    for i in range(len(axs)):
        ax = axs[i]
        ax.set_aspect('auto')
        ax.clear()
        if SCHEMES[i] is not None:
            ax.axis('on')
            ax.set(xlim=XLIM, ylim=YLIM)
            ax.patch.set_facecolor('white')
            line, = ax.plot([], [], lw=2, color='blue')
            lines[i] = line
            help_line_1, = ax.plot([0, X_MAX], [1, 1], lw=2, linestyle='dashed', color='grey', alpha=0.4)
            help_line_2, = ax.plot([0, X_MAX], [0, 0], lw=2, linestyle='dashed', color='grey', alpha=0.4)
            help_lines[i] = [help_line_1, help_line_2]

            steps_text = ax.text(0.02, 0.8, '', transform=ax.transAxes)
            steps_texts[i] = steps_text
        else:
            ax.axis('off')
            ax.set(xlim=(0, STOCK_IMG.shape[1]), ylim=(STOCK_IMG.shape[0], 0))
            ax.imshow(STOCK_IMG, origin="upper")
    return steps_texts


def animate(iter):
    global SCHEMES, IS_RUNNING, lines, help_lines, X, U2_arr, U1_arr, r, h, STEPS, steps_texts, iteration_counter
    for i in range(len(SCHEMES)):
        if SCHEMES[i] is not None:
            if IS_RUNNING:
                lines[i].set_data(X, U2_arr[i])
                U1_arr[i], U2_arr[i] = scheme_step(U1_arr[i], U2_arr[i], SCHEMES[i], r, h, STEPS)
                iteration_counter += STEPS
                steps_texts[i].set_text('steps = {}\niteration = {}'.format(STEPS, iteration_counter))
                print(iter)

    return lines + steps_texts


def up(entry):
    global STEPS
    STEPS+=1
    entry.delete(0, tkinter.END)
    entry.insert(0, str(STEPS))


def down(entry):
    global STEPS
    if STEPS>1:
        STEPS-=1
    entry.delete(0, tkinter.END)
    entry.insert(0, str(STEPS))


def set_steps(entry):
    global STEPS
    STEPS = int(entry.get())


def stop_resume():
    global pause_button, IS_RUNNING, anim
    IS_RUNNING = not IS_RUNNING
    if IS_RUNNING:
        anim.resume()
        pause_button.configure(text="Стоп")
    else:
        anim.pause()
        pause_button.configure(text="Продолжить")


def start():
    global SCHEMES, STEPS, pause_button, IS_RUNNING
    not_none_cnt = 0
    for scheme in SCHEMES:
        if scheme is not None:
            not_none_cnt += 1
    if not_none_cnt > 0 and STEPS > 0:
        init()
        IS_RUNNING = True
        anim.resume()
        pause_button.configure(text="Стоп")


def go_to_iteration(entry):
    global iteration_counter, SCHEMES, lines, iteration_counter, IS_RUNNING
    target_iteration = int(entry.get())
    steps_to_target = abs(target_iteration - 1) if target_iteration < iteration_counter else target_iteration - iteration_counter
    for i in range(len(SCHEMES)):
        if SCHEMES[i] is not None:
            if target_iteration < iteration_counter:
                U1_arr[i] = double_gauss_func(X, B, SIGMA, SHIFT)
                U2_arr[i] = laying_L(U1_arr[i], r, h, 1)
            U1_arr[i], U2_arr[i] = scheme_step(U1_arr[i], U2_arr[i], SCHEMES[i], r, h, steps_to_target)
            lines[i].set_data(X, U2_arr[i])
    iteration_counter = target_iteration


def click_wrapper(window):
    def onclick(event):
        if event.inaxes:
            i = axs.index(event.inaxes)
            if window.schemes[i] is None:
                window.choose_scheme(i)

    return onclick


root = tkinter.Tk()


class MainWindow(tkinter.Frame):
    def __init__(self, parent):
        self.childWindows = [None]*4
        tkinter.Frame.__init__(self, parent)
        self.parent = parent
        self.parent.title("Главное меню")
        self.schemes = [None]*4
        self.f_top = tkinter.Frame(self, borderwidth=1)
        self.f_mid = tkinter.Frame(self, borderwidth=1)
        self.f_bot = tkinter.Frame(self, borderwidth=1)
        self.f_top.pack(fill=tkinter.BOTH, expand=True, padx=5, pady=5)
        self.f_mid.pack(fill=tkinter.BOTH, expand=True, padx=5, pady=5)
        self.f_bot.pack(fill=tkinter.BOTH, expand=True, padx=5, pady=5)
        self.pack(fill=tkinter.BOTH,padx=5,expand=True)
        #f_button = tkinter.Button(self.f_top, text="Выбрать функцию", width=15, command=self.choose_function)
        #f_button.pack(padx=5, side=tkinter.LEFT)
        self.plot()
        myFont = tkinter.font.Font(size=25)
        steps_label = tkinter.Label(self.f_top, text="Шаги:", font=myFont)
        steps_entry = tkinter.Entry(self.f_top, font=myFont, width=5)
        steps_entry.delete(0, tkinter.END)
        steps_entry.insert(0, "1")
        plus_button = tkinter.Button(self.f_top, text="+", width=5, command=partial(up,steps_entry) , font=myFont, background='#c3c3c3')
        minus_button = tkinter.Button(self.f_top, text="-", width=5, command=partial(down,steps_entry), font=myFont, background='#c3c3c3')
        set_button = tkinter.Button(self.f_top, text="Установить шаг", command=partial(set_steps,steps_entry), font=myFont, background='#c3c3c3')
        for obj in [set_button, plus_button, steps_entry, minus_button, steps_label]:
            obj.pack(padx=5, side=tkinter.RIGHT)
        start_b = tkinter.Button(self.f_mid, text="Начать", width=10,command=start, font=myFont, background='#c3c3c3')
        global pause_button
        pause_button = tkinter.Button(self.f_mid, text="Стоп", width=10, command=stop_resume, font=myFont, background='#c3c3c3')
        iteration_entry = tkinter.Entry(self.f_mid, font=myFont, width=5)
        iteration_entry.delete(0, tkinter.END)
        iteration_entry.insert(0, "1")
        iteration_button = tkinter.Button(self.f_mid, text="Перейти к итерации", command= partial(go_to_iteration,iteration_entry), font=myFont, background='#c3c3c3')
        for obj in [iteration_button, iteration_entry, pause_button, start_b]:
            obj.pack(padx=5, side=tkinter.RIGHT)


    def plot (self):
        global fig
        cid = fig.canvas.mpl_connect('button_press_event', click_wrapper(self))
        # fig.canvas.mpl_disconnect(cid)
        self.canvas = FigureCanvasTkAgg(fig, master=self.f_bot)
        toolbar = NavigationToolbar2Tk(self.canvas, self.f_bot)
        toolbar.update()
        tool = tkinter.Label(toolbar, text="")
        tool.pack(side=tkinter.TOP, expand=0)
        self.canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=0)
        self.canvas._tkcanvas.pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=0)
        self.update_plot()


    def update_plot(self):
        for i in range(len(axs)):
            ax = axs[i]
            ax.set(xlim=XLIM, ylim=YLIM)
            line, = ax.plot([], [], lw=2, color='blue')
            lines.append(line)
            help_line_1, = ax.plot([0, X_MAX], [1, 1], lw=2, linestyle='dashed', color='grey', alpha=0.4)
            help_line_2, = ax.plot([0, X_MAX], [0, 0], lw=2, linestyle='dashed', color='grey', alpha=0.4)
            help_lines[i].append(help_line_1)
            help_lines[i].append(help_line_2)
            steps_text = ax.text(0.02, 0.8, '', transform=ax.transAxes)
            steps_texts.append(steps_text)
            if SCHEMES[i] is None:
                #ax.axis('off')
                ax.set(xlim=(0, STOCK_IMG.shape[1]), ylim=(STOCK_IMG.shape[0], 0))
                ax.imshow(STOCK_IMG, origin="upper")

    def choose_function(self):
        if not self.childWindows[0]:
            self.childWindows[0] = tkinter.Toplevel(self.parent)
            w = ChildWindow(self.childWindows[0], self, "function", 0)
            self.childWindows[0].protocol("WM_DELETE_WINDOW", w.on_closing)
        else:
            self.childWindows[0].deiconify()


    def choose_scheme(self, idx):
        global IS_RUNNING
        if IS_RUNNING:
            stop_resume()
        if not self.childWindows[idx]:
            self.childWindows[idx] = tkinter.Toplevel(self.parent)
            w = ChildWindow(self.childWindows[idx], self, "scheme", idx)
            self.childWindows[idx].protocol("WM_DELETE_WINDOW", w.on_closing)
        else:
            self.childWindows[idx].deiconify()


    def destroy_child(self,idx):
        self.childWindows[idx] = None


    def set_scheme(self, scheme, idx):
        global SCHEMES
        self.schemes[idx] = scheme
        SCHEMES[idx] = scheme
        start()


def on_closing():
    #if messagebox.askokcancel("Выход", "Выйти из приложения?"):
        root.destroy()
        sys.exit(0)


def main():
    global app, stopRead, root
    root.geometry("900x700")
    root.protocol("WM_DELETE_WINDOW", on_closing)
    app = MainWindow(root)
    root.mainloop()


if __name__ == '__main__':
    anim = animation.FuncAnimation(fig, animate, init_func=init,
                                   frames=None, interval=20, blit=False)
    anim.pause()
    main()

"""
toolbar = NavigationToolbar2Tk(canvas, frame_top)
toolbar.update()

tool = tk.Button(toolbar, text="my tool")
tool.pack(side='left')#, fill='x', expand=True)

"""