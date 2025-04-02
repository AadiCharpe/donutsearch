import tkinter

app = tkinter.Tk()

app.title("donut search")
app.geometry("600x600")
app.resizable(False, False)
# create tkinter ui
example = tkinter.Entry(width=25, font=('',20))
example.place(x=300, y=30, anchor=tkinter.CENTER)

b = tkinter.Button(text="Search", width=15, height=1, command=lambda:search())
b.place(x=300, y=100, anchor=tkinter.CENTER)

l = tkinter.Label(font=('',12))
l.place(x=300, y=140, anchor='n')
# read index file
f = open('index.txt', 'r', encoding='utf-8')
lines = f.readlines()[2:]
f.close()
words = {}
for line in lines:
    words[line.split('|')[0]] = line.split('|')[1]

def search():
    l.config(text='')
    text = example.get().split()
    matches = {}
    # find all matches
    for t in text:
        if t in words:
            for url in words[t].split(','):
                if url not in matches:
                    matches[url] = 0
    # rank the matches based on how many different searched words each page has
    for key in matches:
        for t in text:
            if t in words and key in words[t].split(','):
                matches[key] += 1
    newtext = ''
    # sort the dictionary
    sorted_items = sorted([(value, key) for key, value in matches.items()])
    for value, key in reversed(sorted_items):
        newtext += key
    l.config(text=newtext)

app.mainloop()