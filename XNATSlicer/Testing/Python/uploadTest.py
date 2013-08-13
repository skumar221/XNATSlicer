def upload():

    login = "sunilk"
    password = "ambuSa5t"
    localSrc = "C:/Users/Sunil Kumar/Desktop/XNATSlicer/XNATSlicer/XNATSlicerLib/data/temp/upload/test1.mrb"
    f=open(localSrc, 'rb')
    filebody = f.read()
    f.close()
    
    
    #url = 'http://central.xnat.org/data' + XNATDst;
    url = 'http://central.xnat.org/data/projects/XNATSlicerTest/subjects/DE-IDENTIFIED/experiments/UCLA_1297/resources/Slicer/files/test5.mrb'
    
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
