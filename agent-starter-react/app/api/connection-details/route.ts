import { NextResponse } from "next/server";
import { AccessToken } from "livekit-server-sdk";

export async function POST() {
  try {
    const apiKey = process.env.LIVEKIT_API_KEY;
    const apiSecret = process.env.LIVEKIT_API_SECRET;
    const url = process.env.LIVEKIT_URL;

    if (!apiKey || !apiSecret || !url) {
      throw new Error("Missing LiveKit environment variables");
    }

    const room = "jarvis-room";
    const identity = "user-" + Math.floor(Math.random() * 1000);

    const at = new AccessToken(apiKey, apiSecret, {
      identity,
    });

    at.addGrant({
      roomJoin: true,
      room,
      canPublish: true,
      canSubscribe: true,
    });

    const token = await at.toJwt();

    return NextResponse.json({
      url,
      token,
      room,
    });
  } catch (err: any) {
    console.error("❌ TOKEN ERROR:", err);

    return NextResponse.json(
      { error: err.message },
      { status: 500 }
    );
  }
}