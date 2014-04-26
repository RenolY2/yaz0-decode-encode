yaz0-decode-encode
==================

A module written in Python that provides yaz0-compatible compression and decompression methods written by RenolY2/Yoshi2.

Notes
==================
Please note that this module still needs to undergo broad testing. While I did
personally test the module myself, there can still be some special cases which
I haven't accounted for yet. If you do encounter issues, don't hesitate to report it
and include a description of what file is causing the problem so that I can fix it.

I used the specifications at http://www.amnoid.de/gc/yaz0.txt to write an
encoder for the format.

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
