import tkinter as tk
import tkinter.messagebox as tkmessagebox

def submit_today():
    global today, window
    import time as _time
    tday = list(_time.localtime())[0:3]
    rating = today.get()
    try:
        import urtutils as urtu
    except ImportError:
        import urtoday.urtutils as urtu
    urtu.submit_to_user_file(tday, rating)
    tkmessagebox.showinfo("Successful!", "Your today rating: {}".format(rating))
    window.quit()


window = tk.Tk()
window.title("URtoday")

text0 = tk.Label(window, text="How do you rate your today [1-100]?")
text0.pack()

today = tk.Scale(window, from_=1, to=100, orient=tk.HORIZONTAL)
today.set(64)
today.pack(anchor=tk.CENTER)

read_today = tk.Button(window, text="Submit", command=submit_today)
read_today.pack()
def run():
    window.mainloop()
    window.destroy()

if __name__=="__main__":
    run()
