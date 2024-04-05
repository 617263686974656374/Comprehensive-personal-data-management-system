
import tkinter as tk
from tkinter import ttk
import function_


# Create the main window
root = tk.Tk()
root.title("Personendatenerfassung")
root.minsize(1100, 500)
# Dictionary for error labels
error_labels = {}
# Create labels and entry widgets
labels = ['Vorname', 'Nachname', 'Geboren', 'Straße', 'Hausnummer', 'Stadt', 'Email', 'Mobil', 'Alter']
entries = {}

# Creation of inputs, their labels and error labels
for i, label in enumerate(labels):
    lbl = tk.Label(root, text=label)
    lbl.grid(row=(2 * (i // 3)) + 2, column=(i % 3) * 2, padx=(10, 2), pady=(2, 2), sticky='e')

    entry = tk.Entry(root)
    entries[label] = entry
    entry.grid(row=(2 * (i // 3)) + 2, column=(i % 3) * 2 + 1, padx=(2, 10), pady=(2, 2), sticky='ew')

    error_label = tk.Label(root, text='', fg='red')
    error_labels[label] = error_label
    error_label.grid(row=(2 * (i // 3)) + 3, column=(i % 3) * 2 + 1, padx=(2, 10), sticky='w')

# Position the clear button
clear_button = tk.Button(root, text="Löschen", command=lambda: function_.clear_all_entries(entries, labels, error_labels))
clear_button.grid(row=0, column=5, padx=(2, 10), pady=(2, 2), sticky='ew')

# Create TreeView
treeview = ttk.Treeview(root, columns=('Vorname', 'Nachname','Geboren','Straße','Hausnummer','Stadt', 'Email', 'Mobil', 'Alter', 'Geburstag Info'), show='headings')
treeview.grid(row=10, column=0, columnspan=6, padx=(10, 10), pady=(10, 0), sticky='ew')
treeview.bind('<<TreeviewSelect>>', lambda event: function_.fill_entries_with_client_data(treeview, entries, labels))


# Define TreeView columns and headings
for col in treeview['columns']:
    treeview.heading(col, text=col)
    treeview.column(col, anchor='w', width=100)  # Set a default width

# Create buttons and place them below the TreeView
buttons = ['Hinzufügen', 'Bearbeiten', 'Listenfilter', 'Gesamte Liste', 'Delete', 'Exit']
button_commands = [lambda: function_.add_entry(entries, labels, error_labels, treeview),
                   lambda: function_.edit_client(entries, error_labels, treeview, labels),
                   lambda: function_.apply_filter(entries, treeview, labels),
                   lambda: function_.display_all_data(treeview, labels, entries, error_labels),
                   lambda: function_.delete_selected_client(treeview, entries, labels, error_labels),
                   lambda: root.destroy()]

for i, (btn_label, cmd) in enumerate(zip(buttons, button_commands)):
    btn = tk.Button(root, text=btn_label, command=cmd)
    btn.grid(row=11 + (i // 3), column=(i % 3) * 2, columnspan=2, padx=(10, 10), pady=(2, 2), sticky='ew')


# Configure column layouts for a uniform look
for i in range(6):  # Adjusted for 6 columns due to entry and label pairs
    root.grid_columnconfigure(i, weight=1)


def initialize_data():
    data = function_.open_json(treeview)
    function_.add_birthday_info_to_treeview(treeview)


def start():
    initialize_data()
    root.mainloop()
  
