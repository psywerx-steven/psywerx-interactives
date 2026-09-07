const LEGACY_HOST = "drivers.psywerx.io";
const TARGET_ORIGIN = "https://psywerx.io";

export function redirectLegacyRequest(request) {
  const source = new URL(request.url);
  if (source.hostname.toLowerCase() !== LEGACY_HOST) {
    return new Response("Misdirected request", { status: 421 });
  }

  const target = new URL(TARGET_ORIGIN);
  target.pathname = source.pathname === "/" ? "/drivers/" : source.pathname;
  target.search = source.search;

  return new Response(null, {
    status: 308,
    headers: {
      Location: target.toString(),
      "Cache-Control": "public, max-age=300",
    },
  });
}

export default {
  fetch(request) {
    return redirectLegacyRequest(request);
  },
};
