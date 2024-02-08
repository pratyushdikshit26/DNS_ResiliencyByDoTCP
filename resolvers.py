RESOLVER_NAMES = {
    "cloudflare-public-dns": ["1.1.1.1", "2606:4700:4700::1111"],
    "google-public-dns": ["8.8.8.8", "2001:4860:4860::8888"],
    'clean-browsing': ['185.228.168.9', "2a0d:2a00:1::"] ,
    'open-dns': ['208.67.222.222', "2620:119:35::35"] ,
    'open-nic': ['185.121.177.177', "2a05:dfc7:5::53"] ,
    'quad-9': ['9.9.9.9', "2620:fe::fe"],
    'comodo-secure-dns': ['8.26.56.26', "0000:0000:ffff:81a:381a"] , # NO IPv6 address for this resolver, this is the directly converted address and will results in a non-successful request to RIPE
    'uncensored-dns': ['91.239.100.100', "2001:67c:28a4::"] ,
    'neustar-ultra-dns-public': ['64.6.64.6', "2620:74:1b::1:1"] ,
    'yandex-dns': ['77.88.8.8', "2a02:6b8::feed:ff"]
}

RESOLVER_ADDRESSES = [item for sublist in RESOLVER_NAMES.values() for item in sublist]
