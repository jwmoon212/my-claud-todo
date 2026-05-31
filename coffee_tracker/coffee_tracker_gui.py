import tkinter as tk
from tkinter import messagebox
import sys
import os
from datetime import date, timedelta, datetime

if getattr(sys, "frozen", False):
    _DIR = os.path.dirname(sys.executable)
else:
    _DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _DIR)
import storage

# ── Ghibli palette ──────────────────────────────────────────────
BG     = "#f5f0e8"
PANEL  = "#ede8d8"
GREEN  = "#7a9e7e"
DKGRN  = "#5a7d5a"
GOLD   = "#c8a876"
TEXT   = "#3d2b1f"
MUTED  = "#6b5a4e"
TERRA  = "#b8735a"
WHITE  = "#fdfaf5"

# Totoro palette (faded so content stays readable)
T_BODY  = "#d0d0dc"
T_BELLY = "#eeeae0"
T_EAR   = "#c4c4d0"
T_MARK  = "#c0bdb0"
T_PINK  = "#dcd8e8"

F_TITLE = ("Georgia", 18, "bold")
F_SUB   = ("Georgia", 10, "italic")
F_BODY  = ("Segoe UI", 11)
F_SMALL = ("Segoe UI", 9)
F_BTN   = ("Segoe UI", 10, "bold")


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Coffee Tracker")
        self.geometry("480x580")
        self.resizable(False, False)
        self.configure(bg=BG)

        self._undo = []
        self._items = []   # canvas draw items cleared on view change
        self._wins  = []   # canvas window items cleared on view change

        self._build_header()
        self._build_canvas()
        self._build_nav()
        self.after(60, self._init)

    # ── Layout ──────────────────────────────────────────────────

    def _build_header(self):
        h = tk.Frame(self, bg=GREEN, pady=14)
        h.pack(fill="x")
        tk.Label(h, text="☕  Coffee Tracker  🌿",
                 font=F_TITLE, bg=GREEN, fg=WHITE).pack()
        tk.Label(h, text="~ a cozy cup at a time ~",
                 font=F_SUB, bg=GREEN, fg="#d4eed4").pack(pady=(2, 0))

    def _build_canvas(self):
        self.cv = tk.Canvas(self, bg=BG, highlightthickness=0)
        self.cv.pack(fill="both", expand=True)
        self.cv.bind("<Configure>", lambda _: self._redraw_totoro())

    def _build_nav(self):
        nav = tk.Frame(self, bg=PANEL, pady=10)
        nav.pack(fill="x", side="bottom")

        r1 = tk.Frame(nav, bg=PANEL)
        r1.pack()
        for label, cmd in [
            ("☕ Log Cup", self.do_log),
            ("Today",     self.show_today),
            ("History",   self.show_history),
            ("Set Goal",  self.do_goal),
        ]:
            self._btn(r1, label, cmd, GREEN).pack(side="left", padx=4, pady=2)

        r2 = tk.Frame(nav, bg=PANEL)
        r2.pack(pady=(4, 0))
        self._btn(r2, "↩ Undo", self.do_undo, TERRA).pack(side="left", padx=4)
        self._btn(r2, "Quit",   self.destroy,  MUTED).pack(side="left", padx=4)

    def _btn(self, parent, text, cmd, color):
        return tk.Button(
            parent, text=text, command=cmd, font=F_BTN,
            bg=color, fg=WHITE, relief="flat",
            padx=14, pady=7, cursor="hand2", bd=0,
            activebackground=DKGRN, activeforeground=WHITE,
        )

    def _init(self):
        self._redraw_totoro()
        self.show_today()

    # ── Totoro ──────────────────────────────────────────────────

    def _redraw_totoro(self):
        self.cv.delete("totoro")
        self._draw_totoro()

    def _draw_totoro(self):
        cv = self.cv
        cv.update_idletasks()
        w = cv.winfo_width()
        h = cv.winfo_height()
        if w < 10 or h < 10:
            return

        cx = w // 2 + 30
        cy = h // 2 + 50

        def s(fn, *a, **kw):
            kw["tags"] = "totoro"
            return fn(*a, **kw)

        # Ground shadow
        s(cv.create_oval, cx-80, cy+118, cx+80, cy+138,
          fill="#d8d4c8", outline="")

        # Body
        s(cv.create_oval, cx-90, cy-50, cx+90, cy+128,
          fill=T_BODY, outline="#b8b8c8", width=2)

        # Belly
        s(cv.create_oval, cx-52, cy-10, cx+52, cy+112,
          fill=T_BELLY, outline="")

        # Belly chevron marks
        for xo, yo in [(-18, 32), (0, 20), (18, 32),
                       (-14, 52), (14, 52), (0, 68)]:
            s(cv.create_oval, cx+xo-7, cy+yo-3, cx+xo+7, cy+yo+3,
              fill=T_MARK, outline="")

        # Head
        s(cv.create_oval, cx-68, cy-158, cx+68, cy+2,
          fill=T_BODY, outline="#b8b8c8", width=2)

        # Left ear
        s(cv.create_polygon, cx-40, cy-142, cx-66, cy-208, cx-14, cy-150,
          fill=T_EAR, outline="#b8b8c8", width=1)
        s(cv.create_polygon, cx-42, cy-146, cx-63, cy-200, cx-18, cy-153,
          fill=T_PINK, outline="")

        # Right ear
        s(cv.create_polygon, cx+40, cy-142, cx+66, cy-208, cx+14, cy-150,
          fill=T_EAR, outline="#b8b8c8", width=1)
        s(cv.create_polygon, cx+42, cy-146, cx+63, cy-200, cx+18, cy-153,
          fill=T_PINK, outline="")

        # Eye whites
        s(cv.create_oval, cx-36, cy-120, cx-8,  cy-88, fill=WHITE, outline="#a0a0b0")
        s(cv.create_oval, cx+8,  cy-120, cx+36, cy-88, fill=WHITE, outline="#a0a0b0")

        # Pupils
        s(cv.create_oval, cx-29, cy-113, cx-15, cy-97, fill="#303040", outline="")
        s(cv.create_oval, cx+15, cy-113, cx+29, cy-97, fill="#303040", outline="")

        # Eye shine
        s(cv.create_oval, cx-26, cy-110, cx-22, cy-106, fill=WHITE, outline="")
        s(cv.create_oval, cx+18, cy-110, cx+22, cy-106, fill=WHITE, outline="")

        # Nose
        s(cv.create_oval, cx-7, cy-82, cx+7, cy-70,
          fill="#e8dcd8", outline="#c0b0ac")

        # Mouth
        s(cv.create_arc, cx-16, cy-78, cx+16, cy-54,
          start=200, extent=140, style="arc", outline="#a0908c", width=2)

        # Whiskers
        for yo in [-76, -68]:
            s(cv.create_line, cx-10, cy+yo, cx-55, cy+yo-4, fill="#b0a8a0", width=1)
            s(cv.create_line, cx+10, cy+yo, cx+55, cy+yo-4, fill="#b0a8a0", width=1)

        # Feet
        s(cv.create_oval, cx-70, cy+118, cx-18, cy+150, fill=T_EAR, outline="#b0b0c0")
        s(cv.create_oval, cx+18, cy+118, cx+70, cy+150, fill=T_EAR, outline="#b0b0c0")

        # Toe lines
        for tx in [cx-56, cx-42, cx-28]:
            s(cv.create_line, tx, cy+150, tx, cy+160, fill="#a8a8b8", width=1)
        for tx in [cx+28, cx+42, cx+56]:
            s(cv.create_line, tx, cy+150, tx, cy+160, fill="#a8a8b8", width=1)

    # ── Canvas content helpers ───────────────────────────────────

    def _clear(self):
        for item in self._items:
            self.cv.delete(item)
        for win in self._wins:
            self.cv.delete(win)
        self._items.clear()
        self._wins.clear()

    def _text(self, x, y, text, **kw):
        self._items.append(self.cv.create_text(x, y, text=text, **kw))

    def _rect(self, x1, y1, x2, y2, **kw):
        self._items.append(self.cv.create_rectangle(x1, y1, x2, y2, **kw))

    def _embed(self, x, y, widget, **kw):
        self._wins.append(self.cv.create_window(x, y, window=widget, **kw))

    # ── Views ────────────────────────────────────────────────────

    def show_today(self):
        self._clear()
        W = self.cv.winfo_width() or 480
        self._text(20, 22, "Today's Log",
                   font=("Georgia", 13, "bold"), fill=TEXT, anchor="nw")

        entries = storage.get_entries_for_date(date.today())
        goal    = storage.get_goal()
        y = 58

        if not entries:
            self._text(20, y, "No cups logged yet today.  ☁️",
                       font=F_BODY, fill=MUTED, anchor="nw")
            y += 30
        else:
            for e in entries:
                t    = datetime.fromisoformat(e["timestamp"]).strftime("%I:%M %p")
                note = f"  ({e['note']})" if e["note"] else ""
                row  = tk.Frame(self.cv, bg=PANEL, padx=10, pady=6)
                tk.Label(row, text=f"☕  {t}{note}",
                         font=F_BODY, bg=PANEL, fg=TEXT).pack(side="left")
                ec = dict(e)
                tk.Button(
                    row, text="✕",
                    command=lambda x=ec: self._del(x),
                    font=("Segoe UI", 8), bg=TERRA, fg=WHITE,
                    relief="flat", padx=5, pady=2, cursor="hand2", bd=0,
                ).pack(side="right", padx=4)
                self._embed(20, y, row, anchor="nw", width=W - 40)
                y += 46

        total = len(entries)
        summ  = f"Total today: {total} cup{'s' if total != 1 else ''}"
        if goal:
            summ += f"   {'🌟 Goal reached!' if total >= goal else f'Goal: {total}/{goal}'}"
        self._rect(20, y + 10, W - 20, y + 50, fill=GOLD, outline="")
        self._text(32, y + 30, summ, font=F_BODY, fill=TEXT, anchor="w")

    def show_history(self):
        self._clear()
        W = self.cv.winfo_width() or 480
        self._text(20, 22, "Last 7 Days",
                   font=("Georgia", 13, "bold"), fill=TEXT, anchor="nw")

        end    = date.today()
        start  = end - timedelta(days=6)
        by_day = storage.get_entries_for_range(start, end)
        y = 58

        for day_str, entries in reversed(list(by_day.items())):
            count = len(entries)
            label = datetime.strptime(day_str, "%Y-%m-%d").strftime("%a, %b %d")
            cups  = ("☕" * min(count, 6) + ("…" if count > 6 else "")) if count else "—"
            row   = tk.Frame(self.cv, bg=PANEL, padx=12, pady=7)
            tk.Label(row, text=label, font=F_BODY, bg=PANEL,
                     fg=TEXT, width=12, anchor="w").pack(side="left")
            tk.Label(row, text=f"{cups}  ({count})",
                     font=F_BODY, bg=PANEL, fg=MUTED).pack(side="left")
            self._embed(20, y, row, anchor="nw", width=W - 40)
            y += 46

    # ── Actions ──────────────────────────────────────────────────

    def _del(self, entry):
        storage.delete_entry(entry["id"])
        self._push_undo("deleted", entry)
        self.show_today()

    def do_log(self):
        win = self._popup("Log a Cup", "330x190")
        tk.Label(win, text="☕  Log a Cup",
                 font=("Georgia", 13, "bold"), bg=BG, fg=TEXT).pack(pady=(18, 4))
        tk.Label(win, text="Add a note (optional):",
                 font=F_BODY, bg=BG, fg=MUTED).pack()
        nv  = tk.StringVar()
        ent = tk.Entry(win, textvariable=nv, font=F_BODY,
                       bg=WHITE, fg=TEXT, relief="flat", bd=2, width=28)
        ent.pack(pady=6)
        ent.focus()

        def ok():
            e, goal = storage.add_entry(note=nv.get().strip())
            self._push_undo("added", e)
            win.destroy()
            self.show_today()
            today = storage.get_entries_for_date(date.today())
            if goal and len(today) >= goal:
                messagebox.showinfo("Goal Reached! 🌟",
                    f"You've had {goal} cups today — well done! ☕")

        f = tk.Frame(win, bg=BG)
        f.pack(pady=10)
        self._btn(f, "Log It ☕", ok,         GREEN).pack(side="left", padx=4)
        self._btn(f, "Cancel",   win.destroy, MUTED).pack(side="left", padx=4)
        win.bind("<Return>", lambda _: ok())
        win.bind("<Escape>", lambda _: win.destroy())

    def do_goal(self):
        win = self._popup("Set Daily Goal", "330x180")
        current = storage.get_goal()
        tk.Label(win, text="🎯  Set Daily Goal",
                 font=("Georgia", 13, "bold"), bg=BG, fg=TEXT).pack(pady=(18, 4))
        tk.Label(win, text=f"Current: {current or 'not set'}",
                 font=F_SMALL, bg=BG, fg=MUTED).pack()
        gv  = tk.StringVar()
        ent = tk.Entry(win, textvariable=gv, font=F_BODY,
                       bg=WHITE, fg=TEXT, relief="flat", bd=2, width=10)
        ent.pack(pady=6)
        ent.focus()

        def ok():
            raw = gv.get().strip()
            if raw.isdigit() and int(raw) >= 1:
                old = storage.get_goal()
                storage.set_goal(int(raw))
                self._push_undo("goal", old)
                win.destroy()
                self.show_today()
            else:
                messagebox.showerror("Invalid", "Please enter a whole number ≥ 1.")

        f = tk.Frame(win, bg=BG)
        f.pack(pady=10)
        self._btn(f, "Set Goal 🎯", ok,         GREEN).pack(side="left", padx=4)
        self._btn(f, "Cancel",      win.destroy, MUTED).pack(side="left", padx=4)
        win.bind("<Return>", lambda _: ok())
        win.bind("<Escape>", lambda _: win.destroy())

    def _popup(self, title, size):
        win = tk.Toplevel(self)
        win.title(title)
        win.geometry(size)
        win.configure(bg=BG)
        win.resizable(False, False)
        win.grab_set()
        win.focus()
        return win

    # ── Undo ─────────────────────────────────────────────────────

    def _push_undo(self, action, data):
        self._undo.append((action, data))

    def do_undo(self):
        if not self._undo:
            messagebox.showinfo("Nothing to Undo ↩", "No recent actions to undo.")
            return
        action, data = self._undo.pop()
        if action == "added":
            storage.delete_entry(data["id"])
            t = datetime.fromisoformat(data["timestamp"]).strftime("%I:%M %p")
            messagebox.showinfo("Undone ↩", f"Removed cup logged at {t}.")
        elif action == "deleted":
            storage.restore_entry(data)
            messagebox.showinfo("Undone ↩", f"Restored cup #{data['id']}.")
        elif action == "goal":
            if data is None:
                storage.clear_goal()
            else:
                storage.set_goal(data)
            messagebox.showinfo("Undone ↩",
                f"Goal restored to {data if data else 'unset'}.")
        self.show_today()


if __name__ == "__main__":
    App().mainloop()
