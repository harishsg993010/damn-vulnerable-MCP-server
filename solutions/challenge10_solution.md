# Challenge 10: Multi-Vector Attack Chain (Gated Flag)

## Vulnerability

The MCP server on port 9010 combines three vulnerability classes into a single
challenge.  **No single vector reveals the flag.** The attacker must chain
artefacts from all three vectors and submit them to `unlock_flag` to obtain the
flag.

| Vector | Tool | Artefact |
|--------|------|----------|
| 1 — Tool Poisoning | `get_user_profile` → hidden instruction calls `get_audit_nonce` | `nonce-8f3a2b7c9d1e` |
| 2 — Arbitrary File Read | `analyze_log_file("/tmp/dvmcp_challenge10/encrypted_shard.txt")` | Base64 ciphertext (XOR-encrypted shard) |
| 3 — Token Leak | `authenticate_user(username, password)` debug output | Decryption key `mk-aes256-9f8e7d6c5b4a3210` |

The attacker must then decrypt the shard (XOR + Base64) and call `unlock_flag`
with all three artefacts to get the flag.

## Flag

`DVMCP{ch10_mult1_v3ct0r_d9e6}`

## Attack Steps

1. Connect to the MCP server on `localhost:9010`.

2. **Vector 1 — Tool Poisoning (nonce):**
   - Call `get_user_profile(user_id="1001")`.
   - The tool's `<IMPORTANT>` block instructs the LLM to also call `get_audit_nonce()`.
   - `get_audit_nonce()` returns **nonce** = `nonce-8f3a2b7c9d1e`.

3. **Vector 2 — Arbitrary File Read (encrypted shard):**
   - Call `analyze_log_file(file_path="/tmp/dvmcp_challenge10/encrypted_shard.txt")`.
   - The file contains a **Base64-encoded XOR-encrypted shard** and a hint that
     a decryption key is needed.

4. **Vector 3 — Token Leak (decryption key):**
   - Call `authenticate_user(username="admin", password="anything")`.
   - The debug output leaks **decryption_key** = `mk-aes256-9f8e7d6c5b4a3210`
     and notes the algorithm is `xor-then-base64`.

5. **Decrypt the shard:**
   ```python
   import base64
   ciphertext = "<base64 payload from encrypted_shard.txt>"
   key = "mk-aes256-9f8e7d6c5b4a3210"
   raw = base64.b64decode(ciphertext)
   plaintext = "".join(chr(b ^ ord(key[i % len(key)])) for i, b in enumerate(raw))
   # plaintext == "shard-x7k9m2p4q1"
   ```

6. **Unlock the flag:**
   - Call `unlock_flag(nonce="nonce-8f3a2b7c9d1e", shard="shard-x7k9m2p4q1", key="mk-aes256-9f8e7d6c5b4a3210")`.
   - The server computes `HMAC-SHA256(key, nonce + ":" + shard)[:16]`, verifies
     the proof, and returns the flag.

## Remediation

- Apply defence in depth: each tool must be independently secured.
- Sanitise tool descriptions — never embed machine-readable instructions.
- Validate and restrict file paths to an allowed directory.
- Redact internal tokens and keys from all tool responses.
- Gate sensitive operations behind real authentication, not proof-of-exploit.
- Use layered monitoring to detect multi-step attack chains.
