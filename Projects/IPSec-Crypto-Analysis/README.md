# Secure Multi-Site Network Design — BGP Underlay + IPsec (AH vs ESP)

## What I built
A hub-and-spoke IPsec deployment (R1 as hub) over a BGP-routed underlay through a simulated ISP, using two different IPsec transform sets on purpose: AH toward R2 (integrity/auth only, payload stays readable) and ESP toward R3 (full encryption). Point was to compare the two protocols side by side on the wire, not just get a tunnel up.

## Topology
- **ISP** — AS 65000, core, links to all three sites on separate /30s
- **R1 (Branch 1 / Hub)** — Gi0/0 100.64.1.1/30, LAN 192.168.1.0/24, AS 65001
- **R2 (Branch 2 / AH peer)** — Gi0/0 100.64.2.1/30, LAN 192.168.2.0/24, AS 65002
- **R3 (Branch 3 / ESP peer)** — Gi0/0 100.64.3.1/30, LAN 192.168.3.0/24, AS 65003
- BGP peers each site to the ISP for underlay reachability; IPsec tunnels ride on top: R1↔R2 (AH), R1↔R3 (ESP)

## Key config
BGP underlay (must be up before any tunnel can form):
```
router bgp 65001
 neighbor 100.64.1.2 remote-as 65000
```
ISAKMP (Phase 1) — same policy on all routers, separate PSK per peer:
```
crypto isakmp policy 1
 encr aes
 authentication pre-share
 group 2
crypto isakmp key CISCO address 100.64.2.1
crypto isakmp key CISCO address 100.64.3.1
```
Transform sets — deliberately different per peer:
```
crypto ipsec transform-set R2-AH ah-sha-hmac
 mode tunnel
crypto ipsec transform-set R3-ESP esp-aes esp-sha-hmac
 mode tunnel
```
Crypto map — ties peer + transform-set + interesting-traffic ACL together, multiple sequence numbers on R1 since it's the hub:
```
crypto map MYMAP 10 ipsec-isakmp
 set peer 100.64.2.1
 set transform-set R2-AH
 match address TO-R2
crypto map MYMAP 20 ipsec-isakmp
 set peer 100.64.3.1
 set transform-set R3-ESP
 match address TO-R3
!
interface GigabitEthernet0/0
 crypto map MYMAP
```

## Gotchas I ran into
- **AH ≠ no security, just no confidentiality.** AH signs the whole packet (including the IP header) for integrity/authentication but never encrypts the payload — that's the point of using it toward R2, to actually see plaintext ICMP in a capture while still proving the header wasn't tampered with.
- **Forgetting to apply `crypto map` to the physical interface** is a classic — the map can be fully built and still do nothing until it's bound to Gi0/0 with `crypto map MYMAP`.
- **The ACL defines "interesting traffic," not a firewall rule.** Traffic that doesn't match the crypto ACL isn't blocked — it just isn't encrypted, which is a different failure mode than people expect (it doesn't fail loudly, it just isn't protected).
- **R1 needs two crypto map entries under one map name** (sequence 10, sequence 20) since it's the hub talking to two different peers with two different transform sets — same map, different peer/transform-set/ACL per sequence number.
- **AH is protocol 51, ESP is protocol 50 on the wire** — useful to remember when filtering a capture, since neither shows up as UDP/TCP.
- **BGP has to be fully up first.** No underlay reachability between WAN IPs means ISAKMP never even gets to send its first packet — always check `show ip bgp` before troubleshooting crypto.

## Proof it works
This is the strongest evidence in the series — actual packet captures back it up, not just `show` command output:
- **ESP capture** (R1↔R3): frames show `ESP (SPI=0x...)` with no visible upper-layer protocol — payload is opaque ciphertext.
- **AH capture** (R1↔R2): frames show the underlying `ICMP Echo (ping) request/reply` in the clear, between 192.168.1.1 and 192.168.2.1 — confirming AH authenticates without encrypting.
- Control-plane verification: `show crypto isakmp sa` → `QM_IDLE` for both peers; `show crypto ipsec sa` → `#pkts encaps`/`#pkts decaps` incrementing on both tunnels.

## What I'd do differently / next steps
- Swap AH for **ESP with NULL encryption** (`esp-null esp-sha-hmac`) as a cleaner side-by-side of "authenticated but visible" vs AH, since AH's IP-header-inclusive signing behaves differently from ESP in real deployments (e.g. NAT compatibility).
- Move ISAKMP from **DH group 2 / SHA-1 defaults to group 14+/SHA-256** — this lab intentionally used weaker legacy defaults for simplicity, not production strength.
- Add a **third tunnel using IKEv2** instead of IKEv1/ISAKMP to compare negotiation behavior.
- Script a repeatable capture-and-compare (tshark filter on protocol 50 vs 51) instead of manually eyeballing Wireshark output.
