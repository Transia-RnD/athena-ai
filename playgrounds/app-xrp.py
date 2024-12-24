#!/usr/bin/env python
# coding: utf-8

# from athenah_ai.indexer import AthenahIndexer

# path: str = "/Users/darkmatter/projects/ledger-works/app-xrp"
# indexer = AthenahIndexer("local", "id", "dist", "app-xrp", "v1")
# indexer.index_dir(path, ["src"], "app-xrp")

from athenah_ai.client import AthenahClient

prompt: str = """
I was asked to add a null reference check to the fmt.c file format_field function.

Will this work? Is there a better way to do it? Should I do dst->buf?

```
if (field == NULL || dst == NULL) {
    return;
}
```

"""
client = AthenahClient("id", "dist", "app-xrp")
response = client.prompt(prompt)
print(response)
