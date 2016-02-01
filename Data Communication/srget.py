#!/usr/bin/env python
import socket as sk
import os, getopt, sys, asyncore, logging
from cStringIO import StringIO
from urlparse import urlparse

port = 80

def check_url(url):
    if url[:7] != "http://":
        url = "http://" + url
    return url

def mkDownloadRequest(serv, objName):
    return ("GET {o} HTTP/1.1\r\n" + "Host: {s}\r\n\r\n").format(o=objName, s=serv)

def HeadRequest(serv, objName):
    return ("HEAD {o} HTTP/1.1\r\n" + "Host: {s}\r\n\r\n").format(o=objName, s=serv)

def resumableRequest(serv, objName, start, stop):
    return ("GET {o} HTTP/1.1\r\n" + "Host: {s}\r\n" + "Range: bytes={h}-{z}" + "\r\n\r\n").format(o=objName, s=serv, h=start, z=stop)

def get_header_information(header):

    header_length = len(header)
    content_length_str = ""
    content_length = 0
    has_content_length = False
    error = True

    if "HTTP/1.1 200 OK" in header:

        error = False

        if "Content-Length: " in header:

            for i in header[header.find("-Length: ") + 9 :]:
                
                has_content_length = True
                
                if i == "\r":
                    
                    break
                
                else:
                
                    content_length_str += i

            content_length = int(content_length_str)
        
    return content_length, header_length, has_content_length, error


def check_redirect(header):

    new_url = ""

    need_redirect = False

    if "HTTP/1.1 301" in header or "HTTP/1.1 302" in header:

        need_redirect = True

        for i in header[header.find("location: ") + 10 :]:

            if i == "\r":

                break

            else:

                new_url += i

    return need_redirect, new_url

    

def getHeader(servName, objName):

    sock = sk.socket(sk.AF_INET, sk.SOCK_STREAM)

    sock.connect((servName, port))
    
    request = HeadRequest(servName, objName)

    sock.send(request)

    header = ""

    while "\r\n\r\n" not in header:

        data = sock.recv(1)

        header += data

        sock.close

    return header



def check_version(headfile, new_header):
    read_head = open(headfile, "r")
    header = read_head.read()
    same_version = False
    old_etag = ""
    old_datemodified = ""

    if "ETag: " in header:
        for i in header[header.find("ETag: ") + 6:]:
            old_etag += i
            if i == "\r":
                break
        if old_etag in new_header:
            same_version = True

    elif "Last-Modified: " in header:
        for i in header[header.find("Last-Modified: ") + 15:]:
            old_datemodified += i
            if i == "\r":
                break
        if old_datemodified in new_header:
            same_version = True

    return same_version



def download_and_resume(servName, objName, filename):

    header = getHeader(servName, objName)

    # redirect check

    redirect_or_not = check_redirect(header)

    print "redirect_or_not =", redirect_or_not

    if redirect_or_not[0] == True:

        print "================",servName+"/"+redirect_or_not[1]

        return main(servName + "/" + redirect_or_not[1]) # call main with new url

    sock = sk.socket(sk.AF_INET, sk.SOCK_STREAM)

    sock.connect((servName, port))

    content_length, header_length, has_content_length, error = get_header_information(header)

    if error:
        return "Error, unable to download the file."

    if os.path.exists(filename):

        file_size = os.stat(filename).st_size
        total_loaded_content = file_size



        # RESUME & DOWNLOAD separate by request!

        if os.path.exists("HEADFILE" + filename):

            print "1"

            same_version = check_version("HEADFILE" + filename, header)

            print header

            if same_version == True and file_size != content_length:

                request = resumableRequest(servName, objName, file_size, content_length)

            else:

                print "2"

                os.remove(filename)

                os.remove("HEADFILE" + filename)

                request = mkDownloadRequest(servName, objName)

                total_loaded_content = 0

        else:

            if file_size == content_length:

                return "File has been successfully downloaded."

            print "show"

            os.remove(filename)

            request = mkDownloadRequest(servName, objName)

            total_loaded_content = 0

    else:

        request = mkDownloadRequest(servName, objName)
        total_loaded_content = 0

    print "4"

    head_content = ""
    head_file = file
    download_file = file

    sock.send(request)

    while "\r\n\r\n" not in head_content:

        data = sock.recv(1)

        head_content += data

        open_head = open("HEADFILE" + filename, "wb")

        open_head.write(head_content)



    if has_content_length == True:

        while total_loaded_content < content_length:

            file_content = ""

            data = sock.recv(1024)

            total_loaded_content += len(data)

            print total_loaded_content, content_length

            file_content += data 

            open_file = open(filename, "a+")
        
            open_file.write(file_content)


        open_file.close()

        open_head.close()

        sock.close

        os.remove("HEADFILE" + filename)

    else:

        while True:

            data = sock.recv(1024)

            if len(data) == 0:
                
                sock.close()
                
                break


def main(url):
    url_with_http = check_url(url)
    parse = urlparse(url_with_http)
    servName = parse.netloc
    path = parse.path
    print download_and_resume(servName, path, filename)

filename = "lionnoi.jpg"
# url = "images.clipartpanda.com/lion-clipart-4Tb5XEETg.png"
url = "classroomclipart.com/images/gallery/Clipart/Animals/Lion_Clipart/TN_lion-clipart-115.jpg"
# url = "http://www.muic.info/"

print main(url)

# def main(argv):
#     filename = ""
#     try:
#         opts, args = getopt.getopt(sys.argv[1:], "o:c:", ["output=","cname="])
#     except getopt.GetoptError as err:
#         print str(err)
#         usage()
#         sys.exit()
#     url = argv[-1]
#     for opt,arg in opts:
#         if opt == "-o":
#             filename=arg
#     url_with_http = check_url(url)
#     parse = urlparse(url_with_http)
#     servName = parse.netloc
#     path = parse.path
#     print download_and_resume(servName, path, filename)



# if __name__ == "__main__":
#     main(sys.argv[1:])