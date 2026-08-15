import { NextResponse } from "next/server";
import { AccessToken, RoomAgentDispatch, RoomConfiguration } from "livekit-server-sdk";

export async function POST() {
  try {
    const apiKey = process.env.LIVEKIT_API_KEY;
    const apiSecret = process.env.LIVEKIT_API_SECRET;
    const url = process.env.LIVEKIT_URL;

    if (!apiKey || !apiSecret || !url) {
      throw new Error("Missing LiveKit environment variables");
    }

    const room = "jarvis-room-" + Math.random().toString(36).substring(2, 10);
    const identity = "user-" + Math.floor(Math.random() * 1000);

    const roomConfig = new RoomConfiguration({
      agents: [
        new RoomAgentDispatch({ agentName: "jarvis-agent" }),
      ],
    });

    const at = new AccessToken(apiKey, apiSecret, {
      identity,
    });

    at.addGrant({
      roomJoin: true,
      room,
      canPublish: true,
      canSubscribe: true,
    });

    at.roomConfig = roomConfig;

    const token = await at.toJwt();

    return NextResponse.json({
      serverUrl: url,
      participantToken: token,
      roomName: room,
    });
  } catch (err: any) {
    console.error("❌ TOKEN ERROR:", err);
    return NextResponse.json({ error: err.message }, { status: 500 });
  }
}