# OpenURL Batch Creation with Python
This is a repository for working on converting a bash process to  Python in order to make large batches of OpenURLs using exported bibliographic data.

## backstory
In 2022, our library implemented Aeon for Special Collections requests, but we didn't have a link resolver and somehow the implementation team failed to communicate that it would be necessary. I wasn't directly involved in the project, but I volunteered to search for alternative OpenURL creation methods because I knew that if we could create them we could overlay them into bib records. 

I initially developed a multi-step process for doing this with Bash, with a colossal assist from NYPL's late systems analyst Aaron Dabbah, who developed his own process for NYPL and generously shared his code with me.

My process was messy, especially because I had to teach myself a lot of Bash and command line skills, but (eventually) worked. However, I believe it can be done much more elegantly and in fewer steps with Python. 

I know a tiny bit of Python but have primarily been using AI tools to work on converting my bash scripts. I expect I'll want to review them with human colleagues eventually, but the stakes are pretty low right now.

## current status
I need to review where I'm at with the python as it currently stands.
Once that's working, I need to test it with some other bib records than the ones I've started with. 

* consider setting up gitignore for files: bib.txt, input.mrc, and output.mrc





