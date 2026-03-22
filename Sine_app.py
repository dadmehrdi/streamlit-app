import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="Sine Wave App", layout="centered")

st.title("📈 Interactive Sine Wave Generator")

st.write("Select a frequency and see how the sine wave changes.")

# Input
freq = st.slider("Choose frequency (1–10)", 1, 10, 3)

# Generate x values
x = np.linspace(0, 2 * np.pi, 500)

# Generate sine wave
y = np.sin(freq * x)

# Plot
fig, ax = plt.subplots()
ax.plot(x, y)
ax.set_title(f"Sine Wave with Frequency = {freq}")
ax.set_xlabel("x")
ax.set_ylabel("sin(fx)")

st.pyplot(fig)