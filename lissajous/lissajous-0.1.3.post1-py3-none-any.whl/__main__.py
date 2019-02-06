#! /usr/bin/env python3

"""
Lissajous Curve Visualizer

In mathematics, a Lissajous curve /ˈlɪsəʒuː/, also known as Lissajous figure
or Bowditch curve /ˈbaʊdɪtʃ/, is the graph of a system of parametric equations
    x = A * sin(at + δ), y = B* sin⁡(bt)
Source: https://en.wikipedia.org/wiki/Lissajous_curve
"""

import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.widgets import Slider, Button


def main():
    # * Lissajous function
    xfunc = np.vectorize(lambda t: A * np.sin(a * t + delta))
    yfunc = np.vectorize(lambda t: B * np.sin(b * t))

    # * Default values
    a = a_val_0 = 2
    b = b_val_0 = 3
    A = A_val_0 = 5
    B = B_val_0 = 5
    delta = delta_val_0 = 0
    N = N_val_0 = 2

    x = xfunc(np.linspace(0, (2 ** N) * np.pi, N * 200))
    y = yfunc(np.linspace(0, (2 ** N) * np.pi, N * 200))

    DARKBLUE = "xkcd:dark navy blue"
    LIGHTBLUE = "xkcd:cornflower"
    SILVER = "xkcd:cloudy blue"

    # * Create plots
    fig, ax = plt.subplots(facecolor=DARKBLUE)  # Background color
    matplotlib.rcParams["savefig.facecolor"] = DARKBLUE
    fig.subplots_adjust(bottom=0.35)  # Add space for sliders
    fig.set_size_inches(10, 10)  # Set figure size
    fig.canvas.set_window_title("Lissajous Curve Visualizer")

    ax.set_aspect(1)  # Fix aspect ratio to 1:1
    ax.set_xlim([-8, 8])  # X axis ranges from -10 to 10
    ax.set_ylim([-8, 8])  # Y axis ranges from -10 to 10
    ax.set_xticks([])  # Remove X axis ticks
    ax.set_yticks([])  # Remove Y axis ticks

    ax.set_facecolor(DARKBLUE)  # Figure color
    for spine in ax.spines:
        ax.spines[spine].set_color(SILVER)  # Figure border color

    line, = ax.plot(x, y, color=SILVER)  # Plot values

    # * Create sliders
    SLIDER_X = 0.257
    SLIDER_LEN = 0.51
    N_slider_ax = fig.add_axes([SLIDER_X, 0.30, SLIDER_LEN, 0.03])
    N_slider = Slider(N_slider_ax, "N", 2, 4, valinit=N_val_0, color=LIGHTBLUE)

    a_slider_ax = fig.add_axes([SLIDER_X, 0.25, SLIDER_LEN, 0.03])
    a_slider = Slider(a_slider_ax, "a", 0, 6, valinit=a_val_0, color=LIGHTBLUE)

    b_slider_ax = fig.add_axes([SLIDER_X, 0.20, SLIDER_LEN, 0.03])
    b_slider = Slider(b_slider_ax, "b", 0, 6, valinit=b_val_0, color=LIGHTBLUE)

    A_slider_ax = fig.add_axes([SLIDER_X, 0.15, SLIDER_LEN, 0.03])
    A_slider = Slider(A_slider_ax, "A", 0, 8, valinit=A_val_0, color=LIGHTBLUE)

    B_slider_ax = fig.add_axes([SLIDER_X, 0.10, SLIDER_LEN, 0.03])
    B_slider = Slider(B_slider_ax, "B", 0, 8, valinit=B_val_0, color=LIGHTBLUE)

    delta_slider_ax = fig.add_axes([SLIDER_X, 0.05, SLIDER_LEN, 0.03])
    delta_slider = Slider(
        delta_slider_ax, "δ", 0, 6, valinit=delta_val_0, color=LIGHTBLUE
    )

    for slider_ax in (
        a_slider_ax,
        b_slider_ax,
        A_slider_ax,
        B_slider_ax,
        delta_slider_ax,
        N_slider_ax,
    ):
        slider_ax.set_facecolor(DARKBLUE)  # Slider face color
        for spine in slider_ax.spines:
            slider_ax.spines[spine].set_color(SILVER)  # Slider border color

    for slider in (a_slider, b_slider, A_slider, B_slider, delta_slider, N_slider):
        slider.vline.set_color(SILVER)  # Set default line color
        slider.label.set_size(14)  # Set slider label text size
        slider.label.set_color(SILVER)  # Set slider label color
        slider.valtext.set_color(SILVER)  # Set slider value color

    # * Slider functions
    def slider_changed(val):
        nonlocal A, B, a, b, delta
        A, B = A_slider.val, B_slider.val
        a, b = a_slider.val, b_slider.val
        delta = delta_slider.val

    def slider_changed_reset(val):
        nonlocal N
        N = N_slider.val
        restart()

    N_slider.on_changed(slider_changed_reset)
    A_slider.on_changed(slider_changed)
    B_slider.on_changed(slider_changed)
    a_slider.on_changed(slider_changed)
    b_slider.on_changed(slider_changed)
    delta_slider.on_changed(slider_changed)

    # * Create buttons
    toggle_button_ax = fig.add_axes([0.60, 0.01, 0.03, 0.03])
    toggle_button = Button(
        toggle_button_ax, "T", hovercolor="xkcd:dark blue", color=DARKBLUE
    )

    reset_button_ax = fig.add_axes([0.65, 0.01, 0.1, 0.03])
    reset_button = Button(
        reset_button_ax, "Reset", hovercolor="xkcd:dark blue", color=DARKBLUE
    )

    for slider_ax in (toggle_button_ax, reset_button_ax):
        for spine in slider_ax.spines:
            slider_ax.spines[spine].set_color(SILVER)

    for slider in (toggle_button, reset_button):
        slider.label.set_color(SILVER)

    # * Button functions
    pause = True

    def toggle_button_clicked(mouse_event):
        nonlocal pause, ani
        if pause:
            ani.event_source.stop()
        else:
            ani.event_source.start()
        pause ^= True

    def reset_button_clicked(mouse_event):
        N_slider.reset()
        a_slider.reset()
        b_slider.reset()
        A_slider.reset()
        B_slider.reset()
        delta_slider.reset()

    toggle_button.on_clicked(toggle_button_clicked)
    reset_button.on_clicked(reset_button_clicked)

    # * Animation
    def update(num, x, y, line):
        x = xfunc(np.linspace(0, (2 ** N) * np.pi, N * 200))
        y = yfunc(np.linspace(0, (2 ** N) * np.pi, N * 200))
        line.set_data(x[:num], y[:num])
        if num == N * 200 + 20:
            restart()
        return (line,)

    def restart():
        nonlocal ani
        ani.frame_seq = ani.new_frame_seq()
        ani.event_source.start()

    ani = animation.FuncAnimation(
        fig,
        update,
        N * 200 + 20,
        fargs=[x, y, line],
        interval=30,
        blit=False,
        repeat=True,
    )
    plt.show()


if __name__ == "__main__":
    main()