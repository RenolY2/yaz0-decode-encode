yaz0-decode-encode
==================

A module written in Python that provides yaz0-compatible compression and decompression methods.


Usage
==================

Decompression of a yaz0-compressed file:
'''
fileobj = open("compressed.dat", "rb")
yazObj = yaz0(fileobj)
output = yazObj.decompress()
fileobj.close()
        
writefile = open("decompressed.dat", "wb")
writefile.write(output.getvalue())
writefile.close()

'''

Compression of a file:
'''
fileobj = open("decompressed.dat", "rb")
yazObj = yaz0(fileobj, compress = True)
output = yazObj.compress(compressLevel = 9)
fileobj.close()
        
writefile = open("compressed.dat", "wb")
writefile.write(output.getvalue())
'''
