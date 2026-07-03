import { NextResponse } from "next/server";
import { AccessToken } from "livekit-server-sdk";

export async function GET() {
  try {
    const apiKey = process.env.LIVEKIT_API_KEY!;
    const apiSecret = process.env.LIVEKIT_API_SECRET!;
    const wsUrl = process.env.NEXT_PUBLIC_LIVEKIT_URL!;

    const room = "jarvis-room";
    const identity = "user-" + Math.floor(Math.random() * 1000);

    const token = new AccessToken(apiKey, apiSecret, {
      identity,
    });

    token.addGrant({
      roomJoin: true,
      room: room,
    });

    const jwt = await token.toJwt();

    return NextResponse.json({
      token: jwt,
      url: wsUrl,
      room,
    });
  } catch (error) {
    console.error(error);

    return NextResponse.json(
      { error: "Token generation failed" },
      { status: 500 }
    );
  }
}