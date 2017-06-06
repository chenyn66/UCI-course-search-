import urllib.request as request
import urllib.parse as parse
from urllib.error import URLError
import time
from email.mime.text import MIMEText
import smtplib

class SearchBot:
    ResultOnConsole = True
    MAXTRY = 3600*24*30*2

    def __init__(self,CourseArgs,IncludeList = None, ExclueList = None, RstrList = None, MailInfo: ('sender','Password','receiver') = None,
                 gap = 1):
        self._CheckRstr = False
        self._CheckIn = False
        self._CheckEx = False
        self._args = CourseArgs
        assert MailInfo==None or len(MailInfo) == 3
        self._Mail = MailInfo
        self._gap = gap
        if RstrList != None:
            self._CheckRstr = True
            self._Rstr = RstrList
        if IncludeList != None:
            self._CheckIn = True
            self._in = IncludeList
        elif ExclueList != None:
            self._CheckEx = True
        self._ex = ExclueList


    def _request(self):
        para = parse.urlencode(self._args)
        para = para.encode("utf8")
        htRes = request.Request("https://www.reg.uci.edu/perl/WebSoc", data=para)
        txtRes = request.urlopen(htRes)
        txtRes = txtRes.read().decode("utf8")
        return txtRes

    def _encodeMail(self,subject,context):
        res = MIMEText(context)
        res["Subject"] = subject
        res["From"] = self._Mail[0]
        res["To"] = self._Mail[2]
        return res


    def _sendMail(self,msg):
        ser = smtplib.SMTP("smtp.gmail.com")
        ser.starttls()
        ser.login(self._Mail[0], self._Mail[1])
        ser.send_message(msg)
        ser.quit()

    def _RstrCheck(self,line):
        Rstr = line.split('</td>')[13][len('<td  nowrap="nowrap">'):]
        if 'and' in Rstr:
            Rstr = Rstr.split(' and ')
        for i in Rstr:
            if i in self._Rstr:
                return False

        return True


    def _analyse(self,msg):
        msg = msg.split('\n')
        courses = []
        for line in msg:
            if line.lstrip().startswith('<tr valign="top">') or line.lstrip().startswith('<tr valign="top" bgcolor="#FFFFCC">'):
                courses.append(line)

        success = []

        if self._CheckIn:
            for line in courses:
                start = line.index('nowrap="nowrap">')
                courseCode = line[start + len('nowrap="nowrap">'):start + len('nowrap="nowrap">') + 5]
                if courseCode in self._in:
                    if 'OPEN' in line:
                        if not self._CheckRstr or self._RstrCheck(line):
                            success.append(courseCode)
        else:
            for line in courses:
                start = line.index('nowrap="nowrap">')
                courseCode = line[start + len('nowrap="nowrap">'):start + len('nowrap="nowrap">') + 5]
                if courseCode not in self._ex:
                    if 'OPEN' in line:
                        if not self._CheckRstr or self._RstrCheck(line):
                            success.append(courseCode)
        return success

    def run(self):
        sendnote = True if self._Mail != None else False
        lastsent = 0
        count = 1
        while True:
            if self.ResultOnConsole:
                print("Trying to find course for {} time(s)...".format(count))

            while True:
                try:
                    webMsg = self._request()
                except URLError:
                    if self.ResultOnConsole:
                        print("Connection Error, Reconnecting...")
                    time.sleep(1)
                else:
                    break

            Res = self._analyse(webMsg)

            if self.ResultOnConsole:
                for course in Res:
                    print('{} is OPEN!!'.format(course))


            if len(Res) != 0  and sendnote:
                if count - lastsent >= 10 * 50 or lastsent == 0:
                    lastsent = count
                    msgList = ['{} is OPEN!!'.format(i) for i in Res]
                    msg = self._encodeMail("Your course is available!!",'\n'.join(msgList))
                    self._sendMail(msg)

            count += 1
            if count>= self.MAXTRY:
                if self.ResultOnConsole:
                    print('MAXTRY, BOT STOP')
                break
            time.sleep(1)







