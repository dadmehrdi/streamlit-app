import streamlit as st
import numpy as np
import plotly.graph_objects as go

# -----------------------------
# Page + Styling
# -----------------------------
st.set_page_config(page_title="Wave Synth Lab", layout="wide")

st.markdown(
    """
    <style>
      .block-container {padding-top: 1.2rem;}
      .big-title {font-size: 2.2rem; font-weight: 800; letter-spacing: -0.02em;}
      .subtitle {opacity: 0.85; margin-top: -0.4rem;}
      .pill {display:inline-block; padding: 0.25rem 0.6rem; border-radius: 999px; 
             background: rgba(99,102,241,0.15); border: 1px solid rgba(99,102,241,0.35);
             margin-right: 0.4rem; font-size: 0.85rem;}
      .panel {padding: 1rem; border-radius: 18px; background: rgba(255,255,255,0.03);
              border: 1px solid rgba(255,255,255,0.08);}
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown('<div class="big-title">🎛️ Wave Synth Lab</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">Mix oscillators, add AM/FM modulation, inspect spectrum, and play sound.</div>',
    unsafe_allow_html=True
)
st.markdown(
    '<span class="pill">2 Oscillators</span>'
    '<span class="pill">AM / FM</span>'
    '<span class="pill">Spectrum</span>'
    '<span class="pill">Lissajous</span>'
    '<span class="pill">Audio</span>',
    unsafe_allow_html=True
)

# -----------------------------
# Helpers
# -----------------------------
def osc_wave(wave_type, t, freq, phase):
    x = 2 * np.pi * freq * t + phase
    if wave_type == "Sine":
        return np.sin(x)
    if wave_type == "Square":
        return np.sign(np.sin(x))
    if wave_type == "Triangle":
        # Triangle via arcsin(sin)
        return (2 / np.pi) * np.arcsin(np.sin(x))
    if wave_type == "Saw":
        # Sawtooth in [-1, 1]
        return 2 * (x / (2*np.pi) - np.floor(0.5 + x / (2*np.pi)))
    return np.sin(x)

def nice_plot(x, y, title, xlab="Time (s)", ylab="Amplitude"):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=y, mode="lines", line=dict(width=3)))
    fig.update_layout(
        title=title,
        height=420,
        margin=dict(l=10, r=10, t=60, b=10),
        template="plotly_dark",
        xaxis_title=xlab,
        yaxis_title=ylab,
    )
    fig.update_xaxes(showgrid=True, gridcolor="rgba(255,255,255,0.08)")
    fig.update_yaxes(showgrid=True, gridcolor="rgba(255,255,255,0.08)")
    return fig

def fft_spectrum(y, sr):
    # windowed FFT
    n = len(y)
    w = np.hanning(n)
    Y = np.fft.rfft(y * w)
    f = np.fft.rfftfreq(n, 1/sr)
    mag = np.abs(Y)
    mag = mag / (mag.max() + 1e-12)
    return f, mag

def envelope(t, attack, decay):
    # Simple A/D envelope (not a full ADSR)
    env = np.ones_like(t)
    if attack > 0:
        env = np.minimum(env, t / attack)
    if decay > 0:
        env = np.minimum(env, 1 - (t / decay) * 0.0)  # keep structure; decay applied below
        # exponential-ish decay starting after attack
        start = attack
        idx = t >= start
        if np.any(idx):
            env[idx] = np.exp(-(t[idx] - start) / decay)
    return np.clip(env, 0, 1)

# -----------------------------
# Sidebar Controls
# -----------------------------
st.sidebar.header("⚙️ Controls")

preset = st.sidebar.selectbox(
    "🎚️ Preset",
    ["Custom", "Lo-Fi Tremolo", "FM Bell", "Detuned Synth", "Noisy Drone"],
)

# sensible defaults per preset
defaults = {
    "Custom": dict(),
    "Lo-Fi Tremolo": dict(w1="Sine", f1=220, a1=0.8, p1=0.0,
                         w2="Triangle", f2=220, a2=0.25, p2=0.2,
                         am_on=True, am_rate=6.0, am_depth=0.55,
                         fm_on=False, fm_rate=0.0, fm_depth=0.0,
                         noise=0.03, attack=0.02, decay=1.2),
    "FM Bell": dict(w1="Sine", f1=440, a1=0.9, p1=0.0,
                    w2="Sine", f2=660, a2=0.0, p2=0.0,
                    am_on=False, am_rate=0.0, am_depth=0.0,
                    fm_on=True, fm_rate=2.0, fm_depth=180.0,
                    noise=0.00, attack=0.005, decay=0.9),
    "Detuned Synth": dict(w1="Saw", f1=110, a1=0.7, p1=0.0,
                          w2="Saw", f2=111.2, a2=0.65, p2=0.2,
                          am_on=False, am_rate=0.0, am_depth=0.0,
                          fm_on=False, fm_rate=0.0, fm_depth=0.0,
                          noise=0.01, attack=0.01, decay=1.8),
    "Noisy Drone": dict(w1="Triangle", f1=55, a1=0.8, p1=0.0,
                        w2="Sine", f2=56, a2=0.35, p2=1.0,
                        am_on=True, am_rate=0.3, am_depth=0.25,
                        fm_on=True, fm_rate=0.2, fm_depth=8.0,
                        noise=0.08, attack=0.2, decay=3.5),
}

D = defaults.get(preset, {})

with st.sidebar.expander("🎛️ Oscillator 1", expanded=True):
    w1 = st.selectbox("Waveform", ["Sine", "Square", "Triangle", "Saw"], index=["Sine","Square","Triangle","Saw"].index(D.get("w1","Sine")))
    f1 = st.slider("Frequency (Hz)", 20, 2000, int(D.get("f1", 220)), step=1)
    a1 = st.slider("Amplitude", 0.0, 1.0, float(D.get("a1", 0.8)), step=0.01)
    p1 = st.slider("Phase", 0.0, float(2*np.pi), float(D.get("p1", 0.0)), step=0.01)

with st.sidebar.expander("🎚️ Oscillator 2 (optional)", expanded=True):
    w2 = st.selectbox("Waveform ", ["Sine", "Square", "Triangle", "Saw"], index=["Sine","Square","Triangle","Saw"].index(D.get("w2","Sine")))
    f2 = st.slider("Frequency (Hz) ", 20, 2000, int(D.get("f2", 220)), step=1)
    a2 = st.slider("Amplitude ", 0.0, 1.0, float(D.get("a2", 0.0)), step=0.01)
    p2 = st.slider("Phase ", 0.0, float(2*np.pi), float(D.get("p2", 0.0)), step=0.01)

with st.sidebar.expander("🌊 Modulation", expanded=True):
    am_on = st.toggle("AM (Tremolo)", value=bool(D.get("am_on", False)))
    am_rate = st.slider("AM Rate (Hz)", 0.1, 30.0, float(D.get("am_rate", 6.0)), step=0.1)
    am_depth = st.slider("AM Depth", 0.0, 1.0, float(D.get("am_depth", 0.4)), step=0.01)

    st.markdown("---")

    fm_on = st.toggle("FM (Frequency Mod)", value=bool(D.get("fm_on", False)))
    fm_rate = st.slider("FM Rate (Hz)", 0.1, 30.0, float(D.get("fm_rate", 2.0)), step=0.1)
    fm_depth = st.slider("FM Depth (Hz)", 0.0, 500.0, float(D.get("fm_depth", 50.0)), step=1.0)

with st.sidebar.expander("🎚️ Texture + Envelope", expanded=True):
    noise = st.slider("Noise", 0.0, 0.2, float(D.get("noise", 0.01)), step=0.005)
    attack = st.slider("Attack (s)", 0.0, 0.5, float(D.get("attack", 0.02)), step=0.005)
    decay = st.slider("Decay (s)", 0.05, 5.0, float(D.get("decay", 1.5)), step=0.05)

with st.sidebar.expander("🧪 Render Settings", expanded=False):
    duration = st.slider("Duration (s)", 0.5, 5.0, 2.0, step=0.1)
    sr = st.selectbox("Sample Rate", [22050, 44100, 48000], index=1)
    view_cycles = st.slider("Show first (ms)", 10, 300, 80, step=5)

# -----------------------------
# Synthesis
# -----------------------------
t = np.linspace(0, duration, int(sr * duration), endpoint=False)

# FM: modulate frequency of osc1 (classic FM feel)
fm = 0.0
if fm_on:
    fm = fm_depth * np.sin(2*np.pi*fm_rate*t)

y1 = a1 * osc_wave(w1, t, f1 + fm, p1)
y2 = a2 * osc_wave(w2, t, f2, p2)

y = y1 + y2

# AM: multiply by (1 - depth + depth*sin)
if am_on:
    am = (1 - am_depth) + am_depth * (0.5 * (1 + np.sin(2*np.pi*am_rate*t)))
    y = y * am

# envelope + noise
env = envelope(t, attack, decay)
y = y * env
y = y + noise * np.random.normal(size=len(y))

# normalize safely
mx = np.max(np.abs(y)) + 1e-12
y_norm = (y / mx) * 0.95

# Short view window
n_view = int(sr * (view_cycles / 1000.0))
n_view = max(200, min(n_view, len(t)))
tv = t[:n_view]
yv = y_norm[:n_view]

# spectrum
f, mag = fft_spectrum(y_norm, sr)

# Lissajous: x=osc1, y=osc2 (if osc2 is off, use delayed version of osc1)
x_l = y1[:n_view]
y_l = (y2[:n_view] if a2 > 0 else np.roll(y1[:n_view], 10))

# -----------------------------
# Layout
# -----------------------------
colA, colB = st.columns([2.2, 1])

with colB:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.subheader("📌 Live Readout")
    st.metric("Osc1", f"{w1} @ {f1} Hz")
    st.metric("Osc2", f"{w2} @ {f2} Hz" if a2 > 0 else "Off")
    st.metric("AM", "On" if am_on else "Off")
    st.metric("FM", "On" if fm_on else "Off")
    st.metric("Noise", f"{noise:.3f}")
    st.metric("Peak (pre-norm)", f"{mx:.3f}")
    st.markdown("---")
    st.write("🔊 **Play Audio**")
    st.audio(y_norm.astype(np.float32), sample_rate=sr)
    st.caption("Tip: try **FM Bell** preset for instant coolness.")
    st.markdown("</div>", unsafe_allow_html=True)

with colA:
    tabs = st.tabs(["🌊 Waveform", "📈 Spectrum (FFT)", "🌀 Lissajous", "🧠 What you're hearing"])

    with tabs[0]:
        fig = nice_plot(tv, yv, "Time Domain (Zoomed View)")
        st.plotly_chart(fig, use_container_width=True)

    with tabs[1]:
        # show up to 5k Hz for readability
        mask = f <= 5000
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=f[mask], y=mag[mask], mode="lines", line=dict(width=3)))
        fig2.update_layout(
            title="Frequency Spectrum (Windowed FFT)",
            height=420,
            margin=dict(l=10, r=10, t=60, b=10),
            template="plotly_dark",
            xaxis_title="Frequency (Hz)",
            yaxis_title="Normalized Magnitude",
        )
        fig2.update_xaxes(showgrid=True, gridcolor="rgba(255,255,255,0.08)")
        fig2.update_yaxes(showgrid=True, gridcolor="rgba(255,255,255,0.08)")
        st.plotly_chart(fig2, use_container_width=True)
        st.caption("Harmonics pop up for non-sine waves (square/saw/triangle). FM spreads energy into sidebands.")

    with tabs[2]:
        fig3 = go.Figure()
        fig3.add_trace(go.Scatter(
            x=x_l, y=y_l, mode="lines",
            line=dict(width=3),
        ))
        fig3.update_layout(
            title="Lissajous (Phase Relationship)",
            height=420,
            margin=dict(l=10, r=10, t=60, b=10),
            template="plotly_dark",
            xaxis_title="Osc1",
            yaxis_title="Osc2",
        )
        fig3.update_xaxes(scaleanchor="y", scaleratio=1, showgrid=True, gridcolor="rgba(255,255,255,0.08)")
        fig3.update_yaxes(showgrid=True, gridcolor="rgba(255,255,255,0.08)")
        st.plotly_chart(fig3, use_container_width=True)
        st.caption("Perfect circles/ellipses = clean phase relation. Messy shapes = modulation/noise/detune.")

    with tabs[3]:
        st.markdown(
            """
            **Quick intuition:**
            - **Waveform type** changes harmonic content (tone color).
            - **AM (tremolo)** = volume pulsing at AM rate.
            - **FM** = pitch wiggle / rich metallic tones; larger depth = more sidebands.
            - **Detuning** (f1 ≠ f2) = beating / chorus effect.
            - **Noise** adds grit (lo-fi / wind / analog-ish texture).
            """
        )
        st.markdown("**Try these:**")
        st.write("- Set Osc1=Saw, Osc2=Saw, f2 = f1 + 0.8 Hz → *instant synth detune*")
        st.write("- Turn FM on with depth 150–250 Hz and rate ~2–6 Hz → *bell / metallic*")
        st.write("- AM on at ~4–8 Hz depth ~0.5 → *classic tremolo*")

st.divider()
st.caption("Built with NumPy + Plotly + Streamlit. Minimal dependencies, maximum vibes.")
