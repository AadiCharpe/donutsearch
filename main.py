import tkinter

app = tkinter.Tk()

app.title('donut search')
app.geometry('600x600')
app.resizable(False, False)
# create tkinter ui
example = tkinter.Entry(width=25, font=('',20))
example.place(x=300, y=30, anchor=tkinter.CENTER)

b = tkinter.Button(text='Search', width=15, height=1, command=lambda:search())
b.place(x=300, y=100, anchor=tkinter.CENTER)

l = tkinter.Text(font=('',12), state=tkinter.DISABLED)
l.pack(fill=tkinter.X, side=tkinter.BOTTOM)
# read index file
f = open('index.txt', 'r', encoding='utf-8')
lines = f.readlines()
f.close()
words = {}
for line in lines[2:]:
    words[line.split('|')[0]] = line.split('|')[1]
u = ''
info = {}
for value in lines[1].split('~'):
    if value.startswith('http'):
        u = value
    else:
        info[u] = value
        u = ''
if '' in info:
    del info['']
def search():
    l.config(state=tkinter.NORMAL)
    l.delete('1.0', 'end')
    l.config(state=tkinter.DISABLED)
    text = example.get().lower().split()
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
    for val, key in reversed(sorted_items):
        if key.endswith('\n'):
            key = key[:-1]
        newtext += f"{info[key].split('`')[0]} - {key}\n{info[key].split('`')[1]}\n"
    l.config(state=tkinter.NORMAL, wrap=tkinter.WORD)
    l.insert('1.0', newtext)
    l.config(state=tkinter.DISABLED)

app.mainloop()