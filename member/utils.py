
import requests

#  Send SMS for Member


def sendSms(mobile: str, message: str,) -> dict:
    mobile = str(mobile)[-11:]
    url = f"https://sms.bluebayit.com/httpapi/sendsms?userId=bluebay&password=bluebayit7811&smsText={message}&commaSeperatedReceiverNumbers={mobile}&nameToShowAsSender=03590002174"
    res = requests.get(url)
    print('res: ', res)
    print('res.json(): ', res.json())
    return res.json()

