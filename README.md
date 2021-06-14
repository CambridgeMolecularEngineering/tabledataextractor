# TableDataExtractor
Extracts data from tables with complicated structures, by standardizing the table.

## Documentation
https://cambridgemolecularengineering-tabledataextractor.readthedocs-hosted.com/en/latest/

## License

The MIT License (MIT)

Copyright © 2019 Juraj Mavračić and contributors

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated 
documentation files (the “Software”), to deal in the Software without restriction, 
including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, 
and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, 
subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, 
INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. 
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, 
WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE 
OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

## Acknowledgements

Core algorithms used and modified in *TableDataExtractor* have originally been developed by Embley et al.
This is the MIPS (*Minimum Indexing Point Search*) algorithm that is used to find the row/column headers
and the data region, as well as algorithms for prefixing header cells. Also, some of the examples in this documentation
are based on examples from Embley et al:

    Embley, D.W., Krishnamoorthy, M.S., Nagy, G., and Seth, S. (2016) Converting heterogeneous statistical tables on the web to searchable databases. *Int. J. Doc. Anal. Recognit.*, *19* (2), 119–138.

Algorithms for duplicating spanning cells and extending headers, that are used in *TableDataExtractor*,
have been developed by Nagy and Seth:

    Nagy, G., and Seth, S. (2017) Table headers: An entrance to the data mine. *Proc. - Int. Conf. Pattern Recognit.*, 4065–4070.

The algorithm for converting `html` files to `Numpy arrays` has been modified from John Rico:

    John Ricco, (2017) Using Python to scrape HTML tables with merged cells, https://johnricco.github.io/2017/04/04/python-html/

Please cite these works where appropriate.
