import os
from athenah_ai.client import AthenahClient

path = "/Users/darkmatter/projects/ledger-works/hook-docs/guides/api"

system: str = """
Here is the Page.tsx template:

```
export const metadata = {
  title: 'util_raddr',
  description:
    '',
}

# util_raddr

Convert a 20 byte Account ID to an r-address

## Behaviour

- Read a 20 byte Account ID from the read_ptr
- Write the equivalent r-address for that Account ID to write_ptr

---
<Row>
  <Col>

    ### Required attributes

    <Properties>
      <Property name="write_ptr" type="uint32_t">
        Pointer to a buffer of a suitable size to store the output r-address. Recommend at least 35 bytes.
      </Property>
      <Property name="write_len" type="uint32_t">
        Length of the output buffer.
      </Property>
      <Property name="read_ptr" type="uint32_t">
        Pointer to the Account ID.
      </Property>
      <Property name="read_len" type="uint32_t">
        The length of the input. Always 20.
      </Property>
    </Properties>
  </Col>
  <Col sticky>

    <CodeGroup title="util_raddr">

    ```bash {{ title: 'c' }}
    uint8_t raddr_out[40];
    uint8_t acc_id[20] =
    {
        0x2dU, 0xd8U, 0xaaU, 0xdbU, 0x4eU, 0x15U,               
        0xebU, 0xeaU,  0xeU, 0xfdU, 0x78U, 0xd1U, 0xb0U,
        0x35U, 0x91U,  0x4U, 0x7bU, 0xfaU, 0x1eU,  0xeU
    };
    int64_t bytes_written = 
        util_raddr(raddr_out, sizeof(raddr_out), acc_id, 20);
    ```
    </CodeGroup>
    ### Return Code `int64_t`

    The number of bytes written (the length of the output r-address).

    | Error Code           | Description                                                                            |
    | -------------------- | -------------------------------------------------------------------------------------- |
    | `OUT_OF_BOUNDS`      | Error code indicating pointers/lengths specified outside of hook memory.               |
    | `INVALID_ARGUMENT`   | Error code indicating read_len was not 20.                                             |
    | `TOO_SMALL`          | Error code indicating write_len was not large enough to store the produced r-address.  |
  </Col>
</Row>
---
```
"""
client = AthenahClient()


# for each file in the directory we need to make a new folder with name split('/')[-1] and then add a file called Page.tsx.
for file in os.listdir(path):
    if file.endswith(".md"):
        with open(os.path.join(path, file), "r") as f:
            content = f.read()
            prompt: str = f"""
            Use the template above to create a new `Page.tsx` for the following content:

            ```
            {content}
            ```
            """
            response = client.base_prompt(system=system, prompt=prompt)
            print(response)
            # save the response to the Page.tsx file in the new folder
            new_folder = os.path.join(path, file.split(".")[0])
            os.makedirs(new_folder, exist_ok=True)
            with open(os.path.join(new_folder, "Page.tsx"), "w") as f:
                f.write(response)
