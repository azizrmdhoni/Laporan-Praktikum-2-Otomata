# Laporan Praktikum 2 Otomata A

 ## Kelompok 09
 ### Anggota Kelompok:
| Name | NRP | Class |
| ---- | --- | ----- |
| Naufal Daffa Alfa Zain | 5025241066 | A |
| Muhamad Aziz Romdhoni  | 5025241071 | A |
| Anak Agung Putu Arda Nareswara | 5025241073 | A |

## 1. Import Library
 ```
 import tkinter as tk
 from tkinter import ttk, messagebox, filedialog
 from tkinter.scrolledtext import ScrolledText
 from dataclasses import dataclass
 ```
   
Pada bagian awal program ini, kami mengimpor beberapa library yang dibutuhkan untuk menjalankan aplikasi. Library utama yang digunakan adalah ``tkinter``, yang berfungsi untuk membuat tampilan GUI. Selain itu, kami juga menggunakan ``ttk`` agar tampilan komponen seperti tombol dan label terlihat lebih bagus & modern. Untuk menampilkan pesan seperti error atau notifikasi, kami menggunakan     ``messagebox``, sedangkan ``filedialog`` digunakan untuk membuka dan menyimpan file dari komputer. Kami juga menggunakan ``ScrolledText`` agar bisa menampilkan teks panjang yang bisa di-scroll, misalnya untuk aturan FSM atau ringkasan hasil. Terakhir, kami memakai ``dataclass`` untuk mempermudah pembuatan struktur data yang digunakan dalam menyimpan langkah-langkah proses FSM.

## 2. Definisi FSM
```
TRANSISI = {
    "S": {"0": "A", "1": "B"},
    "A": {"0": "C", "1": "B"},
    "B": {"0": "A", "1": "B"},
    "C": {"0": "C", "1": "C"},
}

STATE_AWAL = "S"
STATE_FINAL = {"B"}
STATE_TRAP = "C"
```
Pada bagian ini, kami mendefinisikan struktur dari Finite State Machine yang akan digunakan. kami membuat sebuah dictionary bernama ``TRANSISI`` yang berisi aturan perpindahan antar state berdasarkan input 0 atau 1. Selain itu, kami juga menentukan state awal yaitu S, state final yaitu B, dan state trap yaitu C. State trap ini berfungsi sebagai kondisi di mana string sudah pasti ditolak, yaitu ketika ditemukan substring 00. Dengan adanya definisi ini, program bisa mengetahui bagaimana cara berpindah dari satu state ke state lainnya saat membaca input.

## 3. Penjelasan State
```
PENJELASAN_STATE = {
    "S": "Start state / belum membaca simbol apa pun",
    "A": "Terakhir membaca 0, belum ada substring 00",
    "B": "Terakhir membaca 1, belum ada substring 00, state final",
    "C": "Trap state karena sudah ditemukan substring 00",
}
```
Kami juga menambahkan penjelasan untuk setiap state dalam bentuk dictionary ``PENJELASAN_STATE``. Misalnya, state S adalah kondisi awal sebelum membaca input, state A menunjukkan bahwa karakter terakhir adalah 0 tetapi belum ada substring 00, state B berarti karakter terakhir adalah 1 dan ini merupakan kondisi diterima, sedangkan state C menunjukkan bahwa sudah ditemukan substring 00 sehingga masuk ke kondisi trap. Penjelasan ini nantinya ditampilkan di tabel agar pengguna bisa memahami proses FSM dengan lebih jelas.

4. Dataclass StepFSM
```
@dataclass
class StepFSM:
    nomor: int
    state_awal: str
    simbol: str
    state_akhir: str
    keterangan: str
```
Kami membuat class ``StepFSM`` menggunakan ``@dataclass`` untuk menyimpan setiap langkah proses FSM. Di dalamnya terdapat atribut seperti nomor langkah, state awal, simbol yang dibaca, state akhir, dan keterangan. Dengan menggunakan dataclass, kami tidak perlu menulis constructor secara manual sehingga kode menjadi lebih sederhana. Class ini sangat membantu karena digunakan untuk mencatat seluruh proses perpindahan state yang nantinya akan ditampilkan dalam bentuk tabel pada GUI.

### 5. Class MesinFSM
```
class MesinFSM:
```
Class MesinFSM merupakan bagian utama yang menangani logika FSM.

- ### 5.1 Fungsi __init__
  ```
  def __init__(self):
    self.transisi = TRANSISI
    self.state_awal = STATE_AWAL
    self.state_final = STATE_FINAL
  ```
  Pada bagian constructor, kami menginisialisasi tabel transisi, state awal, dan state final.
- ### 5.2 Fungsi validasi_alfabet
  ```
  def validasi_alfabet(self, teks: str):
    """Mengembalikan (valid, pesan). Alfabet hanya boleh 0 dan 1."""
    if teks == "":
        return False, "String kosong ditolak karena bahasa menggunakan (0 + 1)+."
    salah = sorted(set(ch for ch in teks if ch not in "01"))
    if salah:
        return False, "Input hanya boleh berisi 0 dan 1. Karakter salah: " + ", ".join(salah)
    return True, "Input valid."
  ```
   Pada fungsi ini, kami membuat validasi awal untuk memastikan bahwa input yang diberikan oleh pengguna sesuai dengan aturan bahasa yang digunakan. Pertama, kami mengecek  apakah string kosong, karena dalam definisi bahasa (0 + 1)+, string kosong tidak diperbolehkan. Jika kosong, maka langsung dianggap tidak valid. Selanjutnya, kami mengecek apakah terdapat karakter selain 0 dan 1. Jika ditemukan karakter lain, maka input juga dianggap tidak valid dan program akan menampilkan karakter yang salah tersebut. Jika semua pengecekan lolos, maka input dinyatakan valid dan proses FSM dapat dilanjutkan. Fungsi ini berguna agar FSM hanya memproses input yang sesuai aturan.
- ### 5.3 Fungsi proses
  ```
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
  ```
  Fungsi ini merupakan inti dari logika FSM yang kami buat. Di dalam fungsi ini, pertama kami memanggil fungsi ``validasi_alfabet`` untuk memastikan input valid. Jika tidak valid, maka proses langsung dihentikan. Jika valid, kami mulai dari state awal yaitu S, kemudian membaca string input satu per satu menggunakan perulangan. Pada setiap karakter, kami menentukan state berikutnya berdasarkan tabel transisi, lalu menyimpan informasi perpindahan tersebut ke dalam list langkah menggunakan class ``StepFSM``. Selain itu, kami juga memberikan keterangan untuk setiap transisi, misalnya jika masuk state trap atau state final. Setelah seluruh string diproses, kami menentukan apakah string diterima atau ditolak berdasarkan state akhirnya. Fungsi ini menghasilkan output berupa status diterima atau tidak, state akhir, daftar langkah, serta pesan penjelasan.
- ### 5.4 Fungsi cek_langsung
  ```
    @staticmethod
  def cek_langsung(teks: str):
      """Pengecekan pembanding secara sederhana, untuk membantu verifikasi output."""
      return teks != "" and all(ch in "01" for ch in teks) and teks.endswith("1") and "00" not in teks
  ```
  Pada fungsi ini, kami membuat cara alternatif untuk mengecek apakah string memenuhi syarat bahasa tanpa menggunakan FSM. Kami hanya mengecek empat kondisi utama, yaitu string tidak kosong, hanya berisi 0 dan 1, berakhir dengan 1, serta tidak mengandung substring 00. Fungsi ini kami gunakan sebagai pembanding untuk memastikan bahwa hasil dari FSM sudah benar. Dengan fungsi ini, kami bisa melakukan validasi tambahan terhadap hasil yang diperoleh dari proses FSM.

## 6. Class AplikasiFSM
```
class AplikasiFSM(tk.Tk):
```
Class AplikasiFSM merupakan bagian yang mengatur tampilan aplikasi. Class ini merupakan turunan dari tk.Tk, sehingga berfungsi sebagai jendela utama.
- ### 6.1 Fungsi __init__
  ```
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
  ```
  Pada fungsi ini, kami melakukan inisialisasi awal untuk aplikasi GUI. Kami mengatur judul window, ukuran layar, serta ukuran minimum agar tampilan tidak terlalu kecil. Selain itu, kami juga membuat objek dari ``class MesinFSM`` yang akan digunakan untuk memproses input. Kami juga menyiapkan variabel untuk menyimpan langkah terakhir dan hasil terakhir. Setelah itu, kami memanggil fungsi ``_atur_style`` untuk mengatur tampilan,`` _bangun_ui`` untuk membuat komponen GUI, dan ``_isi_contoh_awal`` untuk mengisi input awal. Fungsi ini dijalankan pertama kali saat aplikasi dibuka
- ### 6.2 Fungsi _atur_style
  ```
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
  ```
  Pada fungsi ini, kami mengatur tampilan visual dari aplikasi. Kami mencoba menggunakan tema clam agar tampilannya lebih modern. Selain itu, kami juga mengatur jenis dan ukuran font untuk berbagai komponen seperti judul, subjudul, tombol, dan heading tabel. Tampilan aplikasi menjadi lebih rapi dan nyaman dilihat oleh pengguna.
- ### 6.3 Fungsi _bangun_ui
  ```
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
  ```
  Fungsi ini kami gunakan untuk membangun seluruh tampilan aplikasi. kami membuat frame utama yang kemudian dibagi menjadi dua bagian, yaitu panel kiri dan panel kanan. Panel kiri berisi input string, tombol aksi, contoh input, dan aturan FSM. Sedangkan panel kanan berisi hasil identifikasi, tabel jejak perpindahan state, dan ringkasan hasil. kami juga membuat tabel menggunakan Treeview untuk menampilkan langkah-langkah FSM secara detail. Semua komponen ini kami susun menggunakan sistem grid agar tampilannya rapi dan responsif. Fungsi ini merupakan bagian terbesar karena mencakup seluruh tampilan GUI.
- ### 6.4 Fungsi _isi_contoh_awal
  ```
  def _isi_contoh_awal(self):
    self.input_var.set("101101")
    self._status_input_langsung()
  ```
  Pada fungsi ini, kami mengisi input awal dengan contoh string yaitu 101101. Tujuannya agar saat aplikasi pertama kali dijalankan, pengguna langsung melihat contoh input yang bisa diproses tanpa harus mengetik dari awal. Selain itu, kami juga langsung memanggil fungsi untuk mengecek status input agar informasi awal bisa langsung ditampilkan
- ### 6.5 Fungsi _status_input_langsung
  ```
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
  ```
  Fungsi ini digunakan untuk mengecek kondisi input secara langsung setiap kali pengguna mengetik. Jika input kosong, kami menampilkan pesan bahwa string kosong tidak diperbolehkan. Jika terdapat karakter selain 0 dan 1, kami menampilkan karakter yang salah tersebut. Jika input sudah benar, kami memberikan informasi bahwa input siap diproses. Ini membuat aplikasi lebih interaktif karena pengguna bisa langsung mengetahui kesalahan input tanpa harus menekan tombol proses.
- ### 6.6 Fungsi _pilih_contoh
  ```
  def _pilih_contoh(self, listbox, diterima):
    pilihan = listbox.curselection()
    if not pilihan:
        return
    nilai = listbox.get(pilihan[0])
    if nilai == "ε / kosong":
        nilai = ""
    self.input_var.set(nilai)
    self.proses_input()
  ```
  Pada fungsi ini, kami menangani ketika pengguna memilih salah satu contoh dari listbox. Kami mengambil nilai yang dipilih, kemudian memasukkannya ke dalam input. Jika yang dipilih adalah simbol kosong, kami ubah menjadi string kosong. Setelah itu, kami langsung memproses input tersebut. Fungsi ini memudahkan pengguna untuk mencoba contoh tanpa harus mengetik manual.
- ### 6.7 Fungsi proses_input
  ```
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
  ```
  Fungsi ini merupakan penghubung antara GUI dan logika FSM. Ketika pengguna menekan tombol proses atau Enter, kami mengambil input dari textbox, lalu memanggil fungsi proses dari ``MesinFSM``. Hasilnya kemudian ditampilkan dalam bentuk status diterima atau ditolak, serta detail penjelasannya. Selain itu, kami juga mengisi tabel dengan langkah-langkah FSM dan membuat ringkasan hasil yang berisi informasi lengkap. Ringkasan ini juga disimpan agar bisa diekspor ke file. Fungsi ini sangat berguna karena mengatur seluruh alur proses dari input hingga output.
- ### 6.8 Fungsi _kosongkan_tabel
  ```
  def _kosongkan_tabel(self):
    for item in self.tabel.get_children():
        self.tabel.delete(item)
  ```
  Fungsi ini digunakan untuk menghapus semua data yang ada di tabel sebelum menampilkan hasil baru. Kami melakukan iterasi pada semua item di tabel, kemudian menghapusnya satu per satu. Hal ini berguna supaya data lama tidak tercampur dengan hasil yang baru.
- ### 6.9 Fungsi bersihkan
  ```
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
  ```
  Pada fungsi ini, kami mengembalikan aplikasi ke kondisi awal. Kami mengosongkan input, membersihkan tabel, menghapus hasil dan ringkasan, serta mengatur ulang status menjadi “Bersih”. Selain itu, kami juga mengatur fokus kembali ke input agar pengguna bisa langsung mengetik ulang. Fungsi ini memudahkan pengguna untuk melakukan percobaan baru.
- ### 6.10 Fungsi muat_file
  ```
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
  ```
  Fungsi ini kami gunakan untuk membaca input dari file teks. kami membuka file, lalu membaca isi file tersebut. Jika file memiliki banyak baris, kami mengambil baris pertama yang tidak kosong. Hasilnya kemudian dimasukkan ke dalam input. Jika terjadi error saat membuka file, kami menampilkan pesan error. Fungsi ini membuat aplikasi lebih mudah karena input tidak harus diketik manual.
- ### 6.11 Fungsi simpan_hasil
  ```
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
  ```
  Pada fungsi ini, kami menyimpan hasil proses FSM ke dalam file teks. Jika belum ada hasil, kami menampilkan peringatan. Jika ada, kami membuka dialog untuk menentukan lokasi penyimpanan, lalu menuliskan hasil ke file tersebut. Jika berhasil, kami menampilkan pesan sukses, dan jika gagal, kami menampilkan pesan error. Fungsi ini berguna untuk dokumentasi hasil.

## 7. Program Utama
```
if __name__ == "__main__":
    app = AplikasiFSM()
    app.mainloop()
```
Pada bagian ini, terdapat blok ``if __name__ == "__main__"``: yang berfungsi sebagai titik awal program. Di sini kami membuat objek dari ``AplikasiFSM`` dan menjalankan ``mainloop()`` agar aplikasi GUI bisa berjalan dan merespons interaksi pengguna. Bagian ini wajib ada dalam program GUI agar aplikasi bisa ditampilkan dengan benar.

## 8. Hail Output
<img width="1919" height="1018" alt="Screenshot 2026-04-26 194911" src="https://github.com/user-attachments/assets/9d692f39-a513-439b-911a-7c169d24fda4" />
<br><br>
<img width="1919" height="1022" alt="image" src="https://github.com/user-attachments/assets/4ce17d52-4e55-467b-ab05-642b95becca2" />

## 9. Analisis Output
Berdasarkan percobaan yang kami lakukan, kami menguji dua buah string yaitu “101101” dan “1011001” menggunakan aplikasi FSM yang telah dibuat. Untuk string pertama yaitu “101101”, hasil yang diperoleh adalah DITERIMA. Hal ini karena selama proses pembacaan, mesin tidak pernah masuk ke state trap (C), yang berarti tidak ditemukan substring 00. Selain itu, state akhir berada di B, yang merupakan state final, sehingga string memenuhi semua syarat, terutama karena berakhir dengan 1. Sedangkan untuk string kedua yaitu “1011001”, hasil yang diperoleh adalah DITOLAK. Pada awal proses, perpindahan state masih berjalan normal dan belum ditemukan pelanggaran. Namun ketika membaca bagian tengah string, tepatnya saat terdapat dua karakter 0 yang berurutan, mesin berpindah dari state A ke state C. State C ini merupakan trap state yang menandakan bahwa substring 00 telah ditemukan. Setelah masuk ke state ini, mesin akan tetap berada di state C meskipun membaca simbol berikutnya. Akibatnya, state akhir bukan lagi state final (B), melainkan state trap (C), sehingga string dinyatakan ditolak. Dari kedua percobaan tersebut, terlihat bahwa FSM bekerja sesuai dengan aturan yang telah ditentukan, yaitu menerima string yang berakhir dengan 1 dan tidak mengandung substring 00, serta menolak string yang melanggar salah satu dari syarat tersebut.

## 9. Kesimpulan

Berdasarkan keseluruhan pembuatan program dan hasil pengujian yang telah dilakukan, kami dapat menyimpulkan bahwa aplikasi FSM yang kami buat sudah berjalan dengan baik dan sesuai dengan konsep Finite State Machine dalam teori automata. Program ini berhasil mengimplementasikan aturan bahasa yaitu string harus berakhir dengan `1` dan tidak boleh mengandung substring `00`. Dari sisi kode, struktur program sudah cukup jelas karena memisahkan antara bagian logika FSM dan bagian tampilan (GUI). Class `MesinFSM` berfungsi untuk menangani proses inti seperti validasi input dan perpindahan state, sedangkan class `AplikasiFSM` bertugas mengatur tampilan serta interaksi pengguna. Dengan pemisahan ini, program menjadi lebih terstruktur dan mudah dipahami. Dari sisi hasil pengujian, program mampu memberikan output yang akurat. String seperti **“101101”** diterima karena memenuhi semua syarat, sedangkan string seperti **“1011001”** ditolak karena mengandung substring `00` yang menyebabkan mesin masuk ke trap state. Hasil ini juga konsisten dengan pengecekan langsung, sehingga menunjukkan bahwa implementasi FSM sudah benar. Selain itu, fitur tambahan seperti tampilan jejak perpindahan state dan ringkasan hasil sangat membantu dalam memahami bagaimana proses FSM bekerja secara detail. Hal ini membuat program tidak hanya sekadar memberikan hasil, tetapi juga memberikan penjelasan yang mendukung proses pembelajaran.
