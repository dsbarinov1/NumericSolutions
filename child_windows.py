import tkinter
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.patches import Circle
from tkinter import ttk
from start_functions import *

def click_wrapper(window):#обработка нажатий на график
    def onclick(event):
        if event.xdata is None or event.ydata is None:
            return
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


def draw_scheme_area(ax, mini_mode=False, scheme=None):#оформление сетки для отображения схемы
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


class SchemeWindow():#окно выбора схемы
    def __init__(self, window, parent, idx):
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
        self.initUI()


    def choose_scheme(self):
        self.format_cheme()
        self.parent.set_scheme(self.scheme, self.idx)
        self.on_closing()


    def initUI(self):
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


    def format_cheme(self):#когда схема выбрана, надо ее правильно поместить для функции расчета
        while(np.any(self.scheme[-1,:]) == False):
            for i in range(self.scheme.shape[0]-1, 0, -1):
                self.scheme[i]=np.copy(self.scheme[i-1])
            self.scheme[0].fill(False)
        while (np.any(self.scheme[:, 0]) == False):
            for i in range(self.scheme.shape[1] - 1):
                self.scheme[:,i] = np.copy(self.scheme[:,i + 1])
            self.scheme[:,-1].fill(False)



class StartConfigurationWindow():
    def __init__(self, window, parent, idx):
        self.idx = idx
        self.root = window
        self.window = window
        self.parent = parent
        self.f_names = [u'Гауссиан', u'Двойной Гауссиан', u'Ступенька', u'Треугольник']
        self.functions = [gauss_func, double_gauss_func, step_func, triangle_func]
        self.custom_function = custom_func
        self.init_child()


    def draw_graph(self, func):
        d = self.custom_func_entry.get() if self.is_custom == True else round(self.scale_par.get(), 1)
        if self.draw_flag == False:
            self.graphs_x = np.linspace(0, 10, 1001)
            graph_val = [func(d, x) for x in self.graphs_x]
            fig = Figure(figsize=(3.4, 2.5), dpi=100)
            ax = fig.add_subplot()
            ax.plot(self.graphs_x, graph_val, "-r", linewidth=3)
            ax.grid(color='black', linewidth=0.5)
            ax.set_title(f'{self.combobox.get()}')

            self.fig_canvas = FigureCanvasTkAgg(fig, master=self.window)
            #NavigationToolbar2Tk(self.fig_canvas)
            self.fig_canvas.get_tk_widget().place(x=2, y=2)
            self.draw_flag = True
        else:
            graph_val = [func(d, x) for x in self.graphs_x]
            fig = Figure(figsize=(3.4, 2.5), dpi=100)
            ax = fig.add_subplot()
            ax.plot(self.graphs_x, graph_val, "-r", linewidth=3)
            ax.grid(color='black', linewidth=0.5)
            ax.set_title(f'{self.combobox.get()}')
            self.fig_canvas = FigureCanvasTkAgg(fig, master=self.window)
            self.fig_canvas.get_tk_widget().place(x=2, y=2)

    def clear_my_draw(self):
        for item in self.fig_canvas.get_tk_widget().find_all():
            self.fig_canvas.get_tk_widget().delete(item)


    def btn_apply_func(self):
        self.label_just_d.destroy()
        label_just_d = ttk.Label(self.window, text=f"D = {round(self.scale_par.get(), 1)}", font=('Arial', 11))
        label_just_d.place(x=460, y=210)

        self.clear_my_draw()
        if self.custom_func_entry.get() == '':
            self.is_custom = False
            f_idx = self.f_names.index(self.combobox.get())
            self.draw_graph(self.functions[f_idx])
        else:
            self.is_custom = True
            self.draw_graph(self.custom_function)


    def btn_ok_func(self):
        f_idx = self.f_names.index(self.combobox.get())
        d = round(self.scale_par.get(), 1)
        self.parent.set_function(self.functions[f_idx], d)
        self.on_closing()


    def on_closing(self):
        self.parent.destroy_child(self.idx)
        self.window.destroy()


    def init_child(self):
        self.window.geometry("700x385+600+300")
        self.window.title("Выбор начального условия")

        self.combobox = ttk.Combobox(self.window, values=self.f_names, font=('Arial', 10))
        self.custom_func_entry = ttk.Entry(self.window, width=25)
        self.custom_func_entry.grid(column=1, row=0)
        self.custom_func_entry.place(x=460, y=250)
        self.combobox.current(0)  # индекс списка, график кот. будет по умолчанию
        self.combobox.place(x=460, y=70)

        self.scale_par = ttk.Scale(self.window, orient=tkinter.HORIZONTAL, length=160, from_=0.0, to=9.9, value=5)
        self.scale_par.place(x=460, y=150)

        self.draw_flag = False
        self.is_custom = False
        self.draw_graph(gauss_func)

        btn_cancel = ttk.Button(self.window, text='Закрыть', command=self.on_closing)
        btn_cancel.place(x=545, y=352)

        btn_ok1 = ttk.Button(self.window, text='Ок', command=self.btn_ok_func)
        btn_ok1.place(x=460, y=352)

        btn_apply = ttk.Button(self.window, text="Применить", command=self.btn_apply_func)
        btn_apply.place(x=500, y=290)

        label_start_cond = ttk.Label(self.window, text="Начальное условие:", font=('Arial', 11))
        label_start_cond.place(x=460, y=40)
        label_parameter_d = ttk.Label(self.window, text="Параметр D:", font=('Arial', 11))
        label_parameter_d.place(x=460, y=120)
        self.label_just_d = ttk.Label(self.window, text=f"D = {round(self.scale_par.get(), 1)}", font=('Arial', 11))
        self.label_just_d.place(x=460, y=210)
        label_0 = ttk.Label(self.window, text="0")
        label_0.place(x=458, y=175)
        label_1 = ttk.Label(self.window, text="10")
        label_1.place(x=606, y=175)
