import { NextResponse } from "next/server";

export function POST() {
  const res = NextResponse.json({ ok: true });
  res.cookies.set("access_token", "", {
    maxAge: 0,
    httpOnly: true,
    sameSite: "lax",
    path: "/",
  });
  return res;
}
