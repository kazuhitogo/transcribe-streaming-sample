import datetime,boto3,hmac
from hashlib import sha256
from urllib.parse import quote

# Key derivation functions. See:
# http://docs.aws.amazon.com/general/latest/gr/signature-v4-examples.html#signature-v4-examples-python
def sign(key, msg):
    return hmac.new(key, msg.encode('utf-8'), sha256).digest()

def getSignatureKey(key, dateStamp, regionName, serviceName):
    kDate = sign(('AWS4' + key).encode('utf-8'), dateStamp)
    kRegion = sign(kDate, regionName)
    kService = sign(kRegion, serviceName)
    kSigning = sign(kService, 'aws4_request')
    return kSigning

def make_ws_uri(method:str='GET', service:str='transcribe', region:str='ap-northeast-1', language_code:str='ja-JP' ,media_encoding:str='pcm', sample_rate:int=16000, verbose:bool=False) -> str:
    # Using Amazon Transcribe Streaming with WebSocket. See:
    # https://docs.aws.amazon.com/transcribe/latest/dg/websocket.html
    #
    # 0. get access key and secret key
    credentials = boto3.Session().get_credentials()
    access_key = credentials.access_key
    secret_key = credentials.secret_key

    # 1-1. Define variables for the request in your application.
    endpoint = "wss://transcribestreaming."+region+".amazonaws.com:8443"
    host = "transcribestreaming."+region+".amazonaws.com:8443"
    t = datetime.datetime.utcnow()
    amz_date = t.strftime('%Y%m%dT%H%M%SZ')
    datestamp = t.strftime('%Y%m%d')

    # 1-2. Create a canonical URI. The canonical URI is the part of the URI between the domain and the query string.
    canonical_uri = "/stream-transcription-websocket"

    # 1-3. Create the canonical headers and signed headers. Note the trailing "\n" in the canonical headers.
    canonical_headers = "host:" + host + "\n"
    signed_headers = "host"

    # 1-4. Match the algorithm to the hashing algorithm. You must use SHA-256.
    algorithm = "AWS4-HMAC-SHA256"

    # 1-5. Create the credential scope, which scopes the derived key to the date, Region, and service to which the request is made.
    credential_scope = datestamp + "/" + region + "/" + service + "/" + "aws4_request"
    
    # 1-6. Create the canonical query string. Query string values must be URL-encoded and sorted by name.
    canonical_querystring  = "X-Amz-Algorithm=" + algorithm
    canonical_querystring += "&X-Amz-Credential="+ quote( access_key + "/" + credential_scope, safe='')
    canonical_querystring += "&X-Amz-Date=" + amz_date 
    canonical_querystring += "&X-Amz-Expires=300"
    canonical_querystring += "&X-Amz-SignedHeaders=" + signed_headers
    canonical_querystring += "&language-code="+language_code
    canonical_querystring += "&media-encoding=" + media_encoding
    canonical_querystring += "&sample-rate=" + str(sample_rate)

    # 1-7. Create a hash of the payload. For a GET request, the payload is an empty string.
    payload_hash = sha256(("").encode("utf-8")).hexdigest()
    
    # 1-8. Combine all of the elements to create the canonical request.
    canonical_request = method + '\n' + canonical_uri + '\n' + canonical_querystring + '\n' + canonical_headers + '\n' + signed_headers + '\n' + payload_hash

    # 2. Create the String to Sign
    string_to_sign=algorithm + "\n"+ amz_date + "\n"+ credential_scope + "\n"+ sha256(canonical_request.encode("utf-8")).hexdigest()


    # 3. Calculate the Signature
    signing_key = getSignatureKey(secret_key, datestamp, region, service)
    signature = hmac.new(signing_key, (string_to_sign).encode("utf-8"), sha256).hexdigest()
    
    # 4. Add Signing Information to the Request and Create the Request URL
    canonical_querystring += "&X-Amz-Signature=" + signature
    request_url = endpoint + canonical_uri + "?" + canonical_querystring
    
    if verbose:
        print("\n"*2)
        print("--------------debugger start--------------")
        print(f"access_key : {access_key}")
        print(f"secret_key : {secret_key}")
        print(f"region : {region}") 
        print(f"host : {host}")
        print(f"amz_date : {amz_date}")
        print(f"datestamp : {datestamp}")
        print(f"canonical_uri : {canonical_uri}")
        print(f"canonical_headers : {canonical_headers}")
        print(f"credential_scope : {credential_scope}")
        print(f"canonical_querystring : {canonical_querystring}")
        print(f"payload_hash : {payload_hash}")
        print(f"canonical_request : {canonical_request}")
        print(f"string_to_sign : {string_to_sign}")
        print(f"signing_key : {signing_key}")
        print(f"signature : {signature}")
        print(f"canonical_querystring : {canonical_querystring}")
        print(f"request_url : {request_url}")
        print("--------------debugger end--------------")
        print("\n"*2)
    return request_url

if __name__ == "__main__":
    print(make_ws_uri(verbose=True))
    exit()
