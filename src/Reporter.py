from UptimeDb import Usage


class Action:
    def execute(self):
        pass


class NoAction(Action):
    pass


class LockScreen(Action):
    def execute(self):
        from ctypes import CDLL
        login_pf = CDLL('/System/Library/PrivateFrameworks/login.framework/Versions/Current/login')
        result = login_pf.SACLockScreenImmediate()


class Notify(Action):
    def execute(self):
        pass
#         import pystray
#
# from PIL import Image, ImageDraw

        # from tkinter import Tk, Label, messagebox, Button
        # window = Tk()
        # screen_width = window.winfo_screenwidth()
        # screen_height = window.winfo_screenheight()
        # window.geometry(f"{screen_width}x{screen_height}")
        # window.lift()
        # window.attributes("-topmost", True)
        # window.deiconify()
        # window.after(1, lambda: window.focus_force())
        #
        # Button(window, text="OK", command=window.destroy).pack()


        # w = Label(window, text ='GeeksForGeeks', font = "50")
        # w.pack()
        #
        # messagebox.showinfo("showinfo", "Information")
            # messagebox.showwarning("showwarning", "Warning")
            # messagebox.showerror("showerror", "Error")
            # messagebox.askquestion("askquestion", "Are you sure?")
            # messagebox.askokcancel("askokcancel", "Want to continue?")
            # messagebox.askyesno("askyesno", "Find the value?")
            # messagebox.askretrycancel("askretrycancel", "Try again?")

        window.mainloop()
        print("hold")


class Reporter:
    def report(self, usage: Usage):
        return Notify()
