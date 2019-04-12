async def csv_add(csv_current_entries, csv_new_entries):
    entry_list = csv_current_entries.split(",")
    for one_new_entry in str(csv_new_entries).split(","):
        if not one_new_entry in entry_list:
            entry_list.append(one_new_entry)
    return ",".join(entry_list)


async def csv_remove(csv_current_entries, csv_new_entries):
    entry_list = csv_current_entries.split(",")
    for one_new_entry in str(csv_new_entries).split(","):
        if one_new_entry in entry_list:
            entry_list.remove(one_new_entry)
    return ",".join(entry_list)


async def csv_wrap_entries(csv_current_entries, wrapper = "<#%s>"):
    entry_string = ""
    for one_entry in csv_current_entries.split(","):
        entry_string += wrapper+" " % (one_entry)
    return entry_string