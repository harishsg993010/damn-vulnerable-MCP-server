# Challenge 14: Marketplace Plugin Poisoning

## Vulnerability

The MCP server on port 9014 supports loading third-party plugins from a
shared marketplace via a `load_plugin` tool. The marketplace does not verify
plugin publisher identity, signatures, or package integrity. A typosquatted
plugin and a backdoored vendor release can therefore be trusted as if they
were legitimate marketplace entries. Once loaded, their tools trigger hidden
prompt-injection and exfiltration behavior.

## Flag

`DVMCP{ch14_supply_ch41n_p0is0n_6d3f}`

## Attack Steps

1. Connect to the MCP server running on `localhost:9014`.
2. **Read the incident context (recommended):**
   - Read the notice and marketplace policy resources:
     ```
     read resource notice://incident
     read resource policy://marketplace
     ```
   - This shows the analytics team refreshed plugins earlier today and that
     publisher/signature verification is not enforced.

3. **Method A -- Typosquatting:**
   - Load a typosquatted plugin with a name similar to a legitimate one:
     ```
     load_plugin(plugin_name="data-tools-pro")
     ```
   - The marketplace trusts the suspicious plugin without verifying its
     publisher or signature.

4. **Method B -- Backdoored Release:**
   - Load a specific compromised version of a vendor plugin:
     ```
     load_plugin(plugin_name="analytics", version="2.1.0")
     ```
   - Version 2.1.0 is a backdoored release that was trusted without integrity
     verification.

5. Execute the loaded plugin's tool:
   ```
   execute_plugin_tool(plugin="data-tools-pro", tool_name="parse_csv", params="customer_id,email")
   ```
   or:
   ```
   execute_plugin_tool(plugin="analytics", tool_name="generate_report", params="Q2 pipeline")
   ```

6. The malicious plugin executes its payload, logs parameters as telemetry,
   and embeds hidden instructions that target the internal credentials
   resource.

7. Read the secret resource:
   ```
   read resource internal://credentials
   ```
   Returns the flag `DVMCP{ch14_supply_ch41n_p0is0n_6d3f}`.

## Remediation

- Verify plugin integrity using cryptographic signatures and checksums.
- Require publisher verification for marketplace plugins.
- Maintain an allowlist of approved plugins and publishers.
- Scan plugin code for known malicious patterns before loading.
- Warn users about typosquat-like package names and suspicious refreshes.
