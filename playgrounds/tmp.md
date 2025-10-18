RCLConsensus::Adaptor::preStartRound: PreStart
Consensus<Adaptor>::startRound: Start New Consensus Round
Consensus<Adaptor>::startRoundInternal: ConsensusPhase::open
- playbackProposals: Start Playing Back Peer Proposals
- Consensus<Adaptor>::timerEntry:
    - Consensus<Adaptor>::checkLedger: get previous ledger, handle wrong ledger
        - adaptor_.getPrevLedger
        - handleWrongLedger
        - void
    - Consensus<Adaptor>::phaseOpen: Determins if we should close the ledger based on last ledger time
        - shouldCloseLedger: Should we close the consensus round?
            - Consensus<Adaptor>::closeLedger: Closes the ledger
    - Consensus<Adaptor>::phaseEstablish
        - Consensus<Adaptor>::updateOurPositions
        - RCLConsensus::Adaptor::onAccept
            - RCLConsensus::Adaptor::buildLCL
            - LedgerMaster::consensusBuilt
            - Apply disputed transactions that didn't get in
        - RCLConsensus::Adaptor::doAccept
            - RCLConsensus::Adaptor::buildLCL
            - BuildLedger::buildLedger
            - app_.getTxQ().processClosedLedger
        - NetworkOPsImp::endConsensus
            - setMode
        - NetworkOPsImp::beginConsensus
            - NetworkOPsImp::reportConsensusStateChange
            - RCLConsensus::startRound