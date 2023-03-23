import time

allowed_chars = "tap"
str_as_string = "test"
str_as_bytes = str_as_string.encode("UTF-8")
# str_as_bytes = b'\xd0\xa1\xd0\xbe\xd0\xbb\xd0\xbe \xd0\xb4\xd0\xbb\xd1\x8f \xd1\x81\xd0\xbb\xd0\xbe\xd0\xbd\xd0\xb0 \xd1\x81 \xd0\xbe\xd1\x80\xd0\xba\xd0\xb5\xd1\x81\xd1\x82\xd1\x80\xd0\xbe\xd0\xbc (1975)'
print(str_as_bytes)
print(str_as_bytes.decode('utf-8'))
#str_result = ''.join(chr(c) for c in str_as_bytes)
#print(str_result)
#print(str_as_string)
#str_result = ''.join(c for c in str_as_string if c in allowed_chars)
#print(str_result)
sub = {'name': str_as_bytes, 'refresh': True, 'type': 'movie', 'last_run': time.time()}
sub['last_run'] = time.time()
print(sub)
print(sub['non_exist'] if 'non_exist' in sub else None)
