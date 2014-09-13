
# This file tests the helper functions of the
# yaz0 module. The goal is to quickly make sure that the module
# is working correctly, and if not, find ways to reliably 
# break it so that a solution can be found.

import random
import string
import traceback

from cStringIO import StringIO

from yaz0 import (compress, decompress,
                  compress_fileobj, decompress_fileobj,
                  compress_file, decompress_file)

# These filenames will be used to test the compress_file
# and decompress_file functions.
inputFilename = "__test_data.txt"
compressedFilename = "__test_data_compressed.txt"
decompressedFilename = "__test_data.decompressed.txt"

dont_show_success_msg = False

# This function creates random data for proper testing of the compress
# and decompress features of the module.
#
# The 'repeat' argument specifies how many times a single character should be 
# repeated in a row, mimicing data that can be compressed well.
#
# The 'repeatRandom' flag, when set to True, specifies that characters
# should be repeated a random number of times between 1 and the integer defined
# by 'repeat'
def create_random_data(charSet, dataLen, repeat = 1, repeatRandom = False):
    data = StringIO()
    
    for i in xrange(dataLen):
        char = random.choice(charSet)
        if repeatRandom == True:
            repeat_random = random.randint(1, repeat)
            data.write(char*repeat_random)
        else:
            data.write(char*repeat)
    
    return data.getvalue()

for i in xrange(100):
    data = create_random_data(string.ascii_lowercase, 100, repeat = 10, repeatRandom = True)
    
    try:
        # Test 1: Test compression and decompression of strings.
        compressed_data = compress(data, 9)
        decompressed_data = decompress(compressed_data)
        
        assert data == decompressed_data
        
        # Test 2: Test compression and decompression of content in file-like objects.
        fileobj = StringIO(data)
        compressed_fileobj_data = compress_fileobj(fileobj, 9)
        decompressed_fileobj_data = decompress_fileobj(compressed_fileobj_data)
        
        assert data == decompressed_fileobj_data.getvalue()
        
        # Test 3: Test compression and decompression of content located in a file.
        with open(inputFilename, "w") as f:
            f.write(data)
        compress_file(inputFilename, outputPath = compressedFilename, compressLevel = 9)
        decompress_file(compressedFilename, outputPath = decompressedFilename)
        
        with open(decompressedFilename) as f:
            decompressed_data = f.read()
            
        assert data == decompressed_data
    except:
        traceback.print_exc()
        dont_show_success_msg = True
        
        with open("_error_string.txt", "w") as f:
            f.write(data)
        
        print "-----------------------------"
        print "The string that caused this error"    
        print "has been written to '_error_string.txt'"
        print "for reference."
        
        break

if dont_show_success_msg == False:
    # If you see this message, that means no exceptions 
    # were raised and the tests were successful.
    print "\n---------------------------\n"
    print "All tests were successful!"