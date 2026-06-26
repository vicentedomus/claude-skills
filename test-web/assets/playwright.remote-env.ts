import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';

// ============================================================
// Accommodations to run Playwright inside the Claude Code on the web remote
// execution environment. EVERYTHING is gated by detection: in local dev or a
// normal CI (no proxy, no pre-installed browser) these helpers return neutral
// values and change nothing.
//
// Repo-agnostic: drop this file at the repo root and wire it into the Playwright
// config (see the test-web SKILL.md, "Remote-env proxy routing"). It solves two
// blockers of the remote environment:
//
// 1) Egress only through a CONNECT-only MITM proxy. The environment routes HTTPS
//    through a proxy at $HTTPS_PROXY. Chromium does NOT use that proxy unless
//    told to, so every external request from the browser — CDN <script> deps
//    (e.g. supabase-js, jspdf, fonts) AND runtime API calls to your backend —
//    dies with ERR_CONNECTION_CLOSED and the app never boots (stuck on splash).
//    The cure: (a) route the browser through the proxy, but (b) keep localhost
//    DIRECT — the proxy answers 405 to a plain-HTTP GET (CONNECT only), so there
//    is no point tunneling the local dev server. Fine print discovered the hard
//    way in this Chromium: neither Playwright's `proxy.bypass` nor a PAC in a
//    data: URL work; the ONLY method that routes correctly is --proxy-pac-url
//    pointing at a file://. Since the proxy re-terminates TLS with its own CA,
//    we also ignore certificate errors.
//
// 2) Pre-installed browser whose version != the one @playwright/test resolves
//    (e.g. the package wants build 1208 but the container ships 1194). The
//    environment FORBIDS `playwright install`; it ships a Chromium at
//    /opt/pw-browsers/chromium (symlink). We point executablePath at it instead
//    of downloading.
// ============================================================

const PROXY = process.env.HTTPS_PROXY || process.env.https_proxy || '';
const PRESET_CHROMIUM =
  process.env.PLAYWRIGHT_PRESET_CHROMIUM || '/opt/pw-browsers/chromium';

/** We're behind the remote environment's MITM proxy. */
export const behindProxy = Boolean(PROXY);

/**
 * Ignore certificate errors: when the explicit knob asks for it
 * (PLAYWRIGHT_IGNORE_TLS=1) or when we're behind the MITM proxy, whose CA the
 * Chromium store may not carry.
 */
export const ignoreTLS =
  process.env.PLAYWRIGHT_IGNORE_TLS === '1' || behindProxy;

/**
 * Generate a PAC that sends localhost DIRECT and everything else through the
 * proxy, write it to a temp file and return its file:// URL. `null` when there
 * is no proxy (normal environment → no PAC). The proxy port changes between
 * sessions, so this is generated at runtime from $HTTPS_PROXY, never committed.
 */
function pacFileUrl(): string | null {
  if (!PROXY) return null;
  const hostport = PROXY.replace(/^https?:\/\//, '').replace(/\/$/, '');
  const pac =
    'function FindProxyForURL(url, host) {' +
    'if (host === "localhost" || host === "127.0.0.1" || host === "::1" || host === "[::1]") return "DIRECT";' +
    `return "PROXY ${hostport}";` +
    '}';
  const pacPath = path.join(os.tmpdir(), 'pw-remote-proxy.pac');
  fs.writeFileSync(pacPath, pac);
  return `file://${pacPath}`;
}

/**
 * Browser launchOptions with ONLY what applies in this environment. Returns
 * `undefined` (no overrides) in normal environments.
 */
export function remoteLaunchOptions():
  | { args?: string[]; executablePath?: string }
  | undefined {
  const args: string[] = [];
  if (ignoreTLS) args.push('--ignore-certificate-errors');
  const pac = pacFileUrl();
  if (pac) args.push(`--proxy-pac-url=${pac}`);

  const opts: { args?: string[]; executablePath?: string } = {};
  if (args.length) opts.args = args;
  if (fs.existsSync(PRESET_CHROMIUM)) opts.executablePath = PRESET_CHROMIUM;
  return Object.keys(opts).length ? opts : undefined;
}
