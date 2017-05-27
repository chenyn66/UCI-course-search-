import urllib.request as r
import urllib.parse as p
from urllib.error import URLError
import time
from email.mime.text import MIMEText
import smtplib

paralib = p.parse_qs('YearTerm=2017-92&ShowComments=on&ShowFinals=on&Breadth=ANY&Dept=I%26C+SCI&CourseNum=46&Division=ANY&CourseCodes=&InstrName=&CourseTitle=&ClassType=ALL&Units=&Days=&StartTime=&EndTime=&MaxCap=&FullCourses=ANY&FontSize=100&CancelledCourses=Exclude&Bldg=&Room=&Submit=Display+Web+Results',True)

for key,value in paralib.items():
    paralib[key] = value[0]


def encodemail(sender,receiver,subject,context):
    res = MIMEText(context)
    res["Subject"] = subject
    res["From"] = sender
    res["To"] = receiver
    return res

def sendemail(msg,address,passward):
    ser = smtplib.SMTP("smtp.gmail.com")
    ser.starttls()
    ser.login(address,passward)
    ser.send_message(msg)
    ser.quit()



def takeinput():
    dept = input("department you want: ").strip()
    number = input("course you want: ").strip()
    paralib['Dept'] = dept
    paralib['CourseNum'] = number
    exclude = input("enter courses numbers you want to exclue (seperate by ,): ").strip()
    exclude = exclude.split(',')
    return exclude

def getresult():
    d = p.urlencode(paralib)
    d = d.encode("utf8")
    while True:
        try:
            h = r.Request("https://www.reg.uci.edu/perl/WebSoc",data = d )
            t = r.urlopen(h)
        except URLError:
            print("Connection Error, Reconnecting...")
            time.sleep(1)
        else:
            break


    t = t.read().decode("utf8")
    f = open('test.html',mode = 'w')
    f.write(t)
    f.close()

def outtoscreen(ex):
    res = open('result.txt',mode = 'w')
    outp = open('test.html')
    for line in outp:
        if line.lstrip().startswith('<tr valign="top">') or line.lstrip().startswith('<tr valign="top" bgcolor="#FFFFCC">'):
            res.write(line)

    res.close()
    outp.close()

    res = open('result.txt')
    status = False
    reslist = []
    for line in res:
        if 'OPEN' in line:
            start = line.index('nowrap="nowrap">')
            if line[start+len('nowrap="nowrap">'):start+len('nowrap="nowrap">')+5] in ex:
                continue
            print('{} is OPEN!!'.format(line[start+len('nowrap="nowrap">'):start+len('nowrap="nowrap">')+5]))
            reslist.append('{} is OPEN!!'.format(line[start+len('nowrap="nowrap">'):start+len('nowrap="nowrap">')+5]))
            status = True
    res.close()
    return status,reslist

def askemail():
    while True:
        check = input("Do you want to receive a email notification(require an email address and password)? (yes or no): ").strip()
        if check in ['yes','no']:
            break
    check = True if check == 'yes' else False
    if check:
        a = input("Your email address (must be a Gmail address, @uci.edu is OK): ").strip()
        p = input("Your password(only used for login to Gmail, I will not receive any message): ")
        return a,p
    else:
        return None


def main():
    ex = takeinput()
    emailinfo = askemail()
    sendnote = True if emailinfo != None else False
    lastsent = 0
    count = 1
    while True:
        print("Trying to find course for {} time(s)...".format(count))
        getresult()
        check = outtoscreen(ex)

        if check[0] and sendnote:
            if count - lastsent >= 10*50 or lastsent == 0:
                lastsent = count
                msg = encodemail(emailinfo[0],emailinfo[0],"Your course is available!!",'\n'.join(check[1]))
                sendemail(msg,emailinfo[0],emailinfo[1])

        count += 1
        time.sleep(1)

if __name__ == "__main__":
    print("This program will check websoc every 1 second")
    main()
