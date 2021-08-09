# Usage

## Starting the Server

When you run `Storytime`, several things happen:

- The target directory is scanned for story information
- The output directory is created, if necessary
- The static assets are copied to the output directory, if necessary
- All the HTML for the stories is written
- The server starts up.

```{eval-rst}
.. click:: storytime.__main__:main
   :prog: storytime
   :nested: full
```
