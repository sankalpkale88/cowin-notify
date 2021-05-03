This tool is used to get available slots for vaccination in India. 

This will send an email notification on available slot

This is simple cowin vaccination available slot notification script.

## Installation
Cowin Vaccine Notify
```
Install Python
Install Pip
```
```
pip install requests
```

## Search Slot By PinCode
```
python cowin.py --pincode 440010 --age 31 --email <gmail_id> --password <gmail_password>
```

## Serach Slot By District
```
python cowin.py --state Maharashtra --district Pune  --age 31 --email <gmail_id> --password <gmail_password>
```

### Note
If your gmail has 2FA enabled please follow the steps mentioned below and generate 16 character password.
https://support.google.com/mail/answer/7126229?p=WebLoginRequired
