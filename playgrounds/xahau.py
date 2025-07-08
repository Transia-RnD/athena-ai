#!/usr/bin/env python
# coding: utf-8

AGENT_MODEL = "claude-4-sonnet-20250514"
ATHENAH_CLIENT_NAME: str = "xahaud"


def main():
    # from athenah_ai.indexer import AthenahIndexer

    # path: str = "/Users/darkmatter/projects/ledger-works/xahaud"
    # indexer = AthenahIndexer("local", "id", "dist", "xahaud", "v1")
    # indexer.build_from_dirs(
    #     path, ["src/ripple/app", "src/ripple/protocol"], False, False
    # )

    from athenah_ai.client import AthenahClient

    ai_source: AthenahClient = AthenahClient(
        "id",
        provider="openai",
        model_group="dist",
        custom_model=ATHENAH_CLIENT_NAME,
        version="v1",
        model_name="gpt-4.1",
        best_of=3,
    )
    system_prompt: str = """
/Users/runner/work/xahaud/xahaud/src/ripple/app/tx/impl/InvariantCheck.cpp:696:41: error: no matching member function for call to 'at'
  696 |         possibleIssuers_.emplace(after->at(sfAccount), after);
      |                                  ~~~~~~~^~
/Users/runner/work/xahaud/xahaud/src/ripple/protocol/STObject.h:1020:11: note: candidate function template not viable: no known conversion from 'element_type' (aka 'const ripple::STLedgerEntry') to 'ripple::STObject' for object argument
 1020 | STObject::at(TypedField<T> const& f) -> ValueProxy<T>
      |           ^
/Users/runner/work/xahaud/xahaud/src/ripple/protocol/STObject.h:973:11: note: candidate template ignored: substitution failure [with T = ripple::STAccount]: incomplete type 'ripple::STAccount' named in nested name specifier
  972 | typename T::value_type
      |          ~
  973 | STObject::at(TypedField<T> const& f) const
      |           ^
/Users/runner/work/xahaud/xahaud/src/ripple/protocol/STObject.h:1000:11: note: candidate template ignored: could not match 'OptionaledField' against 'TypedField'
 1000 | STObject::at(OptionaledField<T> const& of) const
      |           ^
/Users/runner/work/xahaud/xahaud/src/ripple/protocol/STObject.h:1027:11: note: candidate template ignored: could not match 'OptionaledField' against 'TypedField'
 1027 | STObject::at(OptionaledField<T> const& of) -> OptionalProxy<T>
      |           ^
/Users/runner/work/xahaud/xahaud/src/ripple/app/tx/impl/InvariantCheck.cpp:811:25: error: no matching member function for call to 'at'
  811 |                 issuer->at(sfAccount);
      |                 ~~~~~~~~^~
/Users/runner/work/xahaud/xahaud/src/ripple/protocol/STObject.h:1020:11: note: candidate function template not viable: no known conversion from 'element_type' (aka 'const ripple::STLedgerEntry') to 'ripple::STObject' for object argument
 1020 | STObject::at(TypedField<T> const& f) -> ValueProxy<T>
      |           ^
/Users/runner/work/xahaud/xahaud/src/ripple/protocol/STObject.h:973:11: note: candidate template ignored: substitution failure [with T = ripple::STAccount]: incomplete type 'ripple::STAccount' named in nested name specifier
  972 | typename T::value_type
      |          ~
  973 | STObject::at(TypedField<T> const& f) const
      |           ^
/Users/runner/work/xahaud/xahaud/src/ripple/protocol/STObject.h:1000:11: note: candidate template ignored: could not match 'OptionaledField' against 'TypedField'
 1000 | STObject::at(OptionaledField<T> const& of) const
      |           ^
/Users/runner/work/xahaud/xahaud/src/ripple/protocol/STObject.h:1027:11: note: candidate template ignored: could not match 'OptionaledField' against 'TypedField'
 1027 | STObject::at(OptionaledField<T> const& of) -> OptionalProxy<T>

"""

    user_input: str = """
Fix the above error
"""
    response = ai_source.rag_prompt_v2(system_prompt, user_input)
    print(response)
    # write to a file
    with open("response.txt", "w") as f:
        f.write(response)


main()
