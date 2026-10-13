export async function onRequest({ request, next }) {
  const u = new URL(request.url);
  if (u.hostname === "www.gulfaideals.com") { u.hostname = "gulfaideals.com"; return Response.redirect(u.toString(), 301); }
  return next();
}
