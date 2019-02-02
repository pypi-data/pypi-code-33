import tkinter as tk
import tkinter.messagebox as tkmessagebox

def get_overview():
    global window, days
    try:
        import urtutils as urtu
    except Exception as e:
        import urtoday.urturils as urtu
    d = days.get()
    try:
        avg = urtu.get_average(d)
        Min = urtu.get_min(d)
        Max = urtu.get_max(d)
        med = urtu.get_median(d)
        tkmessagebox.showinfo("Overview", "Ratings overview for {} past days:\nAverage rating: {}\nMinimum rating: {}\nMaximum rating: {}\nMedian value: {}".format(d+1, avg,Min,Max,med))
        window.quit()
    except:
        tkmessagebox.showinfo("Overview, Error", "Data for the selected range is not available (Do you selected a day you haven't rated?)")

window = tk.Tk()
window.title("URtoday Overview")

text0 = tk.Label(window, text="How many days do you want to get overview?")
text0.pack()

days = tk.Scale(window, from_=1, to=730, orient=tk.HORIZONTAL)
days.set(30)
days.pack(anchor=tk.CENTER)

read_today = tk.Button(window, text="Get Overview", command=get_overview)
read_today.pack()

def run():
    window.mainloop()
    window.destroy()

if __name__=="__main__":
    run()
