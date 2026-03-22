import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# Page config
st.set_page_config(page_title="Sine Wave Lab", layout="wide")

# Title
st.title("🌊 Sine Wave Lab")
st.markdown("Explore how frequency, amplitude, and phase affect a sine wave.")

# Sidebar controls
st.sidebar.header("Controls")

freq = st.sidebar.slider("Frequency", 1, 10, 3)
amp = st.sidebar.slider("Amplitude", 0.5, 5.0, 1.0)
phase = st.sidebar.slider("Phase Shift", 0.0, 2*np.pi, 0.0)

# Generate data
x = np.linspace(0, 2 * np.pi, 500)
y = amp * np.sin(freq * x + phase)

# Layout
col1, col2 = st.columns([2, 1])

# Plot
with col1:
    fig, ax = plt.subplots()
    
    ax.plot(x, y, linewidth=3)
    ax.axhline(0)
    
    ax.set_title("Sine Wave Visualization", fontsize=16)
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    
    ax.grid(alpha=0.3)
    
    st.pyplot(fig)

# Metrics panel
with col2:
    st.subheader("📊 Parameters")
    st.metric("Frequency", freq)
    st.metric("Amplitude", amp)
    st.metric("Phase Shift", round(phase, 2))

    st.markdown("---")
    st.write("### 🧠 Interpretation")
    st.write(f"- Higher frequency → more oscillations")
    st.write(f"- Amplitude controls height")
    st.write(f"- Phase shifts the wave horizontally")
