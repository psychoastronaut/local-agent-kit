# wordstat

Count word frequencies in text files.

    python -m wordstat FILE [FILE ...]

Output is one `word count` line per word, most frequent first, ties broken alphabetically.
Words are lowercase runs of letters/apostrophes. Reads stdin when FILE is `-`.
