# 🌐 Enterprise MPLS L3VPN Lab

A production-style Multi-Tenant Multiprotocol Label Switching (MPLS) Layer 3 Virtual Private Network lab built on Cisco IOS. This project proves advanced routing, underlay/overlay separation, and VRF-based customer traffic isolation.

---

## 🏗️ Topology & Architecture

* **Provider Core (P/PE):** 4 Cisco IOS routers (`R1-PE`, `R2-P`, `R3-P`, `R4-PE`) running OSPF Area 0 underlay and LDP for label switching.
* **Control Plane:** MP-BGP (VPNv4 address family) establishing a secure, scalable iBGP backbone between edge routers.
* **Multi-Tenancy:** Isolated customer environments using unique Route Distinguishers (RD) and Route Targets (RT):
  * **Customer 1:** `VRF CUST_1` (RD `1:1`, RT `1:1`)
  * **Customer 2:** `VRF CUST_2` (RD `2:2`, RT `2:2`)

```
[ CE1 ] \                                      / [ CE3 ]
         \ (CUST_1)                     (CUST_1)/ 
      [ R1-PE ]============================[ R4-PE ]
         / \     (MP-VPNv4 iBGP Backbone)   / \
        /   \                              /   \
[ CE2 ]/     [ R2-P ]----(OSPF/LDP)----[ R3-P ]     [ CE4 ]
         (CUST_2)                       (CUST_2)
```

---

## 🛠️ Key Technical Skills Demonstrated

* **Underlay Routing:** Configured OSPF Area 0 for core reachability and loopback summarization.
* **MPLS Data Plane:** Enabled `mpls ip` and LDP to dynamically distribute label bindings across transit links.
* **VPNv4 Control Plane:** Established MP-iBGP sessions between PE loopbacks with extended community support.
* **VRF Isolation:** Implemented virtual routing and forwarding instances on edge routers to allow overlapping customer IP address spaces securely.

---

## 🔍 Quick Verification Commands

Run these core operational commands on the PE routers (`R1-PE` / `R4-PE`) to validate the data and control planes:

```ios
! Check core OSPF and LDP neighbors
show ip ospf neighbor
show mpls ldp neighbor

! Check MP-BGP VPNv4 session status
show bgp vpnv4 unicast all summary

! Verify VRF routing tables & tenant reachability
show ip route vrf CUST_1
ping vrf CUST_1 172.16.3.33
```