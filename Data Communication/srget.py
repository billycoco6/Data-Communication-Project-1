import socket as sk
import os
from urlparse import urlparse

port = 80

def check_url(url):
    if url[:7] != "http://" and url[:8] != "https://":
        url = "http://" + url
    return url

def mkDownloadRequest(serv, objName):
    return ("GET {o} HTTP/1.1\r\n" + "Host: {s}\r\n\r\n").format(o=objName, s=serv)

def resumableRequest(serv, objName, start, stop):
    return ("GET {o} HTTP/1.1\r\n" + "Host: {s}\r\n\r\n" + "Range: byte={a}-{z}" + "\r\n\r\n").format(o=objName, s=serv, a=start, z=stop)

def getHeaderSize(header):

    header_length = 0
    content_length = 0
    has_content_length = False
    error = True

    if "HTTP/1.1 200 OK" in header:

        error = False
        for i in header:
            header_length += 1
            content_length_str = ""

        if "Content-Length: " in header:

            for i in header[header.find("-Length: ") + 9 :]:
                has_content_length = True
                if i == "\r":
                    break
                else:
                    content_length_str += i

            content_length = int(content_length_str)
        
    return content_length, header_length, has_content_length, error
    
def getDownloadInformation(servName, objName):

    sock = sk.socket(sk.AF_INET, sk.SOCK_STREAM)

    sock.connect((servName, port))

    request = mkDownloadRequest(servName, objName)

    sock.send(request)
    check = False
    head_content = ""
    file_content = ""
    head_file = file
    download_file = file

    while True:

        data = sock.recv(1024)

        if "\r\n\r\n" in data and check != True:
            header = data[:data.find("\r\n\r\n")]
            content_length, header_length, has_content_length, http_error = getHeaderSize(header)[0], getHeaderSize(header)[1], getHeaderSize(header)[2], getHeaderSize(header)[3]
            if http_error:
                return "Error, could not download page."
                 
            print "=====================", content_length, header_length
            total_loaded_content = 0 - header_length - len("\r\n\r\n")
            check = True

        for i in data:
            total_loaded_content += 1
            if total_loaded_content > 0:
                file_content += i
            else:
                head_content += i

        if content_length != 0 and total_loaded_content >= content_length and has_content_length:
            print "total load content =", total_loaded_content
            print "content length =", content_length
            sock.close()
            break

        elif has_content_length == False and len(data) == 0:
            sock.close()
            break

    filename = raw_input("Enter the file name: ")

    if os.path.exists(filename):

        overwrite = raw_input("File exists, do you want to replace? y/n: ")
        if overwrite == "y":
            open_file = open(filename, "wb")
            open_file.write(file_content)
            open_file.close
            head_file = open("HEADFILE:" + filename, "wb")
            head_file.write(head_content)
            head_file.close
    else:
        open_file = open(filename, "wb")
        open_file.write(file_content)
        open_file.close
        head_file = open("HEADFILE:" + filename, "wb")
        head_file.write(head_content)
        head_file.close

def resume(filename):
    if os.path.exists(filename):

        Resumesock = sk.socket(sk.AF_INET, sk.SOCK_STREAM)
        Resumesock.connect((servName, port))
        request = mkDownloadRequest(servName, objName)
        Resumesock.send(request)

def main():
    url = raw_input("Enter the url: ")
    parse = urlparse(url)
    servName = parse.netloc
    path = parse.path
    
    print getDownloadInformation(servName, path)

print main()