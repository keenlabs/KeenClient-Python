# Padding methods for password based encryption
# Author: Peio Popov <peio@peio.org>
# License: Public Domain
# Version: 0.4 

__doc__ = '''
Padding methods for password based encryption

I. Functions:
appendPadding(str, blocksize=AES_blocksize, mode='CMS'):
 Pad (append padding to) string for use with symmetric encryption algorithm
    Input: (string) str - String to be padded
           (int)    blocksize - block size of the encryption algorithm. Usually 8 or 16 bytes
           (string) mode - padding scheme one in (CMS, Bit, ZeroLen, Null, Space, Random)
    Return:(string) Padded string according to chosen padding mode

removePadding(str, blocksize=AES_blocksize, mode='CMS'):
  Remove padding from string 
  Input: (str) str - String to be padded
         (int) blocksize - block size of the algorithm. Usually 8 or 16 bytes
         (string) mode - padding scheme one in (CMS, Bit, ZeroLen, Null, Space, Random)
  Return:(string) Decrypted string without padding

II. Blocksizes:
DES (Triple DES), CAST5 and Blowfish have block size of 64 bits = 8 bytes
DES_blocksize = 8 
CAST5_blocksize = 8
Blowfish_blocksize = 8

AES has fixed block size of 128 bits = 16 bytes and this is the default blocksize
AES_blocksize = 16

III. Mode:
MODES ={
(0,'CMS')     : 'Pad with bytes all of the same value as the number of padding bytes. Default mode used in Cryptographic Message Syntax (CMS as defined in RFC 5652, PKCS#5, PKCS#7 and RFC 1423 PEM)',
(1,'Bit')     : 'BitPadding: Pad with 0x80 (10000000) followed by zero (null) bytes. Described in ANSI X.923 and ISO/IEC 9797-1',
(2,'ZeroLen') : 'Pad with zeroes except make the last byte equal to the number (length) of padding bytes',
(3,'Null')    : 'Pad with null bytes. Only for encrypting of text data.',
(4,'Space')   : 'Pad with spaces. Only for encrypting of text data.',
(5,'Random')  : 'ISO 10126 Padding (withdrawn in 2007): Pad with random bytes + last byte equal to the number of padding bytes'         
       }

CMS mode is the default one

IV. Examples:
Example 1: Add/Remove padding for message to be encrypted/decrypted with AES
> from Padding import appendPadding, removePadding
> msg = 'a'*20
> 
> padded_msg = appendPadding(msg) # 'Default blocksize is 16 bytes (128 bits) which is AES blocksize'
> padded_msg, len(padded_msg)
> msg = removePadding(padded_msg)
> msg, len(msg)

Example 2:  Add/Remove padding for message to be encrypted/decrypted with DES (Triple DES), CAST5 or Blowfish
> import Padding
> msg = 'b'*20
> blocksize = Padding.DES_blocksize
> "DES has fixed block size of %d bits = %d bytes" % (blocksize*8, blocksize)  
> padded_msg = Padding.appendPadding(msg, blocksize)
> padded_msg, len(padded_msg)
> msg = Padding.removePadding(padded_msg)
> msg, len(msg)
'''

'Blocksizes'
'DES (Triple DES), CAST5 and Blowfish have block size of 64 bits = 8 bytes'
DES_blocksize = 8 
CAST5_blocksize = 8
Blowfish_blocksize = 8

'RC4, RC5, RC6 can have variable blocksizes'
 
'AES has fixed block size of 128 bits = 16 bytes'
AES_blocksize = 16

def paddingLength(str_len, blocksize=AES_blocksize):
  ''' Function to calculate the length of the required padding
  Input: (int) str_len   - String length of the text 
         (int) blocksize - block size of the algorithm    
  Returns: (int) number of required pad bytes for string of size.'''
  assert 0 < blocksize < 255, 'blocksize must be between 0 and 255'
  assert str_len > 0 , 'string length should be non-negative'
  
  'If the last block is already full, append an extra block of padding'
  pad_len = blocksize - (str_len % blocksize)
  
  return pad_len   

def appendCMSPadding(str, blocksize=AES_blocksize):
  '''CMS padding: Pad with bytes containing the number of padding bytes
    Cryptographic Message Syntax (CMS) Padding
    Pad with bytes all of the same value as the number of padding bytes
    Recommended in: RFC 5652 (CMS) section 6.3.; 
                PKCS#7 (CMS) section 10.3 (Note2)  
                PKCS#5 section 6.1.1 p.4, 
                RFC 1423 (PEM) section 1.1  
  Each padding byte contains the number of padding bytes.
  '''
  pad_len = paddingLength(len(str), blocksize)
  padding = (chr(pad_len) * pad_len)
  return str + padding

def removeCMSPadding(str, blocksize=AES_blocksize):
  '''CMS padding: Remove padding with bytes containing the number of padding bytes '''
  try:
    pad_len = ord(str[-1]) # last byte contains number of padding bytes
  except TypeError:
    pad_len = str[-1]
  assert pad_len <= blocksize, 'padding error' 
  assert pad_len <= len(str), 'padding error'
    
  return str[:-pad_len]

def appendBitPadding(str, blocksize=AES_blocksize):
  '''Bit padding a.k.a. One and Zeroes Padding
  A single set ('1') bit is added to the message and then as many reset ('0') bits as required (possibly none) are added.
  Input: (str) str - String to be padded
         (int) blocksize - block size of the algorithm
  Return: Padded string according to ANSI X.923 standart

  Used in when padding bit strings.
  0x80 in binary is 10000000
  0x00 in binary is 00000000

  Defined in ANSI X.923 (based on NIST Special Publication 800-38A) and ISO/IEC 9797-1 as Padding Method 2.
  Used in hash functions MD5 and SHA, described in RFC 1321 step 3.1.
  '''
  pad_len = paddingLength(len(str), blocksize) - 1
   
  padding = chr(0x80)+'\0'*pad_len
  
  return str + padding

def removeBitPadding(str, blocksize=AES_blocksize):
    'Remove bit padding with 0x80 followed by zero (null) bytes'
    pad_len = 0    
    for char in str[::-1]: # str[::-1] reverses string
        if char == '\0':
            pad_len += 1
        else:
            break
    pad_len += 1
    str = str[:-pad_len]
   
    return str

def appendZeroLenPadding(str, blocksize=AES_blocksize):
  'Pad with zeroes except make the last byte equal to the number of padding bytes'
  pad_len = paddingLength(len(str), blocksize) - 1
  
  padding = '\0'*pad_len+chr(pad_len)
  
  return str + padding

def removeZeroLenPadding(str, blocksize=AES_blocksize):
  'Remove Padding with zeroes + last byte equal to the number of padding bytes'
  try:
    pad_len = ord(str[-1]) # last byte contains number of padding bytes
  except TypeError:
    pad_len = str[-1]
  assert pad_len < blocksize, 'padding error' 
  assert pad_len < len(str), 'padding error'
    
  return str[:-pad_len]

def appendNullPadding(str, blocksize=AES_blocksize):
  'Pad with null bytes'
  pad_len = paddingLength(len(str), blocksize)

  padding = '\0'*pad_len
  
  return str + padding

def removeNullPadding(str, blocksize=AES_blocksize):
    'Remove padding with null bytes'
    pad_len = 0    
    for char in str[::-1]: # str[::-1] reverses string
        if char == '\0':
            pad_len += 1
        else:
            break
    str = str[:-pad_len]
    return str

def appendSpacePadding(str, blocksize=AES_blocksize):
  'Pad with spaces'
  pad_len = paddingLength(len(str), blocksize)
      
  padding = '\0'*pad_len
  
  return str + padding

def removeSpacePadding(str, blocksize=AES_blocksize):
    'Remove padding with spaces' 
    pad_len = 0    
    for char in str[::-1]: # str[::-1] reverses string
        if char == ' ':
            pad_len += 1
        else:
            break

    str = str[:-pad_len]
   
    return str

def appendRandomLenPadding(str, blocksize=AES_blocksize):
  'ISO 10126 Padding (withdrawn, 2007): Pad with random bytes + last byte equal to the number of padding bytes'
  pad_len = paddingLength(len(str), blocksize) - 1
  
  from os import urandom
  
  padding = urandom(pad_len)+chr(pad_len)
  
  return str + padding

def removeRandomLenPadding(str, blocksize=AES_blocksize):
  'ISO 10126 Padding (withdrawn, 2007): Remove Padding with random bytes + last byte equal to the number of padding bytes'
  pad_len = ord(str[-1]) # last byte contains number of padding bytes
  assert pad_len < blocksize, 'padding error' 
  assert pad_len < len(str), 'padding error'
    
  return str[:-pad_len]
  
def TestPadding(str, blocksize=AES_blocksize):
    'Test adding and removing padding'
    from hashlib import sha1
    
    str_hash = sha1(str).hexdigest()
    str = appendPadding(str)
    str = removePadding(str)
    if sha1(str).hexdigest() == str_hash:
        return True
    else:
        return False

'Padding modes'
MODES ={
        (0,'CMS')     : 'Cryptographic Message Syntax (CMS as defined in RFC 5652, PKCS#5, PKCS#7 and RFC 1423 PEM): Pad with bytes all of the same value as the number of padding bytes',
        (1,'Bit')     : 'ANSI X.923 and ISO/IEC 9797-1: BitPadding: Pad with 0x80 (10000000) followed by zero (null) bytes',
        (2,'ZeroLen') : 'Pad with zeroes except make the last byte equal to the number (length) of padding bytes',
        (3,'Null')    : 'Pad with null bytes. Only for encrypting of text data.',
        (4,'Space')   : 'Pad with spaces. Only for encrypting of text data.',
        (5,'Random')  : 'ISO 10126 Padding (withdrawn in 2007): Pad with random bytes + last byte equal to the number of padding bytes'         
       }

def appendPadding(str, blocksize=AES_blocksize, mode='CMS'):
  ''' Pad (append padding to) string for use with symmetric encryption algorithm
    Input: (string) str - String to be padded
           (int)    blocksize - block size of the encryption algorithm
           (string) mode - padding scheme one in (CMS, Bit, ZeroLen, Null, Space, Random)
    Return:(string) Padded string according to chosen padding mode
  '''
  if mode not in (0,'CMS'):     
    for k in MODES.keys():
        if mode in k:
            return globals()['append'+k[1]+'Padding'](str, blocksize) 
        else:
            return appendCMSPadding(str, blocksize)
  else:
      return appendCMSPadding(str, blocksize)        

def removePadding(str, blocksize=AES_blocksize, mode='CMS'):
  ''' Remove padding from string 
  Input: (str) str - String to be padded
         (int) blocksize - block size of the algorithm
         (string) mode - padding scheme one in (CMS, Bit, ZeroLen, Null, Space, Random)
  Return:(string) Decrypted string without padding 
    '''    
  if mode not in (0,'CMS'):     
    for k in MODES.keys():
        if mode in k:
            return globals()['append'+k[1]+'Padding'](str, blocksize)
        else:
            return removeCMSPadding(str, blocksize)
  else:
      return removeCMSPadding(str, blocksize)        
        

'''Resources on Padding: 
Standarts:
    RFC 5652 (CMS) section 6.3.; http://www.ietf.org/rfc/rfc5652.txt
    PKCS#7 (CMS) section 10.3 (Note2) ftp://ftp.rsasecurity.com/pub/pkcs/ascii/pkcs-7.asc  
    PKCS#5 section 6.1.1 p.4, 
    RFC 1423 (PEM) section 1.1

'''
        
     