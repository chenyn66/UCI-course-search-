import urllib.request as r
import urllib.parse as p
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



def takeinput():
    dept = input("department you want: ").strip()
    number = input("course you wnat: ").strip()
    paralib['Dept'] = dept
    paralib['CourseNum'] = number
    exclude = input("enter courses numbers you want to exclue (seperate by ,): ").strip()
    exclude = exclude.split(',')
    return exclude

def getresult():
    d = p.urlencode(paralib)
    d = d.encode("utf8")
    h = r.Request("https://www.reg.uci.edu/perl/WebSoc",data = d )
    t = r.urlopen(h)
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
    for line in res:
        if 'OPEN' in line:
            start = line.index('nowrap="nowrap">')
            if line[start+len('nowrap="nowrap">'):start+len('nowrap="nowrap">')+5] in ex:
                continue
            print('{} is OPEN!!'.format(line[start+len('nowrap="nowrap">'):start+len('nowrap="nowrap">')+5]))
            status = True
    return status

def main():
    ex = takeinput()
    count = 1
    while True:
        print("Trying to find course for {} time(s)...".format(count))
        getresult()
        check = outtoscreen(ex)
        count += 1
        time.sleep(1)

if __name__ == "__main__":
    print("This program will check websoc every 1 second")
    main()
