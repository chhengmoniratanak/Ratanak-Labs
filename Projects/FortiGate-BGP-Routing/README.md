# BGP with FortiGate Firewalls

## What I built
A 3-way eBGP mesh between three FortiGate firewalls, each acting as its own AS, sharing a common WAN subnet. Beyond just BGP config, this required firewall policies in both directions — a step that's easy to skip on FortiOS since neighbors can form and routes can install while actual traffic is still silently dropped by policy.

## Topology
- **FW1** — port2 (WAN) 100.64.0.1/24, port3 (LAN) 172.16.1.1/24, AS 65001, LAN → PC1 (SW1)
- **FW2** — port2 (WAN) 100.64.0.2/24, port3 (LAN) 172.16.2.1/24, AS 65002, LAN → PC2 (SW2)
- **FW3** — port2 (WAN) 100.64.0.3/24, port3 (LAN) 172.16.3.1/24, AS 65003, LAN → PC3 (SW3)
- All three WAN ports share 100.64.0.0/24 ("Internet" segment); FW1 peers with both FW2 and FW3 directly

## Key config
Interface + management access (repeat per firewall, different IPs):
```
config system interface
 edit "port2"
  set ip 100.64.0.1 255.255.255.0
  set allowaccess ping https ssh
 next
 edit "port3"
  set ip 172.16.1.1 255.255.255.0
  set allowaccess ping
 next
end
```
Firewall policy — required in both directions or BGP forms but pings never cross:
```
config firewall policy
 edit 1
  set name "LAN_to_WAN"
  set srcintf "port3"
  set dstintf "port2"
  set srcaddr "all"
  set dstaddr "all"
  set action accept
  set schedule "always"
  set service "ALL"
 next
 edit 2
  set name "WAN_to_LAN"
  set srcintf "port2"
  set dstintf "port3"
  set action accept
  ...
 next
end
```
eBGP (FW1, peering with both FW2 and FW3, advertising its own LAN):
```
config router bgp
 set as 65001
 set router-id 1.1.1.1
 config neighbor
  edit "100.64.0.2"
   set remote-as 65002
  next
  edit "100.64.0.3"
   set remote-as 65003
  next
 end
 config network
  edit 1
   set prefix 172.16.1.0 255.255.255.0
  next
 end
end
```

## Gotchas I ran into
- **BGP neighbors coming up doesn't mean traffic flows.** FortiOS still needs explicit firewall policies for both LAN→WAN and WAN→LAN — without them, PfxRcd shows routes learned and installed, but PC-to-PC pings across firewalls still fail silently.
- **FortiOS CLI defaults `allowaccess` to nothing** — forgetting `set allowaccess ping https ssh` on the WAN port means you lock yourself out of CLI/GUI management on that interface, not just block BGP.
- **This is a 3-way full mesh, not a hub design**, despite FW1 being labeled the "hub" in the source material — since all three WANs share one broadcast subnet (100.64.0.0/24), FW1 peers directly with both FW2 and FW3, and FW2/FW3 could just as easily peer with each other on the same subnet.
- **`set network` under `config router bgp`** is what actually originates the LAN prefix into BGP — without it, the neighbor session is up but the firewall's own LAN never gets advertised to the other two.
- **`service "ALL"` in the policy is fine for a lab, not for production** — worth narrowing before this pattern gets reused anywhere real.

## Proof it works
Verified entirely via CLI, no GUI: `get router info bgp summary` shows a non-zero `PfxRcd` for each neighbor (session up, routes exchanged) → `get router info routing-table bgp` shows the other two LAN prefixes (172.16.2.0/24, 172.16.3.0/24 as seen from FW1) → `execute ping 172.16.2.1` from FW1 succeeds → PC1 can ping PC2 and PC3 and back, confirming both the BGP control plane and the firewall policies are correct end-to-end.

*(Reflects the guide's verification steps, not a captured live run — swap in real command output if executed.)*

## What I'd do differently / next steps
- Move from a **flat full-mesh WAN to a real internet-edge design** — e.g. put a router/switch between the firewalls instead of sharing one broadcast subnet, closer to how eBGP peering looks with a real ISP.
- Tighten the **firewall policy from `service "ALL"`** to only what's actually needed (ping + whatever app traffic is in scope).
- Add **route filtering/prefix-lists** so each AS only advertises and accepts what it should, instead of a flat `set network` with no constraints.
- Script the verification (`get router info bgp summary`, routing-table check, ping matrix across all three LANs) into one pass instead of running it per-firewall by hand.
