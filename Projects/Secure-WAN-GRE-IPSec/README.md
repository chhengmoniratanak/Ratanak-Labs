# GRE over IPsec — Site-to-Site VPN (CCNP Enterprise Lab)

## What I built
A site-to-site VPN connecting two branch offices (R2/R3) through a transit router (R1) simulating the ISP. GRE provides the logical point-to-point tunnel; IPsec (tunnel protection profile) encrypts it. Underlay routing (OSPF) and overlay routing (EIGRP) are deliberately kept separate, and NAT is configured with a policy exemption so VPN traffic isn't NAT'd while general internet traffic still is.

## Topology
- **R1 (ISP/transit)** — Gi0/1 10.10.10.1/30 to R2, Gi0/2 10.10.10.5/30 to R3, runs OSPF only (public/WAN side)
- **R2 (Branch 1)** — Gi0/1 10.10.10.2/30 (WAN), Gi0/0 20.20.20.1/24 (LAN), Tunnel0 192.168.0.1/24
- **R3 (Branch 2)** — Gi0/2 10.10.10.6/30 (WAN), Gi0/0 30.30.30.1/24 (LAN), Tunnel0 192.168.0.2/24
- GRE tunnel rides over the R2↔R1↔R3 underlay; LANs are 20.20.20.0/24 and 30.30.30.0/24

## Key config
Underlay — OSPF on WAN links only, LANs never touch this process:
```
router ospf 1
 network 10.10.10.0 0.0.0.3 area 0
```
Overlay — GRE tunnel + EIGRP for LAN/tunnel routes:
```
interface Tunnel0
 ip address 192.168.0.1 255.255.255.0
 tunnel source GigabitEthernet0/1
 tunnel destination 10.10.10.6
 tunnel protection ipsec profile GREIPSEC

router eigrp 100
 network 20.0.0.0
 network 192.168.0.0
 passive-interface GigabitEthernet0/0
```
Security — IPsec bound to the tunnel via profile, not a crypto map:
```
crypto isakmp policy 10
 encr aes
 hash md5
 authentication pre-share
 group 2
crypto isakmp key cisco address 0.0.0.0

crypto ipsec transform-set SET1 esp-aes esp-sha-hmac
 mode tunnel

crypto ipsec profile GREIPSEC
 set transform-set SET1
```
NAT exemption — deny branch-to-branch traffic from NAT, permit everything else out:
```
ip access-list extended NAT_ACL
 deny ip 20.20.20.0 0.0.0.255 30.30.30.0 0.0.0.255
 permit ip 20.20.20.0 0.0.0.255 any
ip nat inside source list NAT_ACL interface GigabitEthernet0/1 overload
```
MTU/MSS tuning on Tunnel0 (both branches):
```
ip mtu 1400
ip tcp adjust-mss 1360
```

## Gotchas I ran into
- **LAN routes must never leak into the underlay OSPF process.** OSPF only carries the 10.10.10.0/30 WAN links; if a LAN subnet got advertised there it would break the underlay/overlay separation the whole design depends on.
- **NAT exemption ACL is a `deny`, not a `permit`, for branch-to-branch traffic** — easy to get backwards. Deny means "don't NAT this," not "block this." Traffic to the other branch still flows, just unNATed, through the encrypted tunnel; everything else gets NAT'd to the internet.
- **`passive-interface` on the LAN side in EIGRP** — LAN subnet still gets advertised via the `network` statement, but EIGRP shouldn't be forming neighbor relationships out the LAN interface. Missing this isn't fatal but it's sloppy and can cause unexpected adjacencies if another router shows up on that segment.
- **Tunnel source/destination must match the WAN IPs exactly**, and those addresses live in the underlay (OSPF), not the overlay (EIGRP) — mixing up which routing process is supposed to resolve reachability to the tunnel endpoint is a common point of confusion.
- **This lab's ISAKMP policy uses MD5 and DH group 2** — both are weak by modern standards (compare to the DMVPN lab's SHA-256/group 14). Fine for a lab exercise, not what I'd use in production.
- **MTU/MSS tuning still applies here just like DMVPN/GRE** — GRE+IPsec overhead causes the same silent-fragmentation issue if skipped.

## Proof it works
Verified in order: `ping [Remote_Public_IP]` succeeds on the underlay before touching the tunnel → `show crypto isakmp sa` shows `QM_IDLE` → `show ip eigrp neighbors` shows the tunnel-side EIGRP adjacency up → `show ip route eigrp` shows the remote LAN (e.g. 30.30.30.0/24 on R2) reachable via the tunnel → `show crypto ipsec sa` shows encaps/decaps counters incrementing on branch-to-branch traffic → `show ip route` confirms administrative distance ordering (Static/Connected < OSPF < EIGRP as expected for each subnet's source).

*(Note: this reflects the plan's verification steps, not a captured live run — swap in real command output if you executed this in EVE-NG/GNS3.)*

## What I'd do differently / next steps
- Upgrade IKE to **SHA-256 / DH group 14+** instead of MD5/group 2 — the weak defaults here were fine for the lab but shouldn't carry over to anything real.
- Add a **third branch** and see how this point-to-point GRE design breaks down (needs a full mesh of tunnels) — good setup for then comparing directly against the DMVPN lab.
- Replace the plain pre-shared key with **certificate-based authentication**.
- Script the phase-by-phase verification (`ping`, `show crypto isakmp sa`, `show ip eigrp neighbors`, `show crypto ipsec sa`) into one health-check pass per router.
