import tkinter

app = tkinter.Tk()

app.title("donut search")
app.geometry("600x600")
app.resizable(False, False)

example = tkinter.Entry(width=25, font=('',20))
example.place(x=300, y=30, anchor=tkinter.CENTER)

b = tkinter.Button(text="Search", width=15, height=1, command=lambda:search())
b.place(x=300, y=100, anchor=tkinter.CENTER)

l = tkinter.Label(font=('',12))
l.place(x=300, y=140, anchor='n')

def search():
    l.config(text='')
    text = example.get().split()
    f = open('index.txt', 'r', encoding='utf-8')
    lines = f.readlines()[1:]
    f.close()
    words = {}
    for line in lines:
        words[line.split('|')[0]] = line.split('|')[1]
    matches = ''
    for t in text:
        if t in words:
            matches += words[t].replace(',', '\n')
    l.config(text=matches)

app.mainloop()