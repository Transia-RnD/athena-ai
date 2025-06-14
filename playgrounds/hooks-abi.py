#!/usr/bin/env python
# coding: utf-8

# from athenah_ai.indexer import AthenahIndexer

# path: str = "/Users/darkmatter/projects/ledger-works/hooks-toolkit-ts"
# indexer = AthenahIndexer("local", "id", "dist", "hooks-abi", "v1")
# indexer.build_from_dirs(
#     path,
#     ["contracts-c"],
#     "hooks-abi",
# )

from athenah_ai.client import AthenahClient

prompt: str = """
```hook.dcmp
memory M_a(initial: 2, max: 0);

global g_a:int = 1024;
global g_b:int = 1074;
global g_c:int = 1024;
global g_d:int = 66624;
global g_e:int = 0;
global g_f:int = 1;

data d_BasecCalledbaseFinishedBasec(offset: 1024) =
"Base.c: Called.\00base: Finished.\00\22Base.c: Called.\22";

import function env_trace(a:int, b:int, c:int, d:int, e:int):long; // func0

import function env_g(a:int, b:int):int; // func1

import function env_accept(a:int, b:int, c:long):long; // func2

export function hook(a:int):long { // func3
  env_trace(1056, 17, 1024, 16, 0);
  env_g(1, 1);
  return env_accept(1040, 16, 9L);
}
```

Convert the dcmp back into a c hook using the #include "hookapi.h".

When compiling the hook we use the macro.h file. Convert the env_ functions back to the macros.
"""
client = AthenahClient("id", "dist", "hooks-abi")
response = client.promptv1(prompt)
print(response)
