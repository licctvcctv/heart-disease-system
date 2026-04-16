<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from 'vue';

const canvasEl = ref<HTMLCanvasElement | null>(null);

interface Particle {
  x: number;
  y: number;
  vx: number;
  vy: number;
}

let particles: Particle[] = [];
let animationFrame = 0;
let context: CanvasRenderingContext2D | null = null;
const particleCount = 64;
const connectionDistance = 150;

const createParticles = () => {
  particles = Array.from({ length: particleCount }, () => ({
    x: Math.random() * window.innerWidth,
    y: Math.random() * window.innerHeight,
    vx: (Math.random() - 0.5) * 0.42,
    vy: (Math.random() - 0.5) * 0.42,
  }));
};

const resize = () => {
  const canvas = canvasEl.value;
  if (!canvas) {
    return;
  }

  const ratio = window.devicePixelRatio || 1;
  canvas.width = Math.floor(window.innerWidth * ratio);
  canvas.height = Math.floor(window.innerHeight * ratio);
  canvas.style.width = `${window.innerWidth}px`;
  canvas.style.height = `${window.innerHeight}px`;
  context?.setTransform(ratio, 0, 0, ratio, 0, 0);
  createParticles();
};

const draw = () => {
  const canvas = canvasEl.value;
  if (!canvas || !context) {
    return;
  }

  const width = window.innerWidth;
  const height = window.innerHeight;
  context.clearRect(0, 0, width, height);

  particles.forEach((particle, index) => {
    particle.x += particle.vx;
    particle.y += particle.vy;

    if (particle.x < 0 || particle.x > width) {
      particle.vx *= -1;
    }
    if (particle.y < 0 || particle.y > height) {
      particle.vy *= -1;
    }

    context!.beginPath();
    context!.arc(particle.x, particle.y, 1.8, 0, Math.PI * 2);
    context!.fillStyle = 'rgba(6, 182, 212, 0.38)';
    context!.fill();

    for (let nextIndex = index + 1; nextIndex < particles.length; nextIndex += 1) {
      const nextParticle = particles[nextIndex];
      const dx = particle.x - nextParticle.x;
      const dy = particle.y - nextParticle.y;
      const distance = Math.sqrt(dx * dx + dy * dy);

      if (distance < connectionDistance) {
        context!.beginPath();
        context!.strokeStyle = `rgba(6, 182, 212, ${0.12 * (1 - distance / connectionDistance)})`;
        context!.lineWidth = 1;
        context!.moveTo(particle.x, particle.y);
        context!.lineTo(nextParticle.x, nextParticle.y);
        context!.stroke();
      }
    }
  });

  animationFrame = requestAnimationFrame(draw);
};

onMounted(() => {
  const canvas = canvasEl.value;
  if (!canvas) {
    return;
  }

  context = canvas.getContext('2d');
  if (!context) {
    return;
  }

  resize();
  draw();
  window.addEventListener('resize', resize);
});

onBeforeUnmount(() => {
  window.removeEventListener('resize', resize);
  cancelAnimationFrame(animationFrame);
});
</script>

<template>
  <canvas ref="canvasEl" class="particle-background" aria-hidden="true" />
</template>
