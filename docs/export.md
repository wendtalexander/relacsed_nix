# Exporting file content to pandas

Exploration is fine but too slow for use in-production. Upon creation of a ``rlxnix.Dataset`` object, it will scan and index the file content. Even though there are some buffering mechanisms, crawling the file takes time and processing data from tens or hundreds of file will be slowed down considerably.

