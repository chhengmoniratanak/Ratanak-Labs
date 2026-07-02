# Palo Alto HA (Active/Passive) Lab

## What I built
Short paragraph: two PA firewalls, HA active/passive, tested failover
via [method], validated stateful session sync / GARP behavior.

## Topology
[Topology Diagram](Projects/High-Availability-Palo/images/topology.png)

## Key config
- Group ID, Priority, HA1/HA2 setup (bullet points, not screenshots —
  you can type these out, they're short)

## Gotchas I ran into
- Interface numbering must mirror between FW1/FW2 or dataplane sync
  breaks (explain the e1/1 vs e1/2 issue)
- [any other real issue you hit]

## Proof it works
[HA dashboard screenshot FW1]
[HA dashboard screenshot FW2]
[maybe a ping test showing minimal packet loss during failover]

## What I'd do differently / next steps
- Active/Active testing
- Path monitoring / link monitoring
