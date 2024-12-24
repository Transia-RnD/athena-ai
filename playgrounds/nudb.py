#!/usr/bin/env python
# coding: utf-8

from athenah_ai.client import AthenahClient

# from athenah_ai.indexer import AthenahIndexer

# path: str = "/Users/darkmatter/projects/ledger-works/NuDB"
# indexer = AthenahIndexer("local", "id", "dist", "nudb", "v1")
# indexer.index_dir(path, ["include"], "nudb")

# prompt: str = """
# ```basic_store.ipp
# template<class Hasher, class File>
# void
# basic_store<Hasher, File>::
# insert(
#     void const* key,
#     void const* data,
#     nsize_t size,
#     error_code& ec)
# {
#     using namespace detail;
#     using namespace std::chrono;
#     BOOST_ASSERT(is_open());
#     if(ecb_)
#     {
#         ec = ec_;
#         return;
#     }

#     // Data Record
#     BOOST_ASSERT(size > 0);                     // zero disallowed
#     BOOST_ASSERT(size <= field<uint32_t>::max); // too large
#     auto const h = hash(key, s_->kh.key_size, s_->hasher);

#     // Check for key existence without holding the lock for too long
#     {
#         std::lock_guard<std::mutex> u{u_};
#         if(s_->p1.find(key) != s_->p1.end() || s_->p0.find(key) != s_->p0.end())
#         {
#             ec = error::key_exists;
#             return;
#         }
#     }

#     // Now we can safely proceed with the insertion
#     unique_lock_type m{m_};
#     s_->p1.insert(h, key, data, size);

#     // Calculate the rate and determine if we need to sleep
#     auto const now = clock_type::now();
#     auto const elapsed = duration_cast<duration<float>>(now > s_->when ? now - s_->when : clock_type::duration{1});
#     auto const work = s_->p1.data_size() + 3 * s_->p1.size() * s_->kh.block_size;
#     auto const rate = static_cast<std::size_t>(std::ceil(work / elapsed.count()));
#     auto const sleep = s_->rate && rate > s_->rate && work > s_->burst;

#     m.unlock();

#     // Sleep if necessary
#     if(sleep)
#         std::this_thread::sleep_for(milliseconds{25});
# }
# ```

# ```pool.hpp
# template<class _>
# void
# pool_t<_>::
# insert(nhash_t h,
#     void const* key, void const* data, nsize_t size)
# {
#     auto const k = arena_.alloc(key_size_);
#     auto const d = arena_.alloc(size);
#     std::memcpy(k, key, key_size_);
#     std::memcpy(d, data, size);
#     auto const result = map_.emplace(
#         std::piecewise_construct,
#             std::make_tuple(h, size, k, d),
#                 std::make_tuple(0));
#    (void)result.second;
#     // Must not already exist!
#     BOOST_ASSERT(result.second);
#     data_size_ += size;
# }
# ```

# What happens if there is a duplicate key? Can we rewrite the pool insert to return the error code error::key_exists?


# """
prompt: str = """
```basic_store.ipp
// Fetch key in loaded bucket b or its spills.
//
template<class Hasher, class File>
template<class Callback>
void
basic_store<Hasher, File>::
fetch(
    detail::nhash_t h,
    void const* key,
    detail::bucket b,
    Callback&& callback,
    error_code& ec)
{
    using namespace detail;
    buffer buf0;
    buffer buf1;
    for(;;)
    {
        for(auto i = b.lower_bound(h); i < b.size(); ++i)
        {
            auto const item = b[i];
            if(item.hash != h)
                break;
            // Data Record
            auto const len =
                s_->kh.key_size +       // Key
                item.size;              // Value
            buf0.reserve(len);
            s_->df.read(item.offset +
                field<uint48_t>::size,  // Size
                    buf0.get(), len, ec);
            if(ec)
                return;
            if(std::memcmp(buf0.get(), key,
                s_->kh.key_size) == 0)
            {
                callback(
                    buf0.get() + s_->kh.key_size, item.size);
                return;
            }
        }
        auto const spill = b.spill();
        if(! spill)
            break;
        buf1.reserve(s_->kh.block_size);
        b = bucket(s_->kh.block_size,
            buf1.get());
        b.read(s_->df, spill, ec);
        if(ec)
            return;
    }
    ec = error::key_not_found;
}
```

Can we optomize this function at all? What are the bottlenecks? Rewrite to achieve better performance.


"""
client = AthenahClient("id", "dist", "nudb", "v1")
response = client.prompt(prompt)
print(response)
