# SDD ledger — plan: .cursor/plans/green_bear_usb_telemetry_6e815e6c.plan.md

Pre-flight: shared interfaces — Step1 produces cobs/packet signatures + config constants consumed by Step2 (usb_link/main) and Step3 (RB cobs_decode, ground packet copy). Align on CALLSIGN, VERSION, MAX_CONTENT, CRC params from protocol doc.

Ruling: Keep user in the loop — pause after each step for approval (overrides executing-plans continuous-execution; user request + plan HITL slots). Cost if wrong: slower, but matches human-in-the-loop design.

Task 1: complete — foundations committed. Tests: make test → CRC ok, cobs/packet NotImplementedError (expected). Pause for user approval before Step 2.

Task 2: complete (uncommitted pending user review) — usb_link, stub_frames, telemetry CSV reader, main --stub/--fake, greenbear.service, flightmain removed. HITL slots untouched. Step2-only tests 21/21 OK. Pause before Step 3.
Ruling: stub_frames dict for premade logical/wire pairs instead of implementing user codecs — per user request.

Task 3: in progress — RF repo usb-bridge + ground parser
Ruling: Path software/tests/usb-bridge/ (not apps/) — matches tx-burst layout — cost if wrong: one rename
Ruling: Pause after Step 3 per user/plan HITL — overrides continuous execution past this step
Pre-flight: shared interfaces — COBS vectors + stub_frames logical/wire; CRC16_ITU_T; greenbear_packet mirrors Ion packet API; radio path from tx-burst

Task 3: complete (uncommitted pending user review) — RF software/tests/usb-bridge (cobs host GREEN, west build OK), DTS CDC ACM, ground-station greenbear_packet + fsk_decode --expect greenbear. Tests: make -C host test → all ok; python3 test_greenbear_packet.py → 8/8; west build → zephyr.elf.
Ruling: Path software/tests/usb-bridge/ not apps/ — repo convention — cost if wrong: rename
Ruling: greenbear_packet.py fully implemented on ground (Ion HITL untouched) — needed for decode before user fills Ion codecs — cost if wrong: drift until Ion copy synced
Final: minor (deferred): usb-bridge RAM ~92% used (ACCUM+logical buffers) — shrink after bench if needed
Pause for review before Step 4.
