import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkinter.scrolledtext import ScrolledText
from dataclasses import dataclass

TRANSISI = {
    "S": {"0": "A", "1": "B"},
    "A": {"0": "C", "1": "B"},
    "B": {"0": "A", "1": "B"},
    "C": {"0": "C", "1": "C"},
}

STATE_AWAL = "S"
STATE_FINAL = {"B"}
STATE_TRAP = "C"

PENJELASAN_STATE = {
    "S": "Start state / belum membaca simbol apa pun",
    "A": "Terakhir membaca 0, belum ada substring 00",
    "B": "Terakhir membaca 1, belum ada substring 00, state final",
    "C": "Trap state karena sudah ditemukan substring 00",
}


@dataclass
class StepFSM:
    nomor: int
    state_awal: str
    simbol: str
    state_akhir: str
    keterangan: str


class MesinFSM:
    def __init__(self):
        self.transisi = TRANSISI
        self.state_awal = STATE_AWAL
        self.state_final = STATE_FINAL

    def validasi_alfabet(self, teks: str):
        """Mengembalikan (valid, pesan). Alfabet hanya boleh 0 dan 1."""
        if teks == "":
            return False, "String kosong ditolak karena bahasa menggunakan (0 + 1)+."
        salah = sorted(set(ch for ch in teks if ch not in "01"))
        if salah:
            return False, "Input hanya boleh berisi 0 dan 1. Karakter salah: " + ", ".join(salah)
        return True, "Input valid."

    def proses(self, teks: str):
        """Memproses string dan menghasilkan status diterima/ditolak beserta jejak langkah."""
        valid, pesan = self.validasi_alfabet(teks)
        if not valid:
            return False, STATE_AWAL, [], pesan

        state = self.state_awal
        langkah = []

        for i, simbol in enumerate(teks, start=1):
            sebelum = state
            sesudah = self.transisi[sebelum][simbol]
            state = sesudah

            if sesudah == STATE_TRAP:
                ket = "Masuk trap state; substring 00 ditemukan atau sudah pernah ditemukan."
            elif sesudah in self.state_final:
                ket = "Berada di state final B; string sementara berakhir dengan 1."
            elif sesudah == "A":
                ket = "String sementara berakhir dengan 0, masih belum ada substring 00."
            else:
                ket = PENJELASAN_STATE.get(sesudah, "-")

            langkah.append(StepFSM(i, sebelum, simbol, sesudah, ket))

        diterima = state in self.state_final
        if diterima:
            pesan = "DITERIMA: string berakhir dengan 1 dan tidak memiliki substring 00."
        else:
            if state == STATE_TRAP:
                pesan = "DITOLAK: string memiliki substring 00."
            elif state == "A":
                pesan = "DITOLAK: string tidak memiliki substring 00, tetapi karakter terakhir adalah 0."
            else:
                pesan = "DITOLAK: state akhir bukan state final."

        return diterima, state, langkah, pesan

    @staticmethod
    def cek_langsung(teks: str):
        """Pengecekan pembanding secara sederhana, untuk membantu verifikasi output."""
        return teks != "" and all(ch in "01" for ch in teks) and teks.endswith("1") and "00" not in teks


class AplikasiFSM(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("FSM - Bahasa Berakhir 1 dan Tidak Mengandung 00")
        self.geometry("1180x760")
        self.minsize(1000, 650)

        self.mesin = MesinFSM()
        self.langkah_terakhir = []
        self.hasil_terakhir = ""

        self._atur_style()
        self._bangun_ui()
        self._isi_contoh_awal()

    def _atur_style(self):
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("Judul.TLabel", font=("Segoe UI", 16, "bold"))
        style.configure("Subjudul.TLabel", font=("Segoe UI", 10))
        style.configure("Hasil.TLabel", font=("Segoe UI", 13, "bold"))
        style.configure("TButton", padding=6)
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))

    def _bangun_ui(self):
        utama = ttk.Frame(self, padding=10)
        utama.pack(fill="both", expand=True)
        utama.columnconfigure(0, weight=1)
        utama.columnconfigure(1, weight=2)
        utama.rowconfigure(2, weight=1)

        ttk.Label(
            utama,
            text="Simulator FSM",
            style="Judul.TLabel"
        ).grid(row=0, column=0, columnspan=2, sticky="w")

        deskripsi = (
            "Bahasa L = { x ∈ (0 + 1)+ | karakter terakhir x adalah 1 "
            "dan x tidak memiliki substring 00 }."
        )
        ttk.Label(utama, text=deskripsi, style="Subjudul.TLabel").grid(
            row=1, column=0, columnspan=2, sticky="w", pady=(3, 10)
        )

        panel_kiri = ttk.Frame(utama)
        panel_kiri.grid(row=2, column=0, sticky="nsew", padx=(0, 10))
        panel_kiri.columnconfigure(0, weight=1)

        input_frame = ttk.LabelFrame(panel_kiri, text="Input String", padding=8)
        input_frame.grid(row=0, column=0, sticky="ew")
        input_frame.columnconfigure(0, weight=1)

        self.input_var = tk.StringVar()
        self.input_var.trace_add("write", lambda *args: self._status_input_langsung())

        self.input_entry = ttk.Entry(input_frame, textvariable=self.input_var, font=("Consolas", 16))
        self.input_entry.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        self.input_entry.focus()

        tombol_frame = ttk.Frame(input_frame)
        tombol_frame.grid(row=1, column=0, sticky="ew")
        for i in range(4):
            tombol_frame.columnconfigure(i, weight=1)

        ttk.Button(tombol_frame, text="Proses FSM", command=self.proses_input).grid(row=0, column=0, padx=3, sticky="ew")
        ttk.Button(tombol_frame, text="Bersihkan", command=self.bersihkan).grid(row=0, column=1, padx=3, sticky="ew")
        ttk.Button(tombol_frame, text="Muat TXT", command=self.muat_file).grid(row=0, column=2, padx=3, sticky="ew")
        ttk.Button(tombol_frame, text="Simpan Hasil", command=self.simpan_hasil).grid(row=0, column=3, padx=3, sticky="ew")

        contoh_frame = ttk.LabelFrame(panel_kiri, text="Contoh Cepat", padding=8)
        contoh_frame.grid(row=1, column=0, sticky="ew", pady=(10, 0))
        contoh_frame.columnconfigure(0, weight=1)
        contoh_frame.columnconfigure(1, weight=1)

        contoh_diterima = ["1", "01", "101", "111", "0101", "101101"]
        contoh_ditolak = ["", "0", "10", "1001", "1100", "abc"]

        ttk.Label(contoh_frame, text="Diterima:").grid(row=0, column=0, sticky="w")
        ttk.Label(contoh_frame, text="Ditolak:").grid(row=0, column=1, sticky="w")

        self.list_ok = tk.Listbox(contoh_frame, height=6, exportselection=False)
        self.list_no = tk.Listbox(contoh_frame, height=6, exportselection=False)
        self.list_ok.grid(row=1, column=0, sticky="ew", padx=(0, 5))
        self.list_no.grid(row=1, column=1, sticky="ew", padx=(5, 0))

        for item in contoh_diterima:
            self.list_ok.insert(tk.END, item)
        for item in contoh_ditolak:
            tampil = "ε / kosong" if item == "" else item
            self.list_no.insert(tk.END, tampil)

        self.list_ok.bind("<<ListboxSelect>>", lambda e: self._pilih_contoh(self.list_ok, True))
        self.list_no.bind("<<ListboxSelect>>", lambda e: self._pilih_contoh(self.list_no, False))

        aturan_frame = ttk.LabelFrame(panel_kiri, text="Aturan Transisi", padding=8)
        aturan_frame.grid(row=2, column=0, sticky="nsew", pady=(10, 0))
        panel_kiri.rowconfigure(2, weight=1)

        aturan = (
            "State awal : S\n"
            "State final: B\n\n"
            "S --0--> A\n"
            "S --1--> B\n"
            "A --0--> C\n"
            "A --1--> B\n"
            "B --0--> A\n"
            "B --1--> B\n"
            "C --0--> C\n"
            "C --1--> C\n\n"
            "Makna state:\n"
            "S = awal\n"
            "A = terakhir 0, belum ada 00\n"
            "B = terakhir 1, diterima\n"
            "C = trap, sudah ada 00"
        )
        self.aturan_text = ScrolledText(aturan_frame, height=14, wrap="word", font=("Consolas", 10))
        self.aturan_text.pack(fill="both", expand=True)
        self.aturan_text.insert("1.0", aturan)
        self.aturan_text.config(state="disabled")

        panel_kanan = ttk.Frame(utama)
        panel_kanan.grid(row=2, column=1, sticky="nsew")
        panel_kanan.columnconfigure(0, weight=1)
        panel_kanan.rowconfigure(2, weight=1)

        hasil_frame = ttk.LabelFrame(panel_kanan, text="Hasil Identifikasi", padding=8)
        hasil_frame.grid(row=0, column=0, sticky="ew")
        hasil_frame.columnconfigure(0, weight=1)

        self.hasil_var = tk.StringVar(value="Masukkan string, lalu klik Proses FSM.")
        self.hasil_label = ttk.Label(hasil_frame, textvariable=self.hasil_var, style="Hasil.TLabel")
        self.hasil_label.grid(row=0, column=0, sticky="w")

        self.detail_var = tk.StringVar(value="-")
        ttk.Label(hasil_frame, textvariable=self.detail_var, wraplength=700).grid(row=1, column=0, sticky="w", pady=(4, 0))

        tabel_frame = ttk.LabelFrame(panel_kanan, text="Jejak Perpindahan State", padding=8)
        tabel_frame.grid(row=2, column=0, sticky="nsew", pady=(10, 0))
        tabel_frame.columnconfigure(0, weight=1)
        tabel_frame.rowconfigure(0, weight=1)

        kolom = ("No", "State Awal", "Input", "State Akhir", "Keterangan")
        self.tabel = ttk.Treeview(tabel_frame, columns=kolom, show="headings")
        ukuran = {
            "No": 55,
            "State Awal": 100,
            "Input": 80,
            "State Akhir": 100,
            "Keterangan": 480,
        }
        for k in kolom:
            self.tabel.heading(k, text=k)
            self.tabel.column(k, width=ukuran[k], anchor="w")

        yscroll = ttk.Scrollbar(tabel_frame, orient="vertical", command=self.tabel.yview)
        xscroll = ttk.Scrollbar(tabel_frame, orient="horizontal", command=self.tabel.xview)
        self.tabel.configure(yscrollcommand=yscroll.set, xscrollcommand=xscroll.set)

        self.tabel.grid(row=0, column=0, sticky="nsew")
        yscroll.grid(row=0, column=1, sticky="ns")
        xscroll.grid(row=1, column=0, sticky="ew")

        ringkasan_frame = ttk.LabelFrame(panel_kanan, text="Ringkasan", padding=8)
        ringkasan_frame.grid(row=3, column=0, sticky="ew", pady=(10, 0))
        self.ringkasan_text = ScrolledText(ringkasan_frame, height=7, wrap="word", font=("Consolas", 10))
        self.ringkasan_text.pack(fill="x", expand=False)

        self.status_var = tk.StringVar(value="Siap.")
        status = ttk.Label(self, textvariable=self.status_var, relief="sunken", anchor="w")
        status.pack(fill="x", side="bottom")

        self.bind("<Return>", lambda event: self.proses_input())

    def _isi_contoh_awal(self):
        self.input_var.set("101101")
        self._status_input_langsung()

    def _status_input_langsung(self):
        teks = self.input_var.get().strip()
        if teks == "":
            self.status_var.set("Input kosong. Bahasa menggunakan (0 + 1)+ sehingga string kosong akan ditolak.")
            return
        salah = sorted(set(ch for ch in teks if ch not in "01"))
        if salah:
            self.status_var.set("Ada karakter selain 0 dan 1: " + ", ".join(salah))
        else:
            self.status_var.set("Input hanya berisi alfabet 0 dan 1. Tekan Enter atau klik Proses FSM.")

    def _pilih_contoh(self, listbox, diterima):
        pilihan = listbox.curselection()
        if not pilihan:
            return
        nilai = listbox.get(pilihan[0])
        if nilai == "ε / kosong":
            nilai = ""
        self.input_var.set(nilai)
        self.proses_input()

    def proses_input(self):
        teks = self.input_var.get().strip()
        diterima, state_akhir, langkah, pesan = self.mesin.proses(teks)
        cek_pembanding = self.mesin.cek_langsung(teks)

        self.langkah_terakhir = langkah
        self._kosongkan_tabel()

        for step in langkah:
            self.tabel.insert(
                "",
                "end",
                values=(step.nomor, step.state_awal, step.simbol, step.state_akhir, step.keterangan),
            )

        status_teks = "DITERIMA" if diterima else "DITOLAK"
        self.hasil_var.set(status_teks)
        self.detail_var.set(pesan)

        ringkasan = []
        ringkasan.append(f"Input string       : {teks if teks else 'ε / kosong'}")
        ringkasan.append(f"Panjang string     : {len(teks)}")
        ringkasan.append(f"State awal         : {STATE_AWAL}")
        ringkasan.append(f"State akhir        : {state_akhir}")
        ringkasan.append(f"State final        : {', '.join(sorted(STATE_FINAL))}")
        ringkasan.append(f"Hasil FSM          : {status_teks}")
        ringkasan.append(f"Cek syarat langsung: {'DITERIMA' if cek_pembanding else 'DITOLAK'}")
        ringkasan.append("")
        ringkasan.append("Syarat diterima:")
        ringkasan.append("1. String tidak kosong")
        ringkasan.append("2. Hanya terdiri dari simbol 0 dan 1")
        ringkasan.append("3. Karakter terakhir adalah 1")
        ringkasan.append("4. Tidak memiliki substring 00")

        self.ringkasan_text.config(state="normal")
        self.ringkasan_text.delete("1.0", tk.END)
        self.ringkasan_text.insert("1.0", "\n".join(ringkasan))
        self.ringkasan_text.config(state="disabled")

        self.hasil_terakhir = "\n".join(ringkasan) + "\n\nJejak transisi:\n"
        for step in langkah:
            self.hasil_terakhir += (
                f"{step.nomor}. {step.state_awal} --{step.simbol}--> "
                f"{step.state_akhir} | {step.keterangan}\n"
            )

        self.status_var.set(pesan)

    def _kosongkan_tabel(self):
        for item in self.tabel.get_children():
            self.tabel.delete(item)

    def bersihkan(self):
        self.input_var.set("")
        self._kosongkan_tabel()
        self.hasil_var.set("Masukkan string, lalu klik Proses FSM.")
        self.detail_var.set("-")
        self.ringkasan_text.config(state="normal")
        self.ringkasan_text.delete("1.0", tk.END)
        self.ringkasan_text.config(state="disabled")
        self.hasil_terakhir = ""
        self.status_var.set("Bersih.")
        self.input_entry.focus()

    def muat_file(self):
        path = filedialog.askopenfilename(
            title="Pilih file teks berisi string biner",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
        )
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                isi = f.read().strip()
        except UnicodeDecodeError:
            with open(path, "r", encoding="latin-1") as f:
                isi = f.read().strip()
        except Exception as e:
            messagebox.showerror("Gagal membuka file", str(e))
            return

        # Jika file berisi beberapa baris, ambil baris pertama yang tidak kosong.
        baris = [x.strip() for x in isi.splitlines() if x.strip()]
        self.input_var.set(baris[0] if baris else "")
        self.status_var.set(f"File dimuat: {path}")

    def simpan_hasil(self):
        if not self.hasil_terakhir.strip():
            messagebox.showwarning("Belum ada hasil", "Proses string terlebih dahulu sebelum menyimpan hasil.")
            return
        path = filedialog.asksaveasfilename(
            title="Simpan hasil FSM",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
        )
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(self.hasil_terakhir)
            messagebox.showinfo("Berhasil", "Hasil FSM berhasil disimpan.")
            self.status_var.set(f"Hasil disimpan: {path}")
        except Exception as e:
            messagebox.showerror("Gagal menyimpan", str(e))


if __name__ == "__main__":
    app = AplikasiFSM()
    app.mainloop()
