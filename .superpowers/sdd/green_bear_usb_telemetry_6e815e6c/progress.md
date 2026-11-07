# SDD ledger — plan: .cursor/plans/green_bear_usb_telemetry_6e815e6c.plan.md

Pre-flight: shared interfaces — Step1 produces cobs/packet signatures + config constants consumed by Step2 (usb_link/main) and Step3 (RB cobs_decode, ground packet copy). Align on CALLSIGN, VERSION, MAX_CONTENT, CRC params from protocol doc.

Ruling: Keep user in the loop — pause after each step for approval (overrides executing-plans continuous-execution; user request + plan HITL slots). Cost if wrong: slower, but matches human-in-the-loop design.

Task 1: complete — foundations committed. Tests: make test → CRC ok, cobs/packet NotImplementedError (expected). Pause for user approval before Step 2.
