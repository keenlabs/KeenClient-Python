import binascii
import json
import os
from Crypto.Cipher import AES

from keen import Padding

__author__ = 'dkador'

# the block size for the cipher object; must be 16, 24, or 32 for AES
OLD_BLOCK_SIZE = 32


def pad_aes256(s):
    """
    Pads an input string to a given block size.
    :param s: string
    :returns: The padded string.
    """
    if len(s) % AES.block_size == 0:
        return s

    return Padding.appendPadding(s, blocksize=AES.block_size)


def unpad_aes256(s):
    """
    Removes padding from an input string based on a given block size.
    :param s: string
    :returns: The unpadded string.
    """
    if not s:
        return s

    try:
        return Padding.removePadding(s, blocksize=AES.block_size)
    except AssertionError:
        # if there's an error while removing padding, just return s.
        return s


def old_pad(s):
    """
    Pads an input string to a given block size.
    :param s: string
    :returns: The padded string.
    """
    if len(s) % OLD_BLOCK_SIZE == 0:
        return s

    return Padding.appendPadding(s, blocksize=OLD_BLOCK_SIZE)


def old_unpad(s):
    """
    Removes padding from an input string based on a given block size.
    :param s: string
    :returns: The unpadded string.
    """
    if not s:
        return s

    try:
        return Padding.removePadding(s, blocksize=OLD_BLOCK_SIZE)
    except AssertionError:
        # if there's an error while removing padding, just return s.
        return s


# encrypt with AES-256-CBC, encode with hex
def encode_aes256(key, plaintext):
    """
    Utility method to encode some given plaintext with the given key. Important thing to note:

    This is not a general purpose encryption method - it has specific semantics (see below for
    details).

    Takes the given hex string key and converts it to a 256 bit binary blob. Then pads the given
    plaintext to AES block size which is always 16 bytes, regardless of AES key size. Then
    encrypts using AES-256-CBC using a random IV. Then converts both the IV and the ciphertext
    to hex. Finally returns the IV appended by the ciphertext.

    :param key: string, 64 hex chars long
    :param plaintext: string, any amount of data
    """
    if len(key) != 64:
        raise TypeError("encode_aes256() expects a 256 bit key encoded as a 64 hex character string")

    # generate AES.block_size cryptographically secure random bytes for our IV (initial value)
    iv = os.urandom(AES.block_size)
    # set up an AES cipher object
    cipher = AES.new(binascii.unhexlify(key.encode('ascii')), mode=AES.MODE_CBC, IV=iv)
    # encrypt the plaintext after padding it
    ciphertext = cipher.encrypt(pad_aes256(plaintext))
    # append the hexed IV and the hexed ciphertext
    iv_plus_encrypted = binascii.hexlify(iv) + binascii.hexlify(ciphertext)
    # return that
    return iv_plus_encrypted


def decode_aes256(key, iv_plus_encrypted):
    """
    Utility method to decode a payload consisting of the hexed IV + the hexed ciphertext using
    the given key. See above for more details.

    :param key: string, 64 hex characters long
    :param iv_plus_encrypted: string, a hexed IV + hexed ciphertext
    """
    # grab first AES.block_size bytes (aka 2 * AES.block_size characters of hex) - that's the IV
    iv_size = 2 * AES.block_size
    hexed_iv = iv_plus_encrypted[:iv_size]
    # grab everything else - that's the ciphertext (aka encrypted message)
    hexed_ciphertext = iv_plus_encrypted[iv_size:]
    # unhex the iv and ciphertext
    iv = binascii.unhexlify(hexed_iv)
    ciphertext = binascii.unhexlify(hexed_ciphertext)
    # set up the correct AES cipher object
    cipher = AES.new(binascii.unhexlify(key.encode('ascii')), mode=AES.MODE_CBC, IV=iv)
    # decrypt!
    plaintext = cipher.decrypt(ciphertext)
    # return the unpadded version of this
    return unpad_aes256(plaintext)


def old_encode_aes(key, plaintext):
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
    cipher = AES.new(old_pad(key), mode=AES.MODE_CBC, IV=iv)
    # encrypte the plaintext after padding it
    ciphertext = cipher.encrypt(old_pad(plaintext))
    # append the hexed IV and the hexed ciphertext
    iv_plus_encrypted = binascii.hexlify(iv) + binascii.hexlify(ciphertext)
    # return that
    return iv_plus_encrypted


def old_decode_aes(key, iv_plus_encrypted):
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
    cipher = AES.new(old_pad(key), mode=AES.MODE_CBC, IV=iv)
    # decrypt!
    plaintext = cipher.decrypt(ciphertext)
    # return the unpadded version of this
    return old_unpad(plaintext)


def encrypt(api_key, options):
    options_string = json.dumps(options)
    if len(api_key) == 64:
        return encode_aes256(api_key, options_string)
    else:
        return old_encode_aes(api_key, options_string)


def decrypt(api_key, scoped_key):
    if len(api_key) == 64:
        json_string = decode_aes256(api_key, scoped_key)
    else:
        json_string = old_decode_aes(api_key, scoped_key)
    try:
        return json.loads(json_string)
    except TypeError:
        return json.loads(json_string.decode())
