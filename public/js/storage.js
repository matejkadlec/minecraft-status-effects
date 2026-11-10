/*--------------------------------------------------------------*
 * localStorage wrapper: every key is prefixed with "se-" and  *
 * access never throws (private mode, blocked storage, quota) *
 *--------------------------------------------------------------*/
const PREFIX = "se-";

// Keys used before the rename to "status-effects"; read once, then moved to the new key.
const LEGACY_KEYS = {
  theme: "mcse-theme",
  filters: "mcse-filters",
  "page-length": "mcse-page-length",
  "ignore-filters": "export-ignore-filters",
};

function storage() {
  try {
    return window.localStorage;
  } catch {
    return null;
  }
}

export function read(key) {
  const store = storage();
  if (!store) return null;
  try {
    const value = store.getItem(PREFIX + key);
    if (value !== null) return value;
    const legacy = LEGACY_KEYS[key];
    if (legacy) {
      const old = store.getItem(legacy);
      if (old !== null) {
        store.setItem(PREFIX + key, old);
        store.removeItem(legacy);
        return old;
      }
    }
  } catch {
    /* storage unavailable */
  }
  return null;
}

export function write(key, value) {
  const store = storage();
  if (!store) return;
  try {
    if (value === null || value === undefined || value === "") store.removeItem(PREFIX + key);
    else store.setItem(PREFIX + key, String(value));
  } catch {
    /* storage full or unavailable */
  }
}

export function readJSON(key, fallback) {
  const raw = read(key);
  if (raw === null) return fallback;
  try {
    return JSON.parse(raw);
  } catch {
    return fallback;
  }
}

export function writeJSON(key, value) {
  write(key, JSON.stringify(value));
}
