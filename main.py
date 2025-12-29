import serial
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit

ser = serial.Serial('COM5', 9600, timeout=1)

plt.ion()
fig, ax = plt.subplots()
voltages = []
currents = []

# Shockley diode equation
def diode_eq(V, Is, n):
    Vt = 0.02585  # thermal voltage in V
    return Is * (np.exp(V / (n * Vt)) - 1)

SCALE_CURRENT = 1e-3  # convert mA to A for fitting
MIN_CURRENT = 0.01    # start fitting when current exceeds 0.01 mA

while True:
    line = ser.readline().decode('utf-8').strip()
    if line and ',' in line and "Vled" not in line:
        try:
            V, I_mA = map(float, line.split(','))
            voltages.append(V)
            currents.append(I_mA)

            ax.clear()
            # Plot measured points
            ax.scatter(voltages, currents, color='blue', s=20, label='Measured data')

            # Check if current exceeds threshold
            if max(currents) > MIN_CURRENT:
                # Convert currents to Amps for fitting
                currents_fit = [i*SCALE_CURRENT for i in currents]
                # Fit Shockley diode equation
                try:
                    popt, _ = curve_fit(diode_eq, voltages, currents_fit,
                                        p0=[1e-9, 1.5],
                                        bounds=([1e-12, 0.5], [1e-6, 2.5]),
                                        maxfev=10000)
                    V_fit = np.linspace(min(voltages), max(voltages), 200)
                    I_fit = diode_eq(V_fit, *popt) / SCALE_CURRENT  # convert back to mA
                    ax.plot(V_fit, I_fit, color='red', label=f'Exponential fit')
                except RuntimeError:
                    pass
            else:
                # Draw flat zero line before any current
                ax.plot([min(voltages), max(voltages)], [0,0], color='red', label='Exponential fit')

            ax.set_xlabel("Voltage across LED (V)")
            ax.set_ylabel("Current (mA)")
            ax.set_title("LED I-V Curve with Exponential Fit")
            ax.set_ylim(bottom=0)
            ax.grid(True)
            ax.legend()
            plt.pause(0.05)

        except ValueError:
            continue
