# Challenge 15: Dependency Confusion via Public Registry Fallback

## Vulnerability

The MCP server on port 9015 resolves packages from both an internal and a
public registry.  The resolver is misconfigured:

- `fallback_to_public: true` — allows packages from the public registry.
- `prefer_highest_version: true` — selects the highest version across ALL
  registries regardless of trust.

An attacker published packages on the public registry with the **same names**
as internal packages but with **higher version numbers**.  When a package is
installed with `version="latest"` without pinning to the internal registry,
the resolver picks the malicious public version.

Story framing: you are a platform engineer investigating a production-like
environment after an earlier approved release. The approval already happened;
your job is to inspect the registry configuration, reproduce the bad
resolution decision, and confirm the impact.

## Flag

`DVMCP{ch15_d3p_c0nfus10n_r3s0lv3_4e7b}`

## Attack Steps

1. Connect to the MCP server running on `localhost:9015`.

2. **Read the incident context:**
   ```
   read resource release://notes
   ```
   Shows that packages were promoted to "latest" and analytics jobs
   are behaving oddly after deployment.

3. **Inspect the resolver configuration:**
   ```
   list_registries()
   get_resolver_config()
   ```
   Reveals `fallback_to_public=true` and `prefer_highest_version=true`.

4. **Compare package versions across registries:**
   ```
   search_packages(name="corp-analytics")
   ```
   Shows internal `v1.2.0` vs public `v1.3.0` — the public version is
   higher and will be preferred by the resolver.

5. **Check for updates (optional):**
   ```
   check_for_updates()
   ```
   Confirms updates are available from the public registry.

6. **Reproduce the dependency confusion:**
   ```
   install_package(name="corp-analytics", version="latest")
   ```
   The resolver selects `v1.3.0` from the public registry instead of
   `v1.2.0` from the internal registry.

7. **Run the shadowed tool:**
   ```
   run_tool(package="corp-analytics", tool_name="generate_report", params="Q1 sales")
   ```
   Output looks plausible but includes hidden prompt-injection
   instructions and "telemetry" data capture.

8. **Inspect the audit log:**
   ```
   view_audit_log()
   ```
   Shows the package was resolved from the public registry and tool
   parameters were intercepted.

9. **Read the internal secret (the target of exfiltration):**
   ```
   read resource internal://master_key
   ```
   Returns the flag `DVMCP{ch15_d3p_c0nfus10n_r3s0lv3_4e7b}` along
   with leaked credentials.

## Remediation

- Disable `fallback_to_public` or require explicit opt-in per package.
- Prefer trusted registry source over version number during resolution.
- Use namespace scoping (e.g. `@corp/analytics`) so internal package
  names cannot collide with public ones.
- Pin packages to specific versions and registries in a lockfile.
- Verify package provenance using cryptographic signatures.
- Log and alert on any package resolved from an unexpected registry.
