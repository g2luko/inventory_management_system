from tkinter import *
from tkinter import ttk
import os
import sqlite3
import pandas as pd

conn = sqlite3.connect('database.db')
cur = conn.cursor()

# Function to create tables 
def create_tables():
    cur.execute('''
    CREATE TABLE IF NOT EXISTS info (
        roll TEXT PRIMARY KEY,
        name TEXT NOT NULL
    )
    ''')
    cur.execute('''
    CREATE TABLE IF NOT EXISTS objects (
        num TEXT PRIMARY KEY,
        name TEXT NOT NULL
    )
    ''')
    cur.execute('''
    CREATE TABLE IF NOT EXISTS ITEMS (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        rollno TEXT NOT NULL,
        name TEXT NOT NULL,
        time TEXT NOT NULL,
        objects TEXT NOT NULL,
        status TEXT NOT NULL,
        FOREIGN KEY (rollno) REFERENCES info (roll),
        FOREIGN KEY (objects) REFERENCES objects (num)
    )
    ''')
    conn.commit()

# Call the function to create tables
create_tables()

root = Tk()
root.geometry("1908x1080")
root.title("Inventory")

# Labels and Entry Fields
label1 = Label(root, text="Scan using QR or Enter the Details", fg='black', font=("Mongolian", 11))
label1.pack()

l1 = Label(root, text='Enter Student ID', font=("Mongolian", 20))
l1.place(relx=0.4, rely=0.2)
l2 = Label(root, text="Enter Item ID     ", font=("Mongolian", 20))
l2.place(relx=0.4, rely=0.3)
e1 = Entry(root, font='Mongolian 20')
e1.place(relx=0.6, rely=0.2)
e2 = Entry(root, font='Mongolian 20')
e2.place(relx=0.6, rely=0.3)

# Table for Displaying Data
table = ttk.Treeview(root, columns=('roll', 'name', 'time', 'item', 'stat'), show='headings')
style = ttk.Style(root)
style.configure('Treeview', font=(None, 10))
style.configure('Treeview.Heading', font=(None, 12))
table.heading('roll', text='Rollno')
table.heading('name', text='Name')
table.heading('time', text='Time')
table.heading('item', text='Item')
table.heading('stat', text='Status')
table.place(relx=0.5, rely=0.8, height=300, width=1500, anchor='center')

# Status Bar
status = StringVar()
status.set("Ready")
status_bar = Label(root, textvariable=status, relief=SUNKEN, anchor=W, font=('Arial', 10))
status_bar.place(relx=.12,rely=.97,anchor="s")

# Event Handlers
def click(event):
    value = str(e1.get()).upper()
    item = str(e2.get()).upper()
    in_out(value, item)
    entry(value, item)
    lastdata()
    e1.delete(0, END)
    e2.delete(0, END)

def back(event):
    e1.focus()
    e2.bind('<Return>', click)
    click(event)

def nxt(event):
    e2.focus()
    e2.bind('<Return>', back)

e1.focus()
e1.bind('<Return>', nxt)

# Core Functions
def entry(value, item):
    cur.execute("""SELECT name FROM objects WHERE num = ?""", (item,))
    x = cur.fetchone()[0]
    cur.execute("""INSERT INTO ITEMS (rollno, NAME, time, objects, status)
                   SELECT roll, name, TIME('now', 'localtime'), ?, ? FROM info
                   WHERE (? = roll);""", (x, st, value,))
    conn.commit()
    status.set("Entry Successful")

def in_out(value, item):
    cur.execute("""SELECT name FROM objects WHERE num = ?""", (item,))
    x = cur.fetchone()[0]
    cur.execute("""SELECT * FROM ITEMS WHERE ? = rollno AND ? = objects""", (value, x,))
    items_in_times = cur.fetchall()
    global st
    if not items_in_times or len(items_in_times) % 2 == 0:
        st = 'OUT'
    else:
        st = 'IN'

def lastdata():
    d = """SELECT rollno, NAME, time, objects, status FROM ITEMS WHERE (time = TIME('now', 'localtime'));"""
    data = cur.execute(d)
    f = cur.fetchone()
    table.insert(parent='', index=0, values=f)

# Clear Table
def dele1():
    table.delete(*table.get_children())
    status.set("Table cleared")

# Print Window
def printcsv():
    def printing():
        filename = top_entry.get() + ".csv"
        cli = pd.read_sql("SELECT * FROM ITEMS", conn)
        cli.to_csv(filename, index=False)
        os.system(filename)
        status.set("Exported Successfully")
        top.destroy()

    top = Toplevel(root)
    top.geometry('500x200')
    top_lab = Label(top, text='Enter file name', font=('Arial', 12))
    top_lab.place(relx=0.2, rely=0.4)
    top_entry = Entry(top)
    top_entry.place(relx=0.5, rely=0.4, width=150)
    print_bt = Button(top, text='PRINT', fg='#7247E9', command=printing)
    print_bt.place(relx=1, rely=1, anchor='se', width=100)

# Student Edit Function
def student_fun():
    def del_student():
        cur.execute("""DELETE FROM info WHERE ? = roll""", (rollno_entry.get(),))
        conn.commit()
        status.set("Student deleted")

    def add_student():
        cur.execute("""INSERT INTO info(roll, name) VALUES (?, ?);""", (str(rollno_entry.get()).upper(), top_entry.get(),))
        conn.commit()
        status.set("Student added")

    # Window
    top = Toplevel(root)
    top.geometry('600x200')

    # Student name label and entry box
    top_lab = Label(top, text='Enter Student name', font=('Arial', 12))
    top_lab.place(relx=0.2, rely=0.5)
    top_entry = Entry(top)
    top_entry.place(relx=0.5, rely=0.5, width=150)

    # Rollno label and entry box
    rollno = Label(top, text='Enter Student Roll No', font=('Arial', 12))
    rollno.place(relx=0.2, rely=0.35)
    rollno_entry = Entry(top)
    rollno_entry.place(relx=0.5, rely=0.35, width=150)

    print_bt = Button(top, text='ADD', fg='#7247E9', command=add_student)
    print_bt.place(relx=1, rely=1, anchor='se', width=100)

    print_bt = Button(top, text='Remove', fg='#7247E9', command=del_student)
    print_bt.place(relx=0.80, rely=1, anchor='se', width=100)

# Edit Items Function
def edit_items():
    def del_item():
        cur.execute("""DELETE FROM objects WHERE ? = num""", (item_id.get(),))
        conn.commit()
        status.set("Item deleted")

    def add_item():
        cur.execute("""INSERT INTO objects (num, name) VALUES (?, ?);""", (item_id.get(), item_name.get(),))
        conn.commit()
        status.set("Item added")

    # Window
    top = Toplevel(root)
    top.geometry('600x200')

    # Item name label and entry box
    itemname = Label(top, text='Enter Item name', font=('Arial', 12))
    itemname.place(relx=0.2, rely=0.5)
    item_name = Entry(top)
    item_name.place(relx=0.5, rely=0.5, width=150)

    # Item ID label and entry box
    itemid = Label(top, text='Enter Item ID', font=('Arial', 12))
    itemid.place(relx=0.2, rely=0.35)
    item_id = Entry(top)
    item_id.place(relx=0.5, rely=0.35, width=150)

    print_bt = Button(top, text='ADD', fg='#7247E9', command=add_item)
    print_bt.place(relx=1, rely=1, anchor='se', width=100)

    print_bt = Button(top, text='Remove', fg='#7247E9', command=del_item)
    print_bt.place(relx=0.80, rely=1, anchor='se', width=100)

# Buttons
button1 = Button(root, text="Print", fg='#7247E9', command=printcsv, borderwidth=0.1)
button1.place(relx=0.92, rely=0.59, width=100)

del_button = Button(root, text="Clear table", fg='#7247E9', command=dele1, borderwidth=0.3)
del_button.place(relx=0.85, rely=0.59, width=100)

Edit_student = Button(root, text="Edit student", fg='#7247E9', command=student_fun, borderwidth=0.3)
Edit_student.place(relx=0.78, rely=0.59, width=100)

Edit_items = Button(root, text="Edit items", fg='#7247E9', command=edit_items, borderwidth=0.3)
Edit_items.place(relx=0.71, rely=0.59, width=100)

# Main Loop
root.mainloop()
