#!/usr/bin/env python
# coding: utf-8

from athenah_ai.indexer import AthenahIndexer

# path: str = "/Users/darkmatter/projects/ledger-works/rippled"
# indexer = AthenahIndexer("local", "id", "dist", "rippled-firewall", "v1")
# indexer.build_from_dirs(
#     path,
#     ["include", "src/libxrpl", "src/test", "src/xrpld"],
#     True,
# )

from athenah_ai.client import AthenahClient

prompt: str = """
```
TER
accountRootFirewallRule(
    ApplyView& view,
    SLE::pointer const& sleFirewall,
    STObject const& rule,
    std::shared_ptr<SLE const> const& before,
    std::shared_ptr<SLE const> const& after)
{
    bool const hasTimeLimit = rule.isFieldPresent(sfTimePeriod) &&
        rule.isFieldPresent(sfTimeStart) && rule.isFieldPresent(sfTimeAmount);
    auto const fieldCode = rule.getFieldU32(sfFieldCode);
    SField const& fieldType = ripple::SField::getField(fieldCode);
    if (!before->isFieldPresent(fieldType) || !after->isFieldPresent(fieldType))
    {
        std::cout << "checkFirewall: Field not found" << std::endl;
        return tesSUCCESS;
    }

    auto const& beforeField = before->getField(fieldType);
    auto const& afterField = after->getField(fieldType);
    bool const isDecrease = afterField < beforeField;

    if (hasTimeLimit)
    {
        // Firewall with time period and amount limit
        std::uint32_t const currentTime =
            view.parentCloseTime().time_since_epoch().count();
        std::uint32_t const startTime = rule.getFieldU32(sfTimeStart);
        std::uint32_t const timePeriod = rule.getFieldU32(sfTimePeriod);
        STAmount total = rule.getFieldAmount(sfTimeAmount);

        // Check if the monitoring period has expired
        if (startTime == 0 || (currentTime - startTime > timePeriod))
        {
            // Reset the monitoring period
            resetFirewallOutgoingTimer(view, sleFirewall, currentTime);
            total = isDecrease ? beforeField - afterField
                               : afterField - beforeField;
        }
        else
        {
            // Add the transaction amount to the ongoing total
            total += isDecrease ? beforeField - afterField
                                : afterField - beforeField;
        }

        // Check if the transaction amount exceeds the firewall
        // limit
        if (total <= rule.getFieldAmount(sfAmount))
        {
            updateFirewallOutgoingTotal(view, sleFirewall, total);
            return tesSUCCESS;
        }
    }
    else
    {
        // Firewall with amount limit
        if (isDecrease &&
            beforeField - afterField <= rule.getFieldAmount(sfAmount))
            return tesSUCCESS;
    }
    return tecFIREWALL_BLOCK;
}
```

ment_type' (aka 'const ripple::STLedgerEntry'), but function is not marked const
    auto const& beforeField = before->getField(fieldType);
                              ^~~~~~~~
/Users/darkmatter/projects/ledger-works/rippled/include/xrpl/protocol/STObject.h:206:5: note: 'getField' declared here
    getField(SField const& field);
    ^
/Users/darkmatter/projects/ledger-works/rippled/src/xrpld/app/tx/detail/Transactor.cpp:514:30: error: 'this' argument to member function 'getField' has type 'std::shared_ptr<const ripple::STLedgerEntry>::element_type' (aka 'const ripple::STLedgerEntry'), but function is not marked const
    auto const& afterField = after->getField(fieldType);
                             ^~~~~~~
/Users/darkmatter/projects/ledger-works/rippled/include/xrpl/protocol/STObject.h:206:5: note: 'getField' declared here
    getField(SField const& field);

We cannot update the getField function

"""
client = AthenahClient("id", "dist", "rippled-firewall")
response = client.promptv1(prompt)
print(response)
