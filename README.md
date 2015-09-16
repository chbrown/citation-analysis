# citation-analysis

Citation analysis tools.

Develop:

    git clone https://github.com/chbrown/citation-analysis.git
    cd citation-analysis
    python setup.py develop

Use:

    import pycite
    print pycite.__version__

    from pycite import search
    def read_documents():
        for i, line in enumerate(open('data.csv')):
            yield i, line.split()
    inverted_index = search.InvertedIndex.from_documents(read_documents())


## License

Copyright 2015 Christopher Brown. [MIT Licensed](http://chbrown.github.io/licenses/MIT/#2015).
