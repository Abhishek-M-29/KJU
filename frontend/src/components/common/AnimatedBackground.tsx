import { motion } from 'framer-motion'

interface Node {
  id: number
  x: number
  y: number
  size: number
}

interface Connection {
  from: number
  to: number
}

// Seeded random function for deterministic values
function seededRandom(seed: number): number {
  const x = Math.sin(seed * 9999) * 10000
  return x - Math.floor(x)
}

// Pre-computed nodes for the network mesh (deterministic)
const nodeCount = 20
const nodes: Node[] = Array.from({ length: nodeCount }, (_, i) => ({
  id: i,
  x: seededRandom(i * 3 + 1) * 100,
  y: seededRandom(i * 3 + 2) * 100,
  size: seededRandom(i * 3 + 3) * 4 + 2,
}))

// Create connections between nearby nodes
const connections: Connection[] = []
for (let i = 0; i < nodes.length; i++) {
  for (let j = i + 1; j < nodes.length; j++) {
    const dx = nodes[i].x - nodes[j].x
    const dy = nodes[i].y - nodes[j].y
    const distance = Math.sqrt(dx * dx + dy * dy)
    if (distance < 25) {
      connections.push({ from: i, to: j })
    }
  }
}

export function AnimatedBackground() {

  return (
    <div className="fixed inset-0 overflow-hidden pointer-events-none">
      <motion.svg
        className="w-full h-full opacity-30"
        viewBox="0 0 100 100"
        preserveAspectRatio="xMidYMid slice"
        animate={{ rotate: 360 }}
        transition={{ duration: 200, repeat: Infinity, ease: 'linear' }}
      >
        <defs>
          <linearGradient id="nodeGradient" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="var(--color-primary-light)" />
            <stop offset="100%" stopColor="var(--color-primary)" />
          </linearGradient>
          <filter id="glow">
            <feGaussianBlur stdDeviation="0.5" result="coloredBlur" />
            <feMerge>
              <feMergeNode in="coloredBlur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>

        {/* Connection lines */}
        {connections.map((conn, i) => (
          <motion.line
            key={`conn-${i}`}
            x1={nodes[conn.from].x}
            y1={nodes[conn.from].y}
            x2={nodes[conn.to].x}
            y2={nodes[conn.to].y}
            stroke="var(--color-primary-light)"
            strokeWidth="0.1"
            strokeOpacity="0.4"
            initial={{ pathLength: 0 }}
            animate={{ pathLength: 1 }}
            transition={{ duration: 2, delay: i * 0.05 }}
          />
        ))}

        {/* Nodes */}
        {nodes.map((node) => (
          <motion.circle
            key={`node-${node.id}`}
            cx={node.x}
            cy={node.y}
            r={node.size / 10}
            fill="url(#nodeGradient)"
            filter="url(#glow)"
            initial={{ scale: 0, opacity: 0 }}
            animate={{
              scale: [1, 1.2, 1],
              opacity: [0.6, 1, 0.6],
            }}
            transition={{
              duration: 3,
              repeat: Infinity,
              delay: node.id * 0.1,
            }}
          />
        ))}
      </motion.svg>
    </div>
  )
}
