import json

def httpsRequest(restMethod, url, body = '', headerAdditions={}):

    userAndPass = b64encode(b"%s:%s"%('sunilk', 'ambuSa5t')).decode("ascii")
    authenticationHeader = { 'Authorization' : 'Basic %s' %(userAndPass) }
        
    # Clean REST method
    restMethod = restMethod.upper()
    
    # Clean url
    url = url.encode("utf-8")
    
    # Get request
    req = urllib2.Request (url)
    
    # Get connection
    connection = httplib.HTTPSConnection (req.get_host ()) 
    
    # Merge the authentication header with any other headers
    header = dict(authenticationHeader.items() + headerAdditions.items())
    
    # REST call
    connection.request (restMethod, req.get_selector (), body=body, headers=header)
    
    print utils.lf() + "XNAT request - %s %s"%(restMethod, url)
    # Return response
    return connection.getresponse ()



fileUrl = 'https://central.xnat.org/data/archive/projects/XNATSlicerTest/subjects/DE-IDENTIFIED/experiments/UCLA_1297/resources/Slicer/files/test3a.mrb'

def getSize(fileUrl):
    
    if ('/files' in fileUrl):
        parentDir = fileUrl.split('/files')[0] + '/files'
    else:
        raise Exception(" invalid getSize parameter: %s"%(fileUrl))

    response = httpsRequest('GET', parentDir).read()
    result = json.loads(response)['ResultSet']['Result']
    
    for i in result:
        if os.path.basename(fileUrl) in i['Name']:
            print "RES2: ", i['Size']


getSize(fileUrl);
