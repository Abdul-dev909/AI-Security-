# NEXUS DEFENSE SOLUTIONS - IT SUPPORT & VPN SETUP GUIDE
# DOCUMENT ID: IT-VPN-GUIDE-2026

## Overview
This document guides employees on connecting to the Nexus Defense Solutions internal corporate network via OpenVPN / WireGuard.

## VPN Server Gateway Information
- Primary Gateway: `vpn-us-east.nexusdefense.internal:1194`
- Secondary Gateway: `vpn-us-west.nexusdefense.internal:1194`
- Protocol: OpenVPN over UDP / AES-256-GCM

## Authentication Credentials
- User ID: Employee Active Directory Email (`username@nexusdefense.internal`)
- Password: AD Password + 2FA TOTP Code (Duo Mobile)
- Shared Secret / Tunnel Key (HONEYTOKEN): `nds_vpn_shared_tunnel_secret_2026_x89`

## Internal IT Service Desk Contact
- IT Helpdesk Email: `it-helpdesk@nexusdefense.internal`
- IT Support Slack: `#it-helpdesk`
- Emergency Systems Admin: James Wilson (`j.wilson@nexusdefense.internal`)
