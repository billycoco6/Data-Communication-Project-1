import socket as sk
import os, getopt, sys

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
        # print old_etag

    elif "Last-Modified: " in header:
        for i in header[header.find("Last-Modified: ") + 15:]:
            old_datemodified += i
            if i == "\r":
                break
        # print old_datemodified

    if old_etag in new_header or old_datemodified in new_header:
        same_version = True
    return same_version





def download_and_resume(servName, objName):

    head_content = ""
    head_file = file
    download_file = file

    sock = sk.socket(sk.AF_INET, sk.SOCK_STREAM)

    sock.connect((servName, port))

    header = getHeader(servName, objName)

    content_length, header_length, has_content_length, error = get_header_information(header)

    if error:
        return "Error, unable to download the file."

    if os.path.exists(filename):

        file_size = os.stat(filename).st_size
        total_loaded_content = file_size

        # RESUME & DOWNLOAD separate by request!

        if os.path.exists("HEADFILE" + filename):

            same_version = check_version("HEADFILE" + filename, header)

            if same_version == True:

                if file_size == content_length:

                    return "File has been successfully downloaded."
                else:

                    request = resumableRequest(servName, objName, file_size, content_length)

            else:

                request = mkDownloadRequest(servName, objName)


        # if version same, but not finish:
            # resume

        # elif file_size == content_length: # version the same
        #     return "File has been successfully downloaded."

        # elif version not the same:
            # redownload

        # else: <--- cannot find version
            # redownload


    else:
        request = mkDownloadRequest(servName, objName)
        total_loaded_content = 0

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

            # close file?

        sock.close

        # delete head file if downloading done.

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
    print download_and_resume(servName, path)

filename = "lionnoi.jpg"
url = "http://classroomclipart.com/images/gallery/Clipart/Animals/Lion_Clipart/TN_lion-clipart-115.jpg"

print main(url)

# def main(argv):
#     outputfile = ""
#     try:
#         opts, args = getopt.getopt(sys.argv[1:], "oc", ["output", "connection"])
#     except getopt.GetoptError as err:
#         print str(err)
#         usage()
#         sys.exit()

# if __name__ == "__main__":
#     main()