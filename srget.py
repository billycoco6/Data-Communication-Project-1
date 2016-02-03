#!/usr/bin/env python
import socket as sk
import os, asyncore, logging, sys, getopt
from cStringIO import StringIO
from urlparse import urlparse
 
# def make_request(req_type, what, details, version="1.1"):
#     """ Compose an HTTP request """
#     NL = "\r\n"
#     request_line = "{req_type} {what} HTTP/{ver}".format(
#         req_type=req_type,
#         what=what,
#         ver=version
#     )
 
#     detail_lines = NL.join(
#         "{}: {}".format(name, value) for name, value in details.iteritems()
#     )
 
#     full_request = request_line + NL + detail_lines + NL + NL
#     return full_request
 

class HTTPClient(asyncore.dispatcher):
    def __init__(self, url):
        asyncore.dispatcher.__init__(self)

        self.port = 80
        self.filename = "test.jpg"
 
        self.url = url
        self.servName = None
        self.objName = None
        self.check_and_make_url()
 
        print "cp 1"

        self.head_content = ""
        self.getHeader(self.servName, self.objName)

        print "cp 2"

        self.new_url = ""
        self.need_redirect = False
        self.check_redirect()

        print "cp 3"

        self.header_length = None
        self.has_content_length = False
        self.content_length = 0
        self.error = True

        print "cp 4"

        self.same_version = False

        self.download_and_resume()

        print "cp 5"

        # self.parse_content()

        print "end"

    def check_and_make_url(self):
        if self.url[:7] != "http://":
            self.url = "http://" + self.url
        parse = urlparse(self.url)
        self.servName = parse.netloc
        self.objName = parse.path



    def getHeader(self, servName, objName):

        self.makesocket(None, None, "head")

        while "\r\n\r\n" not in self.head_content:

            data = self.sock.recv(1)

            self.head_content += data

        # print "head content =", self.head_content

        self.closesocket()


    def makerequest(self, condition, objname, serv, start, stop):
    
        if condition == "head":

            return ("HEAD {o} HTTP/1.1\r\n"+"Host: {s}\r\n"+"\r\n\r\n").format(o = objname,s = serv)
        else:
            
            return ("GET {o} HTTP/1.1\r\n"+"Host: {s}\r\n"+"Range: bytes={h}-\r\n\r\n").format(o = objname,s = serv,h = start)

    
    def makesocket(self, start, stop, condition):

        self.sock = sk.socket(sk.AF_INET, sk.SOCK_STREAM)

        try:
            self.sock.connect((self.servName, self.port))
            print start, stop, condition
            request = self.makerequest(condition, self.objName, self.servName, start, stop)
            self.sock.send(request)

        except:
            print "make socket error"
            sys.exit(1)

    def closesocket(self):

        self.sock.close()

    def check_redirect(self):

        new_path = ""

        if "HTTP/1.1 301" in self.head_content or "HTTP/1.1 302" in self.head_content:

            self.need_redirect = True

            for i in self.head_content[self.head_content.find("location: ") + 10 :]:

                if i == "\r":

                    break

                else:

                    new_path += i


            print "==========="
            print "debug 2"

            self.objName = "/" + new_path

            self.head_content = ""

            print self.servName, self.objName

            self.getHeader(self.servName, self.objName)

            print "==========="

    def get_content_length(self):

        content_length_str = ""

        if "HTTP/1.1 200 OK" in self.head_content or "HTTP/1.1 206" in self.head_content:

            self.error = False

            if "Content-Length: " in self.head_content:

                for i in self.head_content[self.head_content.find("-Length: ") + 9 :]:
                    
                    self.has_content_length = True
                    
                    if i == "\r":
                        
                        break
                    
                    else:
                    
                        content_length_str += i

        print "=========="
        print "dubug 1"
        print content_length_str
        print "=========="

        self.header_length = len(self.head_content)

        if content_length_str != "":
            self.content_length = int(content_length_str)


    def check_version(self, headfile):
        read_head = open(headfile, "r")
        file_head_cotent = read_head.read()
        old_etag = ""
        old_datemodified = ""

        if "ETag: " in file_head_cotent:
            for i in file_head_cotent[file_head_cotent.find("ETag: ") + 6:]:
                old_etag += i
                if i == "\r":
                    break
            if old_etag in self.head_content:
                self.same_version = True

        elif "Last-Modified: " in file_head_cotent:
            for i in file_head_cotent[file_head_cotent.find("Last-Modified: ") + 15:]:
                old_datemodified += i
                if i == "\r":
                    break
            if old_datemodified in self.head_content:
                self.same_version = True


    def download_and_resume(self):

        print "debug 0"

        self.get_content_length()

        print "=============="
        print self.header_length
        print self.has_content_length
        print self.content_length
        print self.error
        print "=============="

        if self.error:

            print "unable to download file"

            sys.exit(1)

        if os.path.exists(self.filename):

            file_size = os.stat(self.filename).st_size
            total_loaded_content = file_size

            if os.path.exists("HEADFILE" + self.filename):

                print "1"

                self.check_version("HEADFILE" + self.filename)

                print "check_version =", self.same_version

                if self.same_version == True and file_size != self.content_length and self.content_length != 0:

                    self.makesocket(file_size, None, None)

                elif self.same_version == True and self.content_length == 0:

                    self.makesocket(file_size, None, None)

                else:

                    print "2"

                    os.remove(self.filename)

                    os.remove("HEADFILE" + self.filename)

                    self.makesocket(0, self.content_length, None)

                    total_loaded_content = 0

            else:

                if file_size == self.content_length:

                    print "file has been downloaded"

                    sys.exit(1)

                os.remove(self.filename)

                self.makesocket(0, self.content_length, None)

                total_loaded_content = 0

        else:

            print "k"

            self.makesocket(0, self.content_length, None)

            total_loaded_content = 0

        # print "ssss", self.content_length

        loaded_head_content = ""
        head_file = file
        download_file = file

        while "\r\n\r\n" not in loaded_head_content:

            data = self.sock.recv(1)

            loaded_head_content += data

            open_head = open("HEADFILE" + self.filename, "wb")

            open_head.write(loaded_head_content)


        if self.has_content_length == True:

            while total_loaded_content < self.content_length:

                file_content = ""

                data = self.sock.recv(1024)

                total_loaded_content += len(data)

                print total_loaded_content, self.content_length

                file_content += data

                open_file = open(self.filename, "a+")
            
                open_file.write(file_content)

            open_file.close()

            open_head.close()

            self.closesocket()

        else:

            # print "===== no content length ====="

            while True:

                file_content = ""

                data = self.sock.recv(1024)

                total_loaded_content += len(data)

                print total_loaded_content, self.content_length

                file_content += data 

                open_file = open(self.filename, "a+")
            
                open_file.write(file_content)

                if len(data) == 0:

                    open_file.close()

                    open_head.close()
                    
                    self.closesocket()
                    
                    break

        os.remove("HEADFILE" + self.filename)







    # def parse_content(self):

    #     length = [0]

    #     count = 0

    #     self.get_content_length()

    #     content_left = self.content_length

    #     while content_left > 0:

    #         if content_left - 50000 <= 0:

    #             length.append(length[count] + content_left)

    #             content_left = 0

    #         else:

    #             length.append(length[count] + 50000)
                
    #             content_left -= 50000

    #         count += 1

    #     print length









 
    # # Called when the active opener's socket actually makes a connection.

    # def handle_connect(self):
    #     self.logger.debug("connection established")

 
    # # Called when the socket is closed.

    # def handle_close(self):
    #     self.logger.debug("got disconnected")
    #     self.close()



    # def check_content_length(self, header):

    #     header_length = len(header)
    #     content_length_str = ""
    #     content_length = 0
    #     has_content_length = False
    #     error = True

    #     if "HTTP/1.1 200 OK" in header:

    #         error = False

    #         if "Content-Length: " in header:

    #             for i in header[header.find("-Length: ") + 9 :]:
                    
    #                 has_content_length = True
                    
    #                 if i == "\r":
                        
    #                     break
                    
    #                 else:
                    
    #                     content_length_str += i

    #             content_length = int(content_length_str)
            
    #     return content_length, header_length, has_content_length, error
 

    # # Called when the asynchronous loop detects that a read() call on the channel's socket will succeed.

    # def handle_read(self):
    #     # buf = self.recv(8192)
    #     # self.recvbuf.write(buf)
        
    #     while "\r\n\r\n" not in self.header:

    #         data = self.recv(1)

    #         self.header += data

    #     print self.header


    #     print self.check_content_length(self.header)

    #     data = self.recv(1024)
 
    #     self.logger.debug("recv {0} bytes".format(len(read_head)))



    # # Called each time around the asynchronous loop to determine whether a channel's
    # # socket should be added to the list on which write events can occur.
 
    # def writeable(self):
    #     return len(self.sendbuf) > 0
 

    # # Called when the asynchronous loop detects that a writable socket can be written.
    # # Often this method will implement the necessary buffering for performance.

    # def handle_write(self):
    #     bytes_sent = self.send(self.sendbuf)
        # self.sendbuf = self.sendbuf[bytes_sent:]
 
clients = [
    # HTTPClient("classroomclipart.com/images/gallery/Clipart/Animals/Lion_Clipart/TN_lion-clipart-115.jpg")#,
    # HTTPClient("images.clipartpanda.com/lion-clipart-4Tb5XEETg.png")
    # HTTPClient("http://www.muic.info/")
    HTTPClient("http://static.pexels.com/photos/7976/pexels-photo.jpg")
]
 
logging.basicConfig(level=logging.DEBUG,
    format="%(asctime)-15s %(name)s: %(message)s"
    )
 
asyncore.loop()