import { api } from '../api/client';

// Converts the base64url VAPID public key the backend returns into the raw
// Uint8Array format PushManager.subscribe() requires for applicationServerKey.
function urlBase64ToUint8Array(base64String: string): Uint8Array {
  const padding = '='.repeat((4 - (base64String.length % 4)) % 4);
  const base64 = (base64String + padding).replace(/-/g, '+').replace(/_/g, '/');
  const rawData = window.atob(base64);
  const output = new Uint8Array(rawData.length);
  for (let i = 0; i < rawData.length; i++) output[i] = rawData.charCodeAt(i);
  return output;
}

export type PushSupport = 'unsupported' | 'subscribed' | 'unsubscribed';

export async function getPushState(): Promise<PushSupport> {
  if (!('serviceWorker' in navigator) || !('PushManager' in window)) return 'unsupported';
  try {
    const reg = await navigator.serviceWorker.ready;
    const sub = await reg.pushManager.getSubscription();
    return sub ? 'subscribed' : 'unsubscribed';
  } catch {
    return 'unsupported';
  }
}

export async function enablePush(): Promise<boolean> {
  if (!('serviceWorker' in navigator) || !('PushManager' in window)) return false;

  const permission = await Notification.requestPermission();
  if (permission !== 'granted') return false;

  const { public_key, configured } = await api.get<{ public_key: string; configured: boolean }>(
    '/api/notifications/vapid-public-key'
  );
  if (!configured || !public_key) return false;

  const reg = await navigator.serviceWorker.ready;
  const sub = await reg.pushManager.subscribe({
    userVisibleOnly: true,
    // Cast needed: TS's lib.dom types Uint8Array's buffer as ArrayBuffer
    // specifically, but the DOM API accepts any BufferSource at runtime.
    applicationServerKey: urlBase64ToUint8Array(public_key) as BufferSource,
  });
  const json = sub.toJSON();
  if (!json.endpoint || !json.keys?.p256dh || !json.keys?.auth) return false;

  await api.post('/api/notifications/subscribe', {
    endpoint: json.endpoint,
    keys: { p256dh: json.keys.p256dh, auth: json.keys.auth },
  });
  return true;
}

export async function disablePush(): Promise<void> {
  if (!('serviceWorker' in navigator)) return;
  const reg = await navigator.serviceWorker.ready;
  const sub = await reg.pushManager.getSubscription();
  if (!sub) return;
  await api.post('/api/notifications/unsubscribe', { endpoint: sub.endpoint });
  await sub.unsubscribe();
}
