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

def HeadRequest(serv, objName):
    return ("HEAD {o} HTTP/1.1\r\n" + "Host: {s}\r\n\r\n").format(o=objName, s=serv)

def resumableRequest(serv, objName, start, stop):
    return ("GET {o} HTTP/1.1\r\n" + "Host: {s}\r\n" + "Range: bytes={h}-{z}" + "\r\n\r\n").format(o=objName, s=serv, h=start, z=stop)

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
    

def getContentLength(servName, objName):

    sock = sk.socket(sk.AF_INET, sk.SOCK_STREAM)

    sock.connect((servName, port))
    
    request = HeadRequest(servName, objName)

    sock.send(request)

    header = ""

    while True:

        data = sock.recv(1024)

        header = data[:data.find("\r\n\r\n")]

        sock.close

        break

    return getHeaderSize(header)







def getDownloadInformation(servName, objName):

    file_exist = False
    check = False
    head_content = ""
    file_content = ""
    head_file = file
    download_file = file
    filename = "lionnoiresume.jpg"

    sock = sk.socket(sk.AF_INET, sk.SOCK_STREAM)

    sock.connect((servName, port))

    content_length = getContentLength(servName, objName)[0]
    header_length = getContentLength(servName, objName)[1]
    has_content_length = getContentLength(servName, objName)[2]
    error = getContentLength(servName, objName)[3]

    total_loaded_content = 0 - header_length - len("\r\n\r\n")

    if error:
        return "Error, unable to download the file."

    if os.path.exists(filename):

        print "file exist na"

        file_exist = True

        file_size = os.stat(filename).st_size

        if file_size == content_length:
            return "File already downloaded."

        request = resumableRequest(servName, objName, file_size, content_length)

        mode = "resume mode"

        total_loaded_content = file_size - header_length - len("\r\n\r\n")


        print content_length, file_size, content_length - file_size


    else:

        request = mkDownloadRequest(servName, objName)

        mode = "download mode"

    sock.send(request)

    while True:

        data = sock.recv(1024)

        for i in data:
            print total_loaded_content, content_length, header_length
            total_loaded_content += 1
            if "\r\n\r\n" in head_content:
                file_content += i
            else:
                head_content += i


        if mode == "download mode":
            open_file = open(filename, "wb")
            open_file.write(file_content)
            # print file_content

        elif mode == "resume mode":
            open_file = open(filename, "a+")
            open_file.write(file_content)
            print file_content

        if content_length != 0 and total_loaded_content >= content_length and has_content_length:
            print "total load content =", total_loaded_content, "& content length =", content_length
            sock.close()
            break

        elif has_content_length == False and len(data) == 0:
            sock.close()
            break

    # print content_length - file_size - total_loaded_content
    if os.path.exists(filename):

        open_file.close
            # head_file = open("HEADFILE:" + filename, "wb")
            # head_file.write(head_content)
            # head_file.close
    else:
        open_file = open(filename, "wb")
        open_file.write(file_content)
        open_file.close
        # head_file = open("HEADFILE:" + filename, "wb")
        # head_file.write(head_content)
        # head_file.close





def main(url):
    parse = urlparse(url)
    servName = parse.netloc
    path = parse.path
    # print getContentLength(servName, path)
    print getDownloadInformation(servName, path)

print main("http://images.clipartpanda.com/lion-clipart-4Tb5XEETg.png")