- The following existing test files in the codebase cover the functionality described in the Consensus_Amendments lesson:

1. `/Users/darkmatter/projects/transia/athena-ai/dist/rippled-ai-core/rippled-ai-core-source/src/test/app/Amendment_test.cpp`
   - This file contains tests that directly exercise the amendment process, including registration, voting, activation, and edge cases.

2. `/Users/darkmatter/projects/transia/athena-ai/dist/rippled-ai-core/rippled-ai-core-source/src/test/app/AmendmentTable_test.cpp`
   - This file tests the internal logic of the AmendmentTable, including state management, voting, persistence, and JSON representation.

3. `/Users/darkmatter/projects/transia/athena-ai/dist/rippled-ai-core/rippled-ai-core-source/src/test/app/Change_test.cpp`
   - This file covers the application of amendment pseudo-transactions to the ledger, including enabling amendments and handling operational consequences.

4. `/Users/darkmatter/projects/transia/athena-ai/dist/rippled-ai-core/rippled-ai-core-source/src/test/rpc/Feature_test.cpp`
   - This file tests the RPC/admin interface for querying and managing amendment state.

These test files collectively cover the core Consensus_Amendments functionality, including amendment registration, voting, consensus integration, ledger application, persistence, RPC/admin interface, and operational edge cases, as described in the lesson.