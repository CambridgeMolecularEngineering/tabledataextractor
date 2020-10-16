Acknowledgements
======================

| **TableDataExtractor**
| Molecular Engineering Group
| Cavendish Laboratory,
| University of Cambridge

This software was written by Juraj Mavračić supported by a grant from the UK Engineering and Physical Sciences Research Council (EPSRC) EP/L015552/1 for the Centre for Doctoral Training (CDT) in Computational Methods for Materials Science.

It forms part of a PhD project supervised by Jacqueline M. Cole and Stephen R. Elliott. The PhD was completed in the Molecular Engineering Group at the University of Cambridge, which is financially supported by the Engineering and Physical Sciences Research Council (EPSRC, EP/L015552/1), Science and Technology Facilities Council (STFC) and the Royal Academy of Engineering (RCSRF1819710).


Some algorithms used and modified in *TableDataExtractor* have been originally developed by Embley et al.
This is the MIPS (*Minimum Indexing Point Search*) algorithm that is used to find the row/column headers
and the data region, as well as algorithms for prefixing header cells:

    Embley, D.W., Krishnamoorthy, M.S., Nagy, G., and Seth, S. (2016) Converting heterogeneous statistical tables on the web to searchable databases. *Int. J. Doc. Anal. Recognit.*, *19* (2), 119–138.

Algorithms for duplicating spanning cells and extending headers, that are used in *TableDataExtractor*,
have been developed by Nagy and Seth:

    Nagy, G., and Seth, S. (2017) Table headers: An entrance to the data mine. *Proc. - Int. Conf. Pattern Recognit.*, 4065–4070.

The algorithm for converting `html` files to `Numpy arrays` has been modified from John Rico:

    John Ricco, (2017) Using Python to scrape HTML tables with merged cells, https://johnricco.github.io/2017/04/04/python-html/



