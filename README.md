# secure-tcp-file-message-transfer

Framed, encrypted TCP-based message and file transfer system built in Python.

---

## Encrypted TCP File & Message Transfer (v0.1)

This project implements a **custom application-layer protocol** over TCP for securely transmitting messages and arbitrary binary files (images, audio, video, etc.).

The primary focus is **correctness of transport and cryptographic handling**, rather than UI, performance tuning, or production hardening.

---

## Key Features

- Binary-safe message and file transfer over TCP
- Length-prefixed framing to handle TCP stream boundaries
- Fernet-based authenticated encryption (confidentiality + integrity)
- Multithreaded send/receive model
- Reliable handling of arbitrary binary data without corruption

---

## Motivation

This project was built to explore and understand:

- Why cryptographic padding errors occur over TCP
- How improper framing breaks encrypted communication
- How to correctly design a simple, reliable application-layer protocol

---

## Technical Overview

Each message or file chunk is transmitted in the following format:

[4-byte length header][Fernet-encrypted payload

This design ensures:

- Complete token delivery
- No partial or merged decryptions
- Reliable handling of large binary transfers

---

## Current Limitations
- Works only on LAN currently, can be combined with third party softwares for WAN 
- No peer authentication (vulnerable to MITM)
- No protocol versioning
- Graceful connection teardown still being improved
- Uses threads instead of async or event-driven I/O

---

## Planned Improvements

- Explicit protocol versioning
- Graceful shutdown and session lifecycle handling
- Authentication and key exchange hardening
- Async or selector-based I/O model
- Improved error handling and logging

---

## Disclaimer

This project is **educational** and not intended for production use.
