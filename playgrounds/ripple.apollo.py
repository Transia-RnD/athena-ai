#!/usr/bin/env python
# coding: utf-8

# from athenah_ai.indexer import AthenahIndexer

# path: str = "/Users/darkmatter/projects/ledger-works/rippled"
# indexer = AthenahIndexer("local", "id", "dist", "rippled-apollo", "v1")
# indexer.build_from_dirs(
#     path,
#     ["include", "src/libxrpl", "src/test", "src/xrpld"],
#     False,
# )

from athenah_ai.client import AthenahClient

prompt: str = """
```
//------------------------------------------------------------------------------
/*
    This file is part of rippled: https://github.com/ripple/rippled
    Copyright (c) 2024 Ripple Labs Inc.

    Permission to use, copy, modify, and/or distribute this software for any
    purpose  with  or without fee is hereby granted, provided that the above
    copyright notice and this permission notice appear in all copies.

    THE  SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
    WITH  REGARD  TO  THIS  SOFTWARE  INCLUDING  ALL  IMPLIED  WARRANTIES  OF
    MERCHANTABILITY  AND  FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
    ANY  SPECIAL ,  DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
    WHATSOEVER  RESULTING  FROM  LOSS  OF USE, DATA OR PROFITS, WHETHER IN AN
    ACTION  OF  CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
    OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
*/
//==============================================================================

#include <xrpl/basics/base_uint.h>
#include <xrpl/beast/utility/rngfill.h>
#include <xrpl/crypto/csprng.h>
#include <xrpl/json/json_value.h>
#include <xrpl/protocol/ErrorCodes.h>
#include <xrpl/protocol/RPCErr.h>
#include <xrpl/protocol/jss.h>

#include <boost/beast/core/tcp_stream.hpp>
#include <boost/asio.hpp>
#include <boost/beast/http.hpp>
#include <boost/beast/core/flat_buffer.hpp>
#include <sstream>
#include <iostream>

namespace ripple {

namespace RPC {
struct JsonContext;
}

std::string
uploadToIPFS(const std::string& filename, const std::string& file_contents)
{
    using namespace boost::asio;
    using namespace boost::beast::http;
    try {
        boost::asio::io_context ioc;
        ip::tcp::resolver resolver(ioc);
        boost::beast::tcp_stream stream(ioc);

        auto const host = "127.0.0.1";
        auto const port = "5001";
        auto const target = "/api/v0/add";

        auto const results = resolver.resolve(host, port);
        stream.connect(results);

        // Prepare multipart body
        std::string boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW";
        std::ostringstream body;
        body << "--" << boundary << "\r\n";
        body << "Content-Disposition: form-data; name=\"file\"; filename=\"" << filename << "\"\r\n";
        body << "Content-Type: application/octet-stream\r\n\r\n";
        body << file_contents << "\r\n";
        body << "--" << boundary << "--\r\n";

        // Set up HTTP POST request
        boost::beast::http::request<boost::beast::http::string_body> req{boost::beast::http::verb::post, target, 11};
        req.set(boost::beast::http::field::host, host);
        req.set(boost::beast::http::field::content_type, "multipart/form-data; boundary=" + boundary);
        req.content_length(body.str().size());
        req.body() = body.str();
        req.prepare_payload();

        // Send the request
        boost::beast::http::write(stream, req);

        // Get the response
        boost::beast::flat_buffer buffer;
        boost::beast::http::response<boost::beast::http::string_body> res;
        boost::beast::http::read(stream, buffer, res);

        // Close the connection
        boost::beast::error_code ec;
        stream.socket().shutdown(ip::tcp::socket::shutdown_both, ec);

        // Parse the response to get the CID
        // Json::Value json;
        // if (parseJson(res.body(), json) && json.isMember("Hash"))
        //     return json["Hash"].asString();
        // else
        return "";
    } catch (const std::exception& e) {
        std::cerr << "Upload failed: " << e.what() << std::endl;
        return "";
    }
}

// Result:
// {
//   random: <uint256>
// }
Json::Value
doIPFSAdd(RPC::JsonContext& context)
{
    try
    {
        uint256 rand;
        beast::rngfill(rand.begin(), rand.size(), crypto_prng());

        Json::Value jvResult;
        jvResult[jss::random] = to_string(rand);
        return jvResult;
    }
    catch (std::exception const&)
    {
        return rpcError(rpcINTERNAL);
    }
}

}  // namespace ripple
```
Fix the doIPFSAdd function and then how would I call this frunction from the rpc?

"""
client = AthenahClient("id", "dist", "rippled-apollo", "v1")
response = client.promptv1(prompt)
print(response)
