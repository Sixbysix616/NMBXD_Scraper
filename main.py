"""GUI entry point for the nmbxd thread scraper."""
import os
import re
import sys
import queue
import threading
import tkinter as tk
from tkinter import filedialog, messagebox

from nmbxd_scraper import fetch_thread
from nmbxd_scraper.storage import get_default_output_dir, get_thread_dir, load_checkpoint


class _QueueWriter:
    """File-like object that funnels writes to a queue for the GUI to drain."""

    def __init__(self, q):
        self._q = q

    def write(self, s):
        if s:
            self._q.put(s)

    def flush(self):
        pass


class App:
    def __init__(self, root):
        self.root = root
        self.queue = queue.Queue()
        self.output_dir = get_default_output_dir()
        self.scraping = False

        root.title("X岛串抓取工具")
        root.geometry("580x480")
        self._build_ui()
        self._poll_queue()

    def _build_ui(self):
        pad = {"padx": 12, "pady": 6}

        frm_id = tk.Frame(self.root)
        frm_id.pack(fill="x", **pad)
        tk.Label(frm_id, text="串号：").pack(side="left")
        self.entry_id = tk.Entry(frm_id)
        self.entry_id.pack(side="left", fill="x", expand=True)

        frm_fmt = tk.Frame(self.root)
        frm_fmt.pack(fill="x", **pad)
        tk.Label(frm_fmt, text="保存格式：").pack(side="left")
        self.fmt = tk.StringVar(value="3")
        for text, val in [("仅 TXT", "1"), ("仅 HTML", "2"), ("两者都要", "3")]:
            tk.Radiobutton(frm_fmt, text=text, variable=self.fmt, value=val).pack(side="left")

        frm_dir = tk.Frame(self.root)
        frm_dir.pack(fill="x", **pad)
        tk.Button(frm_dir, text="选择保存文件夹", command=self._choose_dir).pack(side="left")
        self.lbl_dir = tk.Label(frm_dir, text=self.output_dir, anchor="w", fg="#555")
        self.lbl_dir.pack(side="left", fill="x", expand=True, padx=6)

        self.btn_start = tk.Button(
            self.root, text="开始抓取(｀･ω･)", command=self._start, height=2
        )
        self.btn_start.pack(fill="x", **pad)

        self.log = tk.Text(self.root, height=15, state="disabled", wrap="word")
        self.log.pack(fill="both", expand=True, padx=12, pady=(6, 12))

    def _choose_dir(self):
        chosen = filedialog.askdirectory(title="选择保存位置（可新建文件夹）")
        if chosen:
            self.output_dir = chosen
            self.lbl_dir.config(text=chosen)

    def _log(self, text):
        # Tk versions vary in non-BMP (emoji) support; drop them so insert never fails.
        text = "".join(ch if ord(ch) <= 0xFFFF else "" for ch in text)
        self.log.config(state="normal")
        self.log.insert("end", text)
        self.log.see("end")
        self.log.config(state="disabled")

    def _poll_queue(self):
        try:
            while True:
                self._log(self.queue.get_nowait())
        except queue.Empty:
            pass
        self.root.after(100, self._poll_queue)

    def _start(self):
        if self.scraping:
            return
        tid = self.entry_id.get().strip()
        if not re.match(r"^\d+$", tid):
            messagebox.showerror("错误", "串号无效Σ( ﾟдﾟ)，请输入纯数字")
            return

        thread_dir = get_thread_dir(self.output_dir, tid)
        resume = False
        if load_checkpoint(thread_dir):
            resume = messagebox.askyesno(
                "继续抓取", "发现未完成的记录，是否从上次中断处继续(つд⊂)？"
            )

        fmt = self.fmt.get()
        self.scraping = True
        self.btn_start.config(state="disabled", text="抓取中…")
        self._log("\n" + "=" * 46 + "\n")

        threading.Thread(
            target=self._worker,
            args=(tid, fmt in ("1", "3"), fmt in ("2", "3"), resume),
            daemon=True,
        ).start()

    def _worker(self, tid, save_txt, save_html, resume):
        old_stdout = sys.stdout
        sys.stdout = _QueueWriter(self.queue)
        thread_dir = None
        try:
            thread_dir = fetch_thread(
                tid,
                save_txt=save_txt,
                save_html=save_html,
                output_dir=self.output_dir,
                resume=resume,
            )
        except Exception as e:
            print(f"\n❌ 出错了(ﾟДﾟ≡ﾟДﾟ)：{e}\n")
        finally:
            sys.stdout = old_stdout
            self.root.after(0, self._done, thread_dir)

    def _done(self, thread_dir):
        self.scraping = False
        self.btn_start.config(state="normal", text="开始抓取(｀･ω･)")
        if thread_dir and os.path.isdir(thread_dir):
            try:
                os.startfile(thread_dir)
            except Exception:
                pass


def main():
    root = tk.Tk()
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
