"use client";

import { useEffect } from "react";
import { Room, RoomEvent } from "livekit-client";

export default function Home() {
  useEffect(() => {
    const start = async () => {
      try {
        // Fetch token from backend
        const res = await fetch("/api/token");
        const data = await res.json();

        console.log("🔗 Connection:", data);

        const room = new Room();

        // AI Voice Track
        room.on(RoomEvent.TrackSubscribed, (track) => {
          console.log("🔊 AI Voice received");

          if (track.kind === "audio") {
            const audioElement = track.attach();
            document.body.appendChild(audioElement);

            audioElement.play().catch((err) => {
              console.log("Autoplay blocked:", err);
            });
          }
        });

        // Connect
        await room.connect(data.url, data.token);

        // Enable Mic
        await room.localParticipant.setMicrophoneEnabled(true);

        console.log("🎤 Mic enabled");
      } catch (err) {
        console.error("❌ ERROR:", err);
      }
    };

    start();
  }, []);

  return (
    <main
      style={{
        height: "100vh",
        background: "black",
        color: "lime",
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        fontSize: "2rem",
      }}
    >
      JARVIS ONLINE
    </main>
  );
}