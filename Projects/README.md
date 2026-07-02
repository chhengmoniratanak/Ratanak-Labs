---

## 🚀 How to Use and Verify These Labs

Every project folder inside the `Labs/` directory contains a standardized set of files designed to let you explore, deploy, and verify the network architecture yourself. 

### 📁 Lab Components

1. **Topology Blueprint (`.unl` file)**
   * **What it is:** The raw project file exported directly from my cloud-hosted EVE-NG environment.
   * **How to use it:** Download this file and import it directly into your own EVE-NG instance to spin up the exact multi-vendor topology, node for node.

2. **Lab Instructions & Objectives (`.pdf` file)**
   * **What it is:** The engineering brief for the topology.
   * **How to use it:** This document outlines the technical requirements, the target IP schema, the routing policies (OSPF/BGP), and the specific security zone constraints required to complete the lab.

3. **Verified Production Configurations (`.txt` files)**
   * **What it is:** The working proof-of-concept. These are the sanitized, complete running configurations taken directly from the live control plane of each active device (Cisco, Fortinet, Palo Alto, etc.).
   * **How to use it:** Use these files to inspect my routing logic, or copy-paste them directly into your own lab nodes to verify that the topology behaves exactly as documented and passes all end-to-end traffic checks.
