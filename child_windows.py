import tkinter
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.patches import Circle
from tkinter import ttk
from start_functions import *
import tkinter.font

from tkinter import messagebox


def click_wrapper(window):  # обработка нажатий на график
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
                drawObject = Circle((i, j), radius=0.2, fill=True, color="black")
                ax.add_patch(drawObject)
        window.canvas.draw()

    return onclick


def draw_scheme_area(ax, mini_mode=False, scheme=None):  # оформление сетки для отображения схемы
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


class SchemeWindow:
    def __init__(self, window, parent, idx):
        self.idx = idx
        self.root = window
        self.window = window
        self.parent = parent
        self.window.title("Выбор схемы")
        self.window.configure(bg='#121212')
        self.window.geometry("750x650")
        self.COLORS = {
            'bg': '#121212',
            'button_bg': '#272727',
            'entry_bg': '#1E1E1E',
            'text': '#FFFFFF',
            'accent': '#BB86FC'
        }
        self.button_font = tkinter.font.Font(family="Helvetica", size=25)
        self.f_top = self.create_frame()
        self.f_mid = self.create_frame()
        self.f_top.pack(fill=tkinter.BOTH, expand=True, padx=15, pady=8)
        self.f_mid.pack(fill=tkinter.BOTH, expand=True, padx=15, pady=8)
        self.scheme = np.array([
            [False, False, False, False],
            [False, False, False, False],
            [False, False, False, False]
        ])
        self.initUI()

    def create_frame(self):
        frame = tkinter.Frame(
            self.window,
            bg=self.COLORS['bg'],
            padx=10,
            pady=10
        )
        return frame

    def create_styled_button(self, parent, text, command=None, width=None):
        button = tkinter.Button(
            parent,
            text=text,
            font=self.button_font,
            bg=self.COLORS['button_bg'],
            fg=self.COLORS['text'],
            activebackground=self.COLORS['accent'],
            activeforeground=self.COLORS['text'],
            relief='flat',
            command=command,
            width=width,
            cursor='hand2',
            pady=5,
            border=0
        )
        button.bind('<Enter>', lambda e: self.on_hover(button))
        button.bind('<Leave>', lambda e: self.on_leave(button))
        return button

    def on_hover(self, button):
        button.configure(bg=self.COLORS['accent'])

    def on_leave(self, button):
        button.configure(bg=self.COLORS['button_bg'])

    def initUI(self):
        apply_button = self.create_styled_button(
            self.f_top,
            "Применить",
            command=self.choose_scheme,
            width=15
        )
        apply_button.pack(padx=5, side=tkinter.LEFT)

        fig = plt.figure()
        fig.canvas.mpl_connect('button_press_event', click_wrapper(self))
        ax = plt.gca()
        draw_scheme_area(ax)

        self.canvas = FigureCanvasTkAgg(fig, master=self.f_mid)
        self.canvas.get_tk_widget().pack(side=tkinter.TOP, expand=True, fill=tkinter.BOTH, padx=5, pady=5)
        self.canvas._tkcanvas.pack(side=tkinter.TOP, expand=True, fill=tkinter.BOTH, padx=5, pady=5)

    def choose_scheme(self):
        self.format_cheme()
        self.parent.set_scheme(self.scheme, self.idx)
        self.on_closing()

    def on_closing(self):
        self.parent.destroy_child(self.idx)
        # plt.figure(self.idx + 1).clear()
        self.window.destroy()

    def format_cheme(self):  # когда схема выбрана, надо ее правильно поместить для функции расчета
        while (np.any(self.scheme[-1, :]) == False):
            for i in range(self.scheme.shape[0] - 1, 0, -1):
                self.scheme[i] = np.copy(self.scheme[i - 1])
            self.scheme[0].fill(False)
        while (np.any(self.scheme[:, 0]) == False):
            for i in range(self.scheme.shape[1] - 1):
                self.scheme[:, i] = np.copy(self.scheme[:, i + 1])
            self.scheme[:, -1].fill(False)


class StartConfigurationWindow():
    def __init__(self, window, parent, idx):
        self.idx = idx
        self.root = window
        self.window = window
        self.parent = parent
        self.f_names = [u'Гауссиан', u'Двойной Гауссиан', u'Ступенька', u'Треугольник', u'Пользовательская функция']
        self.functions = [gauss_func, double_gauss_func, step_func, triangle_func, custom_func]
        self.custom_func_idx = 4
        self.init_child()
        self.last_state = False

    def draw_graph(self, func):
        if self.f_names.index(self.combobox.get()) != self.custom_func_idx:
            d = round(self.scale_par.get(), 1)
        else:
            d = self.custom_func_entry.get()
        if self.draw_flag == False:
            self.graphs_x = np.linspace(0, 10, 1001)
            graph_val = [func(d, x) for x in self.graphs_x]
            fig = Figure(figsize=(3.5, 2.5), dpi=100)
            ax = fig.add_subplot()
            ax.plot(self.graphs_x, graph_val, "-r", linewidth=3)
            ax.grid(color='black', linewidth=0.5)
            ax.set_title(f'{self.combobox.get()}')

            self.fig_canvas = FigureCanvasTkAgg(fig, master=self.window)
            self.fig_canvas.get_tk_widget().place(x=2, y=2)
            self.draw_flag = True
        else:
            graph_val = [func(d, x) for x in self.graphs_x]
            fig = Figure(figsize=(3.5, 2.5), dpi=100)
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
        self.clear_my_draw()
        f_idx = self.f_names.index(self.combobox.get())
        self.draw_graph(self.functions[f_idx])

    def btn_ok_func(self):
        f_idx = self.f_names.index(self.combobox.get())
        f = self.functions[f_idx]
        if f_idx != self.custom_func_idx:
            d = round(self.scale_par.get(), 1)
        else:
            d = self.custom_func_entry.get()
        self.parent.set_function(f, d)
        self.on_closing()

    def on_closing(self):
        self.parent.destroy_child(self.idx)
        self.window.destroy()

    def scale_modified(self, event):
        self.label_just_d.config(text=f"D = {round(self.scale_par.get(), 1)}", font=('Arial', 12))
        self.btn_apply_func()

    def combobox_modified(self, event):
        state = self.f_names.index(self.combobox.get()) == self.custom_func_idx
        if state != self.last_state:
            self.last_state = state
            if not state:
                self.custom_func_entry.place_forget()
                self.label_0.place(relx=488 / 700, rely=185 / 400, anchor="nw")
                self.label_just_d.place(relx=470 / 700, rely=220 / 400, anchor="nw")
                self.label_parameter_d.place(relx=470 / 700, rely=125 / 400, anchor="nw")
                self.scale_par.place(relx=490 / 700, rely=160 / 400, anchor="nw")
                # self.label_parameter_d.place(x=470, y=125)
                # self.label_just_d.place(x=470, y=220)
                # self.scale_par.place(x=490, y=160)
                # self.label_0.place(x=488, y=185)

            else:
                # self.custom_func_entry.place(x=470, y=250)
                self.custom_func_entry.grid(column=1, row=0)
                self.custom_func_entry.place(relx=470 / 700, rely=250 / 400, anchor="nw")
                self.label_parameter_d.place_forget()
                self.label_just_d.place_forget()
                self.scale_par.place_forget()
                self.label_0.place_forget()
        self.btn_apply_func()

    def init_child(self):
        self.window.geometry("700x400")
        self.window.title("Выбор начального условия")
        # self.window.resizable(False, False)
        self.window.configure(bg='#121212')

        self.COLORS = {
            'bg': '#121212',
            'button_bg': '#272727',
            'entry_bg': '#1E1E1E',
            'text': '#FFFFFF',
            'accent': '#BB86FC'
        }

        self.button_font = tkinter.font.Font(family="Helvetica", size=12)
        self.label_font = tkinter.font.Font(family="Helvetica", size=12)

        self.combobox = ttk.Combobox(self.window,
                                     values=self.f_names,
                                     font=('Arial', 11))
        self.combobox.current(0)
        self.combobox.bind('<<ComboboxSelected>>', self.combobox_modified)
        # self.combobox.place(x=470, y=70)

        self.custom_func_entry = ttk.Entry(self.window, width=25)

        self.scale_par = ttk.Scale(self.window,
                                   orient=tkinter.HORIZONTAL,
                                   length=180,
                                   from_=0.0,
                                   to=9.9,
                                   value=5)
        # self.scale_par.place(x=490, y=160)
        self.scale_par.bind("<ButtonRelease-1>", self.scale_modified)

        btn_cancel = self.create_styled_button(self.window,
                                               "Закрыть",
                                               command=self.on_closing)
        # btn_cancel.place(x=600, y=352)

        btn_ok1 = self.create_styled_button(self.window,
                                            "Ок",
                                            command=self.btn_ok_func)
        # btn_ok1.place(x=500, y=352)

        btn_apply = self.create_styled_button(self.window,
                                              "Применить",
                                              command=self.btn_apply_func)
        # btn_apply.place(x=535, y=290)

        label_start_cond = self.create_styled_label("Начальное условие:")
        # label_start_cond.place(x=470, y=40)

        self.label_parameter_d = self.create_styled_label("Параметр D:")
        # self.label_parameter_d.place(x=470, y=125)

        self.label_just_d = self.create_styled_label(f"D = {round(self.scale_par.get(), 1)}")
        # self.label_just_d.place(x=470, y=220)

        self.label_0 = self.create_styled_label("0")
        self.label_0.place(relx=488 / 700, rely=185 / 400, anchor="nw")
        self.label_just_d.place(relx=470 / 700, rely=220 / 400, anchor="nw")
        self.label_parameter_d.place(relx=470 / 700, rely=125 / 400, anchor="nw")
        label_start_cond.place(relx=470 / 700, rely=40 / 400, anchor="nw")
        btn_apply.place(relx=535 / 700, rely=290 / 400, anchor="nw")
        btn_ok1.place(relx=500 / 700, rely=352 / 400, anchor="nw")
        btn_cancel.place(relx=600 / 700, rely=352 / 400, anchor="nw")
        self.scale_par.place(relx=490 / 700, rely=160 / 400, anchor="nw")
        self.combobox.place(relx=470 / 700, rely=70 / 400, anchor="nw")
        self.custom_func_entry.grid(column=1, row=0)
        self.custom_func_entry.place(relx=470 / 700, rely=250 / 400, anchor="nw")
        self.custom_func_entry.insert(0, "sin(x)")  # Установка начального значения
        self.custom_func_entry.place_forget()

        self.draw_flag = False
        self.draw_graph(gauss_func)

    def create_styled_button(self, parent, text, command=None, width=None):
        button = tkinter.Button(
            parent,
            text=text,
            font=self.button_font,
            bg=self.COLORS['button_bg'],
            fg=self.COLORS['text'],
            activebackground=self.COLORS['accent'],
            activeforeground=self.COLORS['text'],
            relief='flat',
            command=command,
            width=width,
            cursor='hand2',
            pady=5,
            border=0
        )
        button.bind('<Enter>', lambda e: self.on_hover(button))
        button.bind('<Leave>', lambda e: self.on_leave(button))
        return button

    def create_styled_label(self, text):
        return tkinter.Label(
            self.window,
            text=text,
            font=self.label_font,
            bg=self.COLORS['bg'],
            fg=self.COLORS['text']
        )

    def on_hover(self, button):
        button.configure(bg=self.COLORS['accent'])

    def on_leave(self, button):
        button.configure(bg=self.COLORS['button_bg'])

    """
    def init_child(self):
        self.window.geometry("700x400")
        self.window.title("Выбор начального условия")
        #self.window.resizable(False, False)

        self.combobox = ttk.Combobox(self.window, values=self.f_names, font=('Arial', 11))
        self.custom_func_entry = ttk.Entry(self.window, width=25)
        self.combobox.current(0)  # индекс списка, график кот. будет по умолчанию
        self.combobox.bind('<<ComboboxSelected>>', self.combobox_modified)


        self.scale_par = ttk.Scale(self.window, orient=tkinter.HORIZONTAL, length=180, from_=0.0, to=9.9, value=5)
        self.scale_par.bind("<ButtonRelease-1>", self.scale_modified)
        self.fig = Figure(figsize=(3.5, 2.5), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.fig_canvas = FigureCanvasTkAgg(self.fig, master=self.window)
        self.fig_canvas.get_tk_widget().pack(anchor=tkinter.NW, fill=tkinter.Y, expand=1)
        self.draw_flag = False
        self.draw_graph(gauss_func)

        btn_cancel = ttk.Button(self.window, text='Закрыть', command=self.on_closing)


        btn_ok1 = ttk.Button(self.window, text='Ок', command=self.btn_ok_func)
        btn_apply = ttk.Button(self.window, text="Применить", command=self.btn_apply_func)


        label_start_cond = ttk.Label(self.window, text="Начальное условие:", font=('Arial', 12))

        self.label_parameter_d = ttk.Label(self.window, text="Параметр D:", font=('Arial', 12))

        self.label_just_d = ttk.Label(self.window, text=f"D = {round(self.scale_par.get(), 1)}", font=('Arial', 12))

        self.label_0 = ttk.Label(self.window, text="0                   5                   10")
        self.label_0.place(relx=488/700, rely=185/400, anchor="nw")
        self.label_just_d.place(relx=470/700, rely=220/400, anchor="nw")
        self.label_parameter_d.place(relx=470/700, rely=125/400, anchor="nw")
        label_start_cond.place(relx=470/700, rely=40/400, anchor="nw")
        btn_apply.place(relx=535/700, rely=290/400, anchor="nw")
        btn_ok1.place(relx=500/700, rely=352/400, anchor="nw")
        btn_cancel.place(relx=600/700, rely=352/400, anchor="nw")
        self.fig_canvas.get_tk_widget().pack(anchor=tkinter.NW, fill=tkinter.Y, expand=1)
        self.scale_par.place(relx=490/700, rely=160/400, anchor="nw")
        self.combobox.place(relx=470/700, rely=70/400, anchor="nw")
        self.custom_func_entry.grid(column=1, row=0)
        self.custom_func_entry.place(relx=470/700, rely=250/400, anchor="nw")
        self.custom_func_entry.insert(0, "sin(x)") # Установка начального значения
        self.custom_func_entry.place_forget()

    """