
def upload(num):

    login = "sunilk"
    password = "ambuSa5t"
    localSrc = "C:/Users/Sunil Kumar/Desktop/test1.mrb"
    f=open(localSrc, 'rb')
    filebody = f.read()
    f.close()
    
    
    #url = 'http://central.xnat.org/data' + XNATDst;
    url = 'http://central.xnat.org/data/projects/XNATSlicerTest/subjects/DE-IDENTIFIED/experiments/UCLA_1297/resources/Slicer/files/test%s.mrb'%(num)
    
    print "*******************URL: ", url
    
    
    req = urllib2.Request (url)
    connection = httplib.HTTPSConnection (req.get_host ())
    #userAndPass = b64encode(b"%s:%s"%(self.user,self.password)).decode("ascii")     
    userAndPass = b64encode(b"%s:%s"%(login, password)).decode("ascii")       
    header = { 'Authorization' : 'Basic %s' %  userAndPass, 'content-type': 'application/octet-stream'}
    
    connection.request ('PUT', req.get_selector (), body=b64encode(filebody).decode("base64"), headers=header)
    #connection.request ('PUT', req.get_selector (), body=(filebody).encode("utf-8"), headers=header)
    response = connection.getresponse ()
    print "response: ", response.read()
    return response


def notWorking():
    import os
    from os.path import abspath, isabs, isdir, isfile, join
    import string
    import sys
    import httplib
    from base64 import b64encode
    
    
    filePath = "C:/Users/Sunil Kumar/Desktop/test1.mrb"
    url = 'http://central.xnat.org/data/projects/XNATSlicerTest/subjects/DE-IDENTIFIED/experiments/UCLA_1297/resources/Slicer/files'
    
    r = requests.get(url, auth=('sunilk', 'ambuSa5t'))
    print r.text
    
    
    
    fl=open(filePath, 'rb')
    filebody = fl.read()
    fl.close()
    
    
    #url = os.path.join(url, "AAAAA.mrb") 
    url = url.replace("\\", '/')
    
    #files = {'file': ('asdfasdf', open(filePath, 'rb'))}
    
    
    r = requests.put(url,  data={'file': open(filePath, 'rb')}, auth=('sunilk', 'ambuSa5t'))
    #r = requests.put(url, files=files, auth=('sunilk', 'ambuSa5t'))
    print r.text
