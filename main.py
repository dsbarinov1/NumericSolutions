import tkinter
from matplotlib import pyplot as plt
import matplotlib
matplotlib.use('TkAgg')
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from mpl_toolkits.axes_grid1.inset_locator import InsetPosition
from  matplotlib.widgets import Button
from functools import partial
import sys
from matplotlib import animation
from computation import double_gauss_func,laying_L,stairs_step, B, SIGMA, SHIFT, scheme_step
from child_windows import ChildWindow, draw_scheme_area
import os


def resource_path(relative_path):#для того чтобы экзешник не крашился
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


iteration_counter = 0
r = 0.45
h = 0.1
X_MAX = 30
XLIM = (0, X_MAX)
YLIM = (-0.5, 1.5)

STOCK_IMG = plt.imread(resource_path("add.png"))
fig, axs = plt.subplots(2, 2)
axs = [ax for row in axs for ax in row]
fig.tight_layout(pad=2.0)
lines = [None]*4
help_lines = [[],[],[],[]]
steps_texts = [None]*4
plt_buttons = [None]*4
X = np.linspace(0, X_MAX, int(X_MAX/h), dtype=float)
U1_arr = [double_gauss_func(X, B, SIGMA, SHIFT)]*4
U2_arr = [double_gauss_func(X, B, SIGMA, SHIFT)]*4
STEPS = SAVED_STEPS = 1
SCHEMES = [None]*4
IS_RUNNING = False
DELETE_MODE = False
pause_button = None#объявится в основном окне, знаю что говнокод, но каждый раз тащить через параметры еще хуже
anim = None#та же фигня


def init():#функция для подготовки анимации к запуску
    global iteration_counter, U1_arr, U2_arr, steps_texts, axs, plt_buttons
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
            mini_scheme = ax.inset_axes([0.8, 0.8, 0.15, 0.15])
            draw_scheme_area(mini_scheme, mini_mode=True, scheme=SCHEMES[i])
            steps_text = ax.text(0.02, 0.8, '', transform=ax.transAxes)
            steps_texts[i] = steps_text
        else:
            ax.axis('off')
            ax.set(xlim=(0, STOCK_IMG.shape[1]), ylim=(STOCK_IMG.shape[0], 0))
            ax.imshow(STOCK_IMG, origin="upper")
    return steps_texts


def animate(iter):#сама анимация
    global SCHEMES, IS_RUNNING, lines, help_lines, X, U2_arr, U1_arr, r, h, STEPS, steps_texts, iteration_counter
    for i in range(len(SCHEMES)):
        if SCHEMES[i] is not None:
            if IS_RUNNING:
                lines[i].set_data(X, U2_arr[i])
                U1_arr[i], U2_arr[i] = scheme_step(U1_arr[i], U2_arr[i], SCHEMES[i], r, h, STEPS)
                iteration_counter += STEPS
                steps_texts[i].set_text('шаги: {}\nитерация: {}'.format(STEPS, iteration_counter))
                #print(iter)

    return lines + steps_texts


def up(entry):#для кнопочки увеличения шага
    global STEPS
    STEPS+=1
    entry.delete(0, tkinter.END)
    entry.insert(0, str(STEPS))


def down(entry):#для кнопочки уменьшения шага
    global STEPS
    if STEPS>1:
        STEPS-=1
    entry.delete(0, tkinter.END)
    entry.insert(0, str(STEPS))


def set_steps(entry):#для кнопочки установки шага
    global STEPS
    STEPS = int(entry.get())


def stop_resume():#говно идея, но переделывать лень, поэтому в зависимости от очередности нажатия она останавливает или продолжает анимацию
    global pause_button, IS_RUNNING, anim
    IS_RUNNING = not IS_RUNNING
    if IS_RUNNING:
        anim.resume()
        pause_button.configure(text="Стоп")
    else:
        anim.pause()
        pause_button.configure(text="Продолжить")


def start():#для кнопочки запуска
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
    else:
        init()
        anim.resume()
        #anim.pause()


def go_to_iteration(entry):#переход к итерации
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
    if not IS_RUNNING:
        stop_resume()


def set_r_h(entry_r, entry_h):#для установки числа Куранта и шага
    target_r = float(entry_r.get())
    target_h = float(entry_h.get())
    global r, h, X
    r = target_r
    h = target_h
    X = np.linspace(0, X_MAX, int(X_MAX / h))
    start()


def change_mode(button):#меняет режим добавления и удаления схем
    global DELETE_MODE
    DELETE_MODE = not DELETE_MODE
    if DELETE_MODE:
        b_text = "Режим: удаление"
    else:
        b_text = "Режим: добавление"
    button.configure(text=b_text)


def click_wrapper(window):#обработка нажатия на график, если к нему еще не прикреплена схема
    def onclick(event):
        global DELETE_MODE
        if event.inaxes:
            i = axs.index(event.inaxes)
            if window.schemes[i] is None and not DELETE_MODE:
                window.choose_scheme(i)
            elif window.schemes[i] is not None and DELETE_MODE:
                window.remove_scheme(i)
    return onclick


class MainWindow(tkinter.Frame):#основное окошко
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
        delete_button = tkinter.Button(self.f_top, text="Режим: добавление", width=20 , font=myFont, background='#c3c3c3')
        delete_button.configure(command=partial(change_mode,delete_button))
        plus_button = tkinter.Button(self.f_top, text="+", width=5, command=partial(up,steps_entry) , font=myFont, background='#c3c3c3')
        minus_button = tkinter.Button(self.f_top, text="-", width=5, command=partial(down,steps_entry), font=myFont, background='#c3c3c3')
        set_button = tkinter.Button(self.f_top, text="Установить шаг", command=partial(set_steps,steps_entry), font=myFont, background='#c3c3c3')
        for obj in [set_button, plus_button, steps_entry, minus_button, steps_label]:
            obj.pack(padx=5, side=tkinter.RIGHT)
        delete_button.pack(padx=5, side=tkinter.LEFT)
        r_entry = tkinter.Entry(self.f_mid, font=myFont, width=5)
        h_entry = tkinter.Entry(self.f_mid, font=myFont, width=5)
        r_button = tkinter.Button(self.f_mid, text="Установить r и h", width=15,command=partial(set_r_h,r_entry,h_entry), font=myFont, background='#c3c3c3')
        start_b = tkinter.Button(self.f_mid, text="Начать", width=10,command=start, font=myFont, background='#c3c3c3')
        global pause_button, r, h, STEPS
        pause_button = tkinter.Button(self.f_mid, text="Стоп", width=10, command=stop_resume, font=myFont, background='#c3c3c3')
        iteration_entry = tkinter.Entry(self.f_mid, font=myFont, width=5)
        iteration_entry.delete(0, tkinter.END)
        iteration_entry.insert(0, str(STEPS))
        r_entry.delete(0, tkinter.END)
        r_entry.insert(0, str(r))
        h_entry.delete(0, tkinter.END)
        h_entry.insert(0, str(h))
        iteration_button = tkinter.Button(self.f_mid, text="Перейти к итерации", command= partial(go_to_iteration,iteration_entry), font=myFont, background='#c3c3c3')
        for obj in [iteration_button, iteration_entry, pause_button, start_b]:
            obj.pack(padx=5, side=tkinter.RIGHT)
        for obj in [r_button, r_entry, h_entry]:
            obj.pack(padx=5, side=tkinter.LEFT)

    def plot(self):#создание графиков в окне
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


    def remove_scheme(self, idx):
        global SCHEMES
        self.schemes[idx] = None
        SCHEMES[idx] = None
        start()


def on_closing():
    #if messagebox.askokcancel("Выход", "Выйти из приложения?"):
        root.destroy()
        sys.exit(0)


root = tkinter.Tk()


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
