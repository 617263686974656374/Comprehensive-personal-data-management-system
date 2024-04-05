
import re
import tkinter as tk
import json
from datetime import datetime
data_list = []

"""                                  *** Main function buttons ***                                              """


def add_entry(entries, labels, error_labels, treeview):
    all_empty = all(not entries[label].get().strip() for label in labels)
    if all_empty:
        set_error_labels(error_labels, "Pflichtfeld")
        return
    if validate_and_process_data(entries, labels, error_labels, treeview, 'add'):
        clear_all_entries(entries, labels, error_labels)


def edit_client(entries, error_labels, treeview, labels):
    if not treeview.selection():
        return
    if validate_and_process_data(entries, labels, error_labels, treeview, 'edit'):
        clear_all_entries(entries, labels, error_labels)

def apply_filter(entries, treeview, labels):
    filter_criteria = {label: entries[label].get().strip().lower() for label in labels if entries[label].get().strip()}
    refresh_treeview_with_filtered_data(treeview, labels, filter_criteria)


def display_all_data(treeview,labels,entries,error_labels):
    treeview.delete(*treeview.get_children())
    for record in data_list:
        treeview.insert('', 'end', values=[record.get(label, "") for label in labels])
    update_treeview_with_birthday_info(treeview)
    clear_all_entries(entries, labels, error_labels)


def delete_selected_client(treeview, entries, labels, error_labels):
    selected_item = treeview.selection()
    if not selected_item:
        return
    selected_item = selected_item[0]
    selected_index = treeview.index(selected_item)
    if selected_index < len(data_list):
        del data_list[selected_index]
    treeview.delete(selected_item)
    save_json()
    clear_all_entries(entries, labels, error_labels)


"""                                  *** Logic for Age and Birthday ***                                              """


def update_treeview_with_birthday_info(treeview):
    for child in treeview.get_children():
        geboren_index = treeview["columns"].index("Geboren")
        birthday_str = treeview.item(child, 'values')[geboren_index]
        birthday_info = calculate_birthday_info(birthday_str)
        treeview.set(child, 'Geburstag Info', birthday_info)


def calculate_birthday_info(date_str):
    today = datetime.today()
    try:
        birthday = datetime.strptime(date_str, '%d.%m.%Y')
    except ValueError:
        return "Invalid date format"

    # If birthday is in the same month and year
    if birthday.month == today.month:
        if birthday.day == today.day:
            return "Heute!"
        elif birthday.day > today.day:
            return f"in {birthday.day - today.day} Tagen"
        else:
            return f"vor {today.day - birthday.day} Tagen"
    else:
        return ""


def add_birthday_info_to_treeview(treeview):
    for child in treeview.get_children():
        geboren_index = treeview["columns"].index("Geboren")
        geboren_value = treeview.item(child, 'values')[geboren_index]
        birthday_info = calculate_birthday_info(geboren_value)
        treeview.set(child, 'Geburstag Info', birthday_info)


def calculate_age(birthdate_str):
    try:
        birthdate = datetime.strptime(birthdate_str, "%d.%m.%Y")
        today = datetime.today()
        age = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))
        return age
    except ValueError:
        return None


"""                                  *** Logic for Entry and Edit data ***                                          """


def process_entry_data(entries, labels, error_labels):
    processed_data = {}
    is_valid = True

    for label in labels:
        input_text = entries[label].get().strip()
        if not input_text:
            error_labels[label].config(text="Pflichtfeld")
            is_valid = False
            continue

        validation_type = determine_validation_type(label)
        if validation_type:
            valid, error_message = validate_input(input_text, validation_type)
            error_labels[label].config(text=error_message)
            if not valid:
                is_valid = False
            else:
                processed_data[label] = input_text

    if 'Geboren' in labels:
        birthdate_str = entries['Geboren'].get().strip()
        if not birthdate_str:
            error_labels['Geboren'].config(text="Pflichtfeld")
            is_valid = False
        else:
            calculated_age = calculate_age(birthdate_str)
            if calculated_age is None or calculated_age < 0 or calculated_age > 120:
                error_labels['Geboren'].config(text="Gültiges Format tt.mm.yyyy")
                is_valid = False
            else:
                processed_data['Alter'] = str(calculated_age)

    for label in ['Vorname', 'Nachname', 'Straße', 'Stadt']:
        if label in processed_data:
            processed_data[label] = capitalize_input(processed_data[label])
    return processed_data, is_valid


def validate_and_process_data(entries, labels, error_labels, treeview, action):
    processed_data, is_valid = process_entry_data(entries, labels, error_labels)
    if not is_valid:
        return False
    if action == 'add':
        data_list.append(processed_data)
    elif action == 'edit':
        selected_item = treeview.selection()[0]
        selected_index = treeview.index(selected_item)
        data_list[selected_index] = processed_data

    save_json()
    refresh_treeview(treeview, labels)
    return True


def fill_entries_with_client_data(treeview,entries,labels):
    selected_item = treeview.selection()
    if selected_item:
        item_data = treeview.item(selected_item[0], 'values')
        for label, data in zip(labels, item_data):
            entries[label].delete(0, tk.END)
            entries[label].insert(0, data)


def validate_input(input_text, validation_type):
    patterns = {
        "name": (r'^[A-Za-zäöüÄÖÜß ]+$', "Darf nur Buchstaben enthalten."),
        "email": (r'^[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$', "Ungültige E-Mail-Adresse."),
        "phone": (r'^(?:(?:\+|00)\d{1,3}[-.\s]?)?(?:(\d{2,4})[-.\s]?)?(\d{3}[-.\s]?\d{3,4})$', "Ungültige Telefonnummer."),
        "house_number": (r'^\d+[\/]?\d*[a-zA-Z]?$', "Ungültige Hausnummer."),
        "date": (r'^\d{2}.\d{2}.\d{4}$', "Ungültiges Datum. Bitte verwenden Sie das Format DD.MM.YYYY."),
        "age": (r'^\d+$', "Ungültiges Alter."),
    }

    pattern, error_message = patterns.get(validation_type, (None, "Unbekannter Validierungstyp."))
    if not pattern or not re.match(pattern, input_text):
        return False, error_message
    return True, ""


def capitalize_input(text):
    return text.title()


def determine_validation_type(label):
    validation_types = {
        'Vorname': 'name', 'Nachname': 'name', 'Straße': 'name', 'Stadt': 'name',
        'Geboren': 'date', 'Email': 'email', 'Mobil': 'phone', 'Hausnummer': 'house_number', 'Alter': 'age'
    }
    return validation_types.get(label, None)


def match_filter_criteria(record, filter_criteria):
    for label, criteria in filter_criteria.items():
        record_value = str(record.get(label, "")).lower()
        if label == 'Alter':
            try:
                if int(record_value) != int(criteria):
                    return False
            except ValueError:
                return False
        elif criteria not in record_value:
            return False
    return True


"""                                  *** Save,Open and Other function  ***                                          """


def set_error_labels(error_labels, message):
    for label in error_labels:
        error_labels[label].config(text=message)


def refresh_treeview(treeview, labels):
    treeview.delete(*treeview.get_children())
    for record in data_list:
        treeview.insert('', 'end', values=[record.get(label, "") for label in labels])
    update_treeview_with_birthday_info(treeview)


def refresh_treeview_with_filtered_data(treeview, labels, filter_criteria):
    filtered_data = [record for record in data_list if match_filter_criteria(record, filter_criteria)]
    treeview.delete(*treeview.get_children())
    for record in filtered_data:
        treeview.insert('', 'end', values=[record.get(label, "") for label in labels])
    update_treeview_with_birthday_info(treeview)


def clear_all_entries(entries, labels, error_labels):
    for label in labels:
        if label in entries:
            entries[label].delete(0, tk.END)
        if label in error_labels:
            error_labels[label].config(text='')


def open_json(treeview, file_name="database.json"):
    global data_list
    try:
        with open(file_name, "r") as file:
            data_list = json.load(file)
        for item in data_list:
            # Inserting values into the treeview
            treeview.insert('', 'end', values=(
                item.get("Vorname", ""),
                item.get("Nachname", ""),
                item.get("Geboren", ""),
                item.get("Stra\u00dfe", ""),
                item.get("Hausnummer", ""),
                item.get("Stadt", ""),
                item.get("Email", ""),
                item.get("Mobil", ""),
                item.get("Alter", ""),
                ''
            ))
    except FileNotFoundError:
        print("Die Daten werden in database.json gespeichert")


def save_json(file_name="database.json"):
    with open(file_name, "w") as subor:
        json.dump(data_list, subor)
