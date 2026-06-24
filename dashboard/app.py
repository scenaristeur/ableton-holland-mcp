"""Dashboard graphique pour Ableton Holland MCP."""

import os
import tempfile
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
from datetime import datetime
import threading

import numpy as np
import sounddevice as sd
import soundfile as sf
import librosa
import matplotlib

matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


# Krumhansl-Kessler key profiles
_KK_MAJOR = [6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88]
_KK_MINOR = [6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17]
_NOTES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
TESTS_DIR = DATA_DIR / "tests"
ANALYSES_DIR = DATA_DIR / "analyses"
for d in [TESTS_DIR, ANALYSES_DIR]:
    d.mkdir(parents=True, exist_ok=True)


class AudioAnalyzer:
    """Encapsule capture + analyse."""

    @staticmethod
    def get_input_devices():
        devices = []
        for i, d in enumerate(sd.query_devices()):
            if d["max_input_channels"] > 0:
                name = d["name"].strip()
                devices.append((i, f"{i}: {name}"))
        return devices

    @staticmethod
    def capture(device_id, duration, samplerate=None):
        if samplerate is None:
            info = sd.query_devices(device_id)
            samplerate = int(info["default_samplerate"])
        recorded = []

        def callback(indata, frames, time_info, status):
            if status:
                print(f"Capture status: {status}")
            recorded.append(indata.copy())

        with sd.InputStream(
            device=device_id,
            channels=2,
            samplerate=samplerate,
            callback=callback,
        ):
            import time

            time.sleep(duration)

        if not recorded:
            raise RuntimeError("No audio captured")
        audio = np.concatenate(recorded, axis=0)
        return audio, samplerate

    @staticmethod
    def _detect_key(chroma):
        chroma_mean = chroma.mean(axis=1)
        kk_major = np.array(_KK_MAJOR)
        kk_minor = np.array(_KK_MINOR)
        corr_major = np.array(
            [np.correlate(chroma_mean, np.roll(kk_major, i)) for i in range(12)]
        )
        corr_minor = np.array(
            [np.correlate(chroma_mean, np.roll(kk_minor, i)) for i in range(12)]
        )
        idx_major = int(np.argmax(corr_major))
        idx_minor = int(np.argmax(corr_minor))
        if corr_major[idx_major] >= corr_minor[idx_minor]:
            return _NOTES[idx_major], "major", float(corr_major[idx_major])
        return _NOTES[idx_minor], "minor", float(corr_minor[idx_minor])

    @staticmethod
    def analyze(audio, sr):
        if audio.ndim > 1:
            y = np.mean(audio, axis=1)
        else:
            y = audio
        duration = len(y) / sr
        tempo_val = librosa.beat.tempo(y=y, sr=sr)[0]
        onset_frames = librosa.onset.onset_detect(y=y, sr=sr)
        chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
        mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
        key_note, key_mode, key_conf = AudioAnalyzer._detect_key(chroma)
        return {
            "duration_s": round(duration, 2),
            "tempo_bpm": round(float(tempo_val), 1),
            "beat_count": len(onset_frames),
            "chroma": chroma,
            "mfcc": mfcc,
            "y": y,
            "sr": sr,
            "onset_frames": onset_frames,
            "key": f"{key_note} {key_mode}",
            "key_confidence": round(key_conf, 1),
        }

    @staticmethod
    def save_audio(audio, sr, name=None):
        if name is None:
            name = f"capture_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        wav_path = ANALYSES_DIR / f"{name}.wav"
        sf.write(str(wav_path), audio, sr)
        return wav_path


class Dashboard:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Ableton Holland MCP — Dashboard")
        self.root.geometry("1100x750")
        self.root.minsize(900, 600)

        self.last_audio = None
        self.last_sr = None
        self.last_wav_path = None
        self.last_result = None
        self.recording = False

        self._build_ui()
        self._refresh_devices()

    def _build_ui(self):
        main = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        left = ttk.Frame(main)
        main.add(left, weight=0)

        center = ttk.Frame(main)
        main.add(center, weight=1)

        right = ttk.Frame(main, width=220)
        main.add(right, weight=0)

        self._build_controls(left)
        self._build_chart(center)
        self._build_results(right)

    def _build_controls(self, parent):
        box = ttk.LabelFrame(parent, text="Contrôles", padding=10)
        box.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        ttk.Label(box, text="Périphérique d'entrée :").pack(anchor=tk.W)
        self.device_var = tk.StringVar()
        self.device_menu = ttk.Combobox(
            box, textvariable=self.device_var, width=45, state="readonly"
        )
        self.device_menu.pack(fill=tk.X, pady=(0, 10))

        btn_frame = ttk.Frame(box)
        btn_frame.pack(fill=tk.X, pady=5)

        ttk.Label(btn_frame, text="Durée (s) :").pack(side=tk.LEFT)
        self.duration_var = tk.StringVar(value="5")
        duration_spin = ttk.Spinbox(
            btn_frame, from_=1, to=60, textvariable=self.duration_var, width=5
        )
        duration_spin.pack(side=tk.LEFT, padx=5)

        self.capture_btn = ttk.Button(
            btn_frame, text="🎤 Capturer", command=self._on_capture, width=15
        )
        self.capture_btn.pack(side=tk.LEFT, padx=5)

        self.play_btn = ttk.Button(
            btn_frame, text="🔊 Playback", command=self._on_playback, state=tk.DISABLED
        )
        self.play_btn.pack(side=tk.LEFT, padx=5)

        ttk.Separator(box, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)

        ttk.Label(box, text="Fichier existant :").pack(anchor=tk.W)
        file_frame = ttk.Frame(box)
        file_frame.pack(fill=tk.X, pady=5)

        self.file_path_var = tk.StringVar()
        ttk.Entry(file_frame, textvariable=self.file_path_var, width=30).pack(
            side=tk.LEFT
        )
        ttk.Button(file_frame, text="Parcourir", command=self._on_browse).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(file_frame, text="Analyser", command=self._on_analyze_file).pack(
            side=tk.LEFT
        )

        ttk.Separator(box, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)

        self.status_var = tk.StringVar(value="Prêt")
        ttk.Label(box, textvariable=self.status_var, wraplength=300).pack(anchor=tk.W)
        self.progress = ttk.Progressbar(box, mode="indeterminate")
        self.progress.pack(fill=tk.X, pady=5)

    def _build_chart(self, parent):
        self.fig = Figure(figsize=(7, 5), dpi=100)
        self.ax_chroma = self.fig.add_subplot(2, 1, 1)
        self.ax_wave = self.fig.add_subplot(2, 1, 2)
        self.fig.tight_layout(pad=2.0)

        self.canvas = FigureCanvasTkAgg(self.fig, master=parent)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self.ax_chroma.set_title("Chroma CQT")
        self.ax_wave.set_title("Waveform")

    def _build_results(self, parent):
        box = ttk.LabelFrame(parent, text="Résultats", padding=10)
        box.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.results_text = tk.Text(
            box, width=28, height=20, font=("Consolas", 10), state=tk.DISABLED
        )
        self.results_text.pack(fill=tk.BOTH, expand=True)

        ttk.Button(box, text="Effacer", command=self._clear_results).pack(pady=5)

    def _refresh_devices(self):
        devices = AudioAnalyzer.get_input_devices()
        names = [d[1] for d in devices]
        self.device_menu["values"] = names
        cable_idx = None
        for idx, (dev_id, name) in enumerate(devices):
            if "CABLE Output" in name:
                cable_idx = idx
                break
        if cable_idx is not None:
            self.device_menu.current(cable_idx)
        elif names:
            self.device_menu.current(0)

    def _get_device_id(self):
        sel = self.device_var.get()
        if not sel:
            raise ValueError("No device selected")
        return int(sel.split(":")[0])

    def _set_status(self, msg, busy=False):
        self.status_var.set(msg)
        if busy:
            self.progress.start()
        else:
            self.progress.stop()
        self.root.update_idletasks()

    def _append_result(self, text):
        self.results_text.config(state=tk.NORMAL)
        self.results_text.insert(tk.END, text + "\n")
        self.results_text.see(tk.END)
        self.results_text.config(state=tk.DISABLED)

    def _clear_results(self):
        self.results_text.config(state=tk.NORMAL)
        self.results_text.delete("1.0", tk.END)
        self.results_text.config(state=tk.DISABLED)

    def _update_charts(self, result):
        self.ax_chroma.clear()
        self.ax_wave.clear()

        chroma = result["chroma"]
        librosa.display.specshow(
            chroma, y_axis="chroma", x_axis="time", sr=result["sr"], ax=self.ax_chroma
        )
        self.ax_chroma.set_title(f"Chroma CQT — {result['tempo_bpm']} BPM")

        y = result["y"]
        times = np.linspace(0, result["duration_s"], len(y))
        self.ax_wave.plot(times, y, color="steelblue", linewidth=0.5)
        self.ax_wave.set_title(
            f"Waveform ({result['duration_s']}s, {result['beat_count']} onsets)"
        )
        self.ax_wave.set_xlabel("Time (s)")

        for onset in librosa.frames_to_time(result["onset_frames"], sr=result["sr"]):
            self.ax_wave.axvline(x=onset, color="red", alpha=0.5, linewidth=0.5)

        self.fig.tight_layout(pad=2.0)
        self.canvas.draw()

    def _on_capture(self):
        if self.recording:
            return
        self.recording = True
        self.capture_btn.config(state=tk.DISABLED)
        self._set_status("Capture en cours...", busy=True)
        self._append_result("---")

        def task():
            try:
                device_id = self._get_device_id()
                duration = float(self.duration_var.get())

                audio, sr = AudioAnalyzer.capture(device_id, duration)

                wav_path = AudioAnalyzer.save_audio(audio, sr)
                self.last_audio = audio
                self.last_sr = sr
                self.last_wav_path = wav_path

                result = AudioAnalyzer.analyze(audio, sr)
                self.last_result = result

                self.root.after(0, self._on_capture_done, result, wav_path)
            except Exception as e:
                self.root.after(0, self._on_capture_error, str(e))

        threading.Thread(target=task, daemon=True).start()

    def _on_capture_done(self, result, wav_path):
        self.recording = False
        self.capture_btn.config(state=tk.NORMAL)
        self.play_btn.config(state=tk.NORMAL)
        self._set_status(f"Capture terminée : {wav_path.name}")

        self._append_result(f"Fichier : {wav_path.name}")
        self._append_result(f"Durée   : {result['duration_s']}s")
        self._append_result(f"Tempo   : {result['tempo_bpm']} BPM")
        self._append_result(f"Tonalité: {result['key']}")
        self._append_result(f"Onsets  : {result['beat_count']}")

        self._update_charts(result)

    def _on_capture_error(self, msg):
        self.recording = False
        self.capture_btn.config(state=tk.NORMAL)
        self._set_status(f"Erreur : {msg}")
        self._append_result(f"❌ ERREUR : {msg}")

    def _on_playback(self):
        if self.last_audio is None or self.last_sr is None:
            return
        self._set_status("Playback en cours...")
        self._append_result("🔊 Playback...")

        def task():
            sd.play(self.last_audio, self.last_sr)
            sd.wait()
            self.root.after(0, lambda: self._set_status("Prêt"))

        threading.Thread(target=task, daemon=True).start()

    def _on_browse(self):
        path = filedialog.askopenfilename(
            title="Choisir un fichier audio",
            initialdir=str(TESTS_DIR),
            filetypes=[("Audio", "*.wav *.mp3 *.flac *.ogg *.m4a"), ("All", "*.*")],
        )
        if path:
            self.file_path_var.set(path)

    def _on_analyze_file(self):
        path = self.file_path_var.get()
        if not path or not os.path.exists(path):
            messagebox.showerror("Erreur", "Fichier introuvable")
            return
        self._set_status("Analyse en cours...", busy=True)
        self._append_result(f"Analyse : {os.path.basename(path)}")

        def task():
            try:
                y, sr = librosa.load(path, sr=None)
                result = AudioAnalyzer.analyze(y, sr)
                self.last_audio = y
                self.last_sr = sr
                self.last_result = result
                self.root.after(0, self._on_file_analyze_done, result, path)
            except Exception as e:
                self.root.after(0, self._on_capture_error, str(e))

        threading.Thread(target=task, daemon=True).start()

    def _on_file_analyze_done(self, result, path):
        self.play_btn.config(state=tk.NORMAL)
        self._set_status(f"Analyse terminée : {os.path.basename(path)}")

        self._append_result(f"Fichier : {os.path.basename(path)}")
        self._append_result(f"Durée   : {result['duration_s']}s")
        self._append_result(f"Tempo   : {result['tempo_bpm']} BPM")
        self._append_result(f"Tonalité: {result['key']}")
        self._append_result(f"Onsets  : {result['beat_count']}")

        self._update_charts(result)

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    Dashboard().run()
