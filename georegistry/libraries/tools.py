'General purpose tools'
import re
import random
from Crypto.Cipher import AES


alphabet = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
secret = alphabet # Please set this in .development.ini or .production.ini


def encrypt(string):
    'Encrypt string'
    return AES.new(secret[:32], AES.MODE_CFB).encrypt(string.encode('utf-8'))


def decrypt(string):
    'Decrypt string'
    return AES.new(secret[:32], AES.MODE_CFB).decrypt(string).decode('utf-8')


def make_random_string(length):
    'Return a random string of a specified length'
    return ''.join(random.choice(alphabet) for x in xrange(length))


def make_random_unique_string(length, is_unique):
    'Return a random string given a function that checks for uniqueness'
    # Initialize
    iterationCount = 0
    permutationCount = len(alphabet) ** length
    while iterationCount < permutationCount:
        # Make randomID
        randomID = make_random_string(length)
        iterationCount += 1
        # If our randomID is unique, return it
        if is_unique(randomID):
            return randomID
    # Raise exception if we have no more permutations left
    raise RuntimeError('Could not create a unique string')


def get_remote_ip(request):
    'Return IP address of client'
    return request.environ.get('HTTP_X_REAL_IP', 
           request.environ.get('HTTP_X_FORWARDED_FOR',
           request.environ.get('REMOTE_ADDR')))


def get_token(body):
    match = re.search("token = '(.*)'", body)
    return match.group(1) if match else ''
