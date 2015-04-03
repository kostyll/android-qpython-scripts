#-*-coding:utf8;-*-
#qpy:2
import androidhelper
droid = androidhelper.Android()

contacts_ids = droid.contactsGetIds()

var1 =  3/2.0
print var1
droid.makeToast("%s"%var1)

print contacts_ids
droid.makeToast("%s"%contacts_ids)

contacts_count = droid.contactsGetCount()
print contacts_count
droid.makeToast("%s"%contacts_count)