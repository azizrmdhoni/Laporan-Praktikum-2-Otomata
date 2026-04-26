import csv, re, tkinter as tk
from dataclasses import dataclass
from tkinter import filedialog, messagebox, ttk
from tkinter.scrolledtext import ScrolledText

COMMON_KEYWORDS=set('if else elif while for do switch case default break continue return function def class try except finally import from as include using namespace public private protected static void int float double char string bool boolean true false null nil none var const let begin end then repeat until struct enum new delete goto and or not in is lambda yield with pass global nonlocal this self extends implements interface package throws throw catch final abstract'.split())
PYTHON_KEYWORDS=set('False None True and as assert async await break class continue def del elif else except finally for from global if import in is lambda nonlocal not or pass raise return try while with yield'.split())
C_LIKE_KEYWORDS=set('auto break case char const continue default do double else enum extern float for goto if inline int long register restrict return short signed sizeof static struct switch typedef union unsigned void volatile while class public private protected namespace using new delete try catch throw include define'.split())
JAVA_JS_KEYWORDS=set('abstract arguments await boolean break byte case catch char class const continue debugger default delete do double else enum eval export extends false final finally float for function goto if implements import in instanceof int interface let long native new null package private protected public return short static super switch synchronized this throw throws transient true try typeof var void volatile while with yield'.split())
BUILTIN_FUNCTIONS=set('print input len range str int float bool list dict set tuple open read write printf scanf cout cin println console log main'.split())
MULTI_CHAR_OPERATORS=['===','!==','==','!=','<=','>=','+=','-=','*=','/=','%=','++','--','&&','||','->','::',':=','<<','>>','**','//','=>','&=','|=','^=','<<=','>>=']
SINGLE_CHAR_OPERATORS=set('+-*/%=<>!&|^~?:')
SINGLE_CHAR_PUNCTUATION=set('()[]{};,.@')
MATH_OPERATORS={'+','-','*','/','%','**','=','+=','-=','*=','/=','%='}; RELATIONAL_OPERATORS={'==','!=','<=','>=','<','>'}

@dataclass
class Token:
    lexeme: str
    category: str
    line: int
    column: int
    
class LexerAnalyzer:
    def __init__(self, language="Umum"):
        self.language = language
        
    def set_language(self, language):
        self.language = language
        
    def _keyword_set(self):
        if self.language == "Python":
            return PYTHON_KEYWORDS
        if self.language == "C/C++":
            return C_LIKE_KEYWORDS
        if self.language == "Java/JavaScript":
            return JAVA_JS_KEYWORDS
        return COMMON_KEYWORDS
    
    def _is_keyword(self, lexeme):
        keywords = self._keyword_set()
        if self.language == "Python":
            return lexeme in keywords
        return lexeme.lower() in {word.lower() for word in keywords}
    @staticmethod
    
    def _peek_next_non_space(text, index):
        j = index
        while j < len(text) and text[j] in " \t\r":
            j += 1
        return text[j] if j < len(text) else ""
    
    def analyze(self, text):
        tokens = []
        i = 0
        line = 1
        col = 1
        n = len(text)
        
        def add_token(lexeme, category, start_line, start_col):
            tokens.append(Token(lexeme, category, start_line, start_col))
        while i < n:
            ch = text[i]
            if ch in " \t\r":
                i += 1
                col += 1
                continue
            if ch == "\n":
                i += 1
                line += 1
                col = 1
                continue
            if ch == "#" or (ch == "/" and i + 1 < n and text[i + 1] == "/"):
                start_line, start_col = line, col
                lex = ""
                while i < n and text[i] != "\n":
                    lex += text[i]
                    i += 1
                    col += 1
                add_token(lex, "Komentar", start_line, start_col)
                continue
            if ch == "/" and i + 1 < n and text[i + 1] == "*":
                start_line, start_col = line, col
                lex = "/*"
                i += 2
                col += 2
                closed = False
                while i < n:
                    if text[i] == "*" and i + 1 < n and text[i + 1] == "/":
                        lex += "*/"
                        i += 2
                        col += 2
                        closed = True
                        break
                    c = text[i]
                    lex += c
                    i += 1
                    if c == "\n":
                        line += 1
                        col = 1
                    else:
                        col += 1
                add_token(lex, "Komentar" if closed else "Komentar belum ditutup", start_line, start_col)
                continue
            if ch in ("'", '"'):
                quote = ch
                start_line, start_col = line, col
                lex = ch
                i += 1
                col += 1
                escaped = False
                closed = False
                while i < n:
                    c = text[i]
                    lex += c
                    i += 1
                    if c == "\n":
                        line += 1
                        col = 1
                        break
                    else:
                        col += 1
                    if escaped:
                        escaped = False
                    elif c == "\\":
                        escaped = True
                    elif c == quote:
                        closed = True
                        break
                add_token(lex, "Literal string" if closed else "String belum ditutup", start_line, start_col)
                continue
            if ch.isdigit() or (ch == "." and i + 1 < n and text[i + 1].isdigit()):
                start_line, start_col = line, col
                lex = ""
                has_digit = False
                while i < n and text[i].isdigit():
                    has_digit = True
                    lex += text[i]
                    i += 1
                    col += 1
                if i < n and text[i] == ".":
                    lex += "."
                    i += 1
                    col += 1
                    while i < n and text[i].isdigit():
                        has_digit = True
                        lex += text[i]
                        i += 1
                        col += 1
                if has_digit and i < n and text[i] in "eE":
                    j = i + 1
                    exp = text[i]
                    if j < n and text[j] in "+-":
                        exp += text[j]
                        j += 1
                    digits = ""
                    while j < n and text[j].isdigit():
                        digits += text[j]
                        j += 1
                    if digits:
                        lex += exp + digits
                        col += (j - i)
                        i = j
                add_token(lex, "Literal angka", start_line, start_col)
                continue
            if ch.isalpha() or ch == "_":
                start_line, start_col = line, col
                lex = ""
                while i < n and (text[i].isalnum() or text[i] == "_"):
                    lex += text[i]
                    i += 1
                    col += 1
                next_char = self._peek_next_non_space(text, i)
                lex_lower = lex.lower()
                if self._is_keyword(lex):
                    add_token(lex, "Reserve word", start_line, start_col)
                elif lex_lower in {item.lower() for item in BUILTIN_FUNCTIONS} and next_char == "(":
                    add_token(lex, "Fungsi bawaan", start_line, start_col)
                elif next_char == "(":
                    add_token(lex, "Fungsi", start_line, start_col)
                else:
                    add_token(lex, "Variabel", start_line, start_col)
                continue
            matched = None
            for op in sorted(MULTI_CHAR_OPERATORS, key=len, reverse=True):
                if text.startswith(op, i):
                    matched = op
                    break
            if matched:
                category = "Operator relasional" if matched in RELATIONAL_OPERATORS else "Operator matematika" if matched in MATH_OPERATORS else "Simbol / operator"
                add_token(matched, category, line, col)
                i += len(matched)
                col += len(matched)
                continue
            if ch in SINGLE_CHAR_OPERATORS:
                category = "Operator relasional" if ch in RELATIONAL_OPERATORS else "Operator matematika" if ch in MATH_OPERATORS else "Simbol / operator"
                add_token(ch, category, line, col)
                i += 1
                col += 1
                continue
            if ch in SINGLE_CHAR_PUNCTUATION:
                add_token(ch, "Simbol / tanda baca", line, col)
                i += 1
                col += 1
                continue
            add_token(ch, "Tidak dikenal", line, col)
            i += 1
            col += 1
        math_lines, logic_lines = self._extract_expression_lines(text)
        return tokens, math_lines, logic_lines
    
    def _remove_inline_strings(self, line):
        result = []
        i = 0
        quote = None
        escaped = False
        while i < len(line):
            c = line[i]
            if quote:
                if escaped:
                    escaped = False
                elif c == "\\":
                    escaped = True
                elif c == quote:
                    quote = None
                result.append(" ")
            else:
                if c in ("'", '"'):
                    quote = c
                    result.append(" ")
                else:
                    result.append(c)
            i += 1
        return "".join(result)

    def _strip_inline_comment(self, line):
        quote = None
        escaped = False
        i = 0
        while i < len(line):
            c = line[i]
            if quote:
                if escaped:
                    escaped = False
                elif c == "\\":
                    escaped = True
                elif c == quote:
                    quote = None
            else:
                if c in ("'", '"'):
                    quote = c
                elif line.startswith("#", i) or line.startswith("//", i):
                    return line[:i]
            i += 1
        return line

    def _extract_expression_lines(self, text):
        math_lines = []
        logic_lines = []
        assignment_pattern = re.compile(r"\b[A-Za-z_]\w*\s*(=|\+=|-=|\*=|/=|%=)\s*.+")
        math_op_pattern = re.compile(r"(\d+(\.\d+)?|[A-Za-z_]\w*|\))\s*(\+|-|\*|/|%|\*\*)\s*(\d+(\.\d+)?|[A-Za-z_]\w*|\()")
        numeric_assignment_pattern = re.compile(r"=\s*[+-]?\d+(\.\d+)?\b")
        relational_pattern = re.compile(r"(\b[A-Za-z_]\w*\b|\d)\s*(==|!=|<=|>=|<|>)\s*(\b[A-Za-z_]\w*\b|\d)")
        in_block_comment = False

        for idx, raw in enumerate(text.splitlines(), start=1):
            line_work = raw

            while True:
                if in_block_comment:
                    end = line_work.find("*/")
                    if end == -1:
                        line_work = ""
                        break
                    line_work = line_work[end + 2:]
                    in_block_comment = False
                    continue

                start = line_work.find("/*")
                if start == -1:
                    break
                end = line_work.find("*/", start + 2)
                if end == -1:
                    line_work = line_work[:start]
                    in_block_comment = True
                    break
                line_work = line_work[:start] + " " + line_work[end + 2:]

            line = self._strip_inline_comment(line_work).strip()
            if not line:
                continue

            check_line = self._remove_inline_strings(line)

            if relational_pattern.search(check_line):
                logic_lines.append((idx, line))
                continue

            has_assignment = assignment_pattern.search(check_line) is not None
            has_arithmetic = math_op_pattern.search(check_line) is not None
            has_numeric_assignment = numeric_assignment_pattern.search(check_line) is not None

            if has_assignment and (has_arithmetic or has_numeric_assignment):
                math_lines.append((idx, line))
                continue
            if has_arithmetic:
                math_lines.append((idx, line))

        return math_lines, logic_lines
class TokenApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Token Analyzer - Lexical Analyzer")
        self.geometry("1350x850")
        self.minsize(1120, 720)
        self.lexer = LexerAnalyzer()
        self.last_tokens = []
        self.last_math_lines = []
        self.last_logic_lines = []
        self._build_style()
        self._build_ui()
        self._load_example()
    def _build_style(self):
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except Exception:
            pass
        style.configure("Title.TLabel", font=("Segoe UI", 16, "bold"))
        style.configure("Header.TLabel", font=("Segoe UI", 10, "bold"))
        style.configure("TButton", padding=6)
        style.configure("TNotebook.Tab", padding=(14, 8))
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))
    def _build_ui(self):
        top = ttk.Frame(self, padding=10)
        top.pack(fill="both", expand=False)
        ttk.Label(top, text="Token Analyzer", style="Title.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(
            top,
            text="Tempelkan program, pilih mode bahasa, lalu klik Analisis untuk melihat token dan kategorinya.",
        ).grid(row=1, column=0, columnspan=8, sticky="w", pady=(4, 10))
        options = ttk.Frame(top)
        options.grid(row=2, column=0, columnspan=8, sticky="ew", pady=(0, 8))
        ttk.Label(options, text="Mode bahasa:").pack(side="left")
        self.language_var = tk.StringVar(value="Umum")
        self.language_combo = ttk.Combobox(
            options,
            textvariable=self.language_var,
            values=["Umum", "Python", "C/C++", "Java/JavaScript"],
            width=18,
            state="readonly",
        )
        self.language_combo.pack(side="left", padx=(6, 14))
        ttk.Label(options, text="Cari token:").pack(side="left")
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(options, textvariable=self.search_var, width=28)
        self.search_entry.pack(side="left", padx=(6, 6))
        ttk.Button(options, text="Cari", command=self.search_token).pack(side="left")
        ttk.Button(options, text="Reset Cari", command=self.reset_search).pack(side="left", padx=(6, 0))
        input_frame = ttk.LabelFrame(top, text="Input Program", padding=8)
        input_frame.grid(row=3, column=0, columnspan=8, sticky="nsew")
        top.columnconfigure(0, weight=1)
        top.rowconfigure(3, weight=1)
        self.input_text = ScrolledText(input_frame, wrap="none", height=16, font=("Consolas", 11))
        self.input_text.pack(fill="both", expand=True)
        btns = ttk.Frame(top)
        btns.grid(row=4, column=0, columnspan=8, sticky="ew", pady=(8, 0))
        for i in range(8):
            btns.columnconfigure(i, weight=1)
        ttk.Button(btns, text="Analisis", command=self.analyze_input).grid(row=0, column=0, padx=4, sticky="ew")
        ttk.Button(btns, text="Muat File", command=self.load_file).grid(row=0, column=1, padx=4, sticky="ew")
        ttk.Button(btns, text="Contoh", command=self._load_example).grid(row=0, column=2, padx=4, sticky="ew")
        ttk.Button(btns, text="Bersihkan", command=self.clear_all).grid(row=0, column=3, padx=4, sticky="ew")
        ttk.Button(btns, text="Salin Hasil", command=self.copy_results).grid(row=0, column=4, padx=4, sticky="ew")
        ttk.Button(btns, text="Simpan TXT", command=self.save_txt).grid(row=0, column=5, padx=4, sticky="ew")
        ttk.Button(btns, text="Simpan CSV", command=self.save_csv).grid(row=0, column=6, padx=4, sticky="ew")
        ttk.Button(btns, text="Keluar", command=self.destroy).grid(row=0, column=7, padx=4, sticky="ew")
        mid = ttk.Frame(self, padding=(10, 0, 10, 10))
        mid.pack(fill="both", expand=True)
        table_frame = ttk.LabelFrame(mid, text="Daftar Token", padding=8)
        table_frame.pack(fill="both", expand=True, side="left")
        table_cols = ("No", "Baris", "Kolom", "Token", "Kategori")
        self.tree = ttk.Treeview(table_frame, columns=table_cols, show="headings", height=20)
        widths = {"No": 60, "Baris": 70, "Kolom": 70, "Token": 300, "Kategori": 190}
        for col_name in table_cols:
            self.tree.heading(col_name, text=col_name)
            self.tree.column(col_name, width=widths[col_name], anchor="w")
        yscroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        xscroll = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=yscroll.set, xscrollcommand=xscroll.set)
        self.tree.tag_configure("found", background="#fff3b0")
        self.tree.pack(side="top", fill="both", expand=True)
        yscroll.pack(side="right", fill="y")
        xscroll.pack(side="bottom", fill="x")
        side = ttk.Frame(mid)
        side.pack(fill="both", expand=True, side="right", padx=(10, 0))
        side.columnconfigure(0, weight=1)
        side.rowconfigure(0, weight=1)
        self.nb = ttk.Notebook(side)
        self.nb.pack(fill="both", expand=True)
        self.tabs = {}
        for name in [
            "Ringkasan",
            "Reserve Words",
            "Simbol / Operator / Tanda Baca",
            "Variabel",
            "Fungsi",
            "Ekspresi Matematika",
            "Ekspresi Logika",
            "Token Lain",
        ]:
            frame = ttk.Frame(self.nb, padding=6)
            self.nb.add(frame, text=name)
            txt = ScrolledText(frame, wrap="word", font=("Consolas", 10))
            txt.pack(fill="both", expand=True)
            self.tabs[name] = txt
        self.status_var = tk.StringVar(value="Siap.")
        status = ttk.Label(self, textvariable=self.status_var, relief="sunken", anchor="w")
        status.pack(fill="x", side="bottom")
    def _load_example(self):
        example = """# Contoh program Python
/* Ini contoh komentar multi-line
   jika mode bahasa C-like digunakan */
def hitung_luas(p, l):
    luas = p * l
    return luas
x = 10
y = 20
z = hitung_luas(x, y) + 5
if z >= 50:
    print("Besar")
else:
    print("Kecil")
"""
        self.input_text.delete("1.0", tk.END)
        self.input_text.insert("1.0", example)
        self.status_var.set("Contoh program dimuat.")
    def clear_all(self):
        self.input_text.delete("1.0", tk.END)
        for item in self.tree.get_children():
            self.tree.delete(item)
        for txt in self.tabs.values():
            txt.delete("1.0", tk.END)
        self.last_tokens = []
        self.last_math_lines = []
        self.last_logic_lines = []
        self.status_var.set("Bersih.")
    def load_file(self):
        file_path = filedialog.askopenfilename(
            title="Pilih file program",
            filetypes=[
                ("All supported", "*.py *.txt *.c *.cpp *.java *.js *.ts *.php *.html *.cs *.go *.rb"),
                ("Text files", "*.txt"),
                ("All files", "*.*"),
            ],
        )
        if not file_path:
            return
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
        except UnicodeDecodeError:
            with open(file_path, "r", encoding="latin-1") as f:
                content = f.read()
        except Exception as e:
            messagebox.showerror("Gagal membuka file", str(e))
            return
        self.input_text.delete("1.0", tk.END)
        self.input_text.insert("1.0", content)
        self.status_var.set(f"File dimuat: {file_path}")
    def analyze_input(self):
        source = self.input_text.get("1.0", tk.END)
        if not source.strip():
            messagebox.showwarning("Input kosong", "Masukkan program terlebih dahulu.")
            return
        self.lexer.set_language(self.language_var.get())
        tokens, math_lines, logic_lines = self.lexer.analyze(source)
        self.last_tokens = tokens
        self.last_math_lines = math_lines
        self.last_logic_lines = logic_lines
        for item in self.tree.get_children():
            self.tree.delete(item)
        grouped = {
            "Reserve word": [],
            "Operator matematika": [],
            "Operator relasional": [],
            "Simbol / operator": [],
            "Simbol / tanda baca": [],
            "Variabel": [],
            "Fungsi": [],
            "Fungsi bawaan": [],
            "Literal angka": [],
            "Literal string": [],
            "Komentar": [],
            "Komentar belum ditutup": [],
            "String belum ditutup": [],
            "Tidak dikenal": [],
        }
        for idx, tok in enumerate(tokens, start=1):
            self.tree.insert("", "end", values=(idx, tok.line, tok.column, tok.lexeme, tok.category))
            grouped.setdefault(tok.category, []).append(f"[{tok.line}:{tok.column}] {tok.lexeme}")
        self._fill_text("Ringkasan", self._make_summary(tokens, math_lines, logic_lines))
        self._fill_text("Reserve Words", "\n".join(grouped["Reserve word"]) or "-")
        self._fill_text(
            "Simbol / Operator / Tanda Baca",
            "\n".join(
                grouped["Operator matematika"]
                + grouped["Operator relasional"]
                + grouped["Simbol / operator"]
                + grouped["Simbol / tanda baca"]
            ) or "-",
        )
        self._fill_text("Variabel", "\n".join(grouped["Variabel"]) or "-")
        self._fill_text("Fungsi", "\n".join(grouped["Fungsi"] + grouped["Fungsi bawaan"]) or "-")
        self._fill_text("Ekspresi Matematika", "\n".join([f"[baris {ln}] {line}" for ln, line in math_lines]) or "-")
        self._fill_text("Ekspresi Logika", "\n".join([f"[baris {ln}] {line}" for ln, line in logic_lines]) or "-")
        other_text = "\n".join(
            grouped["Literal angka"]
            + grouped["Literal string"]
            + grouped["Komentar"]
            + grouped["Komentar belum ditutup"]
            + grouped["String belum ditutup"]
            + grouped["Tidak dikenal"]
        ) or "-"
        self._fill_text("Token Lain", other_text)
        self.status_var.set(
            f"Selesai. Total token: {len(tokens)} | Ekspresi matematika: {len(math_lines)} | Ekspresi logika: {len(logic_lines)}"
        )
        
    def _fill_text(self, tab_name, content):
        txt = self.tabs[tab_name]
        txt.config(state="normal")
        txt.delete("1.0", tk.END)
        txt.insert("1.0", content)
        txt.config(state="normal")
        
    def _make_summary(self, tokens, math_lines, logic_lines):
        counts = {}
        for tok in tokens:
            counts[tok.category] = counts.get(tok.category, 0) + 1
        lines = []
        lines.append(f"Mode bahasa: {self.language_var.get()}")
        lines.append(f"Total token: {len(tokens)}")
        lines.append("")
        lines.append("Jumlah per kategori:")
        for category in sorted(counts.keys()):
            lines.append(f"- {category}: {counts[category]}")
        lines.append("")
        lines.append(f"Ekspresi matematika terdeteksi: {len(math_lines)}")
        if math_lines:
            lines.append(f"- Contoh: baris {math_lines[0][0]}: {math_lines[0][1]}")
        lines.append(f"Ekspresi logika/kondisi terdeteksi: {len(logic_lines)}")
        if logic_lines:
            lines.append(f"- Contoh: baris {logic_lines[0][0]}: {logic_lines[0][1]}")
        return "\n".join(lines)
    
    def _build_output_text(self):
        if not self.last_tokens:
            return ""
        parts = []
        for name in self.tabs:
            parts.append(f"=== {name.upper()} ===")
            parts.append(self.tabs[name].get("1.0", tk.END).strip())
            parts.append("")
        return "\n".join(parts).strip()
    
    def copy_results(self):
        output = self._build_output_text()
        if not output:
            messagebox.showwarning("Belum ada hasil", "Klik Analisis terlebih dahulu.")
            return
        self.clipboard_clear()
        self.clipboard_append(output)
        self.update()
        messagebox.showinfo("Tersalin", "Hasil analisis telah disalin ke clipboard.")
        
    def save_txt(self):
        output = self._build_output_text()
        if not output:
            messagebox.showwarning("Belum ada hasil", "Klik Analisis terlebih dahulu.")
            return
        file_path = filedialog.asksaveasfilename(
            title="Simpan hasil sebagai TXT",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
        )
        if not file_path:
            return
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(output)
            messagebox.showinfo("Berhasil", f"Hasil disimpan ke:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Gagal menyimpan", str(e))
            
    def save_csv(self):
        if not self.last_tokens:
            messagebox.showwarning("Belum ada hasil", "Klik Analisis terlebih dahulu.")
            return
        file_path = filedialog.asksaveasfilename(
            title="Simpan token sebagai CSV",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
        )
        if not file_path:
            return
        try:
            with open(file_path, "w", encoding="utf-8", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["No", "Baris", "Kolom", "Token", "Kategori"])
                for idx, tok in enumerate(self.last_tokens, start=1):
                    writer.writerow([idx, tok.line, tok.column, tok.lexeme, tok.category])
            messagebox.showinfo("Berhasil", f"Token disimpan ke:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Gagal menyimpan", str(e))
            
    def search_token(self):
        keyword = self.search_var.get().strip().lower()
        if not keyword:
            return
        found = 0
        first_item = None
        for item in self.tree.get_children():
            values = self.tree.item(item, "values")
            lexeme = str(values[3]).lower()
            category = str(values[4]).lower()
            if keyword in lexeme or keyword in category:
                self.tree.item(item, tags=("found",))
                found += 1
                if first_item is None:
                    first_item = item
            else:
                self.tree.item(item, tags=())
        if first_item:
            self.tree.see(first_item)
        self.status_var.set(f"Pencarian '{keyword}': {found} token ditemukan.")
        
    def reset_search(self):
        self.search_var.set("")
        for item in self.tree.get_children():
            self.tree.item(item, tags=())
        self.status_var.set("Pencarian direset.")
        
if __name__ == "__main__":
    app = TokenApp()
    app.mainloop()
