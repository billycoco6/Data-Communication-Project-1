import socket as sk
import os
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

def getHeaderSize(header):

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
    

def getContentLength(servName, objName):

    sock = sk.socket(sk.AF_INET, sk.SOCK_STREAM)

    sock.connect((servName, port))
    
    request = HeadRequest(servName, objName)

    sock.send(request)

    header = ""

    while "\r\n\r\n" not in header:

        data = sock.recv(1)

        header += data

        sock.close

    return getHeaderSize(header)


def getDownloadInformation(servName, objName):

    head_content = ""
    file_content = ""
    head_file = file
    download_file = file

    sock = sk.socket(sk.AF_INET, sk.SOCK_STREAM)

    sock.connect((servName, port))

    for_header_information = getContentLength(servName, objName)
    content_length, header_length, has_content_length, error = for_header_information

    if error:
        return "Error, unable to download the file."

    request = mkDownloadRequest(servName, objName)

    total_loaded_content = 0

    sock.send(request)

    while "\r\n\r\n" not in head_content:

        data = sock.recv(1)

        head_content += data

    if has_content_length == True:

        while total_loaded_content < content_length:

            data = sock.recv(1024)

            total_loaded_content += len(data)

            print total_loaded_content, content_length

            file_content += data 

            open_file = open(filename, "wb")
        
            open_file.write(file_content)

        sock.close

    else:

        while True:

            data = sock.recv(1024)

            if len(data) == 0:
                
                sock.close()
                
                break

def resumeInformation(servName, objName):

    head_content = ""
    head_file = file
    download_file = file
    filename = "lionnoi.jpg"
    file_size = os.stat(filename).st_size
    total_loaded_content = file_size

    for_header_information = getContentLength(servName, objName)
    content_length, header_length, has_content_length, error = for_header_information

    if file_size == content_length:
        return "File has been successfully downloaded."

    sock = sk.socket(sk.AF_INET, sk.SOCK_STREAM)
    sock.connect((servName, port))

    request = resumableRequest(servName, objName, file_size, content_length)

    sock.send(request)

    while "\r\n\r\n" not in head_content:

        data = sock.recv(1)

        head_content += data

    if has_content_length == True:

        while total_loaded_content < content_length:

            file_content = ""

            data = sock.recv(1024)

            total_loaded_content += len(data)

            print total_loaded_content, content_length

            file_content += data 

            open_file = open(filename, "a+")
        
            open_file.write(file_content)

        sock.close

    else:

        while True:

            data = sock.recv(1024)

            if len(data) == 0:
                
                sock.close()
                
                break


def main(url):
    parse = urlparse(url)
    servName = parse.netloc
    path = parse.path
    if os.path.exists(filename):
        print resumeInformation(servName, path)
    else:
        print getDownloadInformation(servName, path)

filename = "lionnoi.jpg"
url = "http://www.clipartsheep.com/images/345/baby-lion-clipart-panda-free-images-clipart.png"

print main(url)