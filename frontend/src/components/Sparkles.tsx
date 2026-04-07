import { useRef } from "react";
import { motion } from "framer-motion";

const SPARKLE_COUNT = 18;

const sparkleData = Array.from({ length: SPARKLE_COUNT }, (_, i) => ({
  id: i,
  x: Math.random() * 100,
  y: Math.random() * 100,
  size: Math.random() * 8 + 4,
  delay: Math.random() * 4,
  duration: Math.random() * 3 + 3,
  color: [
    "#f9a8d4",
    "#e9d5ff",
    "#fcd34d",
    "#a78bfa",
    "#fb7185",
    "#6ee7b7",
  ][Math.floor(Math.random() * 6)],
}));

export function Sparkles() {
  return (
    <div className="fixed inset-0 pointer-events-none overflow-hidden z-0">
      {sparkleData.map((s) => (
        <motion.div
          key={s.id}
          className="absolute rounded-full"
          style={{
            left: `${s.x}%`,
            top: `${s.y}%`,
            width: s.size,
            height: s.size,
            backgroundColor: s.color,
            opacity: 0.5,
          }}
          animate={{
            y: [0, -30, 0],
            opacity: [0.3, 0.7, 0.3],
            scale: [1, 1.3, 1],
          }}
          transition={{
            duration: s.duration,
            delay: s.delay,
            repeat: Infinity,
            ease: "easeInOut",
          }}
        />
      ))}
    </div>
  );
}

export function useConfetti() {
  const fired = useRef(false);

  const fire = async () => {
    if (fired.current) return;
    fired.current = true;
    const confetti = (await import("canvas-confetti")).default;
    confetti({
      particleCount: 120,
      spread: 80,
      origin: { y: 0.6 },
      colors: ["#c026d3", "#f472b6", "#fbbf24", "#a78bfa", "#fb7185"],
      disableForReducedMotion: true,
    });
    setTimeout(() => { fired.current = false; }, 2000);
  };

  return fire;
}
