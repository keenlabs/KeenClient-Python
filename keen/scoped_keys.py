import binascii
import json
import os
from Crypto.Cipher import AES

from keen import Padding

__author__ = 'dkador'

# the block size for the cipher object; must be 16, 24, or 32 for AES
BLOCK_SIZE = 32


def _pad(s):
    """
    Pads an input string to a given block size.
    :param s: string
    :returns: The padded string.
    """
    if len(s) % BLOCK_SIZE == 0:
        return s

    return Padding.appendPadding(s, blocksize=BLOCK_SIZE)


def _unpad(s):
    """
    Removes padding from an input string based on a given block size.
    :param s: string
    :returns: The unpadded string.
    """
    if not s:
        return s

    try:
        return Padding.removePadding(s, blocksize=BLOCK_SIZE)
    except AssertionError:
        # if there's an error while removing padding, just return s.
        return s


# encrypt with AES, encode with hex
def _encode_aes(key, plaintext):
    """
    Utility method to encode some given plaintext with the given key. Important thing to note:

    This is not a general purpose encryption method - it has specific semantics (see below for
    details).

    Takes the given key, pads it to 32 bytes. Then takes the given plaintext and pads that to a
    32 byte block size. Then encrypts using AES-256-CBC using a random IV. Then converts both the
    IV and the ciphertext to hex. Finally returns the IV appended by the ciphertext.

    :param key: string, <= 32 bytes long
    :param plaintext: string, any amount of data
    """
    # generate 16 cryptographically secure random bytes for our IV (initial value)
    iv = os.urandom(16)
    # set up an AES cipher object
    cipher = AES.new(_pad(key), mode=AES.MODE_CBC, IV=iv)
    # encrypte the plaintext after padding it
    ciphertext = cipher.encrypt(_pad(plaintext))
    # append the hexed IV and the hexed ciphertext
    iv_plus_encrypted = binascii.hexlify(iv) + binascii.hexlify(ciphertext)
    # return that
    return iv_plus_encrypted


def _decode_aes(key, iv_plus_encrypted):
    """
    Utility method to decode a payload consisting of the hexed IV + the hexed ciphertext using
    the given key. See above for more details.

    :param key: string, <= 32 bytes long
    :param iv_plus_encrypted: string, a hexed IV + hexed ciphertext
    """
    # grab first 16 bytes (aka 32 characters of hex) - that's the IV
    hexed_iv = iv_plus_encrypted[:32]
    # grab everything else - that's the ciphertext (aka encrypted message)
    hexed_ciphertext = iv_plus_encrypted[32:]
    # unhex the iv and ciphertext
    iv = binascii.unhexlify(hexed_iv)
    ciphertext = binascii.unhexlify(hexed_ciphertext)
    # set up the correct AES cipher object
    cipher = AES.new(_pad(key), mode=AES.MODE_CBC, IV=iv)
    # decrypt!
    plaintext = cipher.decrypt(ciphertext)
    # return the unpadded version of this
    return _unpad(plaintext)


def encrypt(api_key, options):
    options_string = json.dumps(options)
    return _encode_aes(api_key, options_string)


def decrypt(api_key, scoped_key):
    json_string = _decode_aes(api_key, scoped_key)
    return json.loads(json_string)