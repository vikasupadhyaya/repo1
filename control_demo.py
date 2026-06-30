"""
CONTROL SYSTEMS FOR KIDS — Interactive Demo
=============================================
A fun, visual way to show kids how "controllers" work — the same idea
behind thermostats, cruise control, drones, and video game characters!

THE STORY: We have a room with a heater. You set a target temperature
(the "setpoint"). The controller watches the room and turns the heater
up or down to reach that target — just like a real thermostat.

Kids can drag sliders to change:
  - Target Temperature (what we WANT)
  - P (Proportional) — "how hard do I push based on how wrong I am right now?"
  - I (Integral) — "I've been wrong for a while, push harder!"
  - D (Derivative) — "whoa, slow down, I'm approaching fast!"

Run this script and watch the orange line (room temp) chase the
dashed line (target) in real time as you move the sliders!

Requires: matplotlib, numpy  (pip install matplotlib numpy)
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button

# ---------- Simulation settings ----------
dt = 0.1                 # time step (seconds)
history_len = 200         # how many points to show on screen
room_temp = 15.0          # starting room temperature (cold!)
outside_temp = 5.0        # it's cold outside, room naturally cools toward this
target_temp = 22.0        # what we want the room to be

# PID gains (these are what the kids will tune!)
Kp, Ki, Kd = 2.0, 0.05, 0.5

integral_error = 0.0
last_error = 0.0

time_data = list(np.linspace(-history_len * dt, 0, history_len))
temp_data = [room_temp] * history_len
target_data = [target_temp] * history_len
heater_data = [0.0] * history_len

# ---------- Set up the figure ----------
fig, (ax_temp, ax_heater) = plt.subplots(
    2, 1, figsize=(9, 7), gridspec_kw={"height_ratios": [3, 1]}
)
plt.subplots_adjust(left=0.1, bottom=0.38, hspace=0.4)

line_temp, = ax_temp.plot(time_data, temp_data, color="orangered", lw=3, label="Room Temp 🌡️")
line_target, = ax_temp.plot(time_data, target_data, "--", color="royalblue", lw=2, label="Target 🎯")
ax_temp.set_ylim(0, 35)
ax_temp.set_ylabel("Temperature (°C)")
ax_temp.set_title("Can YOU control the room temperature? 🔥❄️", fontsize=14, fontweight="bold")
ax_temp.legend(loc="upper left")
ax_temp.grid(alpha=0.3)

bar_heater = ax_heater.bar(["Heater Power"], [0], color="orange")
ax_heater.set_ylim(-100, 100)
ax_heater.set_ylabel("Heater %\n(- means cooling)")
ax_heater.grid(alpha=0.3)

# ---------- Sliders ----------
ax_target = plt.axes([0.15, 0.25, 0.7, 0.03])
ax_kp = plt.axes([0.15, 0.19, 0.7, 0.03])
ax_ki = plt.axes([0.15, 0.13, 0.7, 0.03])
ax_kd = plt.axes([0.15, 0.07, 0.7, 0.03])

s_target = Slider(ax_target, "Target Temp 🎯", 5, 35, valinit=target_temp, color="royalblue")
s_kp = Slider(ax_kp, "P (react now)", 0, 10, valinit=Kp, color="tomato")
s_ki = Slider(ax_ki, "I (catch up)", 0, 1, valinit=Ki, color="seagreen")
s_kd = Slider(ax_kd, "D (slow down)", 0, 5, valinit=Kd, color="purple")

ax_reset = plt.axes([0.82, 0.01, 0.12, 0.04])
btn_reset = Button(ax_reset, "Reset Room 🔄")


def reset(event=None):
    global room_temp, integral_error, last_error
    room_temp = 15.0
    integral_error = 0.0
    last_error = 0.0


btn_reset.on_clicked(reset)

# ---------- The control loop ----------
def update(frame):
    global room_temp, integral_error, last_error

    target = s_target.val
    Kp, Ki, Kd = s_kp.val, s_ki.val, s_kd.val

    # --- This is the actual PID controller! ---
    error = target - room_temp
    integral_error += error * dt
    derivative = (error - last_error) / dt
    heater_power = Kp * error + Ki * integral_error + Kd * derivative
    heater_power = np.clip(heater_power, -100, 100)  # heater can't exceed 100%
    last_error = error

    # --- Physics: room slowly heats/cools toward outside temp + heater effect ---
    room_temp += (heater_power * 0.05 - (room_temp - outside_temp) * 0.02) * dt

    # --- update plots ---
    time_data.append(time_data[-1] + dt)
    temp_data.append(room_temp)
    target_data.append(target)
    for d in (time_data, temp_data, target_data):
        if len(d) > history_len:
            d.pop(0)

    line_temp.set_data(time_data, temp_data)
    line_target.set_data(time_data, target_data)
    ax_temp.set_xlim(time_data[0], time_data[-1])

    bar_heater[0].set_height(heater_power)
    bar_heater[0].set_color("orangered" if heater_power > 0 else "steelblue")

    return line_temp, line_target, bar_heater


from matplotlib.animation import FuncAnimation
ani = FuncAnimation(fig, update, interval=100, blit=False, cache_frame_data=False)

plt.show()
