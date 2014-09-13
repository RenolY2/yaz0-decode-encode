yaz0-decode-encode
==================

A module written in Python that provides yaz0-compatible compression and decompression methods written by RenolY2/Yoshi2.

Notes
==================
Please note that this module still needs to undergo broad testing. While I did
personally test the module myself, there can still be some special cases which
I haven't accounted for yet. If you do encounter issues, don't hesitate to report it
and include a description of what file is causing the problem so that I can fix it.

I used the specifications at http://www.amnoid.de/gc/yaz0.txt to write a decoder for the format.

Usage
==================
The yaz0 class accepts a file-like object for the input and output. When creating
a new yaz0 instance, specifying an output object is not necessary. A cStringIO.StringIO
object will be created and returned when you use the compress or decompress methods. 
Otherwise, the output object you specified will be returned.

By default, the yaz0 instance is set to decompression. You need to set compress = True
when creating a new yaz0 instance to compress a file.

If you want to use your own output object, for decompression you need to provide a file-like
object that supports both writing and reading at the same time. For compression, you only need
a file-like object that supports writing.

Example of how a yaz0 file can be decompressed:
```python
from yaz0 import yaz0

# Very important: Open file in binary mode
fileobj = open("yaz0_file", "rb")

yazObj = yaz0(inputobj = fileobj, outputobj = None, compress = False) #
output = yazObj.decompress() # We receive a cStringIO object

fileobj.close()

# Again, very important: open file in binary mode, otherwise
# random bytes will appear in the file and make the file invalid.
writefile = open("decompressed_file", "wb")
writefile.write(output.getvalue())
writefile.close()

```

Example of how a file can be compressed:
```python
from yaz0 import yaz0

fileobj = open("decompressed_file", "rb")

yazObj = yaz0(fileobj, outputobj = None, compress = True)

# We can specify a compressLevel. It can be anything from 0 to 9,
# even floats are accepted. Higher means better compression and
# longer compression times, lower means worse but faster compression.
output = yazObj.compress(compressLevel = 9)
fileobj.close()


writefile = open("yaz0_file", "wb")
writefile.write(output.getvalue())
writefile.close()
```


It is also possible to use the helper functions provided
by the yaz0 module for compression and decompression.
The following code will make use of the 6 helper methods
(3 for compression, 3 for decompression) provided by the module:

```python
import yaz0
from cStringIO import StringIO

# Data with a lot of repeated characters can be compressed well.
testData = "A"*64

# Method 1&2: Using compress and decompress, which work on strings directly:
compressedData = yaz0.compress(testData, compressLevel = 9)
decompressedData = yaz0.decompress(compressedData)

# We need to make sure that the decompressed data 
# now is the same as the original data.
assert decompressedData == testData 

# Method 3&4: Using compress_fileobj and decompress_fileobj, which work on file-like objects:
test_fileObj = StringIO(testData)

compressedData_obj = yaz0.compress_fileobj(test_fileObj, compressLevel = 9)
decompressedData_obj = yaz0.decompress_fileobj(compressedData_obj)

decompressedData = decompressedData_obj.getvalue() 
assert decompressedData == testData

# Method 5&6: Using compress_file and decompress_file, which work on file on the HDD:
# If you omit the outputPath for compress_file and decompress_file, the functions
# will return a StringIO object instead of writing the results to a file.

# First we create our test file using the test data.
with open("uncompressedData.txt", "w") as f:
    f.write(testData)

yaz0.compress_file("uncompressedData.txt", outputPath = "compressedData.bin", 
                   compressLevel = 9)

yaz0.decompress_file("compressedData.bin", outputPath = "uncompressedData2.txt")


# Again, we make sure that the content of the decompressed file is the same as 
# the original data.
with open("uncompressedData2.txt", "r") as f:
    decompressedData = f.read()

assert decompressedData == testData

print "If you see this message, everything went fine! :)"

```

					
	


Performance Statistics
==================

In the following statistics a file has been extracted from Zelda: The Wind Waker and decompressed.
Its decompressed size is 13.875 KiB (14208 bytes). It is compressed again using both the python implementation of yaz0, and python's built-in zlib module, using the highest compression level. This allows us to roughly compare the performance of both modules. Finally, the same compressed data will be decompressed again.
Time taken is rounded to the third place after the decimal point for yaz0, and to the fourth place after the decimal point for zlib.

--python yaz0--  
Time taken for compression: 1.358 seconds  
compressed size: ~9.32 KiB (9545 bytes)  
Time taken for decompression: 0.017 seconds  


--zlib--  
Time taken for compression: 0.0018 seconds  
compressed size: ~7.86 KiB (8048 bytes)  
Time taken for decompression: 0.0002 seconds  

For comparison, the original file in the game has a compressed size of ~9.1 KiB (9313 bytes), slightly better than the python implementation, but much worse than what zlib can achieve. As I am lacking statistics on how the yaz0 algorithm performs on the original hardware, it cannot be easily said that zlib is the clear winner.
There is very little point in using yaz0 for general purposes, but there is no way around it if you are dealing with modding for Nintendo games. At least one C implementation of the yaz0 algorithm exists if high performance is desired.


