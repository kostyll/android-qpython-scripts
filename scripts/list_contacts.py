import androidhelper
droid = androidhelper.Android()

contacts_ids = droid.contactsGetIds()
print contacts_ids

contacts_count = droid.contactsGetCount()
print contacts_count